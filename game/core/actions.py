from typing import List, Dict, Any, Callable, Optional, Protocol, TypedDict
from dataclasses import dataclass


@dataclass
class ActionResult:
    success: bool
    message: str
    data: Any = None

class Action:
    def __init__(
        self, 
        func: Callable,
        description: str, 
        required_params: Dict[str, str],
        example: Dict[str, Any]
    ):
        self.func = func
        self.description = description
        self.required_params = required_params
        self.example = example

# a container for all registered actions available to the agent
class ActionRegistry:
    def __init__(self):
        self._actions: Dict[str, Action] = {}
    
    def register(
        self, 
        name: str, 
        action: Action
    ):
        """Register a new action"""
        self._actions[name] = action
    
    def get_action(self, name: str) -> Optional[Action]:
        """Get an action by name"""
        return self._actions.get(name)
    
    def get_action_descriptions(self) -> Dict[str, Dict[str, Any]]:
        """Get descriptions of all registered actions"""
        return {
            name: {
                "description": action.description,
                "required_params": action.required_params,
                "example": action.example
            }
            for name, action in self._actions.items()
        }