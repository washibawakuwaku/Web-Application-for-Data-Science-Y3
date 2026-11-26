"""
Step 2 of the analysis pipeline:  data/raw/attendance_raw.csv  ->  data/processed/attendance_clean.csv

Every cleaning / enrichment rule is written here (never by hand in the CSV) so the
processed dataset can always be rebuilt from the raw one:

    python -m analysis.make_dataset

Cleaning rules
--------------
1. Trim whitespace in text columns.
2. Lower-case the status and keep only valid states (present / late / absent).
3. Parse `date` to a real date and drop rows with no valid date.
4. Drop exact duplicates and keep ONE record per (student, subject, class, date).

Enrichment (features used by the notebooks / report)
----------------------------------------------------
    weekday, week_start, month        – for trend analysis
    attended (1/0)                    – present or late counts as attended
    is_present / is_late / is_absent  – one-hot of the status
"""
import pandas as pd

from analysis import config

TEXT_COLUMNS = ["student_code", "student_name", "class_name",
                "subject_code", "subject_name", "teacher_name", "status", "remark"]


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 1. trim text  (cast to object first so an all-empty column that pandas read as
    #    float64 can still be filled with "")
    for col in TEXT_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype("object").fillna("").astype(str).str.strip()

    # 2. valid status only
    df["status"] = df["status"].str.lower()
    before = len(df)
    df = df[df["status"].isin(config.STATUSES)]
    dropped_status = before - len(df)

    # 3. real dates
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    before = len(df)
    df = df.dropna(subset=["date"])
    dropped_date = before - len(df)

    # 4. de-duplicate: one record per student/subject/class/day (keep the last)
    before = len(df)
    df = df.drop_duplicates(
        subset=["student_code", "subject_code", "class_name", "date"], keep="last")
    dropped_dupes = before - len(df)

    # ---- enrichment -------------------------------------------------------
    df["weekday"] = df["date"].dt.day_name()
    df["week_start"] = (df["date"] - pd.to_timedelta(df["date"].dt.day_of_week, unit="D")).dt.date
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["is_present"] = (df["status"] == "present").astype(int)
    df["is_late"] = (df["status"] == "late").astype(int)
    df["is_absent"] = (df["status"] == "absent").astype(int)
    df["attended"] = (df["is_present"] | df["is_late"]).astype(int)
    df["date"] = df["date"].dt.date

    df = df.sort_values(["date", "class_name", "student_name"]).reset_index(drop=True)

    print(f"Cleaning: dropped {dropped_status} bad-status, {dropped_date} bad-date, "
          f"{dropped_dupes} duplicate row(s).")
    return df


def build(raw_path=config.RAW_DATA_PATH, out_path=config.PROCESSED_DATA_PATH) -> pd.DataFrame:
    if not raw_path.exists():
        raise SystemExit(f"Raw data not found: {raw_path}\n"
                         f"Run  python -m analysis.export_data  first (after seed_demo).")
    raw = pd.read_csv(raw_path)
    clean_df = clean(raw)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"Clean data: {len(clean_df)} rows x {clean_df.shape[1]} cols -> {out_path}")
    return clean_df


if __name__ == "__main__":
    build()
