from django.shortcuts import render, redirect, get_object_or_404
from .models import AIVoiceAssistant
from django.utils.timezone import now
import json


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
