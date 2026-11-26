"""
Automated tests.  Run from the project root:

    pytest

👉 TODO: add tests for your own cleaning rules, features and API endpoints.
"""
import pandas as pd
import pytest

from ml import config, service, train
from ml.data.make_dataset import clean, load_raw
from ml.features import add_features


@pytest.fixture(scope="session")
def raw():
    return load_raw()


@pytest.fixture(scope="session")
def cleaned(raw):
    return clean(raw, verbose=False)


@pytest.fixture(scope="session")
def trained_model():
    if not config.MODEL_PATH.exists():
        train.run(verbose=False)
    return config.MODEL_PATH


# --- Data cleaning -----------------------------------------------------------
def test_no_duplicates(cleaned):
    assert cleaned.duplicated().sum() == 0


def test_target_has_only_valid_labels(cleaned):
    if config.TASK_TYPE == "classification":
        assert set(cleaned[config.TARGET_COLUMN].unique()) <= {config.POSITIVE_CLASS, config.NEGATIVE_CLASS}


def test_no_impossible_ages(cleaned):
    assert cleaned["age"].dropna().between(16, 100).all()


def test_numbers_are_numeric(cleaned):
    assert pd.api.types.is_numeric_dtype(cleaned["total_charges_usd"])


def test_clean_does_not_change_raw(raw):
    before = raw.copy()
    clean(raw, verbose=False)
    pd.testing.assert_frame_equal(raw, before)


# --- Features ----------------------------------------------------------------
def test_add_features_creates_columns(cleaned):
    out = add_features(cleaned)
    assert {"avg_spend_per_month", "is_new_customer", "calls_per_year"} <= set(out.columns)
    assert len(out) == len(cleaned)


# --- Prediction service ------------------------------------------------------
def _example_input():
    return {f["name"]: f["default"] for f in service.get_schema()["features"]}


def test_prediction_returns_valid_label(trained_model):
    result = service.make_prediction(_example_input())
    if config.TASK_TYPE == "classification":
        assert result["prediction"] in {config.POSITIVE_CLASS, config.NEGATIVE_CLASS}
        assert sum(result["probabilities"].values()) == pytest.approx(1, abs=1e-3)


def test_missing_feature_raises_error(trained_model):
    data = _example_input()
    data.pop(next(iter(data)))
    with pytest.raises(ValueError):
        service.make_prediction(data)


def test_model_beats_minimum_quality(trained_model):
    """Fails if a change makes the model much worse. Adjust the threshold for your project."""
    metrics = service.get_metrics()["test_metrics"]
    if config.TASK_TYPE == "classification":
        assert metrics["roc_auc"] > 0.7
