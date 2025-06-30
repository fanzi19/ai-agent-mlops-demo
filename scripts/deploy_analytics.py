#!/usr/bin/env python3
"""
Analytics Action Module for AI Customer Support
Tracks metrics and generates insights
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any
from pathlib import Path

class AnalyticsAction:
    def __init__(self):
        self.name = "AnalyticsAction"
        self.enabled = True
        self.db_path = "/workspace/data/analytics.db"
        self.setup_database()
    
    def setup_database(self):
        """Initialize SQLite database for analytics"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
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
                    email_sent BOOLEAN,
                    response_time_ms INTEGER
                )
            ''')
            
            conn.commit()
    
    def should_execute(self, prediction: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Analytics should always execute to track all interactions"""
        return True
    
    def execute(self, prediction: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analytics tracking"""
        try:
            # Extract data
            customer_id = context.get("customer_id", "unknown")
            customer_tier = context.get("tier", "standard")
            message = context.get("message", "")
            
            issue_type = prediction.get("issue_type", "unknown")
            sentiment = prediction.get("sentiment", "neutral")
            predicted_satisfaction = prediction.get("predicted_satisfaction", "medium")
            priority = prediction.get("recommended_priority", "medium")
            confidence = prediction.get("confidence", 0.0)
            
            # Check if email was sent
            actions_executed = prediction.get("actions_executed", [])
            email_sent = "EmailAction" in actions_executed
            
            # Calculate metrics
            message_length = len(message)
            response_time_ms = context.get("response_time_ms", 0)
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO interactions 
                    (customer_id, customer_tier, issue_type, sentiment, 
                     predicted_satisfaction, priority, confidence, message_length,
                     email_sent, response_time_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    customer_id, customer_tier, issue_type, sentiment,
                    predicted_satisfaction, priority, confidence, message_length,
                    email_sent, response_time_ms
                ))
                conn.commit()
                interaction_id = cursor.lastrowid
            
            return {
                "tracked": True,
                "interaction_id": interaction_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "tracked": False,
                "error": str(e)
            }
    
    def get_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get analytics summary"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get metrics for last N days
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_interactions,
                        COUNT(CASE WHEN priority = 'high' THEN 1 END) as high_priority,
                        COUNT(CASE WHEN sentiment = 'negative' THEN 1 END) as negative_sentiment,
                        COUNT(CASE WHEN email_sent = 1 THEN 1 END) as emails_sent,
                        AVG(confidence) as avg_confidence
                    FROM interactions 
                    WHERE timestamp >= datetime('now', '-{} days')
                '''.format(days))
                
                metrics = cursor.fetchone()
                
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
                    "period_days": days,
                    "total_interactions": metrics[0] if metrics else 0,
                    "high_priority_count": metrics[1] if metrics else 0,
                    "negative_sentiment_count": metrics[2] if metrics else 0,
                    "emails_sent": metrics[3] if metrics else 0,
                    "avg_confidence": round(metrics[4] or 0, 3) if metrics else 0,
                    "issue_distribution": dict(issue_distribution),
                    "generated_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {"error": str(e)}

# Test function
def test_analytics():
    """Test analytics functionality"""
    print("🧪 Testing Analytics Action")
    analytics = AnalyticsAction()
    
    # Test data
    test_prediction = {
        "issue_type": "billing",
        "sentiment": "negative", 
        "predicted_satisfaction": "low",
        "recommended_priority": "high",
        "confidence": 0.85,
        "actions_executed": ["EmailAction"]
    }
    
    test_context = {
        "customer_id": "TEST001",
        "tier": "vip",
        "message": "I have a billing problem",
        "response_time_ms": 150
    }
    
    result = analytics.execute(test_prediction, test_context)
    print("Analytics Result:", json.dumps(result, indent=2))
    
    # Get summary
    summary = analytics.get_summary()
    print("Summary:", json.dumps(summary, indent=2))

if __name__ == "__main__":
    test_analytics()
