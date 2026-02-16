from google.adk import Agent
from .prompt import SYSTEM_PROMPT
from .ai_voice_tools import fetch_config, detect_intent, execute_service

from google.adk.agents import Agent
from .ai_voice_tools import fetch_config, detect_intent, execute_service,get_details_from_calendar,resolve_datetime_range,book_appointment

agent = Agent(
    name="voice_agent",
    model="gemini-2.5-flash",
    instruction=SYSTEM_PROMPT,
    tools=[
        fetch_config,
        detect_intent,
        execute_service,
        resolve_datetime_range, 
        get_details_from_calendar,
        book_appointment
    ],
)

