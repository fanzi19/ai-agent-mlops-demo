#!/usr/bin/env python3
import os
import mlflow
import tempfile

print("🧪 Testing MLflow connection...")

# Test 1: MLflow connection
try:
    os.environ['MLFLOW_TRACKING_URI'] = 'http://mlflow:5000'
    mlflow.set_tracking_uri('http://mlflow:5000')
    print(f"✅ MLflow URI set: {mlflow.get_tracking_uri()}")
    
    # Test experiment creation
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        print(f"🔧 Working in temp dir: {temp_dir}")
        
        mlflow.set_experiment("test-experiment")
        
        with mlflow.start_run() as run:
            mlflow.log_param("test_param", "test_value")
            mlflow.log_metric("test_metric", 0.95)
            print(f"✅ MLflow run successful: {run.info.run_id}")
            
except Exception as e:
    print(f"❌ MLflow test failed: {e}")
    import traceback
    traceback.print_exc()

print("🏁 MLflow test completed")
