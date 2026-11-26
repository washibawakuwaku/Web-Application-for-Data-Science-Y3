# Data Science Web App – Project Template

A complete data-science project: **raw data ➜ cleaning ➜ EDA ➜ modelling ➜ evaluation ➜ API ➜ web app.**

```
┌──────────────┐   HTTP / JSON   ┌──────────────────────┐            ┌────────────────────┐
│  Streamlit   │ ──────────────▶ │  FastAPI  or  Django │ ─────────▶ │  ml/  (pipeline)   │
│  frontend/   │ ◀────────────── │  backend_*/          │ ◀───────── │  models/model.joblib│
└──────────────┘                 └──────────────────────┘            └────────────────────┘
```

It ships with a sample dataset (**customer churn for a Cambodian telecom company**, synthetic but
dirty like real data) so you can run every step before switching to your own data.

---

## The data-science workflow (CRISP-DM)

| # | Phase | Where | Output |
|---|---|---|---|
| 1 | Business understanding | Project Scope sheet, report §1 | Problem, users, success criteria |
| 2 | Data understanding | `notebooks/01_eda.ipynb` | Data quality issues, key findings |
| 3 | Data preparation | `notebooks/02_data_cleaning.ipynb` → `ml/data/make_dataset.py`, `ml/features.py` | `data/processed/clean.csv` |
| 4 | Modelling | `notebooks/03_modeling.ipynb` → `ml/train.py` | Baseline, CV comparison, tuned model |
| 5 | Evaluation | `notebooks/04_evaluation.ipynb` → `ml/evaluate.py` | Test metrics, figures, error analysis |
| 6 | Deployment | `backend_*/`, `frontend/` | Working web app |

**Rule:** explore in notebooks, then move the final code into `ml/` so it is repeatable
and the API can use it.

---

## Project structure

```
ds_project/
├── data/
│   ├── raw/                      # original data – never edit by hand
│   ├── processed/                # created by make_dataset
│   └── README.md                 # data dictionary
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_modeling.ipynb
│   └── 04_evaluation.ipynb
├── ml/                           # reusable pipeline code
│   ├── config.py                 # ⭐ paths, target, task type, metric
│   ├── data/make_dataset.py      # cleaning (raw ➜ processed)
│   ├── features.py               # feature engineering + preprocessing
│   ├── train.py                  # compare models (CV) ➜ tune ➜ evaluate ➜ save
│   ├── evaluate.py               # metrics + figures
│   └── service.py                # functions the API calls
├── models/                       # model.joblib, metrics.json, model_card.md
├── reports/
│   ├── figures/                  # charts for the report / slides
│   └── final_report_template.md  # ⭐ your final report
├── tests/test_pipeline.py        # pytest
├── backend_fastapi/              # Option A
├── backend_django/               # Option B
├── frontend/                     # Streamlit app
└── requirements.txt              # data-science libraries
```

---

## 1. Setup

```bash
python -m venv .venv
# Windows:      .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate

pip install -r requirements.txt                    # data science + notebooks
pip install -r backend_fastapi/requirements.txt    # OR backend_django/requirements.txt
pip install -r frontend/requirements.txt
```

## 2. Run the ML pipeline (from the project root)

```bash
python -m ml.data.make_dataset    # clean raw data ➜ data/processed/clean.csv
python -m ml.train                # compare 4 models, tune the best, evaluate, save
pytest                            # run the tests
jupyter lab                       # open the notebooks
```

Example output of `python -m ml.train` on the sample data:

```
1) Comparing models (5-fold CV on training set):
  Logistic Regression    f1 = 0.6740 ± 0.0149
  Decision Tree          f1 = 0.4986 ± 0.0124
  Random Forest          f1 = 0.6402 ± 0.0239
  Gradient Boosting      f1 = 0.6049 ± 0.0177
2) Tuning best model: Logistic Regression
3) Evaluating on the TEST set:  accuracy 0.73 · recall 0.77 · f1 0.69 · roc_auc 0.82
```

## 3. Run the app (two terminals)

**Terminal 1 – backend** (from the project root):

```bash
# Option A – FastAPI
uvicorn backend_fastapi.main:app --reload --port 8000      # docs: http://localhost:8000/docs

# Option B – Django
python backend_django/manage.py migrate
python backend_django/manage.py runserver 8000             # admin: http://localhost:8000/admin
```

**Terminal 2 – frontend**:

```bash
cd frontend
streamlit run app.py                                       # http://localhost:8501
```

### API endpoints (same for both backends)

| Method | URL | Purpose |
|---|---|---|
| GET  | `/api/health` | Backend is running |
| GET  | `/api/schema` | Model input fields (builds the form) |
| GET  | `/api/data?limit=100` | Clean data rows |
| GET  | `/api/metrics` | Best model, CV comparison, test metrics, confusion matrix |
| POST | `/api/train` | Re-run the whole training pipeline |
| POST | `/api/predict` | `{"features": {...}}` ➜ prediction + probabilities |
| GET  | `/api/predictions` | Last 50 predictions |

---

## 4. Use YOUR dataset

1. Put your CSV in `data/raw/` and fill in the table in `data/README.md`.
2. Edit **`ml/config.py`**: `RAW_DATA_PATH`, `TASK_TYPE`, `TARGET_COLUMN`,
   `POSITIVE_CLASS` / `NEGATIVE_CLASS`, `DROP_COLUMNS`, `PRIMARY_METRIC`.
3. Work through notebook **01** (EDA) and **02** (cleaning). Move your cleaning rules into
   `ml/data/make_dataset.py`.
4. Write features for your problem in `ml/features.py → add_features()`.
5. Run notebook **03** / `python -m ml.train`, then notebook **04**.
6. Update the tests in `tests/` and run `pytest`.
7. Edit `frontend/config.py` (title, team) and add pages / endpoints for the other features
   in your **Project Scope** sheet.
8. Write the report from `reports/final_report_template.md`.

Search the code for **`TODO`** – these are the places you are expected to change.

| Your project | `TASK_TYPE` | Example target | Good metric |
|---|---|---|---|
| Churn, loan default, fraud | `classification` | `churn` Yes/No | `f1`, `recall`, `roc_auc` |
| Crop yield, energy use, price | `regression` | `yield_tons` | `neg_root_mean_squared_error` |
| Recommendation / management system | – | keep the structure, replace the model and prediction page | |

> The pipeline supports **binary** classification and regression. For 3+ classes, change
> `prepare_xy()` in `ml/train.py` and the scoring metrics.

---

## 5. Good practice checklist

- [ ] Raw data is never edited by hand; every cleaning step is in code
- [ ] Test set is used **once**, at the end (notebook 04)
- [ ] Model is compared with a **baseline**
- [ ] Metric chosen for the business problem, not just accuracy
- [ ] Results explained in plain language
- [ ] `pytest` passes
- [ ] Each member commits their own work to Git

## 6. Suggested team roles

| Role | Works in |
|---|---|
| Data analyst | `notebooks/01`, `02`, `data/README.md` |
| ML engineer | `notebooks/03`, `04`, `ml/` |
| Backend developer | `backend_fastapi/` or `backend_django/`, `tests/` |
| Frontend developer | `frontend/` |
| Team leader | Scope sheet, report, integration, presentation |

## 7. Deploy (optional)

- Backend ➜ Render / Railway: `uvicorn backend_fastapi.main:app --host 0.0.0.0 --port $PORT`
- Frontend ➜ Streamlit Community Cloud, set secret `API_URL` to your backend URL.
