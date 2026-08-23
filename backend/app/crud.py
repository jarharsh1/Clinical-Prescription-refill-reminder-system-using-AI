import datetime as dt

from sqlalchemy.orm import Session

from . import models
from .risk import compute_risk


def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(models.User).filter(models.User.username == username).first()


def list_patients(db: Session) -> list[models.Patient]:
    return db.query(models.Patient).order_by(models.Patient.due_date).all()


def get_patient(db: Session, patient_id: str) -> models.Patient | None:
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()


def create_patient(db: Session, data: dict) -> models.Patient:
    patient = models.Patient(**data)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def update_patient(db: Session, patient: models.Patient, data: dict) -> models.Patient:
    for key, value in data.items():
        if value is not None:
            setattr(patient, key, value)
    db.commit()
    db.refresh(patient)
    return patient


def delete_patient(db: Session, patient: models.Patient) -> None:
    db.delete(patient)
    db.commit()


def resolve_ops_issue(db: Session, patient: models.Patient) -> models.Patient:
    patient.ops_issue = "None"
    db.commit()
    db.refresh(patient)
    return patient


def add_contact_log(
    db: Session,
    *,
    patient: models.Patient,
    channel: str,
    message: str,
    risk_level: str,
    generated_by: str,
    triggered_by_user: str,
) -> models.ContactLog:
    log = models.ContactLog(
        patient_id=patient.id,
        timestamp=dt.datetime.utcnow(),
        channel=channel,
        message=message,
        status="simulated",
        risk_level=risk_level,
        generated_by=generated_by,
        triggered_by_user=triggered_by_user,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def patient_risk(db: Session, patient: models.Patient, today: dt.date | None = None):
    return compute_risk(patient, patient.refill_events, today)
