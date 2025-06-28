import ray
from ray import serve
import joblib
import json
from typing import Dict, Any
import logging
from datetime import datetime
from starlette.responses import JSONResponse
from starlette.requests import Request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@serve.deployment(
    name="customer-support-ai",
    num_replicas=1,
    ray_actor_options={"num_cpus": 1}
)
class CustomerSupportAgent:
    def __init__(self):
        logger.info("🤖 Loading Customer Support AI model components...")
        
        try:
            logger.info("  📄 Loading vectorizer...")
            self.vectorizer = joblib.load("/workspace/models/customer_support_ai/vectorizer.pkl")
            
            logger.info("  🎯 Loading satisfaction predictor...")
            self.satisfaction_predictor = joblib.load("/workspace/models/customer_support_ai/satisfaction_model.pkl")
            
            logger.info("  🏷️  Loading issue encoder...")
            self.issue_encoder = joblib.load("/workspace/models/customer_support_ai/issue_encoder.pkl")
            
            logger.info("  📊 Loading satisfaction encoder...")
            self.satisfaction_encoder = joblib.load("/workspace/models/customer_support_ai/satisfaction_encoder.pkl")
            
            logger.info("✅ All model components loaded successfully!")
            
        except Exception as e:
            logger.error(f"❌ Failed to load model components: {e}")
            raise
    
    def predict_satisfaction(self, message: str, issue_type: str = "general") -> Dict[str, Any]:
        try:
            # Log processing
            logger.info(f"🔍 Processing: '{message[:50]}...' (issue: {issue_type})")
            
            # Vectorize message
            message_vector = self.vectorizer.transform([message])
            
            # Predict satisfaction
            satisfaction_pred = self.satisfaction_predictor.predict(message_vector)[0]
            satisfaction_prob = self.satisfaction_predictor.predict_proba(message_vector)[0]
            confidence = max(satisfaction_prob)
            
            # Decode satisfaction
            satisfaction_label = self.satisfaction_encoder.inverse_transform([satisfaction_pred])[0]
            
            # Simple priority logic
            priority_map = {"low": "high", "medium": "medium", "high": "low"}
            priority = priority_map.get(satisfaction_label, "medium")
            
            result = {
                "predicted_satisfaction": satisfaction_label,
                "confidence": float(confidence),
                "recommended_priority": priority
            }
            
            logger.info(f"✅ Prediction: {satisfaction_label} (confidence: {confidence:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Prediction failed: {e}")
            raise
    
    async def __call__(self, request: Request):
        # Add CORS headers
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization"
        }
        
        try:
            # Handle OPTIONS request (CORS preflight)
            if request.method == "OPTIONS":
                return JSONResponse(
                    content={},
                    status_code=200,
                    headers=headers
                )
            
            # Handle health check
            if request.url.path == "/health":
                health_data = {
                    "status": "healthy",
                    "service": "customer-support-ai",
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.0"
                }
                return JSONResponse(
                    content=health_data,
                    status_code=200,
                    headers=headers
                )
            
            # Handle predictions
            if request.url.path == "/predict":
                # Get request data
                data = await request.json()
                
                message = data.get("message", "")
                issue_type = data.get("issue_type", "general")
                
                if not message:
                    return JSONResponse(
                        content={"error": "Message is required"},
                        status_code=400,
                        headers=headers
                    )
                
                # Make prediction
                prediction = self.predict_satisfaction(message, issue_type)
                
                # Prepare response
                response_data = {
                    "status": "success",
                    "message": message,
                    "issue_type": issue_type,
                    "timestamp": datetime.now().isoformat(),
                    **prediction
                }
                
                return JSONResponse(
                    content=response_data,
                    status_code=200,
                    headers=headers
                )
            
            else:
                return JSONResponse(
                    content={"error": "Endpoint not found"},
                    status_code=404,
                    headers=headers
                )
                
        except Exception as e:
            logger.error(f"❌ Request failed: {e}")
            error_response = {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            return JSONResponse(
                content=error_response,
                status_code=500,
                headers=headers
            )

def main():
    print("🚀 Starting Customer Support AI Agent Deployment with CORS")
    
    try:
        # Initialize Ray
        print("🔧 Initializing Ray...")
        ray.init(address="auto", ignore_reinit_error=True)
        
        print("🤖 Deploying Customer Support AI Agent with CORS...")
        
        # Create app with CORS-enabled deployment
        app = CustomerSupportAgent.bind()
        
        # Deploy using serve.run
        serve.run(app, host="0.0.0.0", port=8000)
        
        print("✅ Deployment successful!")
        print("🌐 AI Agent available at: http://localhost:8000/predict")
        print("🏥 Health check at: http://localhost:8000/health")
        print("🌍 CORS enabled for web demo access")
        
        # Test deployment
        print("\n🧪 Testing deployment...")
        import requests
        import time
        
        time.sleep(3)
        
        try:
            print("  📡 Sending test request...")
            test_data = {
                "message": "I can't log into my account and I'm very frustrated!",
                "issue_type": "account_access"
            }
            
            response = requests.post(
                "http://localhost:8000/predict",
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Test prediction successful!")
                print(f"   📝 Message: {result['message']}")
                print(f"   😊 Predicted satisfaction: {result['predicted_satisfaction']}")
                print(f"   🎯 Confidence: {result['confidence']:.3f}")
                print(f"   ⚡ Priority: {result['recommended_priority']}")
            else:
                print(f"❌ Test failed: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️  Test request failed: {e}")
        
        print(f"\n🎉 Customer Support AI Agent is deployed and ready with CORS!")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        raise

if __name__ == "__main__":
    main()
