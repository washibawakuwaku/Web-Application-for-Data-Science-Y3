"""
Service layer: the functions the backend API calls.

Both backends (FastAPI and Django) use exactly these functions, so the API
behaves the same whichever backend your team chooses. Every function returns
plain Python types, ready to be sent as JSON.
"""
import json

import joblib
import pandas as pd

from ml import config, train

_cache = {"bundle": None}


def _bundle():
    if _cache["bundle"] is None and config.MODEL_PATH.exists():
        _cache["bundle"] = joblib.load(config.MODEL_PATH)
    return _cache["bundle"]


def _native(v):
    return v.item() if hasattr(v, "item") else v


def _clean_data() -> pd.DataFrame:
    return train.load_dataset()


def get_schema() -> dict:
    """Describe the model inputs so the frontend can build the form."""
    df = _clean_data()
    bundle = _bundle()
    cols = bundle["input_columns"] if bundle else train.prepare_xy(df)[2]
    fields = []
    for col in cols:
        s = df[col].dropna()
        if pd.api.types.is_numeric_dtype(s):
            is_int = bool((s % 1 == 0).all())
            fields.append({
                "name": col,
                "type": "integer" if is_int else "number",
                "default": int(s.median()) if is_int else round(float(s.median()), 2),
                "min": _native(s.min()),
                "max": _native(s.max()),
            })
        else:
            fields.append({
                "name": col,
                "type": "category",
                "options": sorted(map(str, s.unique())),
                "default": str(s.mode().iloc[0]),
            })
    return {
        "task_type": config.TASK_TYPE,
        "target": config.TARGET_COLUMN,
        "features": fields,
        "model_trained": bundle is not None,
    }


def get_data(limit: int = 100) -> dict:
    df = _clean_data()
    rows = json.loads(df.head(limit).to_json(orient="records", date_format="iso"))
    return {"total_rows": len(df), "columns": list(df.columns), "rows": rows}


def get_metrics() -> dict | None:
    if not config.METRICS_PATH.exists():
        return None
    return json.loads(config.METRICS_PATH.read_text(encoding="utf-8"))


def train_model() -> dict:
    train.run(verbose=False)
    _cache["bundle"] = None  # reload the new model next time
    return get_metrics()


def make_prediction(features: dict) -> dict:
    bundle = _bundle()
    if bundle is None:
        raise RuntimeError("Model is not trained yet. Call POST /api/train first.")
    cols = bundle["input_columns"]
    missing = [c for c in cols if c not in features]
    if missing:
        raise ValueError(f"Missing features: {missing}")

    X = pd.DataFrame([{c: features[c] for c in cols}])
    pipe = bundle["pipeline"]
    if config.TASK_TYPE == "classification":
        p = float(pipe.predict_proba(X)[0, 1])
        label = config.POSITIVE_CLASS if p >= 0.5 else config.NEGATIVE_CLASS
        # TODO: change the 0.5 threshold if missing a positive case is costly
        return {
            "prediction": label,
            "probabilities": {config.NEGATIVE_CLASS: round(1 - p, 4),
                              config.POSITIVE_CLASS: round(p, 4)},
        }
    return {"prediction": round(float(pipe.predict(X)[0]), 4)}
