import smtplib
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from .email_config import TEAM_EMAILS, EMAIL_TEMPLATES, ISSUE_TEAM_MAPPING, TeamType, GMAIL_SMTP_CONFIG

class RealEmailService:
    """
    Real email service for production customer support notifications
    """
    
    def __init__(self, gmail_email: str = None, gmail_password: str = None, use_real_email: bool = False):
        self.gmail_email = gmail_email or os.getenv('GMAIL_EMAIL')
        self.gmail_password = gmail_password or os.getenv('GMAIL_APP_PASSWORD')  # Use App Password for Gmail
        self.use_real_email = use_real_email
        self.sent_emails = []
        
        if self.use_real_email and not (self.gmail_email and self.gmail_password):
            raise ValueError("Gmail credentials required for real email sending")
    
    def send_team_assignment(self, ai_response: Dict, customer_context: Dict = None) -> Dict:
        """
        Send ticket assignment to the appropriate team based on AI analysis
        """
        try:
            # Determine target team
            issue_type = ai_response.get('issue_type', 'general')
            team_type = ISSUE_TEAM_MAPPING.get(issue_type, TeamType.GENERAL)
            
            # Prepare ticket data
            ticket_data = self._prepare_ticket_data(ai_response, customer_context)
            
            # Choose template based on priority
            template_type = 'high_priority_alert' if ai_response.get('recommended_priority') == 'high' else 'team_assignment'
            
            # Send email to team
            result = self._send_team_email(team_type, ticket_data, template_type)
            
            # If high priority, also send manager escalation
            if ai_response.get('recommended_priority') == 'high':
                manager_result = self._send_manager_escalation(team_type, ticket_data)
                result['manager_escalation'] = manager_result
            
            return result
            
        except Exception as e:
            return {'status': 'error', 'message': f'Team assignment email failed: {str(e)}'}
    
    def _prepare_ticket_data(self, ai_response: Dict, customer_context: Dict) -> Dict:
        """Prepare comprehensive ticket data for email templates"""
        ticket_id = f"TKT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            'ticket_id': ticket_id,
            'customer_id': customer_context.get('customer_id', 'UNKNOWN') if customer_context else 'ANONYMOUS',
            'customer_tier': customer_context.get('tier', 'standard') if customer_context else 'standard',
            'issue_type': ai_response.get('issue_type', 'general'),
            'sentiment': ai_response.get('sentiment', 'neutral'),
            'satisfaction': ai_response.get('predicted_satisfaction', 'medium'),
            'priority': ai_response.get('recommended_priority', 'medium'),
            'confidence': int(ai_response.get('confidence', 0) * 100),
            'message': ai_response.get('message', 'No message provided'),
            'sla_time': self._calculate_sla_time(ai_response.get('recommended_priority', 'medium')),
            'estimated_resolution': self._estimate_resolution_time(ai_response),
            'recommended_actions': self._get_recommended_actions(ai_response),
            'escalation_reason': self._get_escalation_reason(ai_response, customer_context),
            'timestamp': datetime.now().isoformat()
        }
    
    def _send_team_email(self, team_type: TeamType, ticket_data: Dict, template_type: str) -> Dict:
        """Send email to team using specified template"""
        
        team_config = TEAM_EMAILS.get(team_type, TEAM_EMAILS[TeamType.GENERAL])
        template = EMAIL_TEMPLATES[template_type]
        
        # Prepare template variables
        template_vars = ticket_data.copy()
        template_vars['team_name'] = team_config['team_name']
        
        # Format email content
        subject = template['subject'].format(**template_vars)
        body = template['template'].format(**template_vars)
        
        # Determine recipients
        recipients = [team_config['team_email']]
        
        # For high priority, add individual team members
        if template_type == 'high_priority_alert':
            recipients.extend([member.email for member in team_config['members']])
            # Remove duplicates
            recipients = list(set(recipients))
        
        # Send email
        email_result = self._send_email(recipients, subject, body, f"team_{template_type}")
        
        return {
            'status': email_result['status'],
            'team': team_type.value,
            'template_type': template_type,
            'recipients_count': len(recipients),
            'ticket_id': ticket_data['ticket_id'],
            'message': email_result.get('message', ''),
            'details': email_result
        }
    
    def _send_manager_escalation(self, team_type: TeamType, ticket_data: Dict) -> Dict:
        """Send escalation email to manager"""
        
        team_config = TEAM_EMAILS.get(team_type, TEAM_EMAILS[TeamType.MANAGEMENT])
        
        # Find manager
        manager = next((m for m in team_config['members'] if m.is_manager), None)
        manager_name = manager.name if manager else "Manager"
        manager_email = manager.email if manager else team_config['manager_email']
        
        # Prepare escalation data
        escalation_data = ticket_data.copy()
        escalation_data['manager_name'] = manager_name
        
        template = EMAIL_TEMPLATES['manager_escalation']
        subject = template['subject'].format(**escalation_data)
        body = template['template'].format(**escalation_data)
        
        # Send to manager
        email_result = self._send_email([manager_email], subject, body, "manager_escalation")
        
        return {
            'status': email_result['status'],
            'manager_name': manager_name,
            'manager_email': manager_email,
            'ticket_id': ticket_data['ticket_id'],
            'message': email_result.get('message', ''),
            'details': email_result
        }
    
    def _send_email(self, recipients: List[str], subject: str, body: str, email_type: str) -> Dict:
        """Actually send the email (real or test mode)"""
        
        email_record = {
            'timestamp': datetime.now().isoformat(),
            'recipients': recipients,
            'subject': subject,
            'body': body,
            'email_type': email_type,
            'sender': self.gmail_email
        }
        
        if not self.use_real_email:
            # Test mode - just log the email
            print(f"\n📧 EMAIL WOULD BE SENT ({email_type}):")
            print(f"From: {self.gmail_email}")
            print(f"To: {', '.join(recipients)}")
            print(f"Subject: {subject}")
            print(f"Body Preview: {body[:300]}...")
            print("=" * 80)
            
            email_record['status'] = 'test_mode'
            self.sent_emails.append(email_record)
            
            return {
                'status': 'success',
                'message': f'Email prepared successfully (test mode) - {len(recipients)} recipients',
                'mode': 'test'
            }
        
        else:
            # Real email sending
            try:
                # Create message
                msg = MIMEMultipart()
                msg['From'] = self.gmail_email
                msg['To'] = ', '.join(recipients)
                msg['Subject'] = subject
                
                # Add body
                msg.attach(MIMEText(body, 'plain'))
                
                # Connect to Gmail SMTP
                server = smtplib.SMTP(GMAIL_SMTP_CONFIG['smtp_server'], GMAIL_SMTP_CONFIG['smtp_port'])
                
                if GMAIL_SMTP_CONFIG['use_tls']:
                    server.starttls()
                
                # Login and send
                server.login(self.gmail_email, self.gmail_password)
                text = msg.as_string()
                server.sendmail(self.gmail_email, recipients, text)
                server.quit()
                
                print(f"✅ REAL EMAIL SENT SUCCESSFULLY!")
                print(f"📧 To: {', '.join(recipients)}")
                print(f"📝 Subject: {subject}")
                print("=" * 50)
                
                email_record['status'] = 'sent'
                self.sent_emails.append(email_record)
                
                return {
                    'status': 'success',
                    'message': f'Email sent successfully to {len(recipients)} recipients',
                    'mode': 'real'
                }
                
            except Exception as e:
                print(f"❌ EMAIL SENDING FAILED: {str(e)}")
                
                email_record['status'] = 'failed'
                email_record['error'] = str(e)
                self.sent_emails.append(email_record)
                
                return {
                    'status': 'error',
                    'message': f'Email sending failed: {str(e)}',
                    'mode': 'real'
                }
    
    def _calculate_sla_time(self, priority: str) -> str:
        """Calculate SLA response time"""
        sla_hours = {'high': 1, 'medium': 4, 'low': 24}
        hours = sla_hours.get(priority, 4)
        target_time = datetime.now() + timedelta(hours=hours)
        return target_time.strftime('%Y-%m-%d %H:%M')
    
    def _estimate_resolution_time(self, ai_response: Dict) -> str:
        """Estimate resolution time based on issue complexity"""
        issue_type = ai_response.get('issue_type', 'general')
        priority = ai_response.get('recommended_priority', 'medium')
        
        if priority == 'high':
            return "1-4 hours"
        elif issue_type in ['account_access', 'billing']:
            return "2-6 hours"
        elif issue_type in ['technical_support', 'product_quality']:
            return "4-24 hours"
        else:
            return "2-8 hours"
    
    def _get_recommended_actions(self, ai_response: Dict) -> str:
        """Get recommended actions based on AI analysis"""
        actions = []
        
        issue_type = ai_response.get('issue_type')
        sentiment = ai_response.get('sentiment')
        priority = ai_response.get('recommended_priority')
        
        if priority == 'high':
            actions.append("Immediate response required")
        
        if sentiment == 'negative':
            actions.append("Use empathetic communication")
            actions.append("Consider goodwill gesture")
        
        if issue_type == 'shipping':
            actions.append("Check tracking information")
            actions.append("Investigate delivery status")
        elif issue_type == 'billing':
            actions.append("Review account history")
            actions.append("Check payment status")
        elif issue_type == 'technical_support':
            actions.append("Review technical documentation")
            actions.append("Test reproduction steps")
        
        return "; ".join(actions) if actions else "Standard support procedures"
    
    def _get_escalation_reason(self, ai_response: Dict, customer_context: Dict) -> str:
        """Get escalation reason"""
        reasons = []
        
        if ai_response.get('recommended_priority') == 'high':
            reasons.append("High priority classification")
        
        if ai_response.get('sentiment') == 'negative':
            reasons.append("Negative customer sentiment")
        
        if customer_context and customer_context.get('tier') == 'vip':
            reasons.append("VIP customer status")
        
        return "; ".join(reasons) if reasons else "Standard escalation criteria met"
    
    def get_email_history(self) -> List[Dict]:
        """Get history of all emails"""
        return self.sent_emails
    
    def get_email_stats(self) -> Dict:
        """Get email statistics"""
        if not self.sent_emails:
            return {'total_emails': 0}
        
        total = len(self.sent_emails)
        successful = len([e for e in self.sent_emails if e['status'] in ['sent', 'test_mode']])
        
        by_type = {}
        for email in self.sent_emails:
            email_type = email.get('email_type', 'unknown')
            by_type[email_type] = by_type.get(email_type, 0) + 1
        
        return {
            'total_emails': total,
            'successful_emails': successful,
            'success_rate': successful / total,
            'by_type': by_type,
            'mode': 'real' if self.use_real_email else 'test'
        }

# Usage example
if __name__ == "__main__":
    # Test the email service
    email_service = RealEmailService(use_real_email=False)  # Set to True for real emails
    
    # Mock AI response
    ai_response = {
        'issue_type': 'shipping',
        'sentiment': 'negative',
        'predicted_satisfaction': 'low',
        'recommended_priority': 'high',
        'confidence': 0.87,
        'message': 'My package is lost and I am very frustrated!'
    }
    
    customer_context = {
        'customer_id': 'CUST_12345',
        'tier': 'premium'
    }
    
    # Send team assignment email
    result = email_service.send_team_assignment(ai_response, customer_context)
    
    print("📧 Email Service Test Results:")
    print(json.dumps(result, indent=2))
    
    print("\n📊 Email Statistics:")
    stats = email_service.get_email_stats()
    print(json.dumps(stats, indent=2))
