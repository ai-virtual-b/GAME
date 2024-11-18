# 🤖 Simple LLM Agent Framework

Example of a restructured version of a modular, clean and simple agentic framework and library.

A flexible, modular framework for building agents powered by Large Language Models. This framework consists of environment and an agent.

```
                   🌍 Environment
                         ⬇️
Plan & Reasoning ➡️ 🤖 Agent ➡️ Actions
                         ⬆️
                   🧠 LLM Provider
```

Agent requires an LLM provider, an environment, and a set of actions to interact with the environment. LLM agents are essentially controlled by their prompts so this should be the most visible part of the agent. This framework makes that very clear. It is very explicit what goes into the prompt (both system and user prompts). This can be found in the [`templates.py`](game/core/templates.py) file.

Just from this prompt, we can clearly see what is passed into the LLM. The variables can be dynamically changed based on the environment, the actions available and the current state. If more detail is needed, everything should be easily accessible and transparent. 

Let's take the DEFAULT SYSTEM PROMPT for example:
```python
DEFAULT_SYSTEM_TEMPLATE = """You are an agent with the following characteristics:
{character_info}

Environment Description:
{world_description}

The environment provides the following state information:
{state_descriptions}

You will also be provided with a history of actions you have previuosly taken and their outputs and outcomes.

You have access to these actions:
{available_actions}

Follow these guidelines:
{agent_guidelines}

...more instructions about response format underneath

```

The character info is obtained at Agent initialization and must be passed at the constructor. The world description is obtained from the environment. The state descriptions are obtained from the environment. The agent guidelines are obtained from the environment. 

The available actions are obtained from action registry, which is a container of actions that have to be registered to the agent. An action has a template which needs to be implemented as a class with a default function which is called as part of that action and has a certain output structure. Once registered with the agent, registry will store it and format it for the prompt approrpately in the agent logic. 


## 🌟 Features

- 🧩 **Modular Architecture**: Easily swap LLM providers, environments, and actions
- 🔄 **Action History**: Maintains some limited context of previous actions and outcomes
- 🛠️ **Extensible**: Simple interfaces for adding new environments and actions
- 🤝 **Provider Agnostic**: Works with any LLM (Claude, GPT-4, etc.)

## 📦 Installation

```bash
pip install blablabla
```

## 🚀 Quick Start

```python
from llm_agent import Agent, Environment, ClaudeLLM
from llm_agent.environments import TwitterEnvironment

# Initialize environment
twitter_env = TwitterEnvironment(
    api_config={
        "api_key": "your_key",
        # ... other config
    }
)

# Create agent
agent = Agent(
    llm_provider=ClaudeLLM(api_key="your_claude_key"),
    environment=twitter_env,
    character_info={
        "name": "TechBot",
        "personality": "Friendly tech enthusiast",
        "tone": "Professional but approachable"
    }
)

# Register actions
agent.register_action(
    name="post_tweet",
    func=twitter_env.post_tweet,
    description="Post a new tweet",
    required_params={"content": "Tweet content"},
    example={"action": "post_tweet", "content": "Hello, Tech World!"}
)

# Run agent
await agent.run_loop(max_steps=5)
```

## 🏗️ Architecture

```
game/
├── core/
│   ├── agent.py      # Main agent logic and and prompt composition
│   ├── environment.py # Environment base class
│   ├── actions.py    # Action/Function handling and storage utils
│   ├── llm.py        # LLM provider interface (with differnt providers)
│   └── templates.py  # Agent System/user prompt templates
├── environments/     # Currently supported environments
│   ├── twitter.py
│   ├── discord.py
│   └── etc...
└── actions/          # Currently supported actions by domain/function
    ├── twitter.py
    ├── discord.py
    ├── perplexity.py
    └── etc...
```

## 🌍 Creating Custom Environments

see [twitter](game/environments/twitter.py) environment example

## 🎯 Action Planning

The agent can plan and execute multiple actions:

```python
# Agent response format
{
    "reasoning": "We need to engage with trending AI topics and provide value...",
    "plan": [
        {
            "reasoning": "First, analyze current AI trends",
            "action": "analyze_trends",
            "parameters": {"topics": ["AI", "Tech"]}
        },
        {
            "reasoning": "Create informative thread based on findings",
            "action": "create_thread",
            "parameters": {"content": [...]}
        }
    ]
}
```

## 🔧 Configuration

Customize agent behavior through:
- System templates
- User templates
- World descriptions
- State descriptions and functions
- Action definitions

## 📚 Examples

### Twitter Bot
```python
# See examples/twitter_bot.py
```

### Discord Bot
```python
# See examples/discord_bot.py
```

