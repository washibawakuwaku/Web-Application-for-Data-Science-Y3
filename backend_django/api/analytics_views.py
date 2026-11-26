"""Features 6, 8, 9 – dashboard statistics, low-attendance alerts, trend analysis."""
from django.conf import settings
from django.http import JsonResponse

from . import stats
from .attendance_views import filter_attendance, scoped_attendance
from .http import ApiError, endpoint

VALUE_FIELDS = ("student_id", "student__student_code", "student__name", "course_id",
                "course__subject__name", "course__school_class__name", "date", "status", "remark")


def stat_rows(request):
    """Filtered attendance (limited to what this user may see) as plain dicts for `stats`."""
    qs = filter_attendance(scoped_attendance(request.api_user), request.GET)
    return [{
        "student": r["student_id"], "student_code": r["student__student_code"],
        "student_name": r["student__name"], "course": r["course_id"],
        "subject": r["course__subject__name"], "class_name": r["course__school_class__name"],
        "date": r["date"], "status": r["status"], "remark": r["remark"],
    } for r in qs.values(*VALUE_FIELDS)]


def threshold_param(request):
    raw = request.GET.get("threshold", settings.LOW_ATTENDANCE_THRESHOLD)
    try:
        value = float(raw)
    except (TypeError, ValueError):
        raise ApiError("'threshold' must be a number.")
    if not 0 < value <= 100:
        raise ApiError("'threshold' must be between 0 and 100.")
    return value


@endpoint("GET")
def summary(request):
    return JsonResponse(stats.summarize(stat_rows(request), settings.LATE_COUNTS_AS_ATTENDED))


@endpoint("GET")
def low_attendance(request):
    threshold = threshold_param(request)
    items = stats.low_attendance(stat_rows(request), threshold, settings.LATE_COUNTS_AS_ATTENDED)
    return JsonResponse({"threshold": threshold, "total": len(items), "items": items})


@endpoint("GET")
def trends(request):
    period = request.GET.get("period", "week")
    if period not in ("week", "month"):
        raise ApiError("period must be 'week' or 'month'.")
    return JsonResponse(stats.trends(stat_rows(request), period=period,
                                     late_counts=settings.LATE_COUNTS_AS_ATTENDED))
