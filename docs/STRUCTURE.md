# Project structure — how it follows the template

The course template (`ds_project`) is for a **prediction** project:
`raw data ➜ clean ➜ EDA ➜ model ➜ evaluate ➜ API ➜ web app`.

Our topic — a **Student Attendance Management System** — is a *management +
descriptive-analytics* project, not a prediction one. The template explicitly allows
this: *"Recommendation / management system — keep the structure, replace the model and
prediction page."* So we keep the template's shape and swap the machine-learning layer
for an **attendance-analytics** layer.

## Template → this project

| Template (`ds_project`) | This project (`hong`) | What changed |
|---|---|---|
| `data/raw`, `data/processed` | same | data comes from our own DB, not a downloaded CSV |
| `notebooks/01_eda.ipynb` | `notebooks/01_attendance_eda.ipynb` | EDA on attendance instead of churn |
| `ml/` (train a model) | **`analysis/`** (compute attendance analytics) | no model — the "output" is rates, trends, alerts |
| `ml/config.py` | `analysis/config.py` | paths + settings |
| `ml/data/make_dataset.py` | `analysis/make_dataset.py` | cleaning rules in code |
| `ml/train.py`, `ml/evaluate.py` | `analysis/metrics.py` | re-uses the live API's `stats.py` |
| `models/model.joblib` | *(none)* | nothing to serialise — analytics are computed live |
| `reports/final_report_template.md` | `reports/final_report.md` | filled in for attendance |
| `backend_fastapi/` **or** `backend_django/` | `backend_django/` | we chose Django |
| `frontend/` (Streamlit) | `frontend/` (Streamlit) | main interface, redesigned |

## The CRISP-DM workflow, mapped to our files

| # | Phase | Where it lives | Output |
|---|---|---|---|
| 1 | Business understanding | `docs/project_scope.md`, report §1 | problem, users, success criteria |
| 2 | Data understanding | `notebooks/01_attendance_eda.ipynb` | data-quality check, key findings |
| 3 | Data preparation | `analysis/export_data.py` → `analysis/make_dataset.py` | `data/processed/attendance_clean.csv` |
| 4 | "Modelling" = analytics | `backend_django/api/stats.py` (shared) | rates, trends, low-attendance |
| 5 | Evaluation | report §5, spot-checks | numbers match a hand count |
| 6 | Deployment | `backend_django/`, `frontend/` | the running web app |

## One source of truth for the maths

The attendance formulas live in **one** file — `backend_django/api/stats.py` — and are
used in two places:

```
backend_django/api/stats.py   (pure Python, no Django imports, unit-tested)
        ├── analytics_views.py / report_views.py   →  the live dashboard & reports
        └── analysis/metrics.py (imports it)        →  the notebooks & the report
```

Because the notebook and the app call the *same* functions, a number in the report can
never drift from the number on screen.

## The data pipeline, end to end

```
teachers record attendance in the app
        │
        ▼  python -m analysis.export_data
data/raw/attendance_raw.csv          (read-only snapshot)
        │
        ▼  python -m analysis.make_dataset
data/processed/attendance_clean.csv  (clean + enriched: weekday, week_start, attended…)
        │
        ▼  notebooks/01_attendance_eda.ipynb  (uses analysis/metrics.py)
charts + findings  →  reports/figures/ + reports/final_report.md
```

## Suggested team roles

| Role | Works in |
|---|---|
| Data analyst | `notebooks/`, `data/README.md`, report §2–3 |
| Backend developer | `backend_django/`, `backend_django/api/tests/` |
| Frontend developer | `frontend/` |
| Team leader | `docs/project_scope.md`, `reports/final_report.md`, integration |
