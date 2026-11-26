"""
Step 2 – Feature engineering and preprocessing.

Everything here runs INSIDE the model pipeline, so the API can send the
original (clean) columns and the pipeline creates the new features itself.
"""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

from ml import config


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create new columns from existing ones.

    👉 TODO: write features that make sense for YOUR problem.
    Good features come from domain knowledge (talk to users / read about the topic).
    """
    df = df.copy()
    if {"total_charges_usd", "tenure_months"} <= set(df.columns):
        df["avg_spend_per_month"] = df["total_charges_usd"] / df["tenure_months"].replace(0, np.nan)
    if "tenure_months" in df.columns:
        df["is_new_customer"] = (df["tenure_months"] <= 6).astype(int)
    if {"support_calls", "tenure_months"} <= set(df.columns):
        df["calls_per_year"] = df["support_calls"] / (df["tenure_months"].clip(lower=1) / 12)
    return df


def get_input_columns(df: pd.DataFrame) -> list[str]:
    """Columns the user/API must provide (before feature engineering)."""
    skip = {config.TARGET_COLUMN, *config.DROP_COLUMNS}
    return [c for c in df.columns if c not in skip]


def split_types(df: pd.DataFrame):
    """Numeric and categorical columns AFTER feature engineering."""
    numeric = df.select_dtypes(include="number").columns.tolist()
    categorical = [c for c in df.columns if c not in numeric]
    return numeric, categorical


def build_preprocessor(X_sample: pd.DataFrame) -> Pipeline:
    """add_features ➜ impute ➜ scale / one-hot encode."""
    numeric, categorical = split_types(add_features(X_sample))
    columns = ColumnTransformer([
        ("num", Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]), numeric),
        ("cat", Pipeline([
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]), categorical),
    ])
    return Pipeline([
        ("add_features", FunctionTransformer(add_features)),
        ("columns", columns),
    ])
