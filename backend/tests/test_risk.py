import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.models import Patient, RefillEvent  # noqa: E402
from app.risk import compute_risk  # noqa: E402


def make_patient(due_offset_days: int, ops_issue: str = "None") -> Patient:
    return Patient(
        id="PX", name="Test", medication="Med", condition="Cond", doctor="Doc",
        due_date=dt.date.today() + dt.timedelta(days=due_offset_days),
        last_refill=dt.date.today() - dt.timedelta(days=30),
        insurance="X", contact="555", ops_issue=ops_issue,
    )


def test_overdue_patient_is_high_or_medium_risk():
    patient = make_patient(due_offset_days=-10)
    result = compute_risk(patient, [], today=dt.date.today())
    assert result.status == "overdue"
    assert result.score > 0
    assert result.level in {"Medium", "High"}


def test_on_track_no_history_is_low_risk():
    patient = make_patient(due_offset_days=30)
    result = compute_risk(patient, [], today=dt.date.today())
    assert result.status == "on_track"
    assert result.level == "Low"
    assert result.score == 0


def test_due_soon_status():
    patient = make_patient(due_offset_days=3)
    result = compute_risk(patient, [], today=dt.date.today())
    assert result.status == "due_soon"
    assert result.score > 0


def test_missed_refills_increase_score():
    patient = make_patient(due_offset_days=30)
    events = [
        RefillEvent(patient_id="PX", refill_date=dt.date.today() - dt.timedelta(days=60), days_late=0, taken=False),
    ]
    result = compute_risk(patient, events, today=dt.date.today())
    assert result.score > 0
    assert any("missed" in r.lower() for r in result.reasons)


def test_open_ops_issue_adds_points():
    patient = make_patient(due_offset_days=30, ops_issue="Out of Stock")
    result = compute_risk(patient, [], today=dt.date.today())
    assert result.score == 10
    assert any("operational issue" in r.lower() for r in result.reasons)


def test_score_is_clamped_to_100():
    patient = make_patient(due_offset_days=-60, ops_issue="Manual Call Required")
    events = [
        RefillEvent(patient_id="PX", refill_date=dt.date.today() - dt.timedelta(days=d), days_late=15, taken=False)
        for d in (30, 60, 90)
    ]
    result = compute_risk(patient, events, today=dt.date.today())
    assert result.score <= 100
    assert result.level == "High"
