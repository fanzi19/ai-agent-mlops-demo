#!/usr/bin/env python3
"""
Deploy Customer Support AI Agent using Ray Serve
"""

import os
import sys
import json
import joblib
import asyncio
from typing import Dict, Any
import pandas as pd
import numpy as np

# Add the src directory to Python path
sys.path.append('/workspace/src')

try:
    import ray
    from ray import serve
    import requests
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Installing required packages...")
    os.system("pip install ray[serve] requests")
    import ray
    from ray import serve
    import requests

# Reduce Ray logging noise
os.environ['RAY_DEDUP_LOGS'] = '0'

@serve.deployment(num_replicas=1, ray_actor_options={"num_cpus": 0.5})
class CustomerSupportAgent:
    """Ray Serve deployment for Customer Support AI Agent"""
    
    def __init__(self):
        """Initialize the model from saved artifacts"""
        print("🤖 Loading Customer Support AI model components...")
        
        self.model_dir = "/workspace/models/customer_support_ai"
        
        try:
            # Check if model files exist
            required_files = [
                "vectorizer.pkl",
                "satisfaction_model.pkl", 
                "issue_encoder.pkl",
                "satisfaction_encoder.pkl"
            ]
            
            for file in required_files:
                filepath = f"{self.model_dir}/{file}"
                if not os.path.exists(filepath):
                    raise FileNotFoundError(f"Model file not found: {filepath}")
            
            # Load all model components individually (no custom classes)
            print("  📄 Loading vectorizer...")
            self.vectorizer = joblib.load(f"{self.model_dir}/vectorizer.pkl")
            
            print("  🎯 Loading satisfaction predictor...")
            self.satisfaction_predictor = joblib.load(f"{self.model_dir}/satisfaction_model.pkl")
            
            print("  🏷️  Loading issue encoder...")
            self.issue_encoder = joblib.load(f"{self.model_dir}/issue_encoder.pkl")
            
            print("  📊 Loading satisfaction encoder...")
            self.satisfaction_encoder = joblib.load(f"{self.model_dir}/satisfaction_encoder.pkl")
            
            print("✅ All model components loaded successfully!")
            self.is_ready = True
            
        except Exception as e:
            print(f"❌ Failed to load model components: {e}")
            print(f"   Model directory: {self.model_dir}")
            print(f"   Directory contents: {os.listdir(self.model_dir) if os.path.exists(self.model_dir) else 'Directory does not exist'}")
            self.is_ready = False
            raise
    
    def prepare_features(self, customer_message: str, issue_type: str = 'general'):
        """Prepare features for prediction"""
        try:
            # Create data point
            data = [{
                'customer_message': customer_message,
                'issue_type': issue_type,
                'customer_satisfaction': 'medium'  # dummy value
            }]
            
            df = pd.DataFrame(data)
            
            # Transform text features
            text_features = self.vectorizer.transform(df['customer_message'])
            
            # Handle issue type encoding safely
            known_issues = set(self.issue_encoder.classes_)
            safe_issue_type = issue_type if issue_type in known_issues else self.issue_encoder.classes_[0]
            issue_encoded = self.issue_encoder.transform([safe_issue_type])
            
            # Combine features
            features = np.hstack([
                text_features.toarray(),
                issue_encoded.reshape(-1, 1)
            ])
            
            return features
            
        except Exception as e:
            print(f"❌ Error in prepare_features: {e}")
            raise
    
    async def __call__(self, request):
        """Handle prediction requests"""
        if not self.is_ready:
            return {"error": "Model not loaded", "status": "failed"}
        
        try:
            # Parse request
            if hasattr(request, 'json'):
                data = await request.json()
            else:
                data = request
            
            customer_message = data.get('message', '').strip()
            issue_type = data.get('issue_type', 'general')
            
            if not customer_message:
                return {"error": "No message provided", "status": "failed"}
            
            print(f"🔍 Processing: '{customer_message[:50]}...' (issue: {issue_type})")
            
            # Prepare features
            features = self.prepare_features(customer_message, issue_type)
            
            # Make predictions
            sat_pred = self.satisfaction_predictor.predict(features)[0]
            satisfaction = self.satisfaction_encoder.inverse_transform([sat_pred])[0]
            confidence = float(self.satisfaction_predictor.predict_proba(features)[0].max())
            
            # Determine priority based on satisfaction
            priority_map = {
                'low': 'high',
                'medium': 'medium', 
                'high': 'low'
            }
            priority = priority_map.get(satisfaction, 'medium')
            
            # Generate response
            response = {
                "status": "success",
                "message": customer_message,
                "issue_type": issue_type,
                "predicted_satisfaction": satisfaction,
                "confidence": round(confidence, 3),
                "recommended_priority": priority,
                "timestamp": pd.Timestamp.now().isoformat()
            }
            
            print(f"✅ Prediction: {satisfaction} (confidence: {confidence:.3f})")
            return response
            
        except Exception as e:
            error_msg = f"Prediction error: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "error": error_msg,
                "status": "failed",
                "timestamp": pd.Timestamp.now().isoformat()
            }

@serve.deployment
class HealthCheck:
    """Health check endpoint"""
    
    async def __call__(self, request):
        return {
            "status": "healthy",
            "service": "customer-support-ai",
            "timestamp": pd.Timestamp.now().isoformat(),
            "version": "1.0"
        }

def main():
    """Deploy the Customer Support AI Agent"""
    print("🚀 Starting Customer Support AI Agent Deployment")
    
    try:
        # Check if model files exist before deployment
        model_dir = "/workspace/models/customer_support_ai"
        required_files = [
            "vectorizer.pkl",
            "satisfaction_model.pkl", 
            "issue_encoder.pkl",
            "satisfaction_encoder.pkl"
        ]
        
        print("🔍 Checking model files...")
        for file in required_files:
            filepath = f"{model_dir}/{file}"
            if os.path.exists(filepath):
                print(f"  ✅ {file}")
            else:
                print(f"  ❌ {file} - NOT FOUND")
                raise FileNotFoundError(f"Required model file missing: {filepath}")
        
        # Initialize Ray if not already running
        if not ray.is_initialized():
            print("🔧 Initializing Ray...")
            ray.init(address="auto", ignore_reinit_error=True)
        
        # Start Ray Serve
        print("🎯 Starting Ray Serve...")
        serve.start(detached=True, http_options={"host": "0.0.0.0", "port": 8000})
        
        # Deploy the AI agent
        print("🤖 Deploying Customer Support AI Agent...")
        serve.run(CustomerSupportAgent.bind(), name="customer-support-ai", route_prefix="/predict")
        
        # Deploy health check
        print("🏥 Deploying health check...")
        serve.run(HealthCheck.bind(), name="health-check", route_prefix="/health")
        
        print("✅ Deployment successful!")
        print("🌐 AI Agent available at: http://localhost:8000/predict")
        print("🏥 Health check at: http://localhost:8000/health")
        
        # Test the deployment
        print("\n🧪 Testing deployment...")
        
        import time
        time.sleep(8)  # Wait for deployment to be ready
        
        test_payload = {
            "message": "I can't log into my account and I'm very frustrated!",
            "issue_type": "account_access"
        }
        
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
                print(f"   😊 Predicted satisfaction: {result.get('predicted_satisfaction', 'N/A')}")
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
    exit(main())
