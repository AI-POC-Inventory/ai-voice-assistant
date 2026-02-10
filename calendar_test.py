# calendar_access_test.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SERVICE_ACCOUNT_FILE = "appointment-486022-5db1b1709556.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]

CALENDAR_ID = "e530b4c1f2e638590bc6973c1f754683125ef95d3b2f88ddecbe5a3027deaa93@group.calendar.google.com"

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("calendar", "v3", credentials=credentials)

try:
    cal = service.calendars().get(calendarId=CALENDAR_ID).execute()
    print("✅ Calendar access successful!")
    print("Calendar summary:", cal.get("summary"))
except HttpError as e:
    print("❌ Calendar access failed:", e)
