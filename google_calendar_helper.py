from googleapiclient.discovery import build
from google.oauth2 import service_account
import datetime
import pytz

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleCalendarHelper:
    def __init__(
        self,
        service_account_file,
        timezone="UTC",
        calendar_id="primary",
    ):
        self.timezone = pytz.timezone(timezone)
        self.calendar_id = calendar_id

        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=SCOPES,
        )

        self.service = build(
            "calendar",
            "v3",
            credentials=credentials,
        )

    def list_events(self, days=7):
        now = datetime.datetime.utcnow().isoformat() + "Z"
        end = (
            datetime.datetime.utcnow()
            + datetime.timedelta(days=days)
        ).isoformat() + "Z"

        events = self.service.events().list(
            calendarId=self.calendar_id,
            timeMin=now,
            timeMax=end,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        return events.get("items", [])

    def create_event(self, title, start_dt, end_dt, description=""):
        event = {
            "summary": title,
            "description": description,
            "start": {
                "dateTime": start_dt.isoformat(),
                "timeZone": str(self.timezone),
            },
            "end": {
                "dateTime": end_dt.isoformat(),
                "timeZone": str(self.timezone),
            },
        }

        return self.service.events().insert(
            calendarId=self.calendar_id,
            body=event,
        ).execute()
