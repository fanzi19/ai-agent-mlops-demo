#!/usr/bin/env python3
"""
Ray Serve Customer Support AI Agent with Email and Analytics Actions
"""

import ray
from ray import serve
import joblib
import pandas as pd
import numpy as np
from scipy.sparse import hstack
import re
import os
import time
# Import email and analytics functionality
import sys
sys.path.append('/workspace/scripts')
from deploy_email import GmailEmailAction
from deploy_analytics import AnalyticsAction

@serve.deployment(num_replicas=1)
class CustomerSupportAgent:
    def __init__(self):
        self.model_dir = "/workspace/models"
        self.is_ready = False
        # Initialize actions
        self.email_action = GmailEmailAction()
        self.analytics_action = AnalyticsAction()
        self.load_models()
    
    def load_models(self):
        try:
            print("🤖 Loading Customer Support AI model components...")
            
            self.vectorizer = joblib.load(f"{self.model_dir}/tfidf_vectorizer.pkl")
            self.issue_classifier = joblib.load(f"{self.model_dir}/issue_classifier.pkl")
            self.sentiment_classifier = joblib.load(f"{self.model_dir}/sentiment_classifier.pkl")
            self.satisfaction_regressor = joblib.load(f"{self.model_dir}/satisfaction_regressor.pkl")
            
            print(f"Vectorizer vocabulary size: {len(self.vectorizer.vocabulary_)}")
            print("✅ All model components loaded successfully!")
            self.is_ready = True
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            raise

    def add_features(self, df):
        """Add engineered features exactly like training"""
        # Add text length features
        df['message_length'] = df['message'].str.len()
        df['word_count'] = df['message'].str.split().str.len()
        
        # Add negative sentiment indicators
        negative_patterns = [
            r'\b(bad|terrible|awful|horrible|worst|hate|angry|frustrated|disappointed)\b',
            r'\b(can\'t|cannot|won\'t|don\'t|never|no|not)\b',
            r'\b(lost|missing|broken|damaged|wrong|error|fail|problem)\b',
            r'[!]{2,}',  # Multiple exclamation marks
            r'[?]{2,}'   # Multiple question marks
        ]
        
        df['negative_indicators'] = 0
        for pattern in negative_patterns:
            df['negative_indicators'] += df['message'].str.count(pattern, flags=re.IGNORECASE)
        
        # Add positive sentiment indicators
        positive_patterns = [
            r'\b(great|excellent|amazing|wonderful|fantastic|perfect|love|thank|good)\b',
            r'\b(yes|absolutely|definitely|sure|of course)\b'
        ]
        
        df['positive_indicators'] = 0
        for pattern in positive_patterns:
            df['positive_indicators'] += df['message'].str.count(pattern, flags=re.IGNORECASE)
            
        # Add urgency indicators
        urgency_patterns = [
            r'\b(urgent|asap|immediately|quickly|fast|emergency|critical)\b',
            r'\b(help|please|need)\b',
            r'[!]{1,}'  # Exclamation marks
        ]
        
        df['urgency_indicators'] = 0
        for pattern in urgency_patterns:
            df['urgency_indicators'] += df['message'].str.count(pattern, flags=re.IGNORECASE)
            
        return df

    def prepare_features(self, customer_message: str):
        """Prepare features exactly like training"""
        try:
            # Create DataFrame with message
            df = pd.DataFrame([{'message': customer_message}])
            
            # Add engineered features exactly like training
            df = self.add_features(df)
            
            # Prepare text features
            X_text = self.vectorizer.transform(df['message'])
            
            # Combine text features with engineered features
            feature_cols = ['message_length', 'word_count', 'negative_indicators', 
                           'positive_indicators', 'urgency_indicators']
            X_features = df[feature_cols].values
            
            # Combine all features exactly like training
            X_combined = hstack([X_text, X_features])
            
            return X_combined
            
        except Exception as e:
            print(f"❌ Error in prepare_features: {e}")
            raise

    async def __call__(self, request):
        if not self.is_ready:
            return {"error": "Model not loaded", "status": "failed"}
        
        # Track request start time for analytics
        start_time = time.time()
        
        try:
            if hasattr(request, 'json'):
                data = await request.json()
            else:
                data = request
            
            # Get data from external client request
            customer_message = data.get('message', '')
            customer_id = data.get('customer_id', 'UNKNOWN')
            customer_tier = data.get('customer_tier', 'standard')
            
            if not customer_message:
                return {"error": "No message provided", "status": "failed"}
            
            print(f"🔍 Processing: {customer_id} - '{customer_message[:50]}...'")
            
            # Prepare features exactly like training
            features = self.prepare_features(customer_message)
            
            # Make predictions
            issue_pred = self.issue_classifier.predict(features)[0]
            sentiment_pred = self.sentiment_classifier.predict(features)[0] 
            satisfaction_pred = self.satisfaction_regressor.predict(features)[0]
            
            # Get confidence
            issue_confidence = float(self.issue_classifier.predict_proba(features)[0].max())
            sentiment_confidence = float(self.sentiment_classifier.predict_proba(features)[0].max())
            
            # Determine priority based on sentiment and satisfaction
            if sentiment_pred == 'negative' and satisfaction_pred == 'low':
                priority = 'high'
            elif sentiment_pred == 'positive' and satisfaction_pred == 'high':
                priority = 'low'
            elif sentiment_pred == 'negative':
                priority = 'high'
            elif satisfaction_pred == 'low':
                priority = 'high'
            else:
                priority = 'medium'
            
            # Calculate response time for analytics
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Execute actions
            actions_executed = []
            actions_skipped = []
            action_results = {}
            
            prediction = {
                "issue_type": issue_pred,
                "sentiment": sentiment_pred,
                "predicted_satisfaction": satisfaction_pred,
                "recommended_priority": priority,
                "confidence": round((issue_confidence + sentiment_confidence) / 2, 3)
            }
            
            customer_context = {
                'customer_id': customer_id,
                'tier': customer_tier,
                'message': customer_message,
                'response_time_ms': response_time_ms
            }
            
            # Execute Email Action
            try:
                if self.email_action.should_execute(prediction, customer_context):
                    email_result = self.email_action.execute(prediction, customer_context)
                    actions_executed.append("EmailAction")
                    action_results["EmailAction"] = email_result
                else:
                    actions_skipped.append("EmailAction")
                    
            except Exception as e:
                print(f"❌ Email action failed: {e}")
                action_results["EmailAction"] = {"error": str(e)}
                actions_skipped.append("EmailAction")
            
            # Execute Analytics Action (always runs)
            try:
                # Update prediction with executed actions for analytics
                prediction["actions_executed"] = actions_executed
                analytics_result = self.analytics_action.execute(prediction, customer_context)
                actions_executed.append("AnalyticsAction")
                action_results["AnalyticsAction"] = analytics_result
                    
            except Exception as e:
                print(f"❌ Analytics action failed: {e}")
                action_results["AnalyticsAction"] = {"error": str(e)}
                actions_skipped.append("AnalyticsAction")
            
            # Build response
            response = {
                "status": "success",
                "message": customer_message,
                "issue_type": issue_pred,
                "sentiment": sentiment_pred,
                "predicted_satisfaction": satisfaction_pred,
                "confidence": round((issue_confidence + sentiment_confidence) / 2, 3),
                "recommended_priority": priority,
                "timestamp": pd.Timestamp.now().isoformat(),
                "actions_executed": actions_executed,
                "actions_skipped": actions_skipped,
                "action_results": action_results
            }
            
            print(f"✅ Prediction: {issue_pred} | {sentiment_pred} | {satisfaction_pred} | {priority}")
            return response
            
        except Exception as e:
            print(f"❌ Prediction error: {str(e)}")
            return {"error": str(e), "status": "failed"}

@serve.deployment
class AnalyticsEndpoint:
    def __init__(self):
        try:
            import sys
            sys.path.append('/workspace/scripts')
            from deploy_analytics import AnalyticsAction
            self.analytics_action = AnalyticsAction()
        except Exception as e:
            print(f"❌ Failed to load analytics: {e}")
            self.analytics_action = None
    
    async def __call__(self, request):
        if not self.analytics_action:
            return {"error": "Analytics not available"}
        
        try:
            # Get query parameters
            if hasattr(request, 'query_params'):
                days = int(request.query_params.get('days', 7))
            else:
                days = 7
            
            summary = self.analytics_action.get_summary(days)
            return summary
            
        except Exception as e:
            return {"error": str(e)}

@serve.deployment
class HealthCheck:
    def __init__(self):
        try:
            import sys
            sys.path.append('/workspace/scripts')
            from deploy_email import GmailEmailAction
            from deploy_analytics import AnalyticsAction
            self.email_action = GmailEmailAction()
            self.analytics_action = AnalyticsAction()
        except:
            self.email_action = None
            self.analytics_action = None
    
    async def __call__(self, request):
        email_status = "not_configured"
        if self.email_action:
            if self.email_action.email_configured and self.email_action.use_real_email:
                email_status = "configured_and_enabled"
            elif self.email_action.email_configured:
                email_status = "configured_but_disabled"
        
        analytics_status = "available" if self.analytics_action else "not_available"
        
        return {
            "status": "healthy", 
            "service": "customer-support-ai-with-actions",
            "email_status": email_status,
            "analytics_status": analytics_status
        }

def main():
    try:
        print("🎯 Starting Ray Serve...")
        serve.start(detached=True, http_options={"host": "0.0.0.0", "port": 8000})
        
        print("🤖 Deploying Customer Support AI Agent with Actions...")
        serve.run(CustomerSupportAgent.bind(), name="customer-support-ai", route_prefix="/predict")
        
        print("📊 Deploying analytics endpoint...")
        serve.run(AnalyticsEndpoint.bind(), name="analytics", route_prefix="/analytics")
        
        print("🏥 Deploying health check...")
        serve.run(HealthCheck.bind(), name="health-check", route_prefix="/health")
        
        print("✅ Deployment successful!")
        print("🌐 AI Agent available at: http://localhost:8000/predict")
        print("📊 Analytics available at: http://localhost:8000/analytics")
        print("🏥 Health check at: http://localhost:8000/health")
        
        print("\n🎉 Customer Support AI Agent with Email & Analytics is ready!")
        
        return 0
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    main()