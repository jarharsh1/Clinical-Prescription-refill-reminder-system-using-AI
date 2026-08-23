# Clinical Prescription Refill Reminder System

A KPI-driven prescription refill reminder dashboard with role-based views for Clinicians,
Operations staff, and Admins. The backend computes a rule-based adherence-risk score per patient
and can generate a personalized reminder message via the Claude API (falling back to a template
when no API key is configured); reminders are logged as "simulated sends," not delivered to a
real SMS/email provider.

## Architecture

- **`backend/`** — FastAPI + SQLAlchemy + SQLite. JWT auth with three roles (`clinician`, `ops`,
  `admin`) enforced server-side on every mutating endpoint. See `backend/app/`:
  - `models.py` / `schemas.py` — `User`, `Patient`, `RefillEvent` (refill history used for risk
    scoring), `ContactLog` (a record of every generated reminder).
  - `risk.py` — deterministic, explainable adherence-risk scoring (0–100, Low/Medium/High) from
    due-date proximity, missed refills, and lateness history.
  - `ai.py` — Claude API reminder-message generation with a template fallback; never blocks the
    reminder pipeline if the API key is missing or the call fails.
  - `routers/` — `auth`, `patients` (CRUD + resolve), `reminders` (generate + log), `dashboard`
    (admin KPI aggregates).
  - `seed.py` — seeds three demo users and the patient roster with dates computed relative to
    today (not hardcoded), run automatically on server startup.
- **`frontend/`** — React (Vite) + Tailwind v4 + Chart.js. Talks to the API under `/api` (proxied
  to the backend in dev). Role-specific dashboards mirror the original prototype's UX
  (`src/dashboards/`), with a shared patient table/filter component and a details modal that adds
  a "Send AI Reminder" action for ops/admin.

## Running locally

**Backend** (from `backend/`):

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optionally set ANTHROPIC_API_KEY for Claude-generated messages
uvicorn app.main:app --reload --port 8000
```

The SQLite DB and demo data are created automatically on first startup.

**Frontend** (from `frontend/`, in a second terminal):

```bash
npm install
npm run dev
```

Visit `http://localhost:5173`. The Vite dev server proxies `/api` requests to
`http://127.0.0.1:8000`.

**Demo accounts** (seeded automatically):

| Role       | Username    | Password       |
|------------|-------------|----------------|
| Clinician  | `clinician` | `clinician123` |
| Operations | `ops`       | `ops123`       |
| Admin      | `admin`     | `admin123`     |

## Tests

```bash
cd backend && source .venv/bin/activate && pytest
```

Covers the risk-scoring rules and API auth/RBAC behavior (login, role-gated endpoints, reminder
generation with the template fallback).

## Notes / known limitations

- Reminders are **simulated** (logged to `ContactLog`, status `simulated`) — no real SMS/email
  provider is wired up. Swapping in Twilio/SendGrid would mean replacing the log-write in
  `routers/reminders.py` with an actual send call, behind the same interface.
- `ANTHROPIC_API_KEY` is optional; without it, reminder messages use a deterministic template
  (`app/ai.py`) instead of Claude-generated text.
- No production deployment config (Docker, migrations) is included — `Base.metadata.create_all`
  is used for schema setup, sufficient for SQLite in a single-instance dev/demo deployment.
