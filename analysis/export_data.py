"""
Step 1 of the analysis pipeline:  Django database  ->  data/raw/attendance_raw.csv

This is the project's *raw* dataset: a flat snapshot of every attendance record in
the running system, with the student / class / subject names already joined in.

Run it from the project root AFTER you have seeded the database:

    python backend_django/manage.py migrate
    python backend_django/manage.py seed_demo
    python -m analysis.export_data            # writes data/raw/attendance_raw.csv

Treat the CSV it produces as read-only – every cleaning step lives in
`analysis/make_dataset.py`, so anyone can rebuild `data/processed/` from it.
"""
import csv
import os
import sys

from analysis import config

# Columns written to the raw CSV (one row = one attendance record).
COLUMNS = ["date", "student_code", "student_name", "class_name",
           "subject_code", "subject_name", "teacher_name", "status", "remark"]


def _setup_django():
    """Make the Django models importable without running the web server."""
    sys.path.insert(0, str(config.BACKEND_DIR))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()


def export(path=config.RAW_DATA_PATH):
    _setup_django()
    from api.models import Attendance            # imported after django.setup()

    rows = (Attendance.objects
            .select_related("student", "course__subject",
                            "course__school_class", "course__teacher")
            .order_by("date", "course__school_class__name", "student__name"))

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(COLUMNS)
        count = 0
        for a in rows.iterator():
            teacher = a.course.teacher
            writer.writerow([
                a.date.isoformat(),
                a.student.student_code,
                a.student.name,
                a.course.school_class.name,
                a.course.subject.code,
                a.course.subject.name,
                (teacher.first_name or teacher.username) if teacher else "",
                a.status,
                a.remark,
            ])
            count += 1

    print(f"Exported {count} attendance records -> {path}")
    return count


if __name__ == "__main__":
    export()
