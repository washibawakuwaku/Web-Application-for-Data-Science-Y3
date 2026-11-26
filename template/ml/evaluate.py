"""
Step 4 – Evaluation: metrics and figures for the final model on the TEST set.
"""
import matplotlib

matplotlib.use("Agg")  # save figures without opening a window
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    RocCurveDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
    root_mean_squared_error,
)

from ml import config


def test_metrics(pipe, X_test, y_test) -> dict:
    y_pred = pipe.predict(X_test)
    if config.TASK_TYPE == "classification":
        proba = pipe.predict_proba(X_test)[:, 1]
        return {
            "accuracy": round(accuracy_score(y_test, y_pred), 4),
            "precision": round(precision_score(y_test, y_pred), 4),
            "recall": round(recall_score(y_test, y_pred), 4),
            "f1": round(f1_score(y_test, y_pred), 4),
            "roc_auc": round(roc_auc_score(y_test, proba), 4),
        }
    return {
        "mae": round(mean_absolute_error(y_test, y_pred), 4),
        "rmse": round(root_mean_squared_error(y_test, y_pred), 4),
        "r2": round(r2_score(y_test, y_pred), 4),
    }


def confusion(pipe, X_test, y_test) -> dict | None:
    if config.TASK_TYPE != "classification":
        return None
    cm = confusion_matrix(y_test, pipe.predict(X_test), labels=[0, 1])
    labels = [config.NEGATIVE_CLASS, config.POSITIVE_CLASS]
    return {"labels": labels, "matrix": cm.tolist()}


def report_text(pipe, X_test, y_test) -> str:
    if config.TASK_TYPE != "classification":
        return ""
    return classification_report(
        y_test, pipe.predict(X_test),
        target_names=[config.NEGATIVE_CLASS, config.POSITIVE_CLASS],
    )


def feature_importance(pipe, top: int = 20) -> dict:
    """Importance for tree models, |coefficient| for linear models."""
    model = pipe.named_steps["model"]
    names = pipe.named_steps["preprocess"].named_steps["columns"].get_feature_names_out()
    names = [n.split("__", 1)[-1] for n in names]
    if hasattr(model, "feature_importances_"):
        values = model.feature_importances_
    elif hasattr(model, "coef_"):
        values = np.abs(np.ravel(model.coef_))
    else:
        return {}
    s = pd.Series(values, index=names).sort_values(ascending=False).head(top)
    return {k: round(float(v), 4) for k, v in s.items()}


def save_figures(pipe, X_test, y_test, cv_table: pd.DataFrame, importance: dict) -> list[str]:
    """Save charts to reports/figures/ for your report and slides."""
    out = config.FIGURES_DIR
    out.mkdir(parents=True, exist_ok=True)
    saved = []

    # 1. Model comparison
    fig, ax = plt.subplots(figsize=(7, 4))
    col = f"cv_{config.PRIMARY_METRIC}_mean"
    cv_table.sort_values(col).plot.barh(x="model", y=col, xerr=f"cv_{config.PRIMARY_METRIC}_std",
                                        ax=ax, legend=False, color="#4472C4")
    ax.set_title(f"Model comparison ({config.CV_FOLDS}-fold CV, {config.PRIMARY_METRIC})")
    ax.set_xlabel(config.PRIMARY_METRIC)
    fig.tight_layout(); fig.savefig(out / "model_comparison.png", dpi=150); plt.close(fig)
    saved.append("model_comparison.png")

    # 2. Feature importance
    if importance:
        fig, ax = plt.subplots(figsize=(7, 5))
        pd.Series(importance).sort_values().plot.barh(ax=ax, color="#4472C4")
        ax.set_title("Feature importance (final model)")
        fig.tight_layout(); fig.savefig(out / "feature_importance.png", dpi=150); plt.close(fig)
        saved.append("feature_importance.png")

    if config.TASK_TYPE == "classification":
        # 3. Confusion matrix
        fig, ax = plt.subplots(figsize=(5, 4))
        ConfusionMatrixDisplay.from_estimator(
            pipe, X_test, y_test, display_labels=[config.NEGATIVE_CLASS, config.POSITIVE_CLASS],
            cmap="Blues", ax=ax)
        ax.set_title("Confusion matrix (test set)")
        fig.tight_layout(); fig.savefig(out / "confusion_matrix.png", dpi=150); plt.close(fig)
        saved.append("confusion_matrix.png")

        # 4. ROC curve
        fig, ax = plt.subplots(figsize=(5, 4))
        RocCurveDisplay.from_estimator(pipe, X_test, y_test, ax=ax)
        ax.plot([0, 1], [0, 1], "--", color="grey")
        ax.set_title("ROC curve (test set)")
        fig.tight_layout(); fig.savefig(out / "roc_curve.png", dpi=150); plt.close(fig)
        saved.append("roc_curve.png")
    else:
        # 3. Predicted vs actual
        fig, ax = plt.subplots(figsize=(5, 5))
        y_pred = pipe.predict(X_test)
        ax.scatter(y_test, y_pred, alpha=0.4)
        lims = [min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())]
        ax.plot(lims, lims, "--", color="grey")
        ax.set_xlabel("Actual"); ax.set_ylabel("Predicted"); ax.set_title("Predicted vs actual (test set)")
        fig.tight_layout(); fig.savefig(out / "predicted_vs_actual.png", dpi=150); plt.close(fig)
        saved.append("predicted_vs_actual.png")

    return saved
