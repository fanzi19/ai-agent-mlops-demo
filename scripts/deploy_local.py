import ray
from ray import serve
import joblib
import pandas as pd
import numpy as np
from scipy.sparse import hstack
import re
import os
import requests

@serve.deployment(num_replicas=1)
class CustomerSupportAgent:
    def __init__(self):
        self.model_dir = "/workspace/models"
        self.is_ready = False
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
            print(f"Text features shape: {X_text.shape}")
            
            # Combine text features with engineered features
            feature_cols = ['message_length', 'word_count', 'negative_indicators', 
                           'positive_indicators', 'urgency_indicators']
            X_features = df[feature_cols].values
            print(f"Engineered features shape: {X_features.shape}")
            
            # Combine all features exactly like training
            X_combined = hstack([X_text, X_features])
            print(f"Combined features shape: {X_combined.shape}")
            
            return X_combined
            
        except Exception as e:
            print(f"❌ Error in prepare_features: {e}")
            raise

    async def __call__(self, request):
        if not self.is_ready:
            return {"error": "Model not loaded", "status": "failed"}
        
        try:
            if hasattr(request, 'json'):
                data = await request.json()
            else:
                data = request
            
            customer_message = data.get('message', '')
            
            if not customer_message:
                return {"error": "No message provided", "status": "failed"}
            
            print(f"🔍 Processing: '{customer_message[:50]}...'")
            
            # Prepare features exactly like training
            features = self.prepare_features(customer_message)
            
            # Make predictions
            issue_pred = self.issue_classifier.predict(features)[0]
            sentiment_pred = self.sentiment_classifier.predict(features)[0] 
            satisfaction_pred = self.satisfaction_regressor.predict(features)[0]
            
            print(f"Raw predictions: issue={issue_pred}, sentiment={sentiment_pred}, satisfaction={satisfaction_pred}")
            
            # Get confidence
            issue_confidence = float(self.issue_classifier.predict_proba(features)[0].max())
            sentiment_confidence = float(self.sentiment_classifier.predict_proba(features)[0].max())
            
            # Determine priority based on sentiment and satisfaction (handle string satisfaction)
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
            
            response = {
                "status": "success",
                "message": customer_message,
                "issue_type": issue_pred,
                "sentiment": sentiment_pred,
                "predicted_satisfaction": satisfaction_pred,  # Keep as string
                "confidence": round((issue_confidence + sentiment_confidence) / 2, 3),
                "recommended_priority": priority,
                "timestamp": pd.Timestamp.now().isoformat()
            }
            
            print(f"✅ Prediction: {issue_pred} | {sentiment_pred} | {satisfaction_pred} | {priority}")
            return response
            
        except Exception as e:
            print(f"❌ Prediction error: {str(e)}")
            return {"error": str(e), "status": "failed"}

@serve.deployment
class HealthCheck:
    async def __call__(self, request):
        return {"status": "healthy", "service": "customer-support-ai"}

def main():
    try:
        print("🎯 Starting Ray Serve...")
        serve.start(detached=True, http_options={"host": "0.0.0.0", "port": 8000})
        
        print("🤖 Deploying Customer Support AI Agent...")
        serve.run(CustomerSupportAgent.bind(), name="customer-support-ai", route_prefix="/predict")
        
        print("🏥 Deploying health check...")
        serve.run(HealthCheck.bind(), name="health-check", route_prefix="/health")
        
        print("✅ Deployment successful!")
        print("🌐 AI Agent available at: http://localhost:8000/predict")
        print("🏥 Health check at: http://localhost:8000/health")
        
        # Test the deployment
        print("\n🧪 Testing deployment...")
        
        import time
        time.sleep(5)  # Wait for deployment to be ready
        
        test_payload = {"message": "My package is lost and I'm very frustrated!"}
        
        try:
            print("  📡 Sending test request...")
            response = requests.post(
                "http://localhost:8000/predict",
                json=test_payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Test prediction successful!")
                print(f"   📝 Message: {result.get('message', 'N/A')}")
                print(f"   🎯 Issue type: {result.get('issue_type', 'N/A')}")
                print(f"   😊 Sentiment: {result.get('sentiment', 'N/A')}")
                print(f"   📊 Satisfaction: {result.get('predicted_satisfaction', 'N/A')}")
                print(f"   🎯 Confidence: {result.get('confidence', 0):.3f}")
                print(f"   ⚡ Priority: {result.get('recommended_priority', 'N/A')}")
            else:
                print(f"⚠️  Test failed with status: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as test_error:
            print(f"⚠️  Test request failed: {test_error}")
            print("   This might be normal if the deployment is still starting up...")
        
        print("\n🎉 Customer Support AI Agent is deployed and ready!")
        print("\n📖 Usage Examples:")
        print("   curl -X POST http://localhost:8000/predict \\")
        print("        -H 'Content-Type: application/json' \\")
        print("        -d '{\"message\": \"Help me!\", \"issue_type\": \"general\"}'")
        
        return 0
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    main()
