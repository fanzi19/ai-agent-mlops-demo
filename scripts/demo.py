#!/usr/bin/env python3
"""
🤖 Customer Support AI Agent - Interactive Demo
"""

import requests
import json
import time
from datetime import datetime

class CustomerSupportDemo:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.predict_url = f"{base_url}/predict"
        self.health_url = f"{base_url}/health"
    
    def check_health(self):
        """Check if the AI agent is running"""
        try:
            response = requests.get(self.health_url, timeout=5)
            if response.status_code == 200:
                print("✅ AI Agent is healthy and running!")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to AI agent: {e}")
            return False
    
    def predict(self, message, issue_type="general"):
        """Make a prediction"""
        payload = {
            "message": message,
            "issue_type": issue_type
        }
        
        try:
            print(f"\n🔍 Processing: '{message}'")
            print(f"📋 Issue Type: {issue_type}")
            
            start_time = time.time()
            response = requests.post(self.predict_url, json=payload, timeout=10)
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"⚡ Response Time: {(end_time - start_time)*1000:.1f}ms")
                print(f"😊 Predicted Satisfaction: {result['predicted_satisfaction']}")
                print(f"🎯 Confidence: {result['confidence']:.1%}")
                print(f"⚡ Recommended Priority: {result['recommended_priority']}")
                print(f"📅 Timestamp: {result['timestamp']}")
                
                return result
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def run_demo_scenarios(self):
        """Run a series of demo scenarios"""
        print("🎭 Customer Support AI Agent Demo")
        print("=" * 50)
        
        # Check health first
        if not self.check_health():
            print("Please start the AI agent first with: make deploy")
            return
        
        scenarios = [
            {
                "message": "I can't log into my account and I'm getting frustrated!",
                "issue_type": "account_access",
                "description": "Frustrated customer with login issues"
            },
            {
                "message": "Your team helped me so quickly! Amazing service!",
                "issue_type": "compliment", 
                "description": "Happy customer giving praise"
            },
            {
                "message": "My order is late and no one is responding to my emails",
                "issue_type": "shipping",
                "description": "Upset customer with shipping delays"
            },
            {
                "message": "I need help setting up my new product",
                "issue_type": "technical_support",
                "description": "Customer needing technical assistance"
            },
            {
                "message": "I want to cancel my subscription immediately",
                "issue_type": "billing",
                "description": "Customer wanting to cancel service"
            },
            {
                "message": "Thank you for the quick refund process!",
                "issue_type": "billing",
                "description": "Satisfied customer after resolution"
            }
        ]
        
        print(f"\n🎯 Running {len(scenarios)} demo scenarios...\n")
        
        results = []
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n📋 Scenario {i}: {scenario['description']}")
            print("-" * 40)
            
            result = self.predict(scenario["message"], scenario["issue_type"])
            if result:
                results.append({**scenario, "result": result})
            
            time.sleep(1)  # Brief pause between demos
        
        # Summary
        print(f"\n📊 Demo Summary")
        print("=" * 50)
        print(f"✅ Scenarios tested: {len(results)}")
        print(f"🚀 System performance: Real-time AI predictions")
        print(f"🎯 Features demonstrated:")
        print(f"   • Customer message analysis")
        print(f"   • Satisfaction prediction")
        print(f"   • Priority recommendation")
        print(f"   • Multi-issue type support")
        print(f"   • Fast response times (<100ms)")
        
        return results
    
    def interactive_mode(self):
        """Interactive demo mode"""
        print("\n🎮 Interactive Mode - Try your own messages!")
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                message = input("💬 Enter customer message: ").strip()
                if message.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not message:
                    continue
                
                issue_type = input("📋 Issue type (or press Enter for 'general'): ").strip()
                if not issue_type:
                    issue_type = "general"
                
                self.predict(message, issue_type)
                print()
                
            except KeyboardInterrupt:
                break
        
        print("👋 Thanks for trying the demo!")

def main():
    print("🤖 Customer Support AI Agent - Demo")
    print("=" * 50)
    
    demo = CustomerSupportDemo()
    
    print("\nDemo Options:")
    print("1. Run automated demo scenarios")
    print("2. Interactive mode (try your own messages)")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice in ['1', '3']:
        demo.run_demo_scenarios()
    
    if choice in ['2', '3']:
        demo.interactive_mode()

if __name__ == "__main__":
    main()
