"""Features 4 & 5 – Recording attendance, and viewing / searching / editing the history."""
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone

from .http import (ApiError, endpoint, get_or_404, int_param, paginate, parse_date, read_json)
from .models import Attendance, Course, Role, Status
from .permissions import can_manage_course, role_of
from .resources import scoped_courses
from .serializers import attendance_dict, course_dict

ADMIN, TEACHER, STUDENT = Role.ADMIN, Role.TEACHER, Role.STUDENT


def scoped_attendance(user):
    """Admin: everything. Teacher: their own courses. Student: only their own records."""
    qs = Attendance.objects.select_related("student", "course__subject", "course__school_class")
    role = role_of(user)
    if role == ADMIN:
        return qs
    if role == TEACHER:
        return qs.filter(course__teacher=user)
    student = getattr(user, "student_profile", None)
    return qs.filter(student=student) if student else qs.none()


def filter_attendance(qs, params):
    """Query-string filters shared by history, analytics and reports."""
    if params.get("student"):
        qs = qs.filter(student_id=int_param(params["student"], "student"))
    if params.get("course"):
        qs = qs.filter(course_id=int_param(params["course"], "course"))
    if params.get("class"):
        qs = qs.filter(course__school_class_id=int_param(params["class"], "class"))
    if params.get("subject"):
        qs = qs.filter(course__subject_id=int_param(params["subject"], "subject"))
    if params.get("date_from"):
        qs = qs.filter(date__gte=parse_date(params["date_from"], "date_from"))
    if params.get("date_to"):
        qs = qs.filter(date__lte=parse_date(params["date_to"], "date_to"))
    if params.get("status"):
        if params["status"] not in Status.values:
            raise ApiError("status must be present, absent or late.")
        qs = qs.filter(status=params["status"])
    search = params.get("search", "").strip()
    if search:
        from django.db.models import Q
        qs = qs.filter(Q(student__name__icontains=search) | Q(student__student_code__icontains=search))
    return qs


# ---------------------------------------------------------------------------- feature 4: record
@endpoint("GET", roles=[ADMIN, TEACHER])
def attendance_sheet(request):
    """The class list for one course on one day, with any status already saved."""
    course = get_or_404(scoped_courses(request.api_user), request.GET.get("course"), "Course")
    day = parse_date(request.GET.get("date") or timezone.localdate().isoformat())
    existing = {a.student_id: a for a in Attendance.objects.filter(course=course, date=day)}
    roster = course.school_class.students.order_by("name")
    return JsonResponse({
        "course": course_dict(course),
        "date": day.isoformat(),
        "students": [{
            "student_id": s.id, "student_code": s.student_code, "student_name": s.name,
            "status": existing[s.id].status if s.id in existing else None,
            "remark": existing[s.id].remark if s.id in existing else "",
        } for s in roster],
    })


@endpoint("POST", roles=[ADMIN, TEACHER])
def attendance_bulk(request):
    """Save a whole class at once. Existing records for that day are updated (no duplicates)."""
    body = read_json(request)
    course = get_or_404(Course.objects.select_related("school_class", "subject"), body.get("course_id"), "Course")
    if not can_manage_course(request.api_user, course):
        raise ApiError("You can only record attendance for your own courses.", 403)
    day = parse_date(body.get("date"))
    if day > timezone.localdate():
        raise ApiError("You cannot record attendance for a future date.")

    records = body.get("records")
    if not isinstance(records, list) or not records:
        raise ApiError("records must be a non-empty list.")
    roster = set(course.school_class.students.values_list("id", flat=True))
    clean = []
    for rec in records:
        if not isinstance(rec, dict):
            raise ApiError("Each record must be an object.", 422)
        sid = rec.get("student_id")
        if not isinstance(sid, int) or sid not in roster:
            raise ApiError(f"Student {sid} is not in class {course.school_class.name}.", 422)
        if rec.get("status") not in Status.values:
            raise ApiError("status must be present, absent or late.", 422)
        clean.append((rec["student_id"], rec["status"], str(rec.get("remark", ""))[:200]))

    with transaction.atomic():
        for student_id, status, remark in clean:
            Attendance.objects.update_or_create(
                student_id=student_id, course=course, date=day,
                defaults={"status": status, "remark": remark, "recorded_by": request.api_user})
    return JsonResponse({"saved": len(clean), "date": day.isoformat(), "course": str(course)})


# ---------------------------------------------------------------------------- feature 5: history
@endpoint("GET")
def attendance_list(request):
    qs = filter_attendance(scoped_attendance(request.api_user), request.GET)
    total, page = paginate(request, qs)
    return JsonResponse({"total": total, "items": [attendance_dict(a) for a in page]})


@endpoint("PUT", "PATCH", "DELETE", roles=[ADMIN, TEACHER])
def attendance_detail(request, pk):
    record = get_or_404(scoped_attendance(request.api_user), pk, "Attendance record")
    if not can_manage_course(request.api_user, record.course):
        raise ApiError("You can only change attendance for your own courses.", 403)
    if request.method == "DELETE":
        record.delete()
        return JsonResponse({"detail": "Attendance record deleted."})

    body = read_json(request)
    if "status" in body:
        if body["status"] not in Status.values:
            raise ApiError("status must be present, absent or late.", 422)
        record.status = body["status"]
    if "remark" in body:
        record.remark = str(body["remark"] or "")[:200]
    record.recorded_by = request.api_user
    record.save()
    return JsonResponse(attendance_dict(record))
