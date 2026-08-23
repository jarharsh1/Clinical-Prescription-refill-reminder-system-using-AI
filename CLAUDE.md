# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A KPI-driven prescription refill reminder system with a FastAPI backend and a React (Vite)
frontend, split into `backend/` and `frontend/`. It computes a rule-based adherence-risk score
per patient and can generate personalized reminder messages via the Claude API (falling back to a
deterministic template when no API key is set). Reminders are **simulated** — logged to the
database, not actually delivered via SMS/email.

See `README.md` for setup/run instructions and demo account credentials.

## Running the app

```bash
# backend (from backend/)
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000   # auto-seeds SQLite DB + demo users on startup

# frontend (from frontend/, separate terminal)
npm install && npm run dev                  # http://localhost:5173, proxies /api to :8000
```

Backend tests: `cd backend && source .venv/bin/activate && pytest`.
Frontend build check: `cd frontend && npm run build`.
There is no frontend test suite configured; `npm run lint` runs oxlint.

## Architecture

### Backend (`backend/app/`)

- **`models.py`** — SQLAlchemy models: `User` (role: `clinician`/`ops`/`admin`), `Patient`,
  `RefillEvent` (historical refill pickups, drives risk scoring), `ContactLog` (every generated
  reminder, with `status` always `"simulated"`).
- **`risk.py`** — `compute_risk(patient, refill_events, today)` — a deterministic, explainable
  rule-based scorer (0–100 → Low/Medium/High) combining due-date proximity, missed-refill count,
  average lateness, and open ops issues. Every point maps to a human-readable reason string
  returned to the frontend. This is intentionally not a trained model, to keep it explainable and
  unit-testable (`tests/test_risk.py`).
- **`ai.py`** — `generate_reminder_message(patient, risk, channel)` calls the Claude API
  (`claude-haiku-4-5-20251001`) when `ANTHROPIC_API_KEY` is set, and falls back to a template
  message on a missing key or any API error — the reminder pipeline (and its `ContactLog` write)
  never breaks on this call failing.
- **`deps.py`** — `get_current_user` (JWT decode) and `require_roles(*roles)` — role checks are
  enforced **server-side** on every mutating route (patient create/update/delete/resolve, sending
  reminders), not just hidden in the UI. `GET /api/patients` is open to any authenticated role;
  role-specific field visibility is a frontend concern, same as the original prototype.
- **`routers/`** — one file per resource (`auth`, `patients`, `reminders`, `dashboard`). Patient
  serialization to `PatientOut` (which embeds the computed `risk` block) happens in
  `routers/patients.py::_to_patient_out`, imported by `reminders.py` too — keep both in sync if
  you change `PatientOut`.
- **`seed.py`** — runs on every startup (via the `lifespan` handler in `main.py`) but is
  idempotent (checks `count() == 0` before inserting). Patient due dates are computed relative to
  `date.today()` at seed time, not hardcoded — unlike the original prototype's frozen
  `2025-07-27` reference date, so overdue/due-soon/on-track status is always meaningful.

### Frontend (`frontend/src/`)

- **`api/client.js`** — thin fetch wrapper; stores the JWT in `localStorage`, attaches
  `Authorization: Bearer`, and clears the token on a 401.
- **`context/AuthContext.jsx`** — login/logout/current-user state, restored from `localStorage`
  on load via `GET /api/auth/me`.
- **`dashboards/{Clinician,Ops,Admin}Dashboard.jsx`** — per-role KPI/chart sets (mirrors the
  original prototype's three views), driven by `utils/chartData.js` helpers that derive Chart.js
  datasets from the fetched `patients` array. `AdminDashboard` additionally calls
  `GET /api/dashboard/kpis` for the four top KPI cards.
- **`components/PatientTable.jsx`** — one shared table for all three roles; filtering (search,
  status, or admin's clinician/condition filters) is client-side against the already-fetched
  `patients` array, same pattern as the original prototype.
- **`components/DetailsModal.jsx`** — role-branches its content (clinical vs. operational vs.
  full overview), shows the risk score/reasons, and for `ops`/`admin` adds "Mark Ops Issue
  Resolved" (`PATCH /patients/{id}/resolve`) and "Send AI Reminder" (`POST
  /patients/{id}/remind`) actions.
- Chart.js elements are registered once in `chartSetup.js`, imported by `components/ChartCard.jsx`
  (a generic bar/doughnut/pie wrapper) — don't re-register elements elsewhere.

## Adding patient fields, new roles, or wiring real notification delivery

- **New patient field**: add it to `Patient` in `models.py`, the relevant Pydantic schema in
  `schemas.py`, and thread it through `routers/patients.py::_to_patient_out` and
  `seed.py`'s patient dicts; then surface it wherever the frontend renders patient fields
  (`DetailsModal.jsx`, `PatientTable.jsx`).
- **New role**: add it to `deps.require_roles(...)` calls where it should have access, and on the
  frontend: `AuthContext`/login flow, `DashboardPage.jsx`'s `TITLES` map and dispatch, a new
  `dashboards/*.jsx`, and the role branches in `DetailsModal.jsx`/`PatientTable.jsx`.
- **Real SMS/email delivery**: replace the log-only write in `routers/reminders.py::send_reminder`
  with an actual provider call (e.g. Twilio/SendGrid), keeping `crud.add_contact_log` as the audit
  trail; `ContactLog.status` would then reflect real delivery state instead of always
  `"simulated"`.
