from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from agent_runner import run_agent

app = FastAPI()

#ngrok http 8000

@app.post("/ivr")
async def ivr_webhook(request: Request):
    form = await request.form()

    caller_number = form.get("From")
    user_speech = form.get("SpeechResult")

    print(f"Incoming call from {caller_number}")
    print(f"User speech: {user_speech}")

    response = VoiceResponse()

    # First call → Ask initial question
    if not user_speech:
        gather = Gather(
            input="speech",
            action="/ivr",
            method="POST",
            speechTimeout="auto"
        )
        gather.say("Welcome to the clinic. How can I help you today?")
        response.append(gather)
        return Response(str(response), media_type="application/xml")

    # Run ADK agent
    caller_number = "+917872435623";
    agent_reply = run_agent(
        phone_number=caller_number,
        user_text=user_speech
    )

    gather = Gather(
        input="speech",
        action="/ivr",
        method="POST",
        speechTimeout="auto"
    )

    gather.say(agent_reply)
    response.append(gather)

    return Response(str(response), media_type="application/xml")
