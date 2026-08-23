import datetime as dt
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import database, models  # noqa: E402
from app.main import app  # noqa: E402
from app.security import hash_password  # noqa: E402


@pytest.fixture()
def db_session(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    database.Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[database.get_db] = override_get_db

    session = TestingSessionLocal()
    yield session
    session.close()
    app.dependency_overrides.clear()


@pytest.fixture()
def client(db_session):
    db_session.add_all([
        models.User(username="clinician", password_hash=hash_password("clinician123"),
                    full_name="Dr. Test", role="clinician"),
        models.User(username="ops", password_hash=hash_password("ops123"),
                    full_name="Ops Test", role="ops"),
        models.User(username="admin", password_hash=hash_password("admin123"),
                    full_name="Admin Test", role="admin"),
    ])
    db_session.add(models.Patient(
        id="P00001", name="Test Patient", medication="Metformin", condition="Diabetes",
        doctor="Dr. Test", due_date=dt.date.today() - dt.timedelta(days=3),
        last_refill=dt.date.today() - dt.timedelta(days=33),
        insurance="Test Insurance", contact="555-0000", ops_issue="None",
    ))
    db_session.commit()
    return TestClient(app)


def auth_headers(client, username, password):
    resp = client.post("/api/auth/login", data={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
