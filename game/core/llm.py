from typing import List, Dict, Any, Callable, Optional, Protocol, TypedDict
from dataclasses import dataclass
from abc import ABC, abstractmethod

"""
Utilities and classes for which to call various LLM APIs
"""

@dataclass
class LLMResponse:
    content: str
    raw_response: Any = None

class LLMProvider(ABC):
    @abstractmethod
    async def generate_response(
        self, 
        model: str,
        system_prompt: str, 
        user_prompt: str,
        **kwargs
    ) -> LLMResponse:
        pass


class ClaudeLLM(LLMProvider):
    def __init__(self, api_key: str):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def generate_response(
        self, 
        model: str,
        system_prompt: str, 
        user_prompt: str,
        **kwargs
    ) -> LLMResponse:
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
        
        response = await self.client.messages.create(
            model=model,
            messages=messages,
            **kwargs
        )
        
        return LLMResponse(
            content=response.content[0].text,
            raw_response=response
        )


class OpenAILLM(LLMProvider):
    def __init__(self, api_key: str):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def generate_response(
        self, 
        model: str,
        system_prompt: str, 
        user_prompt: str,
        **kwargs
    ) -> LLMResponse:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            raw_response=response
        )