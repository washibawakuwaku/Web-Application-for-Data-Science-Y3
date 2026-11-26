# [Project Title] – Final Report

**Class:** M1 · **Team:** Member 1 (leader), Member 2, Member 3, Member 4 · **Date:**

> Fill in every section. Put charts from `reports/figures/` where marked 📊.
> Keep it short and clear: 6–10 pages.

---

## 1. Business Understanding

- **Problem:** What problem are you solving? Who has this problem?
- **Users:** Who will use the app?
- **Goal:** What decision will the prediction help with?
- **Success criteria:** e.g. "Find at least 70 % of customers who will churn (recall ≥ 0.70)".

## 2. Data Understanding  *(notebook 01)*

- **Source:** where the data comes from, licence, date.
- **Size:** rows × columns. Short data dictionary (or link to `data/README.md`).
- **Data quality problems found:** missing values, duplicates, typos, outliers.
- **Key EDA findings:** 3–5 bullet points.
- 📊 Target distribution, 2–3 most important charts.

## 3. Data Preparation  *(notebook 02, `ml/data/make_dataset.py`, `ml/features.py`)*

| Problem | Rows affected | Decision | Reason |
|---|---|---|---|
| | | | |

- **New features** you created and why.
- How you avoided **data leakage** (e.g. imputation inside the pipeline, test set never used for training).

## 4. Modelling  *(notebook 03, `ml/train.py`)*

- Baseline result.
- Models compared and cross-validation results.
- 📊 `model_comparison.png`
- Best model, tuned hyper-parameters.

| Model | CV score (mean ± std) |
|---|---|
| | |

## 5. Evaluation  *(notebook 04)*

- Test-set metrics (from `models/model_card.md`).
- 📊 `confusion_matrix.png`, `roc_curve.png`, `feature_importance.png`
- Does it meet the success criteria from section 1?
- Error analysis: where does the model fail?
- Explain the result for a **non-technical** reader.

## 6. Deployment  *(backend + frontend)*

- Architecture diagram: Streamlit → FastAPI / Django → model.
- API endpoints you built.
- Screenshots of each page of the app.
- Link to the deployed app (if any).

## 7. Conclusion

- What you achieved.
- Limitations (data, model, fairness).
- Future work.

## 8. Team contribution

| Member | Role | Main contributions |
|---|---|---|
| | | |

## References

- Dataset source
- Libraries / tutorials / papers used
