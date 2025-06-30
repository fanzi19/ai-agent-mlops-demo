from dataclasses import dataclass
from typing import List, Dict
from enum import Enum
import os
from pathlib import Path

class TeamType(Enum):
    BILLING = "billing_team"
    SHIPPING = "shipping_team" 
    TECHNICAL = "technical_support_team"
    ACCOUNT = "account_services_team"
    PRODUCT = "product_quality_team"
    GENERAL = "general_support_team"
    MANAGEMENT = "management_team"

@dataclass
class TeamMember:
    name: str
    email: str
    role: str
    specialties: List[str] = None
    is_manager: bool = False

def load_test_email_from_env():
    """Load TEST_EMAIL from .env.real file"""
    # Try to find .env.real file
    env_paths = [
        Path(__file__).parent.parent.parent / '.env.real',  # From src/actions/email/
        Path.cwd() / '.env.real',  # From current directory
        Path('/workspace/.env.real')  # Docker workspace
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('TEST_EMAIL='):
                            test_email = line.split('=', 1)[1].strip()
                            print(f"✅ Loaded TEST_EMAIL from .env.real: {test_email}")
                            return test_email
                        elif line.startswith('GMAIL_EMAIL=') and not any('TEST_EMAIL=' in l for l in open(env_path).readlines()):
                            # Fallback to GMAIL_EMAIL if TEST_EMAIL not found
                            gmail_email = line.split('=', 1)[1].strip()
                            print(f"✅ Using GMAIL_EMAIL as TEST_EMAIL: {gmail_email}")
                            return gmail_email
            except Exception as e:
                print(f"⚠️ Error reading {env_path}: {e}")
                continue
    
    # Fallback to environment variable, then hardcoded default
    test_email = os.getenv('TEST_EMAIL')
    if test_email:
        print(f"✅ Using TEST_EMAIL from environment: {test_email}")
        return test_email
    
    # Last resort fallback (but print warning)
    fallback_email = 'ella.w@gmail.com'  # Fixed: use correct email with dot
    print(f"⚠️ No .env.real found, using fallback: {fallback_email}")
    return fallback_email

# Load email from .env.real
TEST_EMAIL = load_test_email_from_env()

# Team email configurations (using your email for testing)
TEAM_EMAILS = {
    TeamType.BILLING: {
        'team_email': TEST_EMAIL,  # Your email for testing
        'manager_email': TEST_EMAIL,
        'team_name': 'Billing Support Team',
        'members': [
            TeamMember("Sarah Chen", TEST_EMAIL, "Senior Billing Specialist", ["subscriptions", "refunds"]),
            TeamMember("Mike Rodriguez", TEST_EMAIL, "Billing Agent", ["payments", "disputes"]),
            TeamMember("Lisa Wang", TEST_EMAIL, "Billing Manager", ["enterprise", "escalations"], is_manager=True)
        ]
    },
    
    TeamType.SHIPPING: {
        'team_email': TEST_EMAIL,
        'manager_email': TEST_EMAIL, 
        'team_name': 'Shipping & Logistics Team',
        'members': [
            TeamMember("David Kim", TEST_EMAIL, "Logistics Specialist", ["tracking", "lost_packages"]),
            TeamMember("Emma Thompson", TEST_EMAIL, "Shipping Agent", ["delivery", "international"]),
            TeamMember("Carlos Lopez", TEST_EMAIL, "Shipping Manager", ["investigations", "claims"], is_manager=True)
        ]
    },
    
    TeamType.TECHNICAL: {
        'team_email': TEST_EMAIL,
        'manager_email': TEST_EMAIL,
        'team_name': 'Technical Support Team',
        'members': [
            TeamMember("Alex Johnson", TEST_EMAIL, "Senior Developer", ["api", "integrations"]),
            TeamMember("Priya Patel", TEST_EMAIL, "Support Engineer", ["mobile", "web"]),
            TeamMember("James Wilson", TEST_EMAIL, "Tech Lead", ["architecture", "performance"], is_manager=True)
        ]
    },
    
    TeamType.MANAGEMENT: {
        'team_email': TEST_EMAIL,
        'manager_email': TEST_EMAIL,
        'team_name': 'Management Team',
        'members': [
            TeamMember("Jennifer Adams", TEST_EMAIL, "Customer Success Manager", ["escalations", "vip"]),
            TeamMember("Robert Chen", TEST_EMAIL, "Director of Support", ["crisis", "strategy"], is_manager=True)
        ]
    },
    
    TeamType.ACCOUNT: {
        'team_email': TEST_EMAIL,
        'manager_email': TEST_EMAIL,
        'team_name': 'Account Services Team',
        'members': [
            TeamMember("Rachel Green", TEST_EMAIL, "Account Specialist", ["login", "security"]),
            TeamMember("Tom Bradley", TEST_EMAIL, "Account Manager", ["access", "permissions"], is_manager=True)
        ]
    },
    
    TeamType.PRODUCT: {
        'team_email': TEST_EMAIL,
        'manager_email': TEST_EMAIL,
        'team_name': 'Product Quality Team',
        'members': [
            TeamMember("Nina Zhao", TEST_EMAIL, "Quality Specialist", ["defects", "testing"]),
            TeamMember("Ryan Murphy", TEST_EMAIL, "Product Manager", ["feedback", "improvements"], is_manager=True)
        ]
    },
    
    TeamType.GENERAL: {
        'team_email': TEST_EMAIL,
        'manager_email': TEST_EMAIL,
        'team_name': 'General Support Team',
        'members': [
            TeamMember("Sophie Miller", TEST_EMAIL, "Support Agent", ["general_inquiry", "information"]),
            TeamMember("Kevin Chang", TEST_EMAIL, "Support Manager", ["coordination", "training"], is_manager=True)
        ]
    }
}

# Issue type to team mapping
ISSUE_TEAM_MAPPING = {
    'billing': TeamType.BILLING,
    'shipping': TeamType.SHIPPING,
    'technical_support': TeamType.TECHNICAL,
    'account_access': TeamType.ACCOUNT,
    'product_quality': TeamType.PRODUCT,
    'refund': TeamType.BILLING,
    'compliment': TeamType.GENERAL,
    'general': TeamType.GENERAL
}

# Email templates for real production use
EMAIL_TEMPLATES = {
    'team_assignment': {
        'subject': '🎯 New Support Ticket Assignment - #{ticket_id}',
        'template': '''
Hello {team_name},

A new customer support ticket has been assigned to your team based on AI analysis.

📋 TICKET DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Ticket ID: {ticket_id}
• Customer: {customer_id}
• Customer Tier: {customer_tier}
• Issue Type: {issue_type}
• Sentiment: {sentiment}
• Satisfaction Level: {satisfaction}
• Priority: {priority}
• AI Confidence: {confidence}%

📝 CUSTOMER MESSAGE:
"{message}"

🎯 AI RECOMMENDATIONS:
• Response SLA: {sla_time}
• Estimated Resolution Time: {estimated_resolution}
• Recommended Actions: {recommended_actions}

🚀 NEXT STEPS:
• Assign to available team member
• Respond to customer within SLA
• Update ticket status in system
• Escalate if needed

This ticket was automatically routed by our AI Customer Support System.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Best regards,
AI Customer Support System
Company Support Operations
        '''
    },
    
    'high_priority_alert': {
        'subject': '🚨 URGENT: High Priority Customer Issue - #{ticket_id}',
        'template': '''
🚨 HIGH PRIORITY ALERT 🚨

Dear {team_name},

A high-priority customer support issue requires IMMEDIATE attention.

⚠️ URGENT TICKET DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Ticket ID: {ticket_id}
• Customer: {customer_id} ({customer_tier})
• Issue: {issue_type}
• Sentiment: {sentiment} 😠
• Satisfaction: {satisfaction}
• AI Confidence: {confidence}%

📝 CUSTOMER MESSAGE:
"{message}"

🔥 WHY THIS IS URGENT:
• High priority classification by AI
• Negative customer sentiment detected
• Potential churn risk identified
• {escalation_reason}

⏰ IMMEDIATE ACTION REQUIRED:
• Response needed within: 1 HOUR
• Assignment required: IMMEDIATELY
• Manager notification: SENT
• Escalation path: ACTIVATED

🎯 RECOMMENDED IMMEDIATE ACTIONS:
{recommended_actions}

Please handle this ticket immediately and provide status updates every 30 minutes until resolved.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Urgent regards,
AI Customer Support System
PRIORITY ESCALATION SYSTEM
        '''
    },
    
    'manager_escalation': {
        'subject': '⚠️ MANAGER ESCALATION: Critical Customer Issue - #{ticket_id}',
        'template': '''
Dear {manager_name},

A customer support ticket has been escalated to management level and requires your immediate personal attention.

🚨 ESCALATION ALERT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Ticket ID: {ticket_id}
• Customer: {customer_id} ({customer_tier})
• Issue Type: {issue_type}
• Sentiment: {sentiment}
• Satisfaction: {satisfaction}
• Escalation Reason: {escalation_reason}

📝 CUSTOMER MESSAGE:
"{message}"

📊 AI ANALYSIS:
• Confidence Level: {confidence}%
• Churn Risk: HIGH
• Customer Sentiment: NEGATIVE
• Satisfaction Prediction: LOW

🎯 CRITICAL ACTIONS NEEDED:
• Personal manager intervention required
• Consider goodwill compensation
• Schedule immediate callback
• Monitor for retention opportunity
• Coordinate with team lead

⏰ TIMELINE:
• Manager response needed: WITHIN 1 HOUR
• Customer callback: WITHIN 2 HOURS
• Resolution target: SAME DAY
• Follow-up required: 24-48 HOURS

This customer is at HIGH RISK for churn. Please prioritize accordingly.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Escalation Alert System
Management Team
        '''
    }
}

# Gmail SMTP configuration
GMAIL_SMTP_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'use_tls': True
}
