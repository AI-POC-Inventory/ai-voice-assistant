from google.adk import Agent
from . import SYSTEM_PROMPT
from .ai_voice_tools import fetch_config, detect_intent, execute_service

agent = Agent(
    name="AI Voice Orchestrator",
    model="models/gemini-1.5-pro",
    system_prompt=SYSTEM_PROMPT,
    tools=[fetch_config, detect_intent, execute_service],
)
