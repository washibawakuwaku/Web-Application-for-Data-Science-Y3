"""
Step 3 of the analysis pipeline: attendance analytics for the notebooks and report.

This module does NOT re-implement the maths. It imports the exact same pure
functions the live web app uses – `backend_django/api/stats.py` – so a number in a
notebook always matches the same number on the dashboard.

Typical use in a notebook:

    import pandas as pd
    from analysis import metrics
    df = pd.read_csv("data/processed/attendance_clean.csv", parse_dates=["date"])
    summary = metrics.summarize(df)              # overall + by class + by course + daily
    alerts  = metrics.low_attendance(df, 75)     # students below 75%
    trend   = metrics.trends(df, "week")
"""
import sys
from datetime import date

import pandas as pd

from analysis import config

# Re-use the backend's pure analytics module (it has no Django imports).
sys.path.insert(0, str(config.BACKEND_DIR))
from api import stats          # noqa: E402  (import after sys.path tweak)

LATE = config.LATE_COUNTS_AS_ATTENDED


def rows_from_df(df: pd.DataFrame) -> list[dict]:
    """Turn the processed DataFrame into the list-of-dicts that `stats` expects."""
    def as_date(v):
        return v.date() if isinstance(v, pd.Timestamp) else (v if isinstance(v, date)
                                                              else pd.to_datetime(v).date())
    rows = []
    for r in df.to_dict("records"):
        rows.append({
            "student": r["student_code"],                 # a stable key per student
            "student_code": r["student_code"],
            "student_name": r["student_name"],
            "class_name": r["class_name"],
            "course": f'{r["subject_code"]}|{r["class_name"]}',
            "subject": r["subject_name"],
            "date": as_date(r["date"]),
            "status": str(r["status"]).lower(),
            "remark": r.get("remark", ""),
        })
    return rows


# ---- thin wrappers so a notebook works straight from a DataFrame -------------
def summarize(df: pd.DataFrame) -> dict:
    return stats.summarize(rows_from_df(df), late_counts=LATE)


def low_attendance(df: pd.DataFrame, threshold=config.LOW_ATTENDANCE_THRESHOLD) -> list[dict]:
    return stats.low_attendance(rows_from_df(df), threshold=threshold, late_counts=LATE)


def student_table(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(stats.student_table(rows_from_df(df), late_counts=LATE))


def trends(df: pd.DataFrame, period="week") -> dict:
    return stats.trends(rows_from_df(df), period=period, late_counts=LATE)


def overall_rate(df: pd.DataFrame) -> float | None:
    """One headline number: the attendance rate for the whole DataFrame."""
    return summarize(df)["overall"]["rate"]
