from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..deps import require_roles

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/kpis", response_model=schemas.DashboardKpis)
def get_kpis(db: Session = Depends(get_db), _user=Depends(require_roles("admin"))):
    patients = crud.list_patients(db)
    risks = [crud.patient_risk(db, p) for p in patients]
    return schemas.DashboardKpis(
        total_patients=len(patients),
        overdue_refills=sum(1 for r in risks if r.status == "overdue"),
        open_ops_issues=sum(1 for p in patients if p.ops_issue != "None"),
        high_risk_patients=sum(1 for r in risks if r.level == "High"),
    )
