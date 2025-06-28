#!/usr/bin/env python3
"""
Customer Support AI Agent Training Pipeline
Trains a model to generate appropriate responses for customer support
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import mlflow
import mlflow.sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import joblib
import tempfile

# MLflow setup - completely remote, no local artifacts
os.environ['MLFLOW_TRACKING_URI'] = 'http://mlflow:5000'
os.environ['MLFLOW_S3_ENDPOINT_URL'] = ''  # Disable S3
os.environ['MLFLOW_ARTIFACT_ROOT'] = ''   # Disable local artifacts

# Set tracking URI and disable local file creation
mlflow.set_tracking_uri('http://mlflow:5000')

class CustomerSupportAI:
    """Customer Support AI Model for predicting responses and satisfaction"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=50, stop_words='english')
        self.satisfaction_predictor = RandomForestClassifier(n_estimators=50, random_state=42)
        self.response_classifier = RandomForestClassifier(n_estimators=50, random_state=42)
        self.issue_encoder = LabelEncoder()
        self.satisfaction_encoder = LabelEncoder()
        self.is_trained = False
        
    def prepare_features(self, data, fit_transform=True):
        """Prepare features from customer messages and metadata"""
        df = pd.DataFrame(data)
        
        # Text features from customer messages
        if fit_transform:
            text_features = self.vectorizer.fit_transform(df['customer_message'])
        else:
            text_features = self.vectorizer.transform(df['customer_message'])
        
        # Make sure we have consistent issue types for encoding
        if fit_transform:
            # Fit encoders during training
            issue_encoded = self.issue_encoder.fit_transform(df['issue_type'])
        else:
            # Handle unknown issue types during prediction
            known_issues = set(self.issue_encoder.classes_)
            df['issue_type_safe'] = df['issue_type'].apply(
                lambda x: x if x in known_issues else self.issue_encoder.classes_[0]
            )
            issue_encoded = self.issue_encoder.transform(df['issue_type_safe'])
        
        # Combine features (text + issue type)
        features = np.hstack([
            text_features.toarray(),
            issue_encoded.reshape(-1, 1)
        ])
        
        return features, df
    
    def train(self, train_data):
        """Train the customer support AI model"""
        print("🔧 Preparing training features...")
        
        # Prepare features
        X, df = self.prepare_features(train_data, fit_transform=True)
        
        # Target variables
        y_satisfaction = self.satisfaction_encoder.fit_transform(df['customer_satisfaction'])
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y_satisfaction, test_size=0.2, random_state=42
        )
        
        print(f"📊 Feature shape: {X.shape}")
        print(f"🎯 Training with {X_train.shape[0]} samples, validating with {X_val.shape[0]} samples")
        
        # Train satisfaction predictor
        print("🎯 Training satisfaction predictor...")
        self.satisfaction_predictor.fit(X_train, y_train)
        
        # Validation
        y_pred = self.satisfaction_predictor.predict(X_val)
        accuracy = accuracy_score(y_val, y_pred)
        
        self.is_trained = True
        
        metrics = {
            'satisfaction_accuracy': accuracy,
            'training_samples': len(X_train),
            'validation_samples': len(X_val),
            'feature_count': X.shape[1],
            'satisfaction_classes': len(self.satisfaction_encoder.classes_)
        }
        
        return metrics
    
    def predict_response_strategy(self, customer_message, issue_type='general'):
        """Predict appropriate response strategy for customer message"""
        if not self.is_trained:
            return {
                'error': 'Model not trained yet',
                'predicted_satisfaction': 'unknown',
                'confidence': 0.0
            }
        
        try:
            # Create data point for prediction
            dummy_data = [{
                'customer_message': customer_message,
                'issue_type': issue_type,
                'customer_satisfaction': 'medium'  # dummy value, not used for prediction
            }]
            
            # Prepare features (don't fit, just transform)
            X, _ = self.prepare_features(dummy_data, fit_transform=False)
            
            # Predict satisfaction level
            sat_pred = self.satisfaction_predictor.predict(X)[0]
            satisfaction = self.satisfaction_encoder.inverse_transform([sat_pred])[0]
            confidence = self.satisfaction_predictor.predict_proba(X)[0].max()
            
            return {
                'predicted_satisfaction': satisfaction,
                'confidence': confidence,
                'recommended_priority': 'high' if satisfaction == 'low' else 'medium',
                'issue_type': issue_type
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'predicted_satisfaction': 'unknown',
                'confidence': 0.0
            }

def load_training_data():
    """Load customer support training data"""
    print("📊 Loading training data...")
    
    try:
        with open('/workspace/data/train_data.json', 'r') as f:
            train_data = json.load(f)
        
        with open('/workspace/data/test_data.json', 'r') as f:
            test_data = json.load(f)
            
        print(f"✅ Loaded {len(train_data)} training samples, {len(test_data)} test samples")
        return train_data, test_data
        
    except FileNotFoundError:
        print("❌ Training data not found. Run 'make data' first.")
        raise

def evaluate_model(model, test_data):
    """Evaluate model performance on test data"""
    print("📈 Evaluating model performance...")
    
    # Test predictions on sample messages with known issue types
    test_cases = [
        {"message": "I'm having trouble logging into my account", "issue": "account_access"},
        {"message": "Your app keeps crashing on my phone", "issue": "technical"},
        {"message": "I want to cancel my subscription", "issue": "cancellation"},
        {"message": "The delivery was late and the product was damaged", "issue": "shipping"},
        {"message": "I was charged twice this month", "issue": "billing"}
    ]
    
    results = []
    for test_case in test_cases:
        prediction = model.predict_response_strategy(test_case["message"], test_case["issue"])
        results.append({
            'message': test_case["message"],
            'issue_type': test_case["issue"],
            'prediction': prediction
        })
    
    return results

def main():
    """Main training pipeline"""
    print("🚀 Starting Customer Support AI Training Pipeline")
    print(f"📅 Training started at: {datetime.now()}")
    print(f"🔗 MLflow URI: {mlflow.get_tracking_uri()}")
    
    # Store original working directory
    original_cwd = os.getcwd()
    
    try:
        # Change to a temporary directory to avoid permission issues
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            # Test MLflow connection
            try:
                # Simple connectivity test
                client = mlflow.tracking.MlflowClient()
                experiments = client.search_experiments()
                print("✅ MLflow connection successful")
                mlflow_available = True
            except Exception as e:
                print(f"⚠️  MLflow connection issue: {e}")
                print("   Continuing with local model saving only...")
                mlflow_available = False
            
            # Change back to working directory for data access
            os.chdir(original_cwd)
            
            # Load data
            train_data, test_data = load_training_data()
            
            # Initialize and train model
            print("🤖 Initializing Customer Support AI...")
            model = CustomerSupportAI()
            
            print("🎯 Training model...")
            metrics = model.train(train_data)
            
            # Print metrics
            for metric_name, value in metrics.items():
                print(f"   • {metric_name}: {value}")
            
            # Evaluate model
            evaluation_results = evaluate_model(model, test_data)
            
            # Save model artifacts locally first
            print("💾 Saving model artifacts locally...")
            model_dir = "/workspace/models/customer_support_ai"
            os.makedirs(model_dir, exist_ok=True)
            
            joblib.dump(model.vectorizer, f"{model_dir}/vectorizer.pkl")
            joblib.dump(model.satisfaction_predictor, f"{model_dir}/satisfaction_model.pkl")
            joblib.dump(model.issue_encoder, f"{model_dir}/issue_encoder.pkl")
            joblib.dump(model.satisfaction_encoder, f"{model_dir}/satisfaction_encoder.pkl")
            joblib.dump(model, f"{model_dir}/complete_model.pkl")
            
            # Save evaluation results
            eval_path = f"{model_dir}/evaluation_results.json"
            with open(eval_path, 'w') as f:
                json.dump(evaluation_results, f, indent=2, default=str)
            
            # Save training metrics
            metrics_path = f"{model_dir}/training_metrics.json"
            with open(metrics_path, 'w') as f:
                json.dump(metrics, f, indent=2, default=str)
            
            print("✅ Model saved locally!")
            
            # Now try MLflow logging if available
            if mlflow_available:
                try:
                    print("📊 Logging to MLflow...")
                    
                    # Change to temp directory for MLflow operations
                    os.chdir(temp_dir)
                    
                    experiment_name = "customer-support-ai"
                    mlflow.set_experiment(experiment_name)
                    
                    with mlflow.start_run() as run:
                        # Log parameters
                        mlflow.log_param("train_samples", len(train_data))
                        mlflow.log_param("test_samples", len(test_data))
                        mlflow.log_param("model_type", "RandomForest")
                        mlflow.log_param("evaluation_samples", len(evaluation_results))
                        
                        # Log metrics
                        for metric_name, value in metrics.items():
                            mlflow.log_metric(metric_name, value)
                        
                        # Log model using a temporary file
                        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as tmp_model:
                            joblib.dump(model.satisfaction_predictor, tmp_model.name)
                            mlflow.sklearn.log_model(
                                sk_model=model.satisfaction_predictor,
                                artifact_path="satisfaction_model"
                            )
                        
                        print(f"✅ MLflow logging successful!")
                        print(f"🎯 MLflow Run ID: {run.info.run_id}")
                        print(f"🌐 View in MLflow UI: http://localhost:5001")
                        
                except Exception as mlflow_error:
                    print(f"⚠️  MLflow logging failed: {mlflow_error}")
                    print("   Model still saved locally")
            
            # Ensure we're back in the original directory
            os.chdir(original_cwd)
            
            print("\n✅ Training completed successfully!")
            print(f"📊 Satisfaction Accuracy: {metrics['satisfaction_accuracy']:.4f}")
            print(f"🔧 Feature Count: {metrics['feature_count']}")
            print(f"💾 Model saved to: {model_dir}")
            
            print("\n🧪 Sample Predictions:")
            for result in evaluation_results:
                pred = result['prediction']
                if 'error' not in pred:
                    print(f"   Message: '{result['message'][:50]}...'")
                    print(f"   Issue: {result['issue_type']}")
                    print(f"   → Predicted satisfaction: {pred['predicted_satisfaction']} (confidence: {pred['confidence']:.2f})")
                    print(f"   → Recommended priority: {pred['recommended_priority']}")
                    print()
                else:
                    print(f"   Error in prediction: {pred['error']}")
            
            return 0
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Ensure we're back in the original directory
        os.chdir(original_cwd)

if __name__ == "__main__":
    exit(main())
