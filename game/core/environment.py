from typing import Dict, Any, List
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json

@dataclass
class StateDescription:
    """Describes a state variable"""
    name: str
    description: str
    type: str
    example: Any
    relevance: str  # Why this state matters

class Environment(ABC):
    """Abstract base class for different environments"""
    
    def __init__(self, 
                 state_descriptions: Dict[str, Any],
                 world_description: str):
        pass
    
    @abstractmethod
    async def get_state(self) -> Dict[str, Any]:
        """Function that gets current state of the environment"""
        pass
    
    @abstractmethod
    def get_state_descriptions(self) -> Dict[str, StateDescription]:
        """Return descriptions of all state variables for prompts"""
        pass
    
    @abstractmethod
    def get_world_description(self) -> str:
        """Get world description for prompts"""
        pass