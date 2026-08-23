import datetime as dt

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(128))
    role: Mapped[str] = mapped_column(String(16))  # clinician | ops | admin


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    medication: Mapped[str] = mapped_column(String(128))
    condition: Mapped[str] = mapped_column(String(128))
    doctor: Mapped[str] = mapped_column(String(128))
    due_date: Mapped[dt.date] = mapped_column(Date)
    last_refill: Mapped[dt.date] = mapped_column(Date)
    insurance: Mapped[str] = mapped_column(String(128))
    contact: Mapped[str] = mapped_column(String(32))
    ops_issue: Mapped[str] = mapped_column(String(64), default="None")

    refill_events: Mapped[list["RefillEvent"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan", order_by="RefillEvent.refill_date"
    )
    contact_logs: Mapped[list["ContactLog"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan", order_by="ContactLog.timestamp.desc()"
    )


class RefillEvent(Base):
    """Historical refill pickups, used to compute adherence risk."""

    __tablename__ = "refill_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"))
    refill_date: Mapped[dt.date] = mapped_column(Date)
    days_late: Mapped[int] = mapped_column(Integer, default=0)  # vs. that cycle's due date
    taken: Mapped[bool] = mapped_column(Boolean, default=True)  # False = missed entirely

    patient: Mapped["Patient"] = relationship(back_populates="refill_events")


class ContactLog(Base):
    """A reminder that was generated and (simulated) sent to a patient."""

    __tablename__ = "contact_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"))
    timestamp: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    channel: Mapped[str] = mapped_column(String(16))  # SMS | Email
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="simulated")
    risk_level: Mapped[str] = mapped_column(String(16))
    generated_by: Mapped[str] = mapped_column(String(16), default="template")  # template | claude
    triggered_by_user: Mapped[str] = mapped_column(String(64))

    patient: Mapped["Patient"] = relationship(back_populates="contact_logs")
