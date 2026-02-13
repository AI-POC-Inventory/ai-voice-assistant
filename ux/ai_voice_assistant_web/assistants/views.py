from django.shortcuts import render, redirect, get_object_or_404
from .models import AIVoiceAssistant
from django.utils.timezone import now
import json
from google_auth_oauthlib.flow import Flow
from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponse
import requests
import json
from django.conf import settings

def config_page(request):
    if request.method == "POST":
        languages = request.POST.getlist("languages")
        accents = request.POST.getlist("accents")

        AIVoiceAssistant.objects.create(
            user_id=request.POST.get("user_id"),
            twilio_number=request.POST.get("twilio_number"),
            assistant_name=request.POST.get("assistant_name"),
            role=request.POST.get("role"),

            # Store as JSON strings
            languages=json.dumps(languages),
            accents=json.dumps(accents),

            business_sector=request.POST.get("business_sector"),
            voice_tone=request.POST.get("voice_tone"),
            speaking_speed=request.POST.get("speaking_speed"),
            escalation_rules=request.POST.get("escalation_rules"),
            escalate_after=int(request.POST.get("escalate_after", 2)),
            handoff_message=request.POST.get("handoff_message"),

            is_configurable=True if request.POST.get("is_configurable") else False,
            voice_enabled=True if request.POST.get("voice_enabled") else False,
            text_enabled=True if request.POST.get("text_enabled") else False,

            created_at=now(),
            updated_at=now(),
        )
        return redirect("/")

    records = AIVoiceAssistant.objects.all()
    return render(request, "config.html", {"records": records})


def edit_assistant(request, id):
    obj = get_object_or_404(AIVoiceAssistant, id=id)

    # 🔽 Convert JSON → Python lists for template use
    try:
        obj.languages_list = json.loads(obj.languages) if obj.languages else []
        obj.accents_list = json.loads(obj.accents) if obj.accents else []
    except json.JSONDecodeError:
        obj.languages_list = []
        obj.accents_list = []

    if request.method == "POST":
        obj.twilio_number = request.POST.get("twilio_number")
        obj.assistant_name = request.POST.get("assistant_name")
        obj.role = request.POST.get("role")

        obj.languages = json.dumps(request.POST.getlist("languages"))
        obj.accents = json.dumps(request.POST.getlist("accents"))

        obj.business_sector = request.POST.get("business_sector")
        obj.voice_tone = request.POST.get("voice_tone")
        obj.speaking_speed = request.POST.get("speaking_speed")
        obj.escalation_rules = request.POST.get("escalation_rules")
        obj.escalate_after = int(request.POST.get("escalate_after", 2))
        obj.handoff_message = request.POST.get("handoff_message")

        obj.updated_at = now()
        obj.save()
        return redirect("/")

    context = {
        "obj": obj,
        "LANGUAGES": ["English", "French", "Spanish", "Hindi"],
        "ACCENTS": ["American English", "British English", "Indian English"],
        "VOICE_TONES": ["Professional", "Friendly", "Urgent"],
        "SPEEDS": ["Slow", "Normal", "Fast"],
    }

    return render(request, "edit.html", context)


def delete_assistant(request, id):
    obj = get_object_or_404(AIVoiceAssistant, id=id)
    obj.delete()
    return redirect("/")

def google_auth_start(request):
    assistant = get_object_or_404(AIVoiceAssistant)

    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/calendar'],
        redirect_uri='http://localhost:8000/google/callback/'
    )

    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    request.session['oauth_state'] = state
    request.session['assistant_id'] = assistant.id

    return redirect(auth_url)

def google_auth_callback(request):
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/calendar'],
        state=request.session['oauth_state'],
        redirect_uri='http://localhost:8000/google/callback/'
    )

    flow.fetch_token(authorization_response=request.build_absolute_uri())

    creds = flow.credentials
    assistant = AIVoiceAssistant.objects.get(id=request.session['assistant_id'])

    assistant.google_access_token = creds.token
    assistant.google_refresh_token = creds.refresh_token
    assistant.google_token_expiry = creds.expiry
    assistant.google_calendar_email = creds.id_token.get("email")
    assistant.save()

    return redirect("/")

def google_callback(request):
    code = request.GET.get("code")

    if not code:
        return HttpResponse("No code received from Google", status=400)

    token_url = "https://oauth2.googleapis.com/token"

    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    r = requests.post(token_url, data=data)
    token_data = r.json()

    if "access_token" not in token_data:
        return HttpResponse(f"Token error: {token_data}", status=400)

    return HttpResponse("✅ Google Calendar connected successfully.")


