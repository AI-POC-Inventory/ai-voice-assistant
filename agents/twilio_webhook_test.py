import uuid
import os

from agents.agent import agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

os.environ["GOOGLE_API_KEY"] = "AIzaSyCFmGJLnlVTsz_oO3P17bbr7X4-Y5Kq7e0"

APP_NAME = "IVR"
USER_ID = "+917872435623"

def main():
    print("Starting Twilio Webhook Test...")

    session_service = InMemorySessionService()

    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=session_service,
        auto_create_session=True  # Let ADK handle session creation
    )

    session_id = str(uuid.uuid4())

    user_input = "twilio_number: +917872435623. Can you please provide information on orthopedic doctor?"

    while True:
        message = types.Content(
            role="user",
            parts=[types.Part(text=user_input)]
        )

        events = runner.run(
            user_id=USER_ID,
            session_id=session_id,
            new_message=message,
        )

        final_response = None

        for event in events:
            if event.content and event.content.role in ("model", "assistant"):
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        final_response = part.text

        if final_response:
            print(final_response)

            # Continue only if assistant is asking something
            if "?" in final_response:
                user_input = input("User: ")
                continue

        break
if __name__ == "__main__":
    main()
