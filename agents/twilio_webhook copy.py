from django.http import HttpResponse
from agents.agent import agent

user_text = "I need doctor appointment"
twilio_number = "+6734623862"

agent.run(
    input=f"Caller said: '{user_text}'. Twilio number: {twilio_number}"
)

    
