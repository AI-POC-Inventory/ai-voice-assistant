# main.py
from record import record_audio
from stt import transcribe
from tts import speak
from google_calendar import get_availability, create_booking
from ai_infomaniak import ai_reply
from ai_services import get_ai_data
import time

# -----------------------------
# Helpers
# -----------------------------
def human_wait(msg, lang):
    speak(msg, lang)
    time.sleep(1.2)

def speak_interruptible(text, lang):
    sentences = text.split(". ")
    for s in sentences:
        speak(s, lang)
        record_audio(duration=1)
        interrupt = transcribe("input.wav", lang)
        if interrupt.strip():
            return interrupt
    return None

def select_language(languages, assistant_name):
    if len(languages) == 1:
        return languages[0]
    speak(f"Hello! My name is {assistant_name}. Which language do you prefer? Options are: {', '.join(languages)}.", "en")
    while True:
        record_audio(duration=4)
        user_speech = transcribe("input.wav", "en").lower()
        for lang in languages:
            if lang.lower() in user_speech:
                return lang
        speak(f"Sorry, please say one of the available languages: {', '.join(languages)}.", "en")

# -----------------------------
# Initialize
# -----------------------------
TWILIO_NUMBER = "+41225391848"  # Assistant number
ai_data = get_ai_data(TWILIO_NUMBER)

if not ai_data or not ai_data.get("ai_config", {}).get("exists"):
    print("No AI assistant configured for this number.")
    exit()

ai_config = ai_data["ai_config"]
assistant_name = ai_config.get("assistant_name", "Assistant")
languages = ai_config.get("languages", ["English"])
role = ai_config.get("role", "").lower()
conversation_flow = ai_config.get("conversation_flow", {})
conversation = [{"role": "system", "content": conversation_flow.get("greeting", f"Hello I am {assistant_name}!") }]

# -----------------------------
# Fetch specialists if role is medical assistant
# -----------------------------
doctor_list = []
if role == "medical assistant":
    # Fetch availability and specialists from Google Calendar / DB
    availability, doctor_list = get_availability(TWILIO_NUMBER)

    # Print specialists for testing
    print("\n================= SPECIALISTS FETCHED =================")
    for idx, s in enumerate(doctor_list, start=1):
        print(f"{idx}. Doctor Name : {s['speacilist_name']}")
        print(f"   Speciality  : {s['specialities']}")
        print(f"   Calendar ID : {s['calendar_id']}\n")
    print("======================================================\n")

# -----------------------------
# Language selection
# -----------------------------
lang = select_language(languages, assistant_name)

# Greet user
speak(conversation_flow.get("greeting", f"Hello! I am {assistant_name}."), lang)

# -----------------------------
# Main conversation loop
# -----------------------------
while True:
    record_audio(duration=5)
    user_text = transcribe("input.wav", lang).strip()

    if not user_text:
        speak("I’m listening. Please say that again.", lang)
        continue

    conversation.append({"role": "user", "content": user_text})
    user_lower = user_text.lower()

    # -----------------------------
    # Get availability for this assistant
    # -----------------------------
    availability, _ = get_availability(TWILIO_NUMBER)

    # Detect requested doctor
    requested_doctor = None
    for doc in doctor_list:
        if doc['speacilist_name'].lower() in user_lower:
            requested_doctor = doc
            break

    # -----------------------------
    # Availability query
    # -----------------------------
    if any(k in user_lower for k in ["availability", "available", "schedule", "time"]):

        if requested_doctor:
            slots = [s for s in availability if requested_doctor['speacilist_name'] in s]
            reply = "\n".join(slots) if slots else f"No availability found for {requested_doctor['speacilist_name']}."
        else:
            reply = "Here are the available doctors and slots:\n" + "\n".join(availability) if availability else "No slots available at the moment."

    # -----------------------------
    # Booking
    # -----------------------------
    elif any(k in user_lower for k in ["book", "appointment", "reserve"]):

        if not requested_doctor:
            reply = "Please tell me which doctor you want to book."
        else:
            link = create_booking(
                requested_doctor['calendar_id'],
                summary=f"Appointment with {requested_doctor['speacilist_name']}"
            )
            reply = f"Your appointment with {requested_doctor['speacilist_name']} has been booked. {link}" if link else "Sorry, I could not complete the booking."

    # -----------------------------
    # Fallback to AI
    # -----------------------------
    else:
        reply = ai_reply(conversation)

    conversation.append({"role": "assistant", "content": reply})

    # Speak reply with interruption
    interrupt = speak_interruptible(reply, lang)
    if interrupt:
        conversation.append({"role": "user", "content": interrupt})
