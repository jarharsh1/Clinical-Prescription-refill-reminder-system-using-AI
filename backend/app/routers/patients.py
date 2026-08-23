from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from ..deps import get_current_user, require_roles

router = APIRouter(prefix="/api/patients", tags=["patients"])


def _to_patient_out(db: Session, patient: models.Patient) -> schemas.PatientOut:
    risk = crud.patient_risk(db, patient)
    return schemas.PatientOut(
        id=patient.id,
        name=patient.name,
        medication=patient.medication,
        condition=patient.condition,
        doctor=patient.doctor,
        due_date=patient.due_date,
        last_refill=patient.last_refill,
        insurance=patient.insurance,
        contact=patient.contact,
        ops_issue=patient.ops_issue,
        risk=schemas.RiskInfo(**risk.as_dict()),
    )


def _get_or_404(db: Session, patient_id: str) -> models.Patient:
    patient = crud.get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return patient


@router.get("", response_model=list[schemas.PatientOut])
def list_patients(db: Session = Depends(get_db), _user=Depends(get_current_user)):
    return [_to_patient_out(db, p) for p in crud.list_patients(db)]


@router.get("/{patient_id}", response_model=schemas.PatientOut)
def get_patient(patient_id: str, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    return _to_patient_out(db, _get_or_404(db, patient_id))


@router.get("/{patient_id}/history", response_model=list[schemas.RefillEventOut])
def get_patient_history(
    patient_id: str, db: Session = Depends(get_db), _user=Depends(get_current_user)
):
    return _get_or_404(db, patient_id).refill_events


@router.post("", response_model=schemas.PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient(
    data: schemas.PatientCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
):
    if crud.get_patient(db, data.id) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Patient ID already exists")
    patient = crud.create_patient(db, data.model_dump())
    return _to_patient_out(db, patient)


@router.patch("/{patient_id}", response_model=schemas.PatientOut)
def update_patient(
    patient_id: str,
    data: schemas.PatientUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
):
    patient = _get_or_404(db, patient_id)
    patient = crud.update_patient(db, patient, data.model_dump(exclude_unset=True))
    return _to_patient_out(db, patient)


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(
    patient_id: str, db: Session = Depends(get_db), _user=Depends(require_roles("admin"))
):
    crud.delete_patient(db, _get_or_404(db, patient_id))


@router.patch("/{patient_id}/resolve", response_model=schemas.PatientOut)
def resolve_patient_issue(
    patient_id: str,
    _body: schemas.ResolveRequest | None = None,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("ops", "admin")),
):
    patient = crud.resolve_ops_issue(db, _get_or_404(db, patient_id))
    return _to_patient_out(db, patient)
