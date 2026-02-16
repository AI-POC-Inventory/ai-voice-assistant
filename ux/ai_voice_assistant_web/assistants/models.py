from django.db import models

class AIVoiceAssistant(models.Model):
    class Meta:
        db_table = "ai_voice_assistants"
        managed = False   # 🔴 Uses existing SQLite table

    id = models.AutoField(primary_key=True)

    # Core Identity
    user_id = models.IntegerField()
    twilio_number = models.CharField(max_length=100, unique=True)
    assistant_name = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=255, null=True, blank=True)

    # Language & Voice
    languages = models.TextField(null=True, blank=True)   # JSON list
    accents = models.TextField(null=True, blank=True)     # JSON list
    voice_tone = models.CharField(max_length=100, null=True, blank=True)
    speaking_speed = models.CharField(max_length=50, null=True, blank=True)

    # Sector & Services
    business_sector = models.CharField(max_length=100, null=True, blank=True)
    services = models.TextField(null=True, blank=True)    # JSON list

    # Escalation & Flow
    escalation_rules = models.TextField(null=True, blank=True)
    escalate_after = models.IntegerField(default=2)
    handoff_message = models.CharField(max_length=255, null=True, blank=True)

    # Feature Flags
    is_configurable = models.BooleanField(default=True)
    voice_enabled = models.BooleanField(default=True)
    text_enabled = models.BooleanField(default=True)
    booking_required = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    google_calendar_email = models.EmailField(null=True, blank=True)
    google_access_token = models.TextField(null=True, blank=True)
    google_refresh_token = models.TextField(null=True, blank=True)
    google_token_expiry = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return f"{self.assistant_name} ({self.twilio_number})"
