"""
Prompt templates (system prompt and user prompts) for the agent
"""

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

When planning actions:
1. First, analyze the current state and history
2. Think through what needs to be accomplished considering the environment constraints
3. Plan a sequence of actions to achieve your goal
4. Explain your reasoning and strategy

Respond in JSON format:
{
    "reasoning": "Detailed explanation of your thought process and overall strategy",
    "plan": [
        {{
            "reasoning": "Specific reasoning for this step",
            "action": "name_of_action",
            "parameters": {{}}
        }}
    ]
}

Example response:
{
    "reasoning": "Given the Twitter platform constraints and current engagement metrics, 
                 we need to carefully time and structure our content for maximum impact.",
    "plan": [
        {
            "reasoning": "First analyze recent trending topics in our niche",
            "action": "analyze_trends",
            "parameters": {"topics": ["tech", "AI"], "timeframe": "24h"}
        },
        {
            "reasoning": "Draft and post content when our audience is most active",
            "action": "post_tweet",
            "parameters": {"content": "...", "schedule": "optimal_time"}
        }
    ]
}"""


DEFAULT_USER_TEMPLATE = """Current State:
{state}

Action History:
{action_history}

Goal:
{goal}

Given this, think through what needs to be accomplished and develop a plan of action. Explain your overall strategy and then break it down into specific steps."""