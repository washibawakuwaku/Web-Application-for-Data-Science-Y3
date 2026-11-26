"""
Pure analytics functions (features 6, 8, 9) – no Django imports, so they are easy to test.

Every function takes `rows`: a list of dicts with the keys
    student, student_code, student_name, class_name, course, subject, date, status
where `date` is a datetime.date and `status` is "present" | "absent" | "late".

Attendance rate = (present + late) / total * 100   (late counts as attended)
                  or present / total * 100 when late_counts=False.
"""
import calendar
from datetime import timedelta

PRESENT, ABSENT, LATE = "present", "absent", "late"
STATUSES = (PRESENT, ABSENT, LATE)


def _blank():
    return {"total": 0, "present": 0, "absent": 0, "late": 0}


def _add(bucket, status):
    if status in STATUSES:
        bucket["total"] += 1
        bucket[status] += 1


def attendance_rate(bucket, late_counts=True):
    if not bucket["total"]:
        return None
    attended = bucket["present"] + (bucket["late"] if late_counts else 0)
    return round(100 * attended / bucket["total"], 1)


def _group(rows, keyfn):
    groups = {}
    for r in rows:
        _add(groups.setdefault(keyfn(r), _blank()), r["status"])
    return groups


def _with_rate(labels, bucket, late_counts):
    out = dict(labels)
    out.update(bucket)
    out["rate"] = attendance_rate(bucket, late_counts)
    return out


def _course_label(r):
    return f"{r['subject']} ({r['class_name']})"


# --------------------------------------------------------------------------- dashboard
def summarize(rows, late_counts=True):
    overall = _blank()
    for r in rows:
        _add(overall, r["status"])

    by_class = [_with_rate({"class_name": k}, b, late_counts)
                for k, b in sorted(_group(rows, lambda r: r["class_name"]).items())]
    by_course = [_with_rate({"course": k}, b, late_counts)
                 for k, b in sorted(_group(rows, _course_label).items())]
    daily = [_with_rate({"date": k.isoformat()}, b, late_counts)
             for k, b in sorted(_group(rows, lambda r: r["date"]).items())]
    students = len({r["student"] for r in rows})

    return {
        "overall": _with_rate({"students": students}, overall, late_counts),
        "by_class": by_class,
        "by_course": by_course,
        "daily": daily,
    }


# --------------------------------------------------------------------------- feature 8
def student_table(rows, late_counts=True):
    """One row per student with totals and rate (used by alerts and reports)."""
    labels, groups = {}, {}
    for r in rows:
        labels.setdefault(r["student"], {
            "student": r["student"], "student_code": r["student_code"],
            "student_name": r["student_name"],
        })
        _add(groups.setdefault(r["student"], _blank()), r["status"])
    out = [_with_rate(labels[k], b, late_counts) for k, b in groups.items()]
    out.sort(key=lambda x: (x["student_name"], x["student_code"]))
    return out


def low_attendance(rows, threshold=75, late_counts=True):
    """Students whose rate is below `threshold`. severity: critical if rate < 80% of threshold."""
    items = []
    for s in student_table(rows, late_counts):
        if s["rate"] is not None and s["rate"] < threshold:
            s["severity"] = "critical" if s["rate"] < threshold * 0.8 else "warning"
            s["threshold"] = threshold
            items.append(s)
    items.sort(key=lambda x: (x["rate"], x["student_name"]))
    return items


# --------------------------------------------------------------------------- feature 9
def _bucket_date(d, period):
    if period == "month":
        return d.replace(day=1)
    return d - timedelta(days=d.weekday())          # Monday of that week


def trends(rows, period="week", top=10, drop_points=10, late_counts=True):
    """Patterns over time: rate per week/month, weekday pattern, frequent absentees, declining students."""
    period = "month" if period == "month" else "week"

    # 1) rate per period, with change vs. the previous period
    groups = _group(rows, lambda r: _bucket_date(r["date"], period))
    series, prev = [], None
    for key in sorted(groups):
        item = _with_rate({"period": key.isoformat()}, groups[key], late_counts)
        item["change"] = (round(item["rate"] - prev, 1)
                          if prev is not None and item["rate"] is not None else None)
        prev = item["rate"]
        series.append(item)

    # 2) which weekdays have the most absences
    weekday = []
    for k, b in sorted(_group(rows, lambda r: r["date"].weekday()).items()):
        item = _with_rate({"weekday": calendar.day_name[k]}, b, late_counts)
        item["absent_rate"] = round(100 * b["absent"] / b["total"], 1) if b["total"] else None
        weekday.append(item)

    # 3) frequently absent students
    frequent = []
    for s in student_table(rows, late_counts):
        if s["absent"] > 0:
            s["absent_rate"] = round(100 * s["absent"] / s["total"], 1)
            frequent.append(s)
    frequent.sort(key=lambda x: (-x["absent"], -x["absent_rate"], x["student_name"]))
    frequent = frequent[:top]

    # 4) students whose rate dropped between the last two periods
    declining = []
    if len(series) >= 2:
        last_key, prev_key = sorted(groups)[-1], sorted(groups)[-2]
        by_student = {}
        for r in rows:
            key = _bucket_date(r["date"], period)
            if key in (last_key, prev_key):
                slot = by_student.setdefault(r["student"], {"info": r, last_key: _blank(), prev_key: _blank()})
                _add(slot[key], r["status"])
        for slot in by_student.values():
            now, before = (attendance_rate(slot[last_key], late_counts),
                           attendance_rate(slot[prev_key], late_counts))
            if now is None or before is None:
                continue
            if now - before <= -drop_points:
                info = slot["info"]
                declining.append({
                    "student": info["student"], "student_code": info["student_code"],
                    "student_name": info["student_name"],
                    "previous_rate": before, "current_rate": now, "change": round(now - before, 1),
                })
        declining.sort(key=lambda x: x["change"])

    return {
        "period": period,
        "series": series,
        "weekday": weekday,
        "frequent_absentees": frequent,
        "declining": declining,
        "insights": _insights(series, weekday, frequent, declining, period),
    }


def _insights(series, weekday, frequent, declining, period):
    notes = []
    rated = [s for s in series if s["rate"] is not None]
    if len(rated) >= 2:
        diff = rated[-1]["rate"] - rated[-2]["rate"]
        if abs(diff) >= 0.1:
            word = "up" if diff > 0 else "down"
            notes.append(f"Attendance is {word} {abs(round(diff, 1))} points compared with the previous {period}.")
        else:
            notes.append(f"Attendance is unchanged compared with the previous {period}.")
    worst = [w for w in weekday if w["absent_rate"] is not None]
    if worst:
        w = max(worst, key=lambda x: x["absent_rate"])
        if w["absent_rate"] > 0:
            notes.append(f"{w['weekday']} has the highest absence rate ({w['absent_rate']}%).")
    if frequent:
        f = frequent[0]
        notes.append(f"{f['student_name']} is absent most often ({f['absent']} absences).")
    if declining:
        notes.append(f"{len(declining)} student(s) dropped sharply compared with the previous {period}.")
    return notes
