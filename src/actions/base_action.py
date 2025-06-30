"""
Base class for all actions
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class BaseAction(ABC):
    """Base class for all customer support actions"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled = True
        self.priority = 100  # Lower number = higher priority
        self.name = self.__class__.__name__
        
    @abstractmethod
    def should_execute(self, ai_response: Dict[str, Any], customer_context: Dict[str, Any]) -> bool:
        """
        Determine if this action should execute based on AI response and customer context
        """
        pass
    
    @abstractmethod
    async def execute(self, ai_response: Dict[str, Any], customer_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the action
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get action metadata"""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'priority': self.priority,
            'config': self.config
        }
    
    async def validate(self) -> bool:
        """Validate action configuration and dependencies"""
        return True
    
    def disable(self):
        """Disable this action"""
        self.enabled = False
        logger.info(f"Action {self.name} disabled")
    
    def enable(self):
        """Enable this action"""
        self.enabled = True
        logger.info(f"Action {self.name} enabled")
