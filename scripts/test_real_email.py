#!/usr/bin/env python3
"""
Test script for real email functionality - Uses .env.real
"""

import os
import sys
import requests
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

def load_env_real():
    """Load environment variables from .env.real"""
    env_file = Path(__file__).parent.parent / '.env.real'
    
    if not env_file.exists():
        print("❌ .env.real file not found!")
        print("💡 Create .env.real with your Gmail credentials")
        return None, None
    
    env_vars = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    gmail_email = env_vars.get('GMAIL_EMAIL')
    gmail_password = env_vars.get('GMAIL_APP_PASSWORD')
    
    if not gmail_email or not gmail_password:
        print("❌ Missing GMAIL_EMAIL or GMAIL_APP_PASSWORD in .env.real")
        return None, None
    
    print(f"✅ Loaded credentials from .env.real")
    print(f"📤 Sender: {gmail_email}")
    
    return gmail_email, gmail_password

def test_env_loading():
    """Test just the .env.real loading"""
    
    print("\n🔧 Testing .env.real Loading")
    print("=" * 35)
    
    gmail_email, gmail_password = load_env_real()
    
    if gmail_email and gmail_password:
        print(f"✅ Successfully loaded:")
        print(f"   📤 Gmail Email: {gmail_email}")
        print(f"   🔐 Password Length: {len(gmail_password)} characters")
        
        # Test Gmail connection
        try:
            import smtplib
            
            print("🔍 Testing Gmail SMTP connection...")
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(gmail_email, gmail_password)
            server.quit()
            
            print("✅ Gmail connection successful!")
            return True
            
        except Exception as e:
            print(f"❌ Gmail connection failed: {e}")
            return False
    else:
        print("❌ Failed to load credentials from .env.real")
        return False

def test_real_email():
    """Test real email sending with credentials from .env.real"""
    
    # Load credentials from .env.real
    gmail_email, gmail_password = load_env_real()
    
    if not gmail_email or not gmail_password:
        print("🔧 Please update your .env.real file first!")
        return
    
    print(f"\n🔧 Setting up real email service with {gmail_email}")
    
    try:
        from actions.email.email_service import RealEmailService
        
        # Create email service with credentials from .env.real
        email_service = RealEmailService(
            gmail_email=gmail_email,
            gmail_password=gmail_password,
            use_real_email=True  # REAL EMAILS!
        )
        
        # Test scenarios
        test_cases = [
            {
                'name': 'High Priority Shipping Issue',
                'ai_response': {
                    'issue_type': 'shipping',
                    'sentiment': 'negative',
                    'predicted_satisfaction': 'low',
                    'recommended_priority': 'high',
                    'confidence': 0.89,
                    'message': 'My package is lost and I am very frustrated! I need this resolved immediately!'
                },
                'customer_context': {
                    'customer_id': 'CUST_REAL_001',
                    'tier': 'vip'
                }
            },
            {
                'name': 'Medium Priority Billing Question',
                'ai_response': {
                    'issue_type': 'billing',
                    'sentiment': 'neutral',
                    'predicted_satisfaction': 'medium',
                    'recommended_priority': 'medium',
                    'confidence': 0.76,
                    'message': 'I have a question about my recent invoice'
                },
                'customer_context': {
                    'customer_id': 'CUST_REAL_002',
                    'tier': 'standard'
                }
            }
        ]
        
        print("\n🧪 Starting Real Email Tests...")
        print("=" * 60)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📧 Test {i}: {test_case['name']}")
            print(f"   Issue: {test_case['ai_response']['issue_type']}")
            print(f"   Sentiment: {test_case['ai_response']['sentiment']}")
            print(f"   Priority: {test_case['ai_response']['recommended_priority']}")
            
            # Send real email
            result = email_service.send_team_assignment(
                test_case['ai_response'], 
                test_case['customer_context']
            )
            
            print(f"   📊 Status: {result['status']}")
            print(f"   📧 Recipients: {result.get('recipients_count', 0)}")
            print(f"   🎯 Team: {result.get('team', 'unknown')}")
            
            if result['status'] == 'success':
                print(f"   ✅ Email sent successfully!")
                print(f"   🎫 Ticket ID: {result.get('ticket_id', 'unknown')}")
            else:
                print(f"   ❌ Error: {result.get('message', 'Unknown error')}")
            
            # If high priority, check for manager escalation
            if 'manager_escalation' in result:
                mgr_result = result['manager_escalation']
                print(f"   👔 Manager Alert: {mgr_result['status']}")
                print(f"   📧 Manager: {mgr_result.get('manager_name', 'Unknown')}")
        
        # Show final statistics
        print(f"\n📊 Final Email Statistics:")
        stats = email_service.get_email_stats()
        print(f"   Total emails sent: {stats['total_emails']}")
        print(f"   Success rate: {stats['success_rate']:.1%}")
        print(f"   Mode: {stats['mode']}")
        print(f"   By type: {stats['by_type']}")
        
        return email_service
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure email_service.py exists in src/actions/email/")
    except Exception as e:
        print(f"❌ Email service error: {e}")
        import traceback
        traceback.print_exc()

def test_with_ai_prediction():
    """Test with real AI prediction + .env.real credentials"""
    
    print("\n🤖 Testing with Real AI Prediction + .env.real")
    
    # Load credentials from .env.real
    gmail_email, gmail_password = load_env_real()
    
    if not gmail_email or not gmail_password:
        print("🔧 Please update your .env.real file first!")
        return
    
    # Get AI prediction first
    test_message = input("\nEnter a customer message to analyze: ").strip()
    if not test_message:
        test_message = "My package is lost and I'm very frustrated!"
    
    try:
        print(f"🔍 Getting AI prediction for: '{test_message}'")
        
        # Get AI prediction from deployed model
        response = requests.post('http://localhost:8000/predict', 
                               json={'message': test_message}, timeout=10)
        
        if response.status_code == 200:
            ai_response = response.json()
            print(f"✅ AI Analysis complete:")
            print(f"   🎯 Issue: {ai_response['issue_type']}")
            print(f"   😊 Sentiment: {ai_response['sentiment']}")
            print(f"   📊 Satisfaction: {ai_response['predicted_satisfaction']}")
            print(f"   ⚡ Priority: {ai_response['recommended_priority']}")
            print(f"   🎯 Confidence: {ai_response['confidence']:.3f}")
            
            # Use credentials from .env.real
            from actions.email.email_service import RealEmailService
            
            email_service = RealEmailService(
                gmail_email=gmail_email,
                gmail_password=gmail_password, 
                use_real_email=True
            )
            
            customer_context = {
                'customer_id': 'REAL_TEST_CUSTOMER',
                'tier': 'premium'
            }
            
            print(f"\n📧 Sending real email based on AI analysis...")
            result = email_service.send_team_assignment(ai_response, customer_context)
            
            print(f"📊 Email Result: {result['status']}")
            if result['status'] == 'success':
                print(f"✅ Real email sent to {result['team']} team!")
                print(f"📧 Emails sent from: {gmail_email}")
                print(f"🎫 Ticket ID: {result.get('ticket_id', 'unknown')}")
                
                # Check for manager escalation
                if 'manager_escalation' in result:
                    mgr_result = result['manager_escalation']
                    print(f"👔 Manager escalation: {mgr_result['status']}")
                    print(f"📧 Manager: {mgr_result.get('manager_name', 'Unknown')}")
            else:
                print(f"❌ Email failed: {result.get('message')}")
        
        else:
            print(f"❌ AI prediction failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Real Email Testing System (.env.real)")
    print("=" * 45)
    
    while True:
        print("\nChoose test option:")
        print("1. Test .env.real loading only")
        print("2. Test email templates (using .env.real)")
        print("3. Test with real AI prediction (using .env.real)")
        print("4. Exit")
        
        choice = input("\nChoice (1-4): ").strip()
        
        if choice == "1":
            test_env_loading()
        elif choice == "2":
            test_real_email()
        elif choice == "3":
            test_with_ai_prediction()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")
        
        # Ask if they want to continue
        if choice in ["1", "2", "3"]:
            continue_choice = input("\nRun another test? (y/n): ").strip().lower()
            if continue_choice != 'y':
                print("👋 Testing complete!")
                break
