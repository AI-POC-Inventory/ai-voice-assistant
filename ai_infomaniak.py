# ai_infomaniak.py
import requests, os
from dotenv import load_dotenv
from google_calendar import get_availability
from ai_services import get_ai_data
load_dotenv()

API_TOKEN = os.getenv("INFOMANIAK_API_KEY")
PRODUCT_ID = os.getenv("INFOMANIAK_PRODUCT_ID")
BASE_URL = f"https://api.infomaniak.com/2/ai/{PRODUCT_ID}/openai/v1/chat/completions"
MODEL = "mistral3"

def build_system_prompt(twilio_number: str):
    ai_data = get_ai_data(twilio_number)
    if not ai_data or not ai_data.get("ai_config", {}).get("exists"):
        return "Assistant not configured."

    ai_config = ai_data["ai_config"]
    role_name = ai_config.get("role")
    system_rules = ai_config.get("system_rules", "")
    response_guidelines = ai_config.get("response_guidelines", "")
    conversation_greeting = ai_config.get("conversation_flow", {}).get("greeting", f"Hello! I am {ai_config.get('assistant_name', 'Assistant')}")

    system_prompt = f"""
You are a {role_name}.

CRITICAL RULES:
{system_rules}

RESPONSE GUIDELINES:
{response_guidelines}
"""

    # Only for medical assistant add doctors & availability
    if role_name.lower() == "medical assistant":
        doctors_list = ai_data.get("specialists", [])
        availability, doctor_list = get_availability(twilio_number)  # fetch from Google Calendar
        doctors_text = ", ".join([f"{doc['speacilist_name']} ({doc['specialities']})" for doc in doctor_list])
        availability_text = "\n".join(availability) if availability else "No availability found."

        system_prompt += f"""

Doctors (fixed list):
{doctors_text}

Availability (read-only):
{availability_text}
"""

    return system_prompt

def ai_reply(conversation, twilio_number: str = None):
    if twilio_number:
        system_prompt = build_system_prompt(twilio_number)
        if not conversation or conversation[0].get("role") != "system":
            conversation.insert(0, {"role": "system", "content": system_prompt})

    payload = {
        "model": MODEL,
        "messages": conversation[-8:],
        "temperature": 0.3
    }

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    res = requests.post(BASE_URL, json=payload, headers=headers)
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"]
