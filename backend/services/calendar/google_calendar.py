from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from api.config import settings

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service():
    creds = Credentials(
        token=None,
        refresh_token=settings.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scopes=SCOPES,
    )
    if not creds.valid:
        creds.refresh(Request())
    return build("calendar", "v3", credentials=creds)


def list_available_slots(
    calendar_id: str, days_ahead: int = 7, duration_minutes: int = 30
) -> list[str]:
    """Retorna horários livres nos próximos N dias (formato ISO)."""
    service = get_calendar_service()
    now = datetime.utcnow()
    end = now + timedelta(days=days_ahead)

    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=now.isoformat() + "Z",
            timeMax=end.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    busy_times = [
        (e["start"]["dateTime"], e["end"]["dateTime"])
        for e in events_result.get("items", [])
        if "dateTime" in e.get("start", {})
    ]

    slots = []
    current = now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)

    while current < end and len(slots) < 6:
        if current.weekday() < 5:  # seg-sex
            is_busy = any(
                datetime.fromisoformat(b[0].replace("Z", "+00:00")) <= current
                < datetime.fromisoformat(b[1].replace("Z", "+00:00"))
                for b in busy_times
            )
            if not is_busy:
                slots.append(current.isoformat())
        current += timedelta(hours=1)
        if current.hour >= 18:
            current = current.replace(hour=9) + timedelta(days=1)

    return slots


def create_calendar_event(
    calendar_id: str,
    start_iso: str,
    duration_minutes: int,
    summary: str,
    attendee_email: str,
    description: str = "",
) -> dict:
    service = get_calendar_service()
    start = datetime.fromisoformat(start_iso)
    end = start + timedelta(minutes=duration_minutes)

    event = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start.isoformat(), "timeZone": "America/Sao_Paulo"},
        "end": {"dateTime": end.isoformat(), "timeZone": "America/Sao_Paulo"},
        "attendees": [{"email": attendee_email}],
        "conferenceData": {
            "createRequest": {"requestId": f"toin-{start_iso}"},
        },
    }

    result = (
        service.events()
        .insert(
            calendarId=calendar_id,
            body=event,
            conferenceDataVersion=1,
            sendUpdates="all",
        )
        .execute()
    )

    return result
