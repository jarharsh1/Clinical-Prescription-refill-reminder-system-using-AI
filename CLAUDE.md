# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A KPI-driven prescription refill reminder dashboard. Flask serves a single HTML page with an
embedded vanilla-JS single-page app (no build step, no JS framework, no bundler) that fetches
patient data from a JSON API and renders role-specific dashboards (Clinician, Operations, Admin)
with Chart.js visualizations and a filterable patient table.

## Running the app

```bash
pip install flask
python3 main.py
```

The Flask dev server runs with `debug=True` (auto-reload) on `http://127.0.0.1:5000`. There is no
`requirements.txt` in the repo yet — `flask` is the only dependency.

There is no test suite, linter, or build step configured in this repository.

## Architecture

- **`main.py`** — Flask backend. Two routes only:
  - `GET /` renders `templates/index.html`.
  - `GET /api/patients` returns the entire patient roster as JSON from `PATIENTS_DATA`, an
    in-memory Python list of dicts (no database). This is the single source of truth for patient
    data; the frontend has no hardcoded patient data of its own.
- **`templates/index.html`** — The entire frontend: HTML shell + Tailwind (via CDN) + Chart.js
  (via CDN) + one large inline `<script>` implementing the SPA. Key structure inside the
  `DOMContentLoaded` handler:
  - **State**: `patients` (fetched from `/api/patients`), `loggedInUser` (`'clinician'` | `'ops'`
    | `'admin'` | `null`), and a fixed `today` constant used for all "days until due" calculations
    — note this is hardcoded to `2025-07-27`, not `Date.now()`, so refill status/overdue
    calculations are relative to that fixed date rather than the real current date.
  - **Login is not authentication** — it's a role selector (`handleLogin` just sets
    `loggedInUser` from a `<select>`) that determines which dashboard view and chart set render.
  - **Templates as JS string functions**: `loginTemplate`, `dashboardTemplate`, `tableTemplate`,
    and per-role chart container HTML (`clinicianCharts`, `opsCharts`, `adminCharts`,
    `adminKpiCards`) are template-literal functions injected via `innerHTML`. There is no virtual
    DOM/diffing — `render()` does a full re-render of `#app-container` on every state change
    (login, logout) and `renderTable()` does a full re-render of the table body on filter/search.
  - **Role-based dashboards**: each of the three roles gets a distinct combination of KPI charts
    (`renderClinicianCharts`, `renderOpsCharts`, `renderAdminCharts`) and a distinct detail-modal
    payload (`showDetailsModal` branches on `loggedInUser` to show clinical vs. operational vs.
    full-overview fields for the same patient).
  - **Charts** are Chart.js instances stored in the `charts` object and explicitly destroyed
    (`destroyCharts`) before every re-render to avoid canvas reuse errors.
  - Filtering/search (`renderTable`) is done entirely client-side against the in-memory
    `patients` array already fetched from the API — there is no server-side filtering endpoint.

## Adding patient fields or new roles

Because patient data flows from a single backend list (`PATIENTS_DATA` in `main.py`) straight
into `/api/patients` and then directly into the frontend's `patients` array, adding a new patient
field only requires updating the dicts in `main.py` — the frontend already renders arbitrary
fields ad hoc inside `showDetailsModal`/`renderTable`. Adding a new role requires updates in
several places in `index.html` that all branch on `loggedInUser`: the login `<select>` options,
`render()`'s title/chart/table dispatch, `addEventListeners()`, the per-role chart renderer, and
`showDetailsModal()`.
