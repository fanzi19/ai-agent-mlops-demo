"""
Enhanced Analytics Action Plugin - comprehensive logging and insights
"""

from typing import Dict, Any
import logging
from datetime import datetime, timedelta
import json
from pathlib import Path
import sqlite3
import os

from .base_action import BaseAction

logger = logging.getLogger(__name__)

class AnalyticsAction(BaseAction):
    """Enhanced analytics with database storage and insights"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.priority = 100  # Low priority
        self.analytics_file = config.get('log_file', '/workspace/logs/analytics.jsonl')
        self.db_path = config.get('db_path', '/workspace/data/analytics.db')
        self._ensure_directories()
        self._setup_database()
    
    def _ensure_directories(self):
        """Ensure analytics directories exist"""
        Path(self.analytics_file).parent.mkdir(parents=True, exist_ok=True)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _setup_database(self):
        """Initialize SQLite database for analytics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create interactions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS interactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        customer_id TEXT,
                        customer_tier TEXT,
                        issue_type TEXT,
                        sentiment TEXT,
                        predicted_satisfaction TEXT,
                        priority TEXT,
                        confidence REAL,
                        message_length INTEGER,
                        email_triggered BOOLEAN,
                        response_time_ms INTEGER
                    )
                ''')
                
                # Create daily summaries table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS daily_summaries (
                        date TEXT PRIMARY KEY,
                        total_interactions INTEGER,
                        high_priority_count INTEGER,
                        negative_sentiment_count INTEGER,
                        email_alerts_count INTEGER,
                        avg_confidence REAL,
                        top_issue_type TEXT
                    )
                ''')
                
                conn.commit()
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
    
    def should_execute(self, ai_response: Dict[str, Any], customer_context: Dict[str, Any]) -> bool:
        """Analytics should always run unless explicitly disabled"""
        return not customer_context.get('disable_analytics', False)
    
    def _log_to_file(self, analytics_record: Dict[str, Any]):
        """Log to JSONL file (backward compatibility)"""
        try:
            with open(self.analytics_file, 'a') as f:
                f.write(json.dumps(analytics_record) + '\n')
        except Exception as e:
            logger.error(f"File logging failed: {e}")
    
    def _log_to_database(self, ai_response: Dict[str, Any], customer_context: Dict[str, Any]):
        """Log to SQLite database for better analytics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Extract data
                customer_id = customer_context.get('customer_id', 'unknown')
                customer_tier = customer_context.get('tier', 'standard')
                message_length = len(customer_context.get('message', ''))
                response_time_ms = customer_context.get('response_time_ms', 0)
                
                # AI predictions
                issue_type = ai_response.get('issue_type', 'unknown')
                sentiment = ai_response.get('sentiment', 'neutral')
                predicted_satisfaction = ai_response.get('predicted_satisfaction', 'medium')
                priority = ai_response.get('recommended_priority', 'medium')
                confidence = ai_response.get('confidence', 0.0)
                
                # Check if email was triggered
                actions_executed = ai_response.get('actions_executed', [])
                email_triggered = 'EmailAction' in actions_executed
                
                # Insert into database
                cursor.execute('''
                    INSERT INTO interactions 
                    (customer_id, customer_tier, issue_type, sentiment,
                     predicted_satisfaction, priority, confidence, message_length,
                     email_triggered, response_time_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    customer_id, customer_tier, issue_type, sentiment,
                    predicted_satisfaction, priority, confidence, message_length,
                    email_triggered, response_time_ms
                ))
                
                conn.commit()
                return cursor.lastrowid
                
        except Exception as e:
            logger.error(f"Database logging failed: {e}")
            return None
    
    def _update_daily_summary(self):
        """Update daily summary statistics"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Calculate today's metrics
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total,
                        COUNT(CASE WHEN priority = 'high' THEN 1 END) as high_priority,
                        COUNT(CASE WHEN sentiment = 'negative' THEN 1 END) as negative_sentiment,
                        COUNT(CASE WHEN email_triggered = 1 THEN 1 END) as email_alerts,
                        AVG(confidence) as avg_confidence
                    FROM interactions 
                    WHERE DATE(timestamp) = ?
                ''', (today,))
                
                metrics = cursor.fetchone()
                
                if metrics and metrics[0] > 0:  # If there are interactions today
                    total, high_priority, negative_sentiment, email_alerts, avg_confidence = metrics
                    
                    # Get top issue type for today
                    cursor.execute('''
                        SELECT issue_type, COUNT(*) as count
                        FROM interactions 
                        WHERE DATE(timestamp) = ?
                        GROUP BY issue_type
                        ORDER BY count DESC
                        LIMIT 1
                    ''', (today,))
                    
                    top_issue_result = cursor.fetchone()
                    top_issue_type = top_issue_result[0] if top_issue_result else 'unknown'
                    
                    # Insert or update daily summary
                    cursor.execute('''
                        INSERT OR REPLACE INTO daily_summaries
                        (date, total_interactions, high_priority_count, negative_sentiment_count,
                         email_alerts_count, avg_confidence, top_issue_type)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        today, total, high_priority, negative_sentiment,
                        email_alerts, avg_confidence, top_issue_type
                    ))
                    
                    conn.commit()
                    
                    return {
                        'daily_summary_updated': True,
                        'date': today,
                        'total_interactions': total,
                        'high_priority_count': high_priority,
                        'negative_sentiment_count': negative_sentiment,
                        'email_alerts_count': email_alerts,
                        'avg_confidence': round(avg_confidence or 0, 3),
                        'top_issue_type': top_issue_type
                    }
                    
        except Exception as e:
            logger.error(f"Daily summary update failed: {e}")
            return None
    
    def _generate_insights(self):
        """Generate simple insights from recent data"""
        try:
            insights = []
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check for high negative sentiment in last 24 hours
                cursor.execute('''
                    SELECT COUNT(*) 
                    FROM interactions 
                    WHERE sentiment = 'negative' 
                    AND timestamp >= datetime('now', '-1 day')
                ''')
                
                negative_count = cursor.fetchone()[0]
                
                if negative_count > 5:  # Threshold
                    insights.append({
                        'type': 'alert',
                        'message': f'High negative sentiment detected: {negative_count} cases in last 24h',
                        'severity': 'medium'
                    })
                
                # Check for high priority issues
                cursor.execute('''
                    SELECT COUNT(*) 
                    FROM interactions 
                    WHERE priority = 'high' 
                    AND timestamp >= datetime('now', '-1 day')
                ''')
                
                high_priority_count = cursor.fetchone()[0]
                
                if high_priority_count > 3:  # Threshold
                    insights.append({
                        'type': 'alert',
                        'message': f'High priority issues spike: {high_priority_count} cases in last 24h',
                        'severity': 'high'
                    })
                
                # Most common issue type today
                cursor.execute('''
                    SELECT issue_type, COUNT(*) as count
                    FROM interactions 
                    WHERE DATE(timestamp) = DATE('now')
                    GROUP BY issue_type
                    ORDER BY count DESC
                    LIMIT 1
                ''')
                
                top_issue = cursor.fetchone()
                if top_issue and top_issue[1] > 2:
                    insights.append({
                        'type': 'trend',
                        'message': f'Most common issue today: {top_issue[0]} ({top_issue[1]} cases)',
                        'severity': 'info'
                    })
                
                return insights
                
        except Exception as e:
            logger.error(f"Insights generation failed: {e}")
            return []
    
    async def execute(self, ai_response: Dict[str, Any], customer_context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced analytics logging and processing"""
        
        try:
            # Create analytics record for file logging (backward compatibility)
            analytics_record = {
                'timestamp': datetime.now().isoformat(),
                'customer_id': customer_context.get('customer_id', 'unknown'),
                'customer_tier': customer_context.get('tier', 'standard'),
                'ai_prediction': ai_response,
                'message_length': len(customer_context.get('message', ''))
            }
            
            # Log to file (existing functionality)
            self._log_to_file(analytics_record)
            
            # Log to database (new functionality)
            interaction_id = self._log_to_database(ai_response, customer_context)
            
            # Update daily summary every 10th interaction
            daily_summary = None
            if interaction_id and interaction_id % 10 == 0:
                daily_summary = self._update_daily_summary()
            
            # Generate insights periodically
            insights = []
            if interaction_id and interaction_id % 20 == 0:
                insights = self._generate_insights()
            
            result = {
                'action': 'analytics',
                'status': 'success',
                'records_logged': 1,
                'interaction_id': interaction_id,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add optional data
            if daily_summary:
                result['daily_summary'] = daily_summary
            
            if insights:
                result['insights'] = insights
                result['insights_count'] = len(insights)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Analytics processing failed: {e}")
            return {
                'action': 'analytics',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_analytics_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get analytics summary for specified days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get summary for last N days
                cursor.execute('''
                    SELECT * FROM daily_summaries
                    WHERE date >= date('now', '-{} days')
                    ORDER BY date DESC
                '''.format(days))
                
                summaries = cursor.fetchall()
                
                # Get issue type distribution
                cursor.execute('''
                    SELECT issue_type, COUNT(*) as count
                    FROM interactions 
                    WHERE timestamp >= datetime('now', '-{} days')
                    GROUP BY issue_type
                    ORDER BY count DESC
                '''.format(days))
                
                issue_distribution = cursor.fetchall()
                
                return {
                    'summary_available': True,
                    'period_days': days,
                    'daily_summaries': summaries,
                    'issue_distribution': issue_distribution,
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Analytics summary failed: {e}")
            return {
                'summary_available': False,
                'error': str(e)
            }