"""
Step 1 – Data cleaning:  data/raw/  ➜  data/processed/clean.csv

Run from the project root:

    python -m ml.data.make_dataset

👉 TODO: every dataset is dirty in its own way. Rewrite the functions below
for YOUR data. Explore first in notebooks/02_data_cleaning.ipynb, then move
the final steps here so they are repeatable.
"""
import numpy as np
import pandas as pd

from ml import config

# Mapping messy spellings ➜ one clean value
CATEGORY_FIXES = {
    "province": {
        "phnom penh": "Phnom Penh", "pp": "Phnom Penh",
        "siem reap": "Siem Reap", "siemreap": "Siem Reap",
    },
    "payment_method": {
        "aba pay": "ABA Pay", "aba": "ABA Pay", "wing": "Wing", "cash": "Cash",
        "credit card": "Credit card",
    },
    "churn": {"yes": "Yes", "y": "Yes", "no": "No", "n": "No"},
}

# Valid ranges – values outside become missing (NaN) and are imputed later
VALID_RANGES = {
    "age": (16, 100),
    "monthly_charges_usd": (0, 200),
}


def load_raw(path=config.RAW_DATA_PATH) -> pd.DataFrame:
    return pd.read_csv(path)


def clean(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """Return a cleaned copy of the raw data."""
    log = []
    df = df.copy()

    # 1. Remove exact duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    log.append(f"Removed {before - len(df)} duplicate rows")

    # 2. Strip spaces in text columns
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].str.strip()

    # 3. Fix inconsistent category spellings
    for col, mapping in CATEGORY_FIXES.items():
        if col in df.columns:
            lower = df[col].str.lower()
            fixed = lower.map(mapping)
            n = int((fixed.notna() & (fixed != df[col])).sum())
            df[col] = fixed.fillna(df[col])
            log.append(f"Fixed {n} spellings in '{col}'")

    # 4. Convert text numbers to real numbers (" " ➜ NaN)
    for col in ["age", "total_charges_usd"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 5. Impossible values ➜ NaN
    for col, (lo, hi) in VALID_RANGES.items():
        if col in df.columns:
            bad = ~df[col].between(lo, hi) & df[col].notna()
            df.loc[bad, col] = np.nan
            log.append(f"Set {int(bad.sum())} out-of-range values in '{col}' to missing")

    # 6. Rows without a target cannot be used
    before = len(df)
    df = df.dropna(subset=[config.TARGET_COLUMN])
    log.append(f"Dropped {before - len(df)} rows with missing target")

    # 7. Correct data types
    if "signup_date" in df.columns:
        df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")

    # NOTE: remaining missing values are filled INSIDE the model pipeline
    # (SimpleImputer), so the fill values are learned from training data only.

    if verbose:
        print("\n".join("  - " + line for line in log))
        print(f"  Clean shape: {df.shape}")
    return df.reset_index(drop=True)


def main():
    raw = load_raw()
    print(f"Raw shape: {raw.shape}")
    df = clean(raw)
    config.PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.PROCESSED_DATA_PATH, index=False)
    print(f"Saved ➜ {config.PROCESSED_DATA_PATH.relative_to(config.ROOT_DIR)}")


if __name__ == "__main__":
    main()
