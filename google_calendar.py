# google_calendar.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import pytz
from ai_services import get_ai_data  # unified service

SERVICE_ACCOUNT_FILE = "appointment-486022-5db1b1709556.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]
TIMEZONE = pytz.timezone("Asia/Dhaka")

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("calendar", "v3", credentials=credentials)

def format_datetime(iso_string, is_date_only=False):
    if not iso_string:
        return "Time not specified"

    if is_date_only:
        dt = datetime.strptime(iso_string, "%Y-%m-%d")
        dt = TIMEZONE.localize(dt)
        return dt.strftime("%d %B %Y (All day)")

    dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
    local = dt.astimezone(TIMEZONE)
    return local.strftime("%d %B %Y at %I:%M %p")

# Load specialists and print
def load_specialists(twilio_number):
    ai_data = get_ai_data(twilio_number)
    specialists = ai_data.get("specialists", [])

    doctor_list = []
    print("\n================= SPECIALISTS =================")
    print(f"Total doctors received: {len(specialists)}\n")
    for idx, s in enumerate(specialists, start=1):
        print(f"{idx}. Doctor Name : {s['doctor_name']}")
        print(f"   Speciality  : {s['specialities']}")
        print(f"   Calendar ID : {s['calendar_id']}\n")

        doctor_list.append({
            "speacilist_name": s["doctor_name"],
            "specialities": s["specialities"],
            "calendar_id": s["calendar_id"]
        })
    print("================================================\n")
    return doctor_list

# Fetch availability for all doctors (only medical assistant role)
def get_availability(twilio_number, max_results=50):
    doctor_list = load_specialists(twilio_number)
    availability = []
    now = datetime.now(TIMEZONE).isoformat()

    for doc in doctor_list:
        calendar_id = doc.get("calendar_id")
        if not calendar_id:
            continue

        try:
            events = service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime"
            ).execute().get("items", [])
        except HttpError as e:
            print(f"Error fetching calendar for {doc['speacilist_name']}: {e}")
            continue

        for e in events:
            if e.get("transparency") != "transparent":
                continue
            start = e["start"].get("dateTime") or e["start"].get("date")
            end = e["end"].get("dateTime") or e["end"].get("date")
            is_date_only = "date" in e["start"]

            slot = f"{doc['speacilist_name']} ({doc['specialities']}): {format_datetime(start, is_date_only)} → {format_datetime(end, is_date_only)}"
            availability.append(slot)

    return availability, doctor_list
# Create booking
def create_booking(specialist, summary="Appointment", start_time=None):
    tz = TIMEZONE
    start_time = start_time or datetime.now(tz) + timedelta(hours=2)
    end_time = start_time + timedelta(minutes=30)

    event = {
        "summary": summary,
        "start": {"dateTime": start_time.isoformat(), "timeZone": "Asia/Dhaka"},
        "end": {"dateTime": end_time.isoformat(), "timeZone": "Asia/Dhaka"},
    }

    try:
        created = service.events().insert(calendarId=specialist["calendar_id"], body=event).execute()
        print(f"[DEBUG] Booking created: {created.get('htmlLink')}")
        return created.get("htmlLink")
    except HttpError as e:
        print(f"Booking failed for {specialist['speacilist_name']}: {e}")
        return None
