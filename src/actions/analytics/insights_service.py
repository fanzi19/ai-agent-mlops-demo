#!/usr/bin/env python3
"""
Insights Service - Single comprehensive insight updated with all data
"""

from flask import Flask, jsonify, request
import sqlite3
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List
import os
import requests
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class OllamaClient:
    def __init__(self, host="http://ollama-server:11434"):
        self.host = host
        self.model = "llama3.2:1b"
        self.available = self._check_availability()
    
    def _check_availability(self):
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_comprehensive_insights(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a single comprehensive insight using all data"""
        if not self.available:
            logger.warning("Ollama not available, using fallback insights")
            return self._fallback_comprehensive_insight(analytics_data)
        
        try:
            prompt = self._build_comprehensive_prompt(analytics_data)
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 800
                }
            }
            
            response = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_comprehensive_response(result.get('response', ''), analytics_data)
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return self._fallback_comprehensive_insight(analytics_data)
                
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return self._fallback_comprehensive_insight(analytics_data)
    
    def _build_comprehensive_prompt(self, data: Dict[str, Any]) -> str:
        """Build comprehensive analysis prompt using ALL data"""
        overview = data.get('overview', {})
        issue_dist = data.get('issue_distribution', [])
        sentiment_dist = data.get('sentiment_distribution', [])
        recent = data.get('recent_interactions', [])
        
        total = overview.get('total_interactions', 0)
        high_priority = overview.get('high_priority', 0)
        negative = overview.get('negative_sentiment', 0)
        
        # Calculate comprehensive metrics
        high_priority_rate = (high_priority / total * 100) if total > 0 else 0
        negative_rate = (negative / total * 100) if total > 0 else 0
        
        # Analyze patterns across all data
        top_issues = sorted(issue_dist, key=lambda x: x['count'], reverse=True)[:3]
        
        prompt = f"""
You are an expert customer service analyst. Analyze ALL the data comprehensively and provide a single, detailed business intelligence summary.

COMPLETE DATA ANALYSIS:
📊 OVERALL METRICS:
- Total interactions analyzed: {total}
- High priority cases: {high_priority} ({high_priority_rate:.1f}%)
- Negative sentiment: {negative} ({negative_rate:.1f}%)
- Average confidence: {overview.get('avg_confidence', 0):.1f}
- Average response time: {overview.get('avg_response_time', 0):.1f}ms

🎯 TOP ISSUE TYPES:
{self._format_issue_analysis(top_issues)}

😊 SENTIMENT BREAKDOWN:
{self._format_sentiment_analysis(sentiment_dist)}

🔍 RECENT PATTERNS:
{self._analyze_comprehensive_patterns(recent)}

Provide a comprehensive business insight in this EXACT format:

{{
  "title": "Customer Service Analytics Summary",
  "overview": "Brief 2-sentence overview of current situation",
  "key_findings": [
    "Finding 1 with specific data",
    "Finding 2 with specific data", 
    "Finding 3 with specific data"
  ],
  "alerts": [
    "Any critical issues requiring immediate attention"
  ],
  "recommendations": [
    "Specific actionable recommendation 1",
    "Specific actionable recommendation 2"
  ],
  "trends": "Description of patterns observed across all data"
}}

Focus on actionable insights, specific data points, and business impact. Respond ONLY with valid JSON.
"""
        return prompt
    
    def _format_issue_analysis(self, issues):
        """Format issue distribution for prompt"""
        if not issues:
            return "No issue data available"
        
        result = []
        for issue in issues:
            result.append(f"- {issue['issue_type']}: {issue['count']} cases")
        return "\n".join(result)
    
    def _format_sentiment_analysis(self, sentiments):
        """Format sentiment distribution for prompt"""
        if not sentiments:
            return "No sentiment data available"
        
        result = []
        for sentiment in sentiments:
            result.append(f"- {sentiment['sentiment'].title()}: {sentiment['count']} cases")
        return "\n".join(result)
    
    def _analyze_comprehensive_patterns(self, recent_interactions):
        """Analyze patterns across all recent interactions"""
        if not recent_interactions:
            return "No recent interaction data available"
        
        # Analyze customer tiers
        tiers = {}
        issues_by_priority = {'high': 0, 'medium': 0, 'low': 0}
        
        for interaction in recent_interactions:
            tier = interaction.get('customer_tier', 'unknown')
            tiers[tier] = tiers.get(tier, 0) + 1
            
            priority = interaction.get('priority', 'medium')
            if priority in issues_by_priority:
                issues_by_priority[priority] += 1
        
        return f"""
- Customer tier distribution: {dict(tiers)}
- Priority distribution: {dict(issues_by_priority)}
- Recent interaction volume: {len(recent_interactions)} cases
"""
    
    def _parse_comprehensive_response(self, response: str, analytics_data: Dict) -> Dict[str, Any]:
        """Parse comprehensive Ollama response"""
        try:
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = response[start:end]
                parsed = json.loads(json_str)
                
                # Add metadata
                parsed['generated_at'] = datetime.now().isoformat()
                parsed['data_points'] = analytics_data.get('overview', {}).get('total_interactions', 0)
                parsed['type'] = 'comprehensive_analysis'
                parsed['severity'] = self._determine_severity(analytics_data)
                
                return parsed
            
            logger.warning("Could not parse Ollama response, using fallback")
            return self._fallback_comprehensive_insight(analytics_data)
            
        except Exception as e:
            logger.error(f"Error parsing comprehensive response: {e}")
            return self._fallback_comprehensive_insight(analytics_data)
    
    def _determine_severity(self, data: Dict) -> str:
        """Determine overall severity based on data"""
        overview = data.get('overview', {})
        total = overview.get('total_interactions', 0)
        
        if total == 0:
            return 'low'
        
        high_priority_rate = (overview.get('high_priority', 0) / total * 100) if total > 0 else 0
        negative_rate = (overview.get('negative_sentiment', 0) / total * 100) if total > 0 else 0
        
        if high_priority_rate > 40 or negative_rate > 50:
            return 'high'
        elif high_priority_rate > 20 or negative_rate > 30:
            return 'medium'
        else:
            return 'low'
    
    def _fallback_comprehensive_insight(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive fallback insight"""
        overview = data.get('overview', {})
        total = overview.get('total_interactions', 0)
        
        if total == 0:
            return {
                "title": "Customer Service Analytics Summary",
                "overview": "No customer interactions data available yet. Start processing customer requests to generate insights.",
                "key_findings": ["No data to analyze"],
                "alerts": [],
                "recommendations": ["Begin collecting customer interaction data"],
                "trends": "Insufficient data for trend analysis",
                "generated_at": datetime.now().isoformat(),
                "data_points": 0,
                "type": "comprehensive_analysis",
                "severity": "low"
            }
        
        high_priority = overview.get('high_priority', 0)
        negative = overview.get('negative_sentiment', 0)
        
        high_priority_rate = (high_priority / total * 100) if total > 0 else 0
        negative_rate = (negative / total * 100) if total > 0 else 0
        
        alerts = []
        if high_priority_rate > 30:
            alerts.append(f"High priority issue spike: {high_priority_rate:.1f}% of cases need urgent attention")
        if negative_rate > 40:
            alerts.append(f"Customer satisfaction concern: {negative_rate:.1f}% negative sentiment detected")
        
        return {
            "title": "Customer Service Analytics Summary",
            "overview": f"Analyzed {total} customer interactions with {high_priority_rate:.1f}% high priority and {negative_rate:.1f}% negative sentiment.",
            "key_findings": [
                f"Total interactions processed: {total}",
                f"High priority cases: {high_priority} ({high_priority_rate:.1f}%)",
                f"Customer satisfaction: {100-negative_rate:.1f}% positive/neutral sentiment"
            ],
            "alerts": alerts if alerts else ["System operating within normal parameters"],
            "recommendations": [
                "Continue monitoring customer satisfaction trends",
                "Review high priority case resolution processes" if high_priority_rate > 20 else "Maintain current service levels"
            ],
            "trends": "Stable operational metrics observed" if not alerts else "Attention needed in highlighted areas",
            "generated_at": datetime.now().isoformat(),
            "data_points": total,
            "type": "comprehensive_analysis",
            "severity": self._determine_severity(data)
        }

class InsightsService:
    def __init__(self):
        self.db_path = "/workspace/data/analytics.db"
        self.ollama = OllamaClient()
        self.last_insight_time = datetime.now()
        self.last_interaction_count = 0
        self.setup_database()
        
        # Start monitoring thread
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("🔍 Comprehensive Insights Service started")
    
    def setup_database(self):
        """Setup single comprehensive insight table"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Drop old insights table and create new comprehensive one
                cursor.execute('DROP TABLE IF EXISTS insights')
                
                cursor.execute('''
                    CREATE TABLE comprehensive_insight (
                        id INTEGER PRIMARY KEY,
                        title TEXT,
                        overview TEXT,
                        key_findings TEXT,
                        alerts TEXT,
                        recommendations TEXT,
                        trends TEXT,
                        severity TEXT,
                        data_points INTEGER,
                        generated_at DATETIME,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                logger.info("✅ Comprehensive insights database setup complete")
                
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
    
    def _monitor_loop(self):
        """Monitor and update comprehensive insight every 10 seconds"""
        while self.running:
            try:
                self._check_for_insight_update()
                time.sleep(10)
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
                time.sleep(10)
    
    def _check_for_insight_update(self):
        """Check if comprehensive insight needs updating"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get current interaction count
                cursor.execute("SELECT COUNT(*) FROM interactions")
                current_count = cursor.fetchone()[0]
                
                # Update insight if we have 5+ new interactions OR no insight exists
                new_interactions = current_count - self.last_interaction_count
                
                cursor.execute("SELECT COUNT(*) FROM comprehensive_insight")
                insight_exists = cursor.fetchone()[0] > 0
                
                if new_interactions >= 5 or not insight_exists:
                    logger.info(f"🔍 Updating comprehensive insight: {new_interactions} new interactions")
                    self._update_comprehensive_insight()
                    self.last_interaction_count = current_count
                    self.last_insight_time = datetime.now()
                
        except Exception as e:
            logger.error(f"Error checking insight update: {e}")
    
    def _update_comprehensive_insight(self):
        """Update the single comprehensive insight with ALL data"""
        try:
            # Get ALL analytics data
            analytics_data = self._get_all_analytics_data()
            
            # Generate comprehensive insight using Ollama
            insight = self.ollama.generate_comprehensive_insights(analytics_data)
            
            # Store/update the single comprehensive insight
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Clear existing insight and insert new one
                cursor.execute('DELETE FROM comprehensive_insight')
                
                cursor.execute('''
                    INSERT INTO comprehensive_insight 
                    (title, overview, key_findings, alerts, recommendations, trends, 
                     severity, data_points, generated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    insight.get('title', 'Analytics Summary'),
                    insight.get('overview', ''),
                    json.dumps(insight.get('key_findings', [])),
                    json.dumps(insight.get('alerts', [])),
                    json.dumps(insight.get('recommendations', [])),
                    insight.get('trends', ''),
                    insight.get('severity', 'low'),
                    insight.get('data_points', 0),
                    insight.get('generated_at', datetime.now().isoformat())
                ))
                
                conn.commit()
                logger.info(f"✅ Updated comprehensive insight with {insight.get('data_points', 0)} data points")
                
        except Exception as e:
            logger.error(f"Error updating comprehensive insight: {e}")
    
    def _get_all_analytics_data(self):
        """Get ALL analytics data for comprehensive analysis"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get overview metrics (ALL TIME)
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_interactions,
                        COUNT(CASE WHEN priority = 'high' THEN 1 END) as high_priority,
                        COUNT(CASE WHEN sentiment = 'negative' THEN 1 END) as negative_sentiment,
                        COUNT(CASE WHEN email_sent = 1 THEN 1 END) as emails_sent,
                        AVG(confidence) as avg_confidence,
                        AVG(response_time_ms) as avg_response_time
                    FROM interactions
                ''')
                
                overview = cursor.fetchone()
                
                # Get issue distribution (ALL TIME)
                cursor.execute('''
                    SELECT issue_type, COUNT(*) as count
                    FROM interactions
                    GROUP BY issue_type
                    ORDER BY count DESC
                ''')
                
                issue_distribution = cursor.fetchall()
                
                # Get sentiment distribution (ALL TIME)
                cursor.execute('''
                    SELECT sentiment, COUNT(*) as count
                    FROM interactions
                    GROUP BY sentiment
                ''')
                
                sentiment_distribution = cursor.fetchall()
                
                # Get recent interactions for pattern analysis
                cursor.execute('''
                    SELECT timestamp, customer_id, customer_tier, issue_type, 
                           sentiment, priority, email_sent
                    FROM interactions 
                    ORDER BY timestamp DESC
                    LIMIT 20
                ''')
                
                recent_interactions = cursor.fetchall()
                
                return {
                    "overview": {
                        "total_interactions": overview[0] if overview else 0,
                        "high_priority": overview[1] if overview else 0,
                        "negative_sentiment": overview[2] if overview else 0,
                        "emails_sent": overview[3] if overview else 0,
                        "avg_confidence": round(overview[4] or 0, 3) if overview else 0,
                        "avg_response_time": round(overview[5] or 0, 1) if overview else 0
                    },
                    "issue_distribution": [
                        {"issue_type": row[0], "count": row[1]}
                        for row in issue_distribution
                    ],
                    "sentiment_distribution": [
                        {"sentiment": row[0], "count": row[1]}
                        for row in sentiment_distribution
                    ],
                    "recent_interactions": [
                        {
                            "timestamp": row[0],
                            "customer_id": row[1],
                            "customer_tier": row[2],
                            "issue_type": row[3],
                            "sentiment": row[4],
                            "priority": row[5],
                            "email_sent": bool(row[6])
                        }
                        for row in recent_interactions
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error getting analytics data: {e}")
            return {"overview": {}, "issue_distribution": [], "sentiment_distribution": [], "recent_interactions": []}
    
    def get_comprehensive_insight(self):
        """Get the single comprehensive insight"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT title, overview, key_findings, alerts, recommendations, 
                           trends, severity, data_points, generated_at
                    FROM comprehensive_insight 
                    ORDER BY updated_at DESC
                    LIMIT 1
                ''')
                
                result = cursor.fetchone()
                
                if result:
                    return {
                        "title": result[0],
                        "overview": result[1],
                        "key_findings": json.loads(result[2]) if result[2] else [],
                        "alerts": json.loads(result[3]) if result[3] else [],
                        "recommendations": json.loads(result[4]) if result[4] else [],
                        "trends": result[5],
                        "severity": result[6],
                        "data_points": result[7],
                        "generated_at": result[8],
                        "type": "comprehensive_analysis"
                    }
                else:
                    # No insight exists, trigger generation
                    self._update_comprehensive_insight()
                    return {
                        "title": "Generating Comprehensive Insight...",
                        "overview": "Analysis in progress, please refresh in a moment.",
                        "key_findings": [],
                        "alerts": [],
                        "recommendations": [],
                        "trends": "",
                        "severity": "low",
                        "data_points": 0,
                        "generated_at": datetime.now().isoformat(),
                        "type": "comprehensive_analysis"
                    }
                
        except Exception as e:
            logger.error(f"Error getting comprehensive insight: {e}")
            return {
                "title": "Error Loading Insight",
                "overview": f"Error: {str(e)}",
                "key_findings": [],
                "alerts": [],
                "recommendations": [],
                "trends": "",
                "severity": "low",
                "data_points": 0,
                "generated_at": datetime.now().isoformat(),
                "type": "comprehensive_analysis"
            }

# Initialize service
insights_service = InsightsService()

# Flask API Routes
@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "comprehensive-insights-service",
        "ollama_available": insights_service.ollama.available,
        "last_insight_time": insights_service.last_insight_time.isoformat()
    })

@app.route('/api/insights')
def get_insights():
    """Get the comprehensive insight"""
    insight = insights_service.get_comprehensive_insight()
    
    return jsonify({
        "status": "success",
        "insights": [insight],  # Return as array for dashboard compatibility
        "count": 1,
        "last_updated": insights_service.last_insight_time.isoformat()
    })

@app.route('/api/insights/generate', methods=['POST'])
def force_generate():
    """Manually trigger comprehensive insight update"""
    try:
        insights_service._update_comprehensive_insight()
        return jsonify({"status": "success", "message": "Comprehensive insight updated"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == '__main__':
    print("🔍 Starting Comprehensive Insights Service...")
    print("📊 Service will be available at: http://localhost:5003")
    print("🤖 Single comprehensive insight with ALL data")
    print("⏰ Updates every 5 new interactions")
    print("🎯 Analyzes complete dataset each time")
    
    app.run(host='0.0.0.0', port=5003, debug=False)