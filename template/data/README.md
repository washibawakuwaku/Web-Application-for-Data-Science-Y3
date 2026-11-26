# Data

```
data/
├── raw/         # Original data – NEVER edit these files by hand
└── processed/   # Clean data created by: python -m ml.data.make_dataset
```

> **Rule:** raw data is read-only. Every cleaning step is written in code
> (`ml/data/make_dataset.py`) so anyone can rebuild `processed/` from `raw/`.

## Sample dataset: `raw/telco_churn_cambodia.csv`

A **synthetic** telecom-customer dataset (3,035 rows) made for teaching.
It behaves like real data: it has missing values, duplicates, typos and outliers
that you must clean. **Replace it with your team's real dataset.**

| Column | Type | Description |
|---|---|---|
| `customer_id` | ID | Unique customer code (not used by the model) |
| `gender` | category | Male / Female |
| `age` | number | Age in years – has missing values and impossible values (0, 150, 999) |
| `province` | category | Province – inconsistent spelling (`PP`, `phnom penh`, `Siemreap` …) |
| `contract_type` | category | Month-to-month / One year / Two year |
| `payment_method` | category | ABA Pay / Wing / Cash / Credit card – inconsistent spelling |
| `internet_service` | category | 4G / 5G / Fiber / None – has missing values |
| `tenure_months` | number | Months as a customer |
| `monthly_charges_usd` | number | Monthly bill (USD) – has a few extreme outliers |
| `total_charges_usd` | text→number | Total paid (USD) – blank `" "` for some rows |
| `data_usage_gb` | number | Average monthly data usage (GB) |
| `support_calls` | number | Calls to customer support in the last 6 months |
| `late_payments` | number | Late payments in the last 12 months |
| `has_mobile_app` | category | Uses the operator's mobile app (Yes/No) |
| `signup_date` | date | Date the customer joined |
| **`churn`** | **target** | **Customer left (Yes/No)** – inconsistent labels (`Y`, `no` …) |

## Your dataset – fill this in

| Item | Your answer |
|---|---|
| Source (URL / organisation) | |
| Licence / permission to use | |
| Date collected | |
| Number of rows × columns | |
| Target column | |
| Known problems | |
