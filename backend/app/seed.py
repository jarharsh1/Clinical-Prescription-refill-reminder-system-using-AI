"""Seeds demo users, patients, and refill history.

Dates are computed relative to today() at seed time (rather than hardcoded),
so the overdue/due-soon/on-track spread is always meaningful whenever this
is run — unlike the original prototype's frozen 2025-07-27 reference date.
"""

import datetime as dt

from . import models
from .database import Base, SessionLocal, engine
from .security import hash_password

DEMO_USERS = [
    {"username": "clinician", "password": "clinician123", "full_name": "Dr. Priya Carter", "role": "clinician"},
    {"username": "ops", "password": "ops123", "full_name": "Jordan Reyes", "role": "ops"},
    {"username": "admin", "password": "admin123", "full_name": "Sam Whitfield", "role": "admin"},
]


def _rel(days: int) -> dt.date:
    return dt.date.today() + dt.timedelta(days=days)


def _patients() -> list[dict]:
    return [
        {"id": "P12345", "name": "Alex Johnson", "medication": "Metformin", "condition": "Diabetes",
         "doctor": "Dr. Carter", "due_date": _rel(-2), "last_refill": _rel(-32),
         "insurance": "Aetna - Verified", "contact": "555-0101", "ops_issue": "Manual Call Required"},
        {"id": "P67890", "name": "Maria Garcia", "medication": "Atorvastatin", "condition": "Hyperlipidemia",
         "doctor": "Dr. Lee", "due_date": _rel(5), "last_refill": _rel(-25),
         "insurance": "Cigna - Verified", "contact": "555-0102", "ops_issue": "None"},
        {"id": "P55432", "name": "David Chen", "medication": "Ozempic", "condition": "Diabetes",
         "doctor": "Dr. Patel", "due_date": _rel(9), "last_refill": _rel(-21),
         "insurance": "BCBS - Pending", "contact": "555-0103", "ops_issue": "Insurance Mismatch"},
        {"id": "P87654", "name": "Sarah Miller", "medication": "Levothyroxine", "condition": "Hypothyroidism",
         "doctor": "Dr. Carter", "due_date": _rel(14), "last_refill": _rel(-16),
         "insurance": "United - Verified", "contact": "555-0104", "ops_issue": "Out of Stock"},
        {"id": "P99876", "name": "James Brown", "medication": "Lisinopril", "condition": "Hypertension",
         "doctor": "Dr. Lee", "due_date": _rel(26), "last_refill": _rel(-4),
         "insurance": "Humana - Verified", "contact": "555-0105", "ops_issue": "None"},
        {"id": "P11223", "name": "Emily White", "medication": "Amlodipine", "condition": "Hypertension",
         "doctor": "Dr. Patel", "due_date": _rel(6), "last_refill": _rel(-24),
         "insurance": "Aetna - Verified", "contact": "555-0106", "ops_issue": "None"},
        {"id": "P22334", "name": "Michael Clark", "medication": "Metformin", "condition": "Diabetes",
         "doctor": "Dr. Carter", "due_date": _rel(19), "last_refill": _rel(-11),
         "insurance": "Cigna - Verified", "contact": "555-0107", "ops_issue": "None"},
    ]


# (patient_id, days_late, taken) history entries, oldest-relevant adherence signal per patient
_REFILL_HISTORY = {
    "P12345": [(-95, 3, True), (-63, 6, True), (-32, 0, False)],
    "P67890": [(-85, 1, True), (-55, 0, True), (-25, 2, True)],
    "P55432": [(-80, 0, True), (-50, 0, True), (-21, 0, True)],
    "P87654": [(-75, 0, True), (-45, 1, True), (-16, 0, True)],
    "P99876": [(-64, 0, True), (-34, 0, True), (-4, 0, True)],
    "P11223": [(-84, 4, True), (-54, 5, True), (-24, 3, True)],
    "P22334": [(-71, 0, True), (-41, 0, True), (-11, 0, True)],
}


def seed(reset: bool = False) -> None:
    if reset:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(models.User).count() == 0:
            for u in DEMO_USERS:
                db.add(models.User(
                    username=u["username"],
                    password_hash=hash_password(u["password"]),
                    full_name=u["full_name"],
                    role=u["role"],
                ))

        if db.query(models.Patient).count() == 0:
            for p in _patients():
                db.add(models.Patient(**p))
            db.commit()

            for patient_id, events in _REFILL_HISTORY.items():
                for offset, days_late, taken in events:
                    db.add(models.RefillEvent(
                        patient_id=patient_id,
                        refill_date=_rel(offset),
                        days_late=days_late,
                        taken=taken,
                    ))
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    print("Database seeded.")
