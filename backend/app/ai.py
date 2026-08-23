"""Reminder message generation.

Uses the Claude API to draft a short, personalized reminder when
ANTHROPIC_API_KEY is configured. Falls back to a deterministic template
otherwise (or if the API call fails), so the reminder pipeline never breaks
on a missing key or a transient API error — the risk score / audit log
still get written either way, only the message wording differs.
"""

import logging

from . import models
from .config import settings
from .risk import RiskResult

logger = logging.getLogger(__name__)

CLAUDE_MODEL = "claude-haiku-4-5-20251001"

_client = None


def _get_client():
    global _client
    if _client is None and settings.anthropic_api_key:
        from anthropic import Anthropic

        _client = Anthropic(api_key=settings.anthropic_api_key)
    return _client


def _template_message(patient: models.Patient, risk: RiskResult, channel: str) -> str:
    if risk.status == "overdue":
        due_phrase = f"is now {abs(risk.days_until_due)} day(s) overdue"
    elif risk.status == "due_soon":
        due_phrase = f"is due in {risk.days_until_due} day(s)"
    else:
        due_phrase = f"is due on {patient.due_date.isoformat()}"

    if channel == "SMS":
        return (
            f"Hi {patient.name.split()[0]}, this is a reminder that your "
            f"{patient.medication} refill {due_phrase}. Reply REFILL to request it "
            f"or call your pharmacy. — Refill Reminder System"
        )
    return (
        f"Dear {patient.name},\n\n"
        f"Our records show your {patient.medication} refill (for {patient.condition}) "
        f"{due_phrase}. Please contact your pharmacy or {patient.doctor}'s office to "
        f"arrange your refill.\n\nThank you,\nRefill Reminder System"
    )


def generate_reminder_message(
    patient: models.Patient, risk: RiskResult, channel: str = "SMS"
) -> tuple[str, str]:
    """Returns (message, generated_by) where generated_by is 'claude' or 'template'."""
    client = _get_client()
    if client is None:
        return _template_message(patient, risk, channel), "template"

    length_hint = "under 320 characters, suitable for a single SMS" if channel == "SMS" else "a short email, 3-5 sentences"
    prompt = (
        "Write a friendly, respectful medication refill reminder for a patient. "
        f"Patient first name: {patient.name.split()[0]}. Medication: {patient.medication}. "
        f"Condition being treated: {patient.condition}. Refill status: {risk.status.replace('_', ' ')} "
        f"({risk.days_until_due} days relative to due date). Adherence risk level: {risk.level}. "
        f"Channel: {channel}. Keep it {length_hint}. Do not include a subject line or greeting boilerplate "
        "beyond a simple opener. Output only the message text."
    )

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in response.content if block.type == "text").strip()
        if text:
            return text, "claude"
    except Exception:
        logger.exception("Claude reminder generation failed; falling back to template")

    return _template_message(patient, risk, channel), "template"
