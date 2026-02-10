from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
import logging
import requests
import os
from pathlib import Path
from openai import OpenAI
import tempfile
from dotenv import load_dotenv
from app.nlu.extractor import extract_intent_and_entities
from app.nlu.dialogue.manager import decide_next_question, get_prompt_for_slot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Twilio credentials - Set these as environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")

# OpenAI client for STT
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="Patient IVR", version="1.0.0")


async def transcribe_twilio_recording(recording_url: str) -> str:
    """
    Download WAV recording from Twilio and transcribe it using OpenAI Whisper
    
    Args:
        recording_url: The Twilio recording URL
    
    Returns:
        Transcribed text from the audio
    """
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        logger.error("Twilio credentials not configured")
        return ""
    
    try:
        # Download recording as WAV
        download_url = recording_url + ".wav"
        response = requests.get(
            download_url,
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to download recording: HTTP {response.status_code}")
            return ""
        
        # Save to temporary file and transcribe
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name
        
        # Transcribe using OpenAI Whisper
        with open(tmp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        logger.info(f"Transcript: {transcript}")
        return transcript
        
    except Exception as e:
        logger.error(f"Error transcribing recording: {str(e)}")
        return ""


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Twilio Webhook API is running"}

@app.post("/webhook/voice")
async def voice_webhook(
    request: Request,
    From: str = Form(...),
    To: str = Form(...),
    CallSid: str = Form(None),
):
    """
    Webhook endpoint for incoming voice calls from Twilio
    
    Twilio sends the following parameters:
    - From: The caller's phone number
    - To: Your Twilio phone number
    - CallSid: Unique identifier for the call
    """
    logger.info(f"Received call from {From} to {To}")
    
    # Return TwiML response that records the caller's message
    twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Hello! Please leave your message after the beep. Press the star key when finished.</Say>
    <Record action="/webhook/recording" maxLength="120" timeout="10" finishOnKey="*" playBeep="true" />
    <Say voice="alice">We did not receive a recording. Goodbye!</Say>
</Response>"""
    
    return Response(content=twiml_response, media_type="application/xml")


@app.post("/webhook/recording")
async def recording_webhook(
    request: Request,
    RecordingUrl: str = Form(None),
    RecordingSid: str = Form(None),
    RecordingDuration: str = Form(None),
    From: str = Form(None),
    To: str = Form(None),
    CallSid: str = Form(None),
):
    """
    Webhook endpoint for receiving audio recording from Twilio
    
    Twilio sends the following parameters:
    - RecordingUrl: URL to access the audio recording
    - RecordingSid: Unique identifier for the recording
    - RecordingDuration: Duration of the recording in seconds
    - From: The caller's phone number
    - To: Your Twilio phone number
    - CallSid: Unique identifier for the call
    """
    logger.info(f"Received recording from {From}")
    logger.info(f"Recording URL: {RecordingUrl}")
    logger.info(f"Recording Duration: {RecordingDuration} seconds")
    logger.info(f"Recording SID: {RecordingSid}")
    
    # Transcribe the recording
    transcript = await transcribe_twilio_recording(RecordingUrl)
    
    if transcript:
        logger.info(f"Transcribed text: {transcript}")
        
        # Extract intent and entities from transcript
        nlu_result = extract_intent_and_entities(transcript)
        
        # Decide next question based on NLU result
        next_slot = decide_next_question(nlu_result.intent, nlu_result.entities)
        
        if next_slot:
            # Ask for more information
            response_msg = get_prompt_for_slot(next_slot)
        else:
            # All information collected
            response_msg = "Thank you. Your appointment details are complete."
    else:
        response_msg = "I'm sorry, I couldn't understand your message. Please try again."
    
    # Return dynamic TwiML response
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">{response_msg}</Say>
    <Hangup/>
</Response>"""
    
    return Response(content=twiml_response, media_type="application/xml")


@app.post("/webhook/status")
async def status_webhook(
    request: Request,
    MessageSid: str = Form(None),
    MessageStatus: str = Form(None),
    To: str = Form(None),
    From: str = Form(None),
):
    """
    Webhook endpoint for message status callbacks from Twilio
    
    Tracks message delivery status: queued, sent, delivered, failed, etc.
    """
    logger.info(f"Message {MessageSid} status: {MessageStatus}")
    
    return {"status": "received"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
