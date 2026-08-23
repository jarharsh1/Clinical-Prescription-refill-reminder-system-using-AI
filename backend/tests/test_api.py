import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tests.conftest import auth_headers  # noqa: E402


def test_login_requires_valid_credentials(client):
    resp = client.post("/api/auth/login", data={"username": "admin", "password": "wrong"})
    assert resp.status_code == 401


def test_login_succeeds_and_lists_patients(client):
    headers = auth_headers(client, "clinician", "clinician123")
    resp = client.get("/api/patients", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["id"] == "P00001"
    assert "risk" in body[0]


def test_unauthenticated_request_is_rejected():
    from fastapi.testclient import TestClient
    from app.main import app

    resp = TestClient(app).get("/api/patients")
    assert resp.status_code == 401


def test_clinician_cannot_create_patient(client):
    headers = auth_headers(client, "clinician", "clinician123")
    resp = client.post("/api/patients", json={
        "id": "P99999", "name": "New", "medication": "Med", "condition": "Cond",
        "doctor": "Doc", "due_date": "2030-01-01", "last_refill": "2029-12-01",
        "insurance": "Ins", "contact": "555-9999",
    }, headers=headers)
    assert resp.status_code == 403


def test_admin_can_create_patient(client):
    headers = auth_headers(client, "admin", "admin123")
    resp = client.post("/api/patients", json={
        "id": "P99999", "name": "New", "medication": "Med", "condition": "Cond",
        "doctor": "Doc", "due_date": "2030-01-01", "last_refill": "2029-12-01",
        "insurance": "Ins", "contact": "555-9999",
    }, headers=headers)
    assert resp.status_code == 201


def test_ops_can_resolve_issue(client, db_session):
    from app import models
    patient = db_session.query(models.Patient).first()
    patient.ops_issue = "Out of Stock"
    db_session.commit()

    headers = auth_headers(client, "ops", "ops123")
    resp = client.patch(f"/api/patients/{patient.id}/resolve", json={}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["ops_issue"] == "None"


def test_send_reminder_falls_back_to_template_without_api_key(client):
    headers = auth_headers(client, "ops", "ops123")
    resp = client.post("/api/patients/P00001/remind", json={"channel": "SMS"}, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["log"]["generated_by"] == "template"
    assert body["log"]["status"] == "simulated"
    assert len(body["log"]["message"]) > 0


def test_clinician_cannot_send_reminder(client):
    headers = auth_headers(client, "clinician", "clinician123")
    resp = client.post("/api/patients/P00001/remind", json={"channel": "SMS"}, headers=headers)
    assert resp.status_code == 403
