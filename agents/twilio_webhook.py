from django.http import HttpResponse
from .agent import agent

def twilio_webhook(request):
    user_text = request.POST.get("SpeechResult")
    twilio_number = request.POST.get("To")

    response = agent.run(
        input=f"Caller said: '{user_text}'. Twilio number: {twilio_number}"
    )

    return HttpResponse(f"<Response><Say>{response}</Say></Response>", content_type="text/xml")
