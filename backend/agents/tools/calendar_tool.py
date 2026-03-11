from services.calendar.google_calendar import list_available_slots, create_calendar_event
from api.config import settings
from datetime import datetime


def check_availability(days_ahead: int = 7) -> str:
    """Consulta horários disponíveis e retorna texto formatado para o usuário."""
    try:
        slots = list_available_slots(settings.google_calendar_id, days_ahead, 30)
        if not slots:
            return "Não encontrei horários disponíveis nos próximos dias. Por favor, entre em contato diretamente com nossa equipe."
        formatted = []
        for s in slots[:4]:
            dt = datetime.fromisoformat(s)
            dia = dt.strftime("%A, %d/%m")
            hora = dt.strftime("%H:%M")
            formatted.append(f"• {dia} às {hora}")
        return "Horários disponíveis:\n" + "\n".join(formatted)
    except Exception as e:
        return f"Não consegui verificar a agenda agora: {e}"


def create_event(
    start_iso: str,
    lead_name: str,
    lead_email: str,
    lead_phone: str = "",
) -> str:
    """Cria evento no Google Calendar e retorna confirmação."""
    try:
        result = create_calendar_event(
            calendar_id=settings.google_calendar_id,
            start_iso=start_iso,
            duration_minutes=30,
            summary=f"Demo TOIN — {lead_name}",
            attendee_email=lead_email,
            description=f"Lead: {lead_name}\nTelefone: {lead_phone}",
        )
        dt = datetime.fromisoformat(start_iso)
        return (
            f"Reunião agendada com sucesso!\n"
            f"📅 {dt.strftime('%A, %d/%m às %H:%M')}\n"
            f"📧 Convite enviado para {lead_email}"
        )
    except Exception as e:
        return f"Não consegui criar o evento: {e}"
