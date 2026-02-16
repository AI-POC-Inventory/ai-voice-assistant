import sqlite3
from typing import Optional, Dict
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz

DB_PATH = "D:\\Sujit\\AiML\\ai-voice-assistant\\db\\ai-voice.db"   # adjust if needed


def fetch_config(twilio_number: str) -> Optional[Dict]:
    """Fetch AI assistant config using Twilio number (no Django ORM)"""
    print(f"Fetching config for Twilio number: {twilio_number}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # return dict-like rows
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM ai_voice_assistants
        WHERE twilio_number = ?
        """,
        (twilio_number,)
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)

    return None


def detect_intent(user_text: str):
    """Detect intent from user speech"""
    print(f"Detecting intent from user text: {user_text}")
    return {"text": user_text}

def execute_service(intent: str, context: dict):
    """Execute service dynamically and decide next steps based on intent and context"""
    return {"status": "success", "details": f"Executed {intent} with context {context}"}
    



def get_details_from_calendar(
    action: str,
    access_token: str,
    refresh_token: str,
    token_expiry: str,
    start_datetime_iso: str,
    end_datetime_iso: str,
    timezone: str,
    summary: str
):
    """Fetch only  details for doctors from Google Calendar for next steps based on action"""
    print(f"Fetching calendar details with action: {action}, start: {start_datetime_iso}, end: {end_datetime_iso}, timezone: {timezone}, summary filter: {summary}")
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id="989713142030-38j6ajhumsf381i79t7ga3qq81tg86rj.apps.googleusercontent.com",
        client_secret="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"
    )

    # 🔄 Auto refresh token if expired
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    service = build("calendar", "v3", credentials=creds)

    events_result = service.events().list(
    calendarId="primary",
    timeMin=start_datetime_iso,
    timeMax=end_datetime_iso,
    singleEvents=True,
    orderBy="startTime",
    ).execute()

    events = events_result.get('items', [])
    print("Fetched events from Google Calendar:", events)
    return events

def book_appointment(
    action: str,
    access_token: str,
    refresh_token: str,
    token_expiry: str,
    start_datetime_iso: str,
    end_datetime_iso: str,
    timezone: str,
    summary: str
):
    """Always check availability in calendar before booking.
       Book appointment in Google Calendar for doctors based on action and details, Add Dr name and patient name in summary"""
    print(f"book appointment with action: {action}, start: {start_datetime_iso}, end: {end_datetime_iso}, timezone: {timezone}, summary filter: {summary}")
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id="989713142030-38j6ajhumsf381i79t7ga3qq81tg86rj.apps.googleusercontent.com",
        client_secret="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"
    )

    # 🔄 Auto refresh token if expired
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    service = build("calendar", "v3", credentials=creds)

    event = {
            'summary': summary,
            'start': {'dateTime': start_datetime_iso, 'timeZone': 'Asia/Kolkata'},
            'end': {'dateTime': end_datetime_iso, 'timeZone': 'Asia/Kolkata'},
        }

    service.events().insert(calendarId='primary', body=event).execute()

    return {"status": "booked"}

from google.adk.tools import FunctionTool

from google.adk.tools import FunctionTool
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import calendar
import re
import dateparser


def resolve_datetime_range(start_datetime: str, end_datetime: str):
    """
    Fully automatic datetime range resolver.
    Handles:
    - next week
    - next X days
    - next month
    - tomorrow
    - specific weekday
    - morning / afternoon / evening
    """

    tz = ZoneInfo("Asia/Kolkata")
    now = datetime.now(tz)

    text = (start_datetime or "").lower().strip()

    # ---------------------------
    # 1️⃣ Handle next X days
    # ---------------------------
    match_days = re.search(r"next\s+(\d+)\s+days", text)
    if match_days:
        days = int(match_days.group(1))
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=days)
        end = end.replace(hour=23, minute=59, second=59)
        return {
            "start_datetime": start.isoformat(),
            "end_datetime": end.isoformat()
        }

    # ---------------------------
    # 2️⃣ Handle next week
    # ---------------------------
    if "next week" in text:
        next_week = now + timedelta(days=(7 - now.weekday()))
        start = next_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=6)
        end = end.replace(hour=23, minute=59, second=59)
        return {
            "start_datetime": start.isoformat(),
            "end_datetime": end.isoformat()
        }

    # ---------------------------
    # 3️⃣ Handle next month
    # ---------------------------
    if "next month" in text:
        year = now.year + (1 if now.month == 12 else 0)
        month = 1 if now.month == 12 else now.month + 1

        start = datetime(year, month, 1, tzinfo=tz)
        last_day = calendar.monthrange(year, month)[1]
        end = datetime(year, month, last_day, 23, 59, 59, tzinfo=tz)

        return {
            "start_datetime": start.isoformat(),
            "end_datetime": end.isoformat()
        }

    # ---------------------------
    # 4️⃣ Handle time-of-day words
    # ---------------------------
    time_ranges = {
        "morning": (6, 11),
        "afternoon": (12, 16),
        "evening": (17, 21),
    }

    for key, (start_hour, end_hour) in time_ranges.items():
        if key in text:
            parsed = dateparser.parse(
                text,
                settings={
                    "TIMEZONE": "Asia/Kolkata",
                    "RETURN_AS_TIMEZONE_AWARE": True,
                    "RELATIVE_BASE": now
                }
            )

            if not parsed:
                parsed = now + timedelta(days=1)

            start = parsed.replace(hour=start_hour, minute=0, second=0)
            end = parsed.replace(hour=end_hour, minute=59, second=59)

            return {
                "start_datetime": start.isoformat(),
                "end_datetime": end.isoformat()
            }

    # ---------------------------
    # 5️⃣ Default fallback (dateparser)
    # ---------------------------
    parsed = dateparser.parse(
        text,
        settings={
            "TIMEZONE": "Asia/Kolkata",
            "RETURN_AS_TIMEZONE_AWARE": True,
            "RELATIVE_BASE": now
        }
    )

    if parsed:
        start = parsed.replace(hour=0, minute=0, second=0)
        end = parsed.replace(hour=23, minute=59, second=59)
        return {
            "start_datetime": start.isoformat(),
            "end_datetime": end.isoformat()
        }

    # ---------------------------
    # 6️⃣ Final fallback: next 7 days
    # ---------------------------
    start = now.replace(hour=0, minute=0, second=0)
    end = start + timedelta(days=7)
    end = end.replace(hour=23, minute=59, second=59)

    return {
        "start_datetime": start.isoformat(),
        "end_datetime": end.isoformat()
    }


datetime_tool = FunctionTool(resolve_datetime_range)

