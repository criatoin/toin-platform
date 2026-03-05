from services.calendar.google_calendar import list_available_slots, create_calendar_event
from datetime import datetime

TOIN_CALENDAR_ID = "primary"  # ou ID especifico configurado por tenant


def check_availability(days_ahead: int = 7, duration_minutes: int = 30) -> list[str]:
    slots = list_available_slots(TOIN_CALENDAR_ID, days_ahead, duration_minutes)
    formatted = []
    for s in slots:
        dt = datetime.fromisoformat(s)
        formatted.append(dt.strftime("%A, %d/%m as %H:%M"))
    return formatted


def create_event(
    tenant_id: str,
    slot: str,
    lead_name: str,
    lead_email: str,
    lead_phone: str,
) -> dict:
    # Para MVP: assume que slot ja esta em formato ISO
    result = create_calendar_event(
        calendar_id=TOIN_CALENDAR_ID,
        start_iso=slot,
        duration_minutes=30,
        summary=f"Demo TOIN — {lead_name}",
        attendee_email=lead_email,
        description=f"Lead: {lead_name}\nTelefone: {lead_phone}",
    )
    return result
