"""
Email Action Plugin - integrates with existing email service
"""

import asyncio
from typing import Dict, Any
import logging
from datetime import datetime
import sys
from pathlib import Path

from .base_action import BaseAction

logger = logging.getLogger(__name__)

class EmailAction(BaseAction):
    """Email action that uses the existing email service"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.priority = 10  # High priority
        self.email_service = None
        self._initialize_email_service()
    
    def _initialize_email_service(self):
        """Initialize the existing email service"""
        try:
            # Import your existing email service
            from .email.email_service import RealEmailService
            
            # Load credentials using your existing method
            gmail_email, gmail_password = self._load_credentials()
            
            if gmail_email and gmail_password:
                self.email_service = RealEmailService(
                    gmail_email=gmail_email,
                    gmail_password=gmail_password,
                    use_real_email=self.config.get('use_real_email', True)
                )
                logger.info(f"✅ Email service initialized with {gmail_email}")
            else:
                logger.warning("⚠️ Email credentials not found - email action disabled")
                self.enabled = False
                
        except Exception as e:
            logger.error(f"❌ Email service initialization failed: {e}")
            self.enabled = False
    
    def _load_credentials(self):
        """Load Gmail credentials from .env.real (using your existing method)"""
        env_paths = [
            Path(__file__).parent.parent.parent / '.env.real',
            Path('/workspace/.env.real')  # Fixed: removed mismatched bracket
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                try:
                    env_vars = {}
                    with open(env_path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                env_vars[key.strip()] = value.strip()
                    
                    gmail_email = env_vars.get('GMAIL_EMAIL')
                    gmail_password = env_vars.get('GMAIL_APP_PASSWORD')
                    
                    if gmail_email and gmail_password:
                        return gmail_email, gmail_password
                except Exception as e:
                    logger.warning(f"Error reading {env_path}: {e}")
        
        return None, None
    
    def should_execute(self, ai_response: Dict[str, Any], customer_context: Dict[str, Any]) -> bool:
        """Determine if email should be sent"""
        
        if not self.email_service:
            return False
        
        # Check if explicitly disabled for this request
        if customer_context.get('disable_email', False):
            return False
        
        # You can add your own rules here
        return True
    
    async def execute(self, ai_response: Dict[str, Any], customer_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email sending using your existing service"""
        
        logger.info(f"📧 Executing email action for customer {customer_context.get('customer_id', 'unknown')}")
        
        try:
            # Use your existing email service
            result = self.email_service.send_team_assignment(ai_response, customer_context)
            
            # Add action metadata
            result['action'] = 'email'
            result['timestamp'] = datetime.now().isoformat()
            result['ai_confidence'] = ai_response.get('confidence', 0.0)
            
            logger.info(f"✅ Email action completed: {result['status']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Email action failed: {e}")
            return {
                'action': 'email',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
