"""Feature 7 – Attendance reports, exported as CSV or PDF."""
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone

from . import reporting, stats
from .analytics_views import stat_rows, threshold_param
from .http import ApiError, endpoint

REPORT_TYPES = {
    "attendance": "Attendance records",
    "student_summary": "Attendance summary by student",
    "class_summary": "Attendance summary by class",
    "low_attendance": "Low attendance students",
}


def _build(report_type, rows, request):
    late = settings.LATE_COUNTS_AS_ATTENDED
    pct = lambda v: "" if v is None else f"{v}%"   # noqa: E731

    if report_type == "attendance":
        rows = sorted(rows, key=lambda r: (r["date"], r["class_name"], r["student_name"]))
        return (["Date", "Student ID", "Student", "Class", "Subject", "Status", "Remark"],
                [[r["date"].isoformat(), r["student_code"], r["student_name"], r["class_name"],
                  r["subject"], r["status"].capitalize(), r["remark"]] for r in rows])

    if report_type == "class_summary":
        items = stats.summarize(rows, late)["by_class"]
        return (["Class", "Total", "Present", "Late", "Absent", "Rate"],
                [[i["class_name"], i["total"], i["present"], i["late"], i["absent"], pct(i["rate"])]
                 for i in items])

    columns = ["Student ID", "Student", "Total", "Present", "Late", "Absent", "Rate"]
    if report_type == "low_attendance":
        items = stats.low_attendance(rows, threshold_param(request), late)
        return (columns + ["Level"],
                [[i["student_code"], i["student_name"], i["total"], i["present"], i["late"],
                  i["absent"], pct(i["rate"]), i["severity"].capitalize()] for i in items])

    items = stats.student_table(rows, late)
    return (columns, [[i["student_code"], i["student_name"], i["total"], i["present"], i["late"],
                       i["absent"], pct(i["rate"])] for i in items])


@endpoint("GET")
def export(request):
    report_type = request.GET.get("type", "attendance")
    fmt = request.GET.get("format", "csv")
    if report_type not in REPORT_TYPES:
        raise ApiError(f"type must be one of: {', '.join(REPORT_TYPES)}.")
    if fmt not in ("csv", "pdf"):
        raise ApiError("format must be csv or pdf.")

    columns, table = _build(report_type, stat_rows(request), request)
    today = timezone.localdate().isoformat()
    filename = f"{report_type}_{today}.{fmt}"

    if fmt == "csv":
        response = HttpResponse(reporting.build_csv(columns, table), content_type="text/csv; charset=utf-8")
    else:
        period = f"{request.GET.get('date_from') or 'start'} to {request.GET.get('date_to') or 'today'}"
        subtitle = f"Generated {today} | Period: {period} | Rows: {len(table)}"
        response = HttpResponse(reporting.build_pdf(REPORT_TYPES[report_type], subtitle, columns, table),
                                content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
