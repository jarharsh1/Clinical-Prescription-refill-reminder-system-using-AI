from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import ai, crud, schemas
from ..database import get_db
from ..deps import require_roles
from .patients import _get_or_404

router = APIRouter(prefix="/api/patients", tags=["reminders"])


class ReminderRequest(BaseModel):
    channel: str = "SMS"  # SMS | Email


@router.post("/{patient_id}/remind", response_model=schemas.ReminderResponse)
def send_reminder(
    patient_id: str,
    body: ReminderRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("ops", "admin")),
):
    patient = _get_or_404(db, patient_id)
    risk = crud.patient_risk(db, patient)
    message, generated_by = ai.generate_reminder_message(patient, risk, body.channel)
    log = crud.add_contact_log(
        db,
        patient=patient,
        channel=body.channel,
        message=message,
        risk_level=risk.level,
        generated_by=generated_by,
        triggered_by_user=user.username,
    )
    return schemas.ReminderResponse(log=log, risk=schemas.RiskInfo(**risk.as_dict()))


@router.get("/{patient_id}/contact-logs", response_model=list[schemas.ContactLogOut])
def list_contact_logs(patient_id: str, db: Session = Depends(get_db), _user=Depends(require_roles("ops", "admin", "clinician"))):
    return _get_or_404(db, patient_id).contact_logs
