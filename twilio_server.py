# twilio_server_full.py
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from ai_infomaniak import ai_reply
from ai_services import get_ai_data
import json

app = Flask(__name__)

# -----------------------------
# Store caller sessions
# -----------------------------
CALLERS = {}  # key = Twilio number

def get_caller_data(to_number):
    """
    Fetch AI assistant config and session for a given Twilio number.
    """
    if to_number in CALLERS:
        return CALLERS[to_number]

    # Fetch AI configuration and specialists
    ai_data = get_ai_data(to_number)
    if not ai_data or not ai_data.get("ai_config", {}).get("exists"):
        print(f"[DEBUG] No AI assistant configured for number: {to_number}")
        return None

    ai_config = ai_data["ai_config"]

    # Parse conversation flow and languages
    conversation_flow = ai_config.get("conversation_flow") or {}
    languages = ai_config.get("languages") or []
    assistant_name = ai_config.get("assistant_name") or "Assistant"

    # Only fetch specialists if role is medical assistant
    role = ai_config.get("role", "").lower()
    doctor_list = []
    if role == "medical assistant":
        doctor_list = ai_data.get("specialists", [])
        print("\n================= SPECIALISTS FETCHED =================")
        for idx, s in enumerate(doctor_list, start=1):
            print(f"{idx}. Doctor Name : {s['doctor_name']}")
            print(f"   Speciality  : {s['specialities']}")
            print(f"   Calendar ID : {s['calendar_id']}\n")
        print("======================================================\n")

    # Initialize session
    CALLERS[to_number] = {
        "user_id": ai_config["user_id"],
        "assistant_name": assistant_name,
        "lang": None,  # will be selected dynamically
        "conversation": [
            {"role": "system", "content": conversation_flow.get("greeting", f"Hello I am {assistant_name}!")}
        ],
        "doctor_list": doctor_list,
        "ai_config": ai_config,
        "languages": languages
    }

    print(f"[DEBUG] Caller session created for Twilio number {to_number}")
    return CALLERS[to_number]

# -----------------------------
# /voice route
# -----------------------------
@app.route("/voice", methods=["POST"])
def voice():
    to_number = request.form.get("To", "")
    caller_data = get_caller_data(to_number)

    resp = VoiceResponse()
    if not caller_data:
        resp.say("Sorry, this number is not configured.", voice="alice")
        resp.hangup()
        return Response(str(resp), mimetype="text/xml")

    # Select language if multiple
    if len(caller_data["languages"]) > 1 and not caller_data["lang"]:
        gather = Gather(input="speech", speechTimeout="auto", action="/select_language", method="POST")
        lang_options = ", ".join(caller_data["languages"])
        gather.say(f"Hello! My name is {caller_data['assistant_name']}. Which language do you prefer? Options are: {lang_options}.", voice="alice")
        resp.append(gather)
        return Response(str(resp), mimetype="text/xml")

    # Single language or already selected
    lang = caller_data["lang"] or (caller_data["languages"][0] if caller_data["languages"] else "en")
    caller_data["lang"] = lang

    # Greeting
    greeting = caller_data["ai_config"].get("conversation_flow", {}).get("greeting", f"Hello I am {caller_data['assistant_name']}!")
    resp.say(greeting, voice="alice", language=lang_to_twilio(lang))

    # Ask user question
    gather = Gather(input="speech", speechTimeout="auto", action="/process_speech", method="POST")
    gather.say("Please tell me your request after the beep.", voice="alice", language=lang_to_twilio(lang))
    resp.append(gather)

    return Response(str(resp), mimetype="text/xml")

# -----------------------------
# Language selection
# -----------------------------
@app.route("/select_language", methods=["POST"])
def select_language():
    to_number = request.form.get("To", "")
    caller_data = get_caller_data(to_number)
    resp = VoiceResponse()

    if not caller_data:
        resp.say("Error loading configuration.", voice="alice")
        resp.hangup()
        return Response(str(resp), mimetype="text/xml")

    # Get language choice from user
    choice = request.form.get("SpeechResult", "").strip().lower()
    available = [l.lower() for l in caller_data["languages"]]

    if choice in available:
        caller_data["lang"] = choice
        resp.say(f"{caller_data['assistant_name']} will speak in {choice}.", voice="alice", language=lang_to_twilio(choice))
    else:
        gather = Gather(input="speech", speechTimeout="auto", action="/select_language", method="POST")
        gather.say("Sorry, I didn't catch that. Please select one of the available languages.", voice="alice")
        resp.append(gather)
        return Response(str(resp), mimetype="text/xml")

    # Proceed to ask first question
    gather = Gather(input="speech", speechTimeout="auto", action="/process_speech", method="POST")
    gather.say("Please tell me your request after the beep.", voice="alice", language=lang_to_twilio(caller_data["lang"]))
    resp.append(gather)

    return Response(str(resp), mimetype="text/xml")

# -----------------------------
# /process_speech route
# -----------------------------
@app.route("/process_speech", methods=["POST"])
def process_speech():
    to_number = request.form.get("To", "")
    caller_data = get_caller_data(to_number)

    resp = VoiceResponse()
    if not caller_data:
        resp.say("Error loading configuration.", voice="alice")
        resp.hangup()
        return Response(str(resp), mimetype="text/xml")

    lang = caller_data["lang"] or "en"
    user_text = request.form.get("SpeechResult", "").strip()

    if not user_text:
        resp.say("I didn't catch that. Please speak again.", voice="alice")
        gather = Gather(input="speech", speechTimeout="auto", action="/process_speech", method="POST")
        gather.say("Please say your request after the beep.", voice="alice")
        resp.append(gather)
        return Response(str(resp), mimetype="text/xml")

    # Add user message to conversation
    caller_data["conversation"].append({"role": "user", "content": user_text})

    # Generate AI reply
    reply = ai_reply(caller_data["conversation"], twilio_number=to_number)
    caller_data["conversation"].append({"role": "assistant", "content": reply})

    # Speak AI reply
    resp.say(reply, voice="alice", language=lang_to_twilio(lang))

    # Gather next question
    gather = Gather(input="speech", speechTimeout="auto", action="/process_speech", method="POST")
    gather.say("Do you want to continue? You can ask another question.", voice="alice", language=lang_to_twilio(lang))
    resp.append(gather)

    return Response(str(resp), mimetype="text/xml")

# -----------------------------
# Helpers
# -----------------------------
def lang_to_twilio(lang):
    """Map simple language codes to Twilio voice language codes"""
    lang_map = {
        "english": "en-US",
        "french": "fr-FR",
        "français": "fr-FR"
    }
    return lang_map.get(lang.lower(), "en-US")

# -----------------------------
# Main entry
# -----------------------------
if __name__ == "__main__":
    print("🚀 Twilio AI Server running on port 5000")
    app.run(port=5000)
