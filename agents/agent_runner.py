
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from agent import agent
from google.genai import types
import os
from dotenv import load_dotenv
import re
import json


load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
APP_NAME = "ivr_app"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

session_service = InMemorySessionService()

runner = Runner(
    agent=agent,
    app_name=APP_NAME,
    session_service=session_service,
    auto_create_session=True
)


def run_agent(phone_number: str, user_text: str) -> str:
    
    user_text += f" Twilio number: {phone_number}."
    
    message = types.Content(
            role="user",
            parts=[types.Part(text=user_text)]
        )
    print(f"Phone number: {phone_number}, User text: {user_text}")
    events = runner.run(
        user_id=phone_number,
        session_id=phone_number,
        new_message=message,
    )

    final_text = None

    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    final_text = part.text


    print(f"Agent reply: {final_text}")
    
    match = re.search(r'({.*})', final_text, re.DOTALL)
    if match:
        json_content = match.group(1)
        data = json.loads(json_content)
        # Extract 'response' from JSON object if possible
        if isinstance(data, dict) and "response" in data:
            return data["response"]
    return "Sorry, I didn't understand that."

