"""Rule-based adherence-risk and refill-urgency scoring.

Deterministic and explainable by design: every point on the 0-100 score maps
to a concrete, listed reason. This is the "AI" in the sense of a small expert
system, not a trained model — it's intentionally simple enough to unit test
and to explain to a clinician, which a black-box classifier would not be.
"""

import datetime as dt
from dataclasses import dataclass, field

from . import models


@dataclass
class RiskResult:
    score: int
    level: str
    days_until_due: int
    status: str
    reasons: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "score": self.score,
            "level": self.level,
            "days_until_due": self.days_until_due,
            "status": self.status,
            "reasons": self.reasons,
        }


def _due_status(days_until_due: int) -> str:
    if days_until_due < 0:
        return "overdue"
    if days_until_due <= 7:
        return "due_soon"
    return "on_track"


def compute_risk(
    patient: models.Patient,
    refill_events: list[models.RefillEvent] | None = None,
    today: dt.date | None = None,
) -> RiskResult:
    today = today or dt.date.today()
    refill_events = refill_events or []

    days_until_due = (patient.due_date - today).days
    status = _due_status(days_until_due)

    score = 0
    reasons: list[str] = []

    if days_until_due < 0:
        overdue_points = min(40, abs(days_until_due) * 4)
        score += overdue_points
        reasons.append(f"Refill is {abs(days_until_due)} day(s) overdue")
    elif days_until_due <= 7:
        due_soon_points = (8 - days_until_due) * 3
        score += due_soon_points
        reasons.append(f"Refill due in {days_until_due} day(s)")

    missed_events = [e for e in refill_events if not e.taken]
    if missed_events:
        missed_points = min(30, len(missed_events) * 15)
        score += missed_points
        reasons.append(f"{len(missed_events)} missed refill(s) in history")

    late_events = [e for e in refill_events if e.taken and e.days_late > 0]
    if late_events:
        avg_late = sum(e.days_late for e in late_events) / len(late_events)
        late_points = min(20, round(avg_late * 2))
        score += late_points
        reasons.append(f"Avg. {avg_late:.1f} day(s) late on past refills")

    if patient.ops_issue and patient.ops_issue != "None":
        score += 10
        reasons.append(f"Open operational issue: {patient.ops_issue}")

    score = max(0, min(100, score))
    if score >= 60:
        level = "High"
    elif score >= 30:
        level = "Medium"
    else:
        level = "Low"

    if not reasons:
        reasons.append("No adherence or logistics concerns on record")

    return RiskResult(
        score=score,
        level=level,
        days_until_due=days_until_due,
        status=status,
        reasons=reasons,
    )
