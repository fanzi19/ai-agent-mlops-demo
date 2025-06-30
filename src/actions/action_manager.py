"""
Action Manager - orchestrates all customer support actions
"""

import importlib
import inspect
import asyncio
from typing import Dict, Any, List, Type
from pathlib import Path
import logging
import json

from .base_action import BaseAction

logger = logging.getLogger(__name__)

class ActionManager:
    """Manages and orchestrates customer support actions"""
    
    def __init__(self, config_file: str = None):
        self.actions: List[BaseAction] = []
        self.config = self._load_config(config_file)
        self.results = {}
        
    def _load_config(self, config_file: str = None) -> Dict[str, Any]:
        """Load action configuration"""
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_file}: {e}")
        
        # Default configuration
        return {
            'actions': {
                'email': {'enabled': True, 'priority': 10},
                'analytics': {'enabled': True, 'priority': 100}
            },
            'execution': {
                'parallel': True,
                'timeout': 30,
                'continue_on_failure': True
            }
        }
    
    def register_action(self, action_class: Type[BaseAction], **kwargs) -> bool:
        """Register a new action"""
        try:
            action_name = action_class.__name__.lower().replace('action', '')
            action_config = self.config.get('actions', {}).get(action_name, {})
            
            action = action_class(config=action_config, **kwargs)
            
            if 'priority' in action_config:
                action.priority = action_config['priority']
            
            if 'enabled' in action_config:
                action.enabled = action_config['enabled']
            
            self.actions.append(action)
            self.actions.sort(key=lambda x: x.priority)
            
            logger.info(f"Registered action: {action.name} (priority: {action.priority}, enabled: {action.enabled})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register action {action_class.__name__}: {e}")
            return False
    
    def auto_discover_actions(self, actions_dir: str = None) -> int:
        """Auto-discover and register actions from directory"""
        if actions_dir is None:
            actions_dir = Path(__file__).parent
        
        actions_dir = Path(actions_dir)
        discovered = 0
        
        for action_file in actions_dir.glob("*_action.py"):
            try:
                module_name = f"actions.{action_file.stem}"
                module = importlib.import_module(module_name)
                
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, BaseAction) and 
                        obj != BaseAction):
                        
                        if self.register_action(obj):
                            discovered += 1
                            
            except Exception as e:
                logger.warning(f"Failed to load action from {action_file}: {e}")
        
        logger.info(f"Auto-discovered {discovered} actions")
        return discovered
    
    async def execute_actions(self, ai_response: Dict[str, Any], customer_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all applicable actions"""
        
        execution_results = {
            'executed': [],
            'skipped': [],
            'failed': [],
            'results': {}
        }
        
        applicable_actions = []
        for action in self.actions:
            if not action.enabled:
                execution_results['skipped'].append({
                    'action': action.name,
                    'reason': 'disabled'
                })
                continue
            
            try:
                if action.should_execute(ai_response, customer_context):
                    applicable_actions.append(action)
                else:
                    execution_results['skipped'].append({
                        'action': action.name,
                        'reason': 'conditions_not_met'
                    })
            except Exception as e:
                logger.error(f"Error checking if {action.name} should execute: {e}")
                execution_results['failed'].append({
                    'action': action.name,
                    'error': str(e),
                    'phase': 'should_execute'
                })
        
        if not applicable_actions:
            return execution_results
        
        parallel_execution = self.config.get('execution', {}).get('parallel', True)
        timeout = self.config.get('execution', {}).get('timeout', 30)
        
        if parallel_execution:
            tasks = []
            for action in applicable_actions:
                task = asyncio.create_task(
                    self._execute_single_action(action, ai_response, customer_context)
                )
                tasks.append((action, task))
            
            for action, task in tasks:
                try:
                    result = await asyncio.wait_for(task, timeout=timeout)
                    execution_results['executed'].append(action.name)
                    execution_results['results'][action.name] = result
                    
                except asyncio.TimeoutError:
                    execution_results['failed'].append({
                        'action': action.name,
                        'error': 'timeout',
                        'phase': 'execution'
                    })
                    
                except Exception as e:
                    execution_results['failed'].append({
                        'action': action.name,
                        'error': str(e),
                        'phase': 'execution'
                    })
        else:
            for action in applicable_actions:
                try:
                    result = await asyncio.wait_for(
                        self._execute_single_action(action, ai_response, customer_context),
                        timeout=timeout
                    )
                    execution_results['executed'].append(action.name)
                    execution_results['results'][action.name] = result
                    
                except Exception as e:
                    execution_results['failed'].append({
                        'action': action.name,
                        'error': str(e),
                        'phase': 'execution'
                    })
        
        return execution_results
    
    async def _execute_single_action(self, action: BaseAction, ai_response: Dict[str, Any], customer_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single action with error handling"""
        logger.info(f"Executing action: {action.name}")
        
        try:
            result = await action.execute(ai_response, customer_context)
            logger.info(f"Action {action.name} completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Action {action.name} failed: {e}")
            raise
    
    def get_action_status(self) -> List[Dict[str, Any]]:
        """Get status of all registered actions"""
        return [action.get_metadata() for action in self.actions]
