from google.adk import tool


@tool
def fetch_config(twilio_number: str):
    """Fetch AI assistant config using Twilio number"""
    return AIVoiceAssistant.objects.filter(twilio_number=twilio_number).values().first()

@tool
def detect_intent(user_text: str):
    """Detect intent from user speech"""
    return {"text": user_text}

@tool
def execute_service(intent: str, context: dict):
    """Execute service dynamically"""
    return {
        "status": "ok",
        "message": f"Executing {intent} with context {context}"
    }
