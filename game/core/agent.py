# game/core/agent.py
from typing import List, Dict, Any, Callable, Optional
import json
import asyncio

from game.core.actions import Action, ActionRegistry
from game.core.environment import Environment
from game.core.llm import LLMProvider
from game.core.templates import DEFAULT_SYSTEM_TEMPLATE, DEFAULT_USER_TEMPLATE

class ActionResult:
    def __init__(self, success: bool, message: str, data: Any = None):
        self.success = success
        self.message = message
        self.data = data

class Agent:
    def __init__(
        self,
        llm_provider: LLMProvider,
        environment: Environment,
        system_template: str = DEFAULT_SYSTEM_TEMPLATE,
        user_template: str = DEFAULT_USER_TEMPLATE,
        character_info: Dict[str, str] = None,
        agent_guidelines: List[str] = None,
        max_history: int = 5
    ):
        self.llm_provider = llm_provider
        self.environment = environment
        self.system_template = system_template
        self.user_template = user_template
        self.character_info = character_info or {}
        self.agent_guidelines = agent_guidelines or []
        self.action_registry = ActionRegistry()
        self.action_history: List[Dict] = []
        self.max_history = max_history
    
    def build_system_prompt(self) -> str:
        """Build the complete system prompt"""
        action_descriptions = self.action_registry.get_action_descriptions()
        state_descriptions = self.environment.get_state_descriptions()
        world_description = self.environment.get_world_description()
        
        return self.system_template.format(
            character_info=json.dumps(self.character_info, indent=2),
            world_description=world_description,
            state_descriptions=json.dumps(state_descriptions, indent=2),
            available_actions=json.dumps(action_descriptions, indent=2),
            agent_guidelines="\n".join(f"- {g}" for g in self.agent_guidelines)
        )
    
    def build_user_prompt(self, state: Dict[str, Any]) -> str:
        """Build the user prompt with state and history"""
        history = self._format_action_history()
        return self.user_template.format(
            state=json.dumps(state, indent=2),
            action_history=history
        )
    
    def _format_action_history(self) -> str:
        """Format recent actions for prompt inclusion"""
        if not self.action_history:
            return "No previous actions taken."
            
        return "\n".join(
            f"- {action['name']} ({action['timestamp']}): "
            f"{action['reasoning']}\n  Result: {action['result']}"
            for action in self.action_history[-self.max_history:]
        )
    
    def register_action(
        self, 
        name: str, 
        func: Callable, 
        description: str,
        required_params: Dict[str, str],
        example: Dict[str, Any]
    ):
        """Register a new action"""
        action = Action(func, description, required_params, example)
        self.action_registry.register(name, action)
    
    async def execute_action(
        self, 
        action_name: str, 
        reasoning: str = "",
        **kwargs
    ) -> ActionResult:
        """Execute a registered action and store in history"""
        action = self.action_registry.get_action(action_name)
        if not action:
            return ActionResult(False, f"Action '{action_name}' not found")
        
        try:
            result = await action.func(**kwargs)
            
            # Store in history
            self.action_history.append({
                'name': action_name,
                'parameters': kwargs,
                'reasoning': reasoning,
                'result': result,
            })
            
            # Maintain history size
            if len(self.action_history) > self.max_history:
                self.action_history.pop(0)
                
            return ActionResult(True, "Action executed successfully", result)
            
        except Exception as e:
            return ActionResult(False, f"Action failed: {str(e)}")
    
    async def get_next_action(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Get the next action from the LLM"""
        system_prompt = self.build_system_prompt()
        user_prompt = self.build_user_prompt(state)
        
        response = await self.llm_provider.generate_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        
        try:
            action_data = json.loads(response.content)
            return action_data
        except json.JSONDecodeError:
            raise ValueError("LLM response was not in the expected JSON format")
    
    async def run_loop(self, max_steps: int = 5):
        """Run the agent loop"""
        for step in range(max_steps):
            try:
                # Get current state
                state = await self.environment.get_state()
                
                # Get next action from LLM
                action_data = await self.get_next_action(state)
                action_name = action_data.pop("action")
                reasoning = action_data.pop("reasoning", "")
                
                # Execute the action
                result = await self.execute_action(
                    action_name, 
                    reasoning=reasoning, 
                    **action_data
                )
                
                if not result.success:
                    print(f"Action failed: {result.message}")
                    break
                    
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"Error in agent loop: {str(e)}")
                break