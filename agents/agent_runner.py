from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from agents.agent import agent
from google.genai import types
import os

APP_NAME = "ivr_app"
os.environ["GOOGLE_API_KEY"] = "AIzaSyCFmGJLnlVTsz_oO3P17bbr7X4-Y5Kq7e0"

session_service = InMemorySessionService()

runner = Runner(
    agent=agent,
    app_name=APP_NAME,
    session_service=session_service,
    auto_create_session=True
)


def run_agent(phone_number: str, user_text: str) -> str:
    message = types.Content(
            role="user",
            parts=[types.Part(text=user_text)]
        )
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

    return final_text or "Sorry, I didn't understand that."

response = run_agent("+7872435623", "Hello, I want to book an appointment with an orthopedic doctor.")   
print(response)
