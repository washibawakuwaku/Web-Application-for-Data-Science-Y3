"""Tests for the offline analysis pipeline (no database needed).

Run from the project root:  pytest
"""
from datetime import date

import pandas as pd

from analysis import make_dataset, metrics


def _raw():
    """A tiny raw frame with the problems make_dataset is meant to fix."""
    return pd.DataFrame([
        # student, subject, class, date, status, name
        ("S1", "PY", "M1-A", "2026-11-02", "present", "Alice"),
        ("S1", "PY", "M1-A", "2026-11-02", "late",    "Alice"),   # duplicate -> keep last (late)
        ("S2", "PY", "M1-A", "2026-11-02", "absent",  "Bob"),
        ("S2", "PY", "M1-A", "not-a-date", "present", "Bob"),      # bad date -> dropped
        ("S3", "PY", "M1-A", "2026-11-02", "sleeping", "Cara"),    # bad status -> dropped
    ], columns=["student_code", "subject_code", "class_name", "date", "status", "student_name"])


def _frame(rows):
    df = pd.DataFrame(rows)
    df["subject_name"] = df["subject_code"]
    df["teacher_name"] = ""
    df["remark"] = ""
    return df


class TestClean:
    def setup_method(self):
        self.clean = make_dataset.clean(_frame(_raw()))

    def test_bad_rows_removed(self):
        # 5 raw rows -> 1 dup + 1 bad date + 1 bad status removed -> 2 clean rows
        assert len(self.clean) == 2
        assert set(self.clean["status"]) == {"late", "absent"}

    def test_duplicate_keeps_last(self):
        alice = self.clean[self.clean["student_code"] == "S1"]
        assert len(alice) == 1
        assert alice.iloc[0]["status"] == "late"

    def test_enrichment_columns(self):
        for col in ("weekday", "week_start", "month", "is_present", "is_late",
                    "is_absent", "attended"):
            assert col in self.clean.columns
        row = self.clean[self.clean["student_code"] == "S1"].iloc[0]
        assert row["weekday"] == "Monday"          # 2026-11-02 is a Monday
        assert row["attended"] == 1                 # late counts as attended


class TestMetrics:
    def test_summary_rate_matches_formula(self):
        # 2 present, 1 late, 1 absent -> (2+1)/4 = 75%
        rows = [("S1", "PY", "M1-A", "2026-11-02", "present", "Al"),
                ("S2", "PY", "M1-A", "2026-11-02", "present", "Bo"),
                ("S3", "PY", "M1-A", "2026-11-02", "late",    "Ca"),
                ("S4", "PY", "M1-A", "2026-11-02", "absent",  "Di")]
        df = make_dataset.clean(_frame(
            pd.DataFrame(rows, columns=["student_code", "subject_code", "class_name",
                                        "date", "status", "student_name"])))
        summary = metrics.summarize(df)
        assert summary["overall"]["total"] == 4
        assert summary["overall"]["rate"] == 75.0
        assert summary["overall"]["students"] == 4

    def test_low_attendance_flags_below_threshold(self):
        rows = [("S1", "PY", "M1-A", d, "absent", "Al") for d in
                ("2026-11-02", "2026-11-03", "2026-11-04")]
        rows += [("S2", "PY", "M1-A", "2026-11-02", "present", "Bo")]
        df = make_dataset.clean(_frame(
            pd.DataFrame(rows, columns=["student_code", "subject_code", "class_name",
                                        "date", "status", "student_name"])))
        low = metrics.low_attendance(df, threshold=75)
        assert [i["student_code"] for i in low] == ["S1"]      # only the 0% student
        assert low[0]["severity"] == "critical"
