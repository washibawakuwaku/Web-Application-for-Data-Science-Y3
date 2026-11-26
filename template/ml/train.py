"""
Step 3 – Modelling: compare models with cross-validation, tune the best one,
evaluate it on the test set, and save everything.

Run from the project root:

    python -m ml.train

Outputs:
    models/model.joblib       the trained pipeline (used by the API)
    models/metrics.json       CV results, test metrics, best parameters
    models/model_card.md      short human-readable summary of the model
    reports/figures/*.png     charts for your report
"""
import json
from datetime import datetime

import joblib
import pandas as pd
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
from sklearn.model_selection import (
    KFold,
    RandomizedSearchCV,
    StratifiedKFold,
    cross_validate,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from ml import config, evaluate
from ml.data.make_dataset import clean, load_raw
from ml.features import build_preprocessor, get_input_columns

RS = config.RANDOM_STATE


def candidate_models() -> dict:
    """Models to compare + the hyper-parameters to tune for each.

    👉 TODO: add or remove models (e.g. XGBoost, LightGBM, SVM, KNN).
    """
    if config.TASK_TYPE == "classification":
        return {
            "Logistic Regression": (LogisticRegression(max_iter=2000, class_weight="balanced"),
                                    {"model__C": [0.01, 0.1, 0.3, 1, 3, 10]}),
            "Decision Tree": (DecisionTreeClassifier(random_state=RS, class_weight="balanced"),
                              {"model__max_depth": [3, 4, 5, 6, 8, 10],
                               "model__min_samples_leaf": [1, 5, 10, 20]}),
            "Random Forest": (RandomForestClassifier(random_state=RS, n_jobs=-1, class_weight="balanced"),
                              {"model__n_estimators": [200, 300, 500],
                               "model__max_depth": [None, 6, 10, 15],
                               "model__min_samples_leaf": [1, 3, 5, 10]}),
            "Gradient Boosting": (GradientBoostingClassifier(random_state=RS),
                                  {"model__n_estimators": [100, 200, 300],
                                   "model__learning_rate": [0.03, 0.05, 0.1],
                                   "model__max_depth": [2, 3, 4]}),
        }
    return {
        "Linear Regression": (LinearRegression(), {}),
        "Ridge": (Ridge(), {"model__alpha": [0.1, 0.3, 1, 3, 10, 30]}),
        "Random Forest": (RandomForestRegressor(random_state=RS, n_jobs=-1),
                          {"model__n_estimators": [200, 300, 500],
                           "model__max_depth": [None, 6, 10, 15],
                           "model__min_samples_leaf": [1, 3, 5, 10]}),
        "Gradient Boosting": (GradientBoostingRegressor(random_state=RS),
                              {"model__n_estimators": [100, 200, 300],
                               "model__learning_rate": [0.03, 0.05, 0.1],
                               "model__max_depth": [2, 3, 4]}),
    }


def scoring() -> list[str]:
    if config.TASK_TYPE == "classification":
        return ["accuracy", "precision", "recall", "f1", "roc_auc"]
    return ["neg_mean_absolute_error", "neg_root_mean_squared_error", "r2"]


def load_dataset() -> pd.DataFrame:
    if config.PROCESSED_DATA_PATH.exists():
        return pd.read_csv(config.PROCESSED_DATA_PATH)
    print("Processed data not found – cleaning raw data first.")
    return clean(load_raw())


def prepare_xy(df: pd.DataFrame):
    input_cols = get_input_columns(df)
    X = df[input_cols]
    y = df[config.TARGET_COLUMN]
    if config.TASK_TYPE == "classification":
        y = (y == config.POSITIVE_CLASS).astype(int)   # 1 = positive class
    return X, y, input_cols


def compare_models(X_train, y_train, verbose=True) -> pd.DataFrame:
    """Cross-validate every candidate model on the TRAINING set only."""
    cv = (StratifiedKFold(config.CV_FOLDS, shuffle=True, random_state=RS)
          if config.TASK_TYPE == "classification" else KFold(config.CV_FOLDS, shuffle=True, random_state=RS))
    rows = []
    for name, (model, _) in candidate_models().items():
        pipe = Pipeline([("preprocess", build_preprocessor(X_train)), ("model", model)])
        res = cross_validate(pipe, X_train, y_train, cv=cv, scoring=scoring(), n_jobs=-1)
        row = {"model": name}
        for m in scoring():
            row[f"cv_{m}_mean"] = round(res[f"test_{m}"].mean(), 4)
            row[f"cv_{m}_std"] = round(res[f"test_{m}"].std(), 4)
        rows.append(row)
        if verbose:
            print(f"  {name:<22} {config.PRIMARY_METRIC} = "
                  f"{row[f'cv_{config.PRIMARY_METRIC}_mean']:.4f} ± {row[f'cv_{config.PRIMARY_METRIC}_std']:.4f}")
    return pd.DataFrame(rows).sort_values(f"cv_{config.PRIMARY_METRIC}_mean", ascending=False)


def tune(name, X_train, y_train):
    model, params = candidate_models()[name]
    pipe = Pipeline([("preprocess", build_preprocessor(X_train)), ("model", model)])
    if not params:
        return pipe.fit(X_train, y_train), {}, None
    n_combos = 1
    for v in params.values():
        n_combos *= len(v)
    search = RandomizedSearchCV(
        pipe, params, n_iter=min(config.TUNING_ITERATIONS, n_combos),
        scoring=config.PRIMARY_METRIC, cv=config.CV_FOLDS, random_state=RS, n_jobs=-1,
    )
    search.fit(X_train, y_train)
    best_params = {k.replace("model__", ""): v for k, v in search.best_params_.items()}
    return search.best_estimator_, best_params, round(search.best_score_, 4)


def write_model_card(report: dict):
    lines = [
        "# Model Card", "",
        f"- **Trained:** {report['trained_at']}",
        f"- **Task:** {report['task_type']} – predict `{report['target']}`",
        f"- **Model:** {report['best_model']}",
        f"- **Best parameters:** {report['best_params']}",
        f"- **Data:** {report['n_train']} training rows, {report['n_test']} test rows",
        f"- **Selection metric:** {report['primary_metric']} ({config.CV_FOLDS}-fold CV)", "",
        "## Test-set performance", "",
        "| Metric | Value |", "|---|---|",
        *[f"| {k} | {v} |" for k, v in report["test_metrics"].items()], "",
        "## Model comparison (cross-validation)", "",
        "| Model | " + config.PRIMARY_METRIC + " (mean ± std) |", "|---|---|",
        *[f"| {r['model']} | {r[f'cv_{config.PRIMARY_METRIC}_mean']} ± {r[f'cv_{config.PRIMARY_METRIC}_std']} |"
          for r in report["cv_results"]], "",
        "## Limitations", "",
        "👉 TODO: who should NOT use this model, known biases, data limitations.", "",
    ]
    config.MODEL_CARD_PATH.write_text("\n".join(lines), encoding="utf-8")


def run(verbose=True) -> dict:
    df = load_dataset()
    X, y, input_cols = prepare_xy(df)
    stratify = y if config.TASK_TYPE == "classification" else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.TEST_SIZE, random_state=RS, stratify=stratify)
    if verbose:
        print(f"Data: {len(X_train)} train / {len(X_test)} test rows, {len(input_cols)} input columns")
        print(f"\n1) Comparing models ({config.CV_FOLDS}-fold CV on training set):")

    cv_table = compare_models(X_train, y_train, verbose)
    best_name = cv_table.iloc[0]["model"]
    if verbose:
        print(f"\n2) Tuning best model: {best_name}")
    pipe, best_params, tuned_score = tune(best_name, X_train, y_train)
    if verbose:
        print(f"   best params: {best_params}  (CV {config.PRIMARY_METRIC} = {tuned_score})")

    if verbose:
        print("\n3) Evaluating on the TEST set (data the model has never seen):")
    metrics = evaluate.test_metrics(pipe, X_test, y_test)
    importance = evaluate.feature_importance(pipe)
    figures = evaluate.save_figures(pipe, X_test, y_test, cv_table, importance)
    if verbose:
        for k, v in metrics.items():
            print(f"   {k:<10} {v}")
        txt = evaluate.report_text(pipe, X_test, y_test)
        if txt:
            print("\n" + txt)

    report = {
        "trained_at": datetime.now().isoformat(timespec="seconds"),
        "task_type": config.TASK_TYPE,
        "target": config.TARGET_COLUMN,
        "primary_metric": config.PRIMARY_METRIC,
        "best_model": best_name,
        "best_params": best_params,
        "tuned_cv_score": tuned_score,
        "n_train": len(X_train),
        "n_test": len(X_test),
        "cv_results": cv_table.to_dict(orient="records"),
        "test_metrics": metrics,
        "confusion_matrix": evaluate.confusion(pipe, X_test, y_test),
        "feature_importance": importance,
        "figures": figures,
    }

    config.MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipe, "input_columns": input_cols}, config.MODEL_PATH)
    config.METRICS_PATH.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    write_model_card(report)
    if verbose:
        print("Saved ➜ models/model.joblib, models/metrics.json, models/model_card.md, reports/figures/")
    return report


if __name__ == "__main__":
    run()
