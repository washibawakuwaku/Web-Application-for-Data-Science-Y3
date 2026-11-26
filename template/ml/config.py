"""
Project configuration – ONE place to change settings.

👉 TODO (every team): change these values to match YOUR dataset.
The notebooks, the training script and both backends all read from this file.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = ROOT_DIR / "data" / "raw" / "telco_churn_cambodia.csv"
PROCESSED_DATA_PATH = ROOT_DIR / "data" / "processed" / "clean.csv"
MODEL_PATH = ROOT_DIR / "models" / "model.joblib"
METRICS_PATH = ROOT_DIR / "models" / "metrics.json"
MODEL_CARD_PATH = ROOT_DIR / "models" / "model_card.md"
FIGURES_DIR = ROOT_DIR / "reports" / "figures"

# ---------------------------------------------------------------------------
# Problem definition
# ---------------------------------------------------------------------------
# "classification" (binary: Yes/No, churn/not churn, default/no default)
# "regression"     (a number: price, yield, energy usage)
TASK_TYPE = "classification"

TARGET_COLUMN = "churn"
POSITIVE_CLASS = "Yes"     # classification only: the class you care about
NEGATIVE_CLASS = "No"

# Columns that must NOT be used as model inputs (IDs, dates, leakage)
DROP_COLUMNS = ["customer_id", "signup_date"]

# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------
TEST_SIZE = 0.2
CV_FOLDS = 5
RANDOM_STATE = 42

# Metric used to choose the best model
#   classification: "f1", "roc_auc", "recall", "precision", "accuracy"
#   regression:     "neg_root_mean_squared_error", "neg_mean_absolute_error", "r2"
PRIMARY_METRIC = "f1" if TASK_TYPE == "classification" else "neg_root_mean_squared_error"

# Number of random combinations tried when tuning the best model
TUNING_ITERATIONS = 15
