import datetime as dt

from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: str
    username: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    full_name: str
    role: str


class RefillEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    refill_date: dt.date
    days_late: int
    taken: bool


class ContactLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: dt.datetime
    channel: str
    message: str
    status: str
    risk_level: str
    generated_by: str
    triggered_by_user: str


class RiskInfo(BaseModel):
    score: int  # 0-100
    level: str  # Low | Medium | High
    days_until_due: int
    status: str  # overdue | due_soon | on_track
    reasons: list[str]


class PatientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    medication: str
    condition: str
    doctor: str
    due_date: dt.date
    last_refill: dt.date
    insurance: str
    contact: str
    ops_issue: str
    risk: RiskInfo


class PatientCreate(BaseModel):
    id: str
    name: str
    medication: str
    condition: str
    doctor: str
    due_date: dt.date
    last_refill: dt.date
    insurance: str
    contact: str
    ops_issue: str = "None"


class PatientUpdate(BaseModel):
    medication: str | None = None
    condition: str | None = None
    doctor: str | None = None
    due_date: dt.date | None = None
    last_refill: dt.date | None = None
    insurance: str | None = None
    contact: str | None = None
    ops_issue: str | None = None


class ResolveRequest(BaseModel):
    resolution_note: str | None = None


class ReminderResponse(BaseModel):
    log: ContactLogOut
    risk: RiskInfo


class DashboardKpis(BaseModel):
    total_patients: int
    overdue_refills: int
    open_ops_issues: int
    high_risk_patients: int
