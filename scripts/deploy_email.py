#!/usr/bin/env python3
"""
Gmail Email Action Module for AI Customer Support
Enhanced version with better .env.real loading
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

class GmailEmailAction:
    def __init__(self):
        self.name = "EmailAction"
        self.enabled = True
        self.load_gmail_config()
    
    def load_env_real(self):
        """Load environment variables from .env.real file"""
        # Try multiple locations for .env.real
        env_paths = [
            Path('/workspace/.env.real'),
            Path('/workspace/scripts/.env.real'),
            Path('.env.real'),
            Path('/app/.env.real')
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                try:
                    with open(env_path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                os.environ[key.strip()] = value.strip()
                    return True
                except Exception as e:
                    continue
        return False
    
    def load_gmail_config(self):
        """Load Gmail configuration from environment variables"""
        
        # First try to load from .env.real file
        env_loaded = self.load_env_real()
        
        # Get environment variables
        self.gmail_email = os.getenv('GMAIL_EMAIL', '')
        self.gmail_app_password = os.getenv('GMAIL_APP_PASSWORD', '')
        self.test_email = os.getenv('TEST_EMAIL', '')
        self.use_real_email = os.getenv('USE_REAL_EMAIL', 'false').lower() == 'true'
        
        # Gmail SMTP settings
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        
        # Check if email is configured
        self.email_configured = bool(self.gmail_email and self.gmail_app_password and self.test_email)
    
    def should_execute(self, prediction: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if email should be sent based on conditions"""
        customer_tier = context.get("tier", "").lower()
        priority = prediction.get("recommended_priority", "").lower()
        message = context.get("message", "").lower()
        
        # Email trigger conditions
        triggers = [
            customer_tier in ["vip", "premium", "enterprise"],  # Premium customers
            priority == "high",                                 # High priority issues
            "urgent" in message,                               # Urgent keywords
            "critical" in message,                             # Critical keywords
            "emergency" in message,                            # Emergency keywords
            "angry" in message,                                # Angry customers
            "frustrated" in message,                           # Frustrated customers
            "terrible" in message,                             # Negative sentiment
            "awful" in message,                                # Negative sentiment
            "billing" in message and "charge" in message      # Billing issues
        ]
        
        return any(triggers)
    
    def send_gmail(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        """Send real email via Gmail SMTP"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.gmail_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            # Connect to Gmail SMTP server and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.gmail_email, self.gmail_app_password)
                server.send_message(msg)
            
            return {
                "real_email_sent": True,
                "smtp_server": "Gmail",
                "delivery_status": "sent"
            }
            
        except Exception as e:
            return {
                "real_email_sent": False,
                "error": str(e),
                "delivery_status": "failed"
            }
    
    def execute(self, prediction: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email action"""
        customer_id = context.get("customer_id", "unknown")
        issue_type = prediction.get("issue_type", "general")
        priority = prediction.get("recommended_priority", "medium")
        sentiment = prediction.get("sentiment", "neutral")
        confidence = prediction.get("confidence", 0)
        
        # Current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        subject = f"🚨 [AI ALERT] {priority.upper()} Priority - {issue_type.title()} Issue"
        
        # GET THE CUSTOMER MESSAGE FROM CONTEXT
        customer_message = context.get("message", "No message provided")

        # HTML email body
        body = f"""
        <html>
        <body>
        <h2>🤖 AI Customer Support Alert</h2>
        
        <table border="1" cellpadding="10" cellspacing="0" style="border-collapse: collapse;">
        <tr><td><strong>Customer ID:</strong></td><td>{customer_id}</td></tr>
        <tr><td><strong>Customer Message:</strong></td><td>{customer_message}</td></tr>
        <tr><td><strong>Issue Type:</strong></td><td>{issue_type.title()}</td></tr>
        <tr><td><strong>Priority:</strong></td><td><span style="color: {'red' if priority == 'high' else 'orange' if priority == 'medium' else 'green'};">{priority.upper()}</span></td></tr>
        <tr><td><strong>Sentiment:</strong></td><td>{sentiment.title()}</td></tr>
        <tr><td><strong>AI Confidence:</strong></td><td>{confidence:.1%}</td></tr>
        <tr><td><strong>Timestamp:</strong></td><td>{timestamp}</td></tr>
        </table>
        
        <p><strong>📋 Alert Summary:</strong></p>
        <ul>
        <li>A {priority} priority {issue_type} issue has been detected</li>
        <li>Customer sentiment appears {sentiment}</li>
        <li>AI prediction confidence: {confidence:.1%}</li>
        </ul>
        
        <p><em>This is an automated alert from the AI Customer Support System.<br>
        Please follow up with the customer promptly.</em></p>
        
        <hr>
        <small>Generated at {timestamp}</small>
        </body>
        </html>
        """.strip()
        
        # Determine recipient
        to_email = self.test_email if self.test_email else self.gmail_email
        
        result = {
            "email_prepared": True,
            "recipient": to_email,
            "subject": subject,
            "timestamp": timestamp,
            "email_configured": self.email_configured,
            "use_real_email": self.use_real_email
        }
        
        # Send email if configured
        if self.email_configured and self.use_real_email:
            email_result = self.send_gmail(to_email, subject, body)
            result.update(email_result)
        else:
            reason = "not_configured" if not self.email_configured else "real_email_disabled"
            result.update({
                "real_email_sent": False,
                "reason": reason,
                "simulation": True
            })
        
        return result

# Test function
def test_email_config():
    """Test email configuration"""
    print("🧪 Testing Email Configuration")
    print("=" * 40)
    
    email_action = GmailEmailAction()
    
    # Test configuration
    print(f"\n📊 Configuration Summary:")
    print(f"   Email Configured: {email_action.email_configured}")
    print(f"   Use Real Email: {email_action.use_real_email}")
    print(f"   Ready to Send: {email_action.email_configured and email_action.use_real_email}")
    
    # Test trigger logic
    test_contexts = [
        {"tier": "vip", "message": "hello"},
        {"tier": "standard", "message": "urgent help needed"},
        {"tier": "standard", "message": "terrible service"},
        {"tier": "standard", "message": "thank you"}
    ]
    
    print(f"\n🧪 Testing Trigger Logic:")
    for i, context in enumerate(test_contexts):
        prediction = {"recommended_priority": "medium"}
        should_send = email_action.should_execute(prediction, context)
        print(f"   Test {i+1}: {should_send} - {context}")

if __name__ == "__main__":
    test_email_config()
