"""
Analysis configuration – ONE place to change paths and settings.

The attendance system is a *management / descriptive-analytics* project, so instead
of the template's `ml/` (train a model) layer we have this `analysis/` layer:

    export_data.py   Django DB  ->  data/raw/attendance_raw.csv     (a snapshot)
    make_dataset.py  raw        ->  data/processed/attendance_clean.csv
    metrics.py       clean CSV  ->  attendance rate, trends, low-attendance

The maths (`metrics.py`) is the SAME pure code the live API uses
(`backend_django/api/stats.py`), so the notebooks and the web app can never disagree.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent          # the project root (hong/)
BACKEND_DIR = ROOT_DIR / "backend_django"

RAW_DATA_PATH = ROOT_DIR / "data" / "raw" / "attendance_raw.csv"
PROCESSED_DATA_PATH = ROOT_DIR / "data" / "processed" / "attendance_clean.csv"
FIGURES_DIR = ROOT_DIR / "reports" / "figures"

# ---------------------------------------------------------------------------
# Analysis settings  (keep these equal to backend_django/config/settings.py)
# ---------------------------------------------------------------------------
# A student is flagged when their attendance rate falls below this percentage.
LOW_ATTENDANCE_THRESHOLD = 75
# True  -> rate = (present + late) / total       False -> rate = present / total
LATE_COUNTS_AS_ATTENDED = True

# The three attendance states, in display order.
STATUSES = ("present", "late", "absent")
