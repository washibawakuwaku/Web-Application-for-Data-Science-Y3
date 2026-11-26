"""Features 2 & 3 – Student management, class / subject / course management, enrollment."""
from django.db.models import Count, Q
from django.http import JsonResponse

from .http import (ApiError, endpoint, get_or_404, int_param, paginate, read_json, require_text)
from .models import Course, Role, SchoolClass, Student, Subject
from .permissions import role_of
from .serializers import class_dict, course_dict, student_dict, subject_dict

ADMIN, TEACHER, STUDENT = Role.ADMIN, Role.TEACHER, Role.STUDENT


# ---------------------------------------------------------------------------- students
def _student_fields(body, partial=False):
    out = {}
    if not partial or "student_code" in body:
        out["student_code"] = require_text(body, "student_code", "Student ID")
    if not partial or "name" in body:
        out["name"] = require_text(body, "name")
    if "email" in body:
        email = str(body["email"] or "").strip()
        if email and "@" not in email:
            raise ApiError("Email is not valid.")
        out["email"] = email
    if "class_id" in body:
        cid = body["class_id"]
        out["school_class"] = get_or_404(SchoolClass.objects, cid, "Class") if cid not in (None, "") else None
    return out


@endpoint("GET", "POST", roles={"GET": [ADMIN, TEACHER], "POST": [ADMIN]})
def students(request):
    if request.method == "POST":
        fields = _student_fields(read_json(request))
        if Student.objects.filter(student_code=fields["student_code"]).exists():
            raise ApiError("A student with that Student ID already exists.", 409)
        student = Student.objects.create(**fields)
        return JsonResponse(student_dict(student), status=201)

    qs = Student.objects.select_related("school_class")
    search = request.GET.get("search", "").strip()
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(student_code__icontains=search) | Q(email__icontains=search))
    if request.GET.get("class"):
        qs = qs.filter(school_class_id=int_param(request.GET["class"], "class"))
    total, page = paginate(request, qs)
    return JsonResponse({"total": total, "items": [student_dict(s) for s in page]})


@endpoint("GET", roles=[STUDENT])
def student_me(request):
    student = getattr(request.api_user, "student_profile", None)
    if student is None:
        raise ApiError("Your account is not linked to a student record.", 404)
    return JsonResponse(student_dict(student))


@endpoint("GET", "PUT", "PATCH", "DELETE", roles={"GET": [ADMIN, TEACHER], "PUT": [ADMIN],
                                                  "PATCH": [ADMIN], "DELETE": [ADMIN]})
def student_detail(request, pk):
    student = get_or_404(Student.objects.select_related("school_class"), pk, "Student")
    if request.method == "GET":
        return JsonResponse(student_dict(student))
    if request.method == "DELETE":
        student.delete()
        return JsonResponse({"detail": "Student deleted (their attendance records were deleted too)."})

    fields = _student_fields(read_json(request), partial=True)
    code = fields.get("student_code")
    if code and Student.objects.filter(student_code=code).exclude(pk=student.pk).exists():
        raise ApiError("A student with that Student ID already exists.", 409)
    for key, value in fields.items():
        setattr(student, key, value)
    student.save()
    return JsonResponse(student_dict(student))


# ---------------------------------------------------------------------------- classes
@endpoint("GET", "POST", roles={"POST": [ADMIN]})
def classes(request):
    if request.method == "POST":
        body = read_json(request)
        name = require_text(body, "name")
        if SchoolClass.objects.filter(name__iexact=name).exists():
            raise ApiError("A class with that name already exists.", 409)
        obj = SchoolClass.objects.create(name=name, academic_year=str(body.get("academic_year", "")).strip(),
                                         description=str(body.get("description", "")).strip())
        return JsonResponse(class_dict(obj), status=201)

    qs = SchoolClass.objects.annotate(student_count=Count("students", distinct=True),
                                      course_count=Count("courses", distinct=True))
    return JsonResponse({"items": [class_dict(c) for c in qs]})


@endpoint("GET", "PUT", "PATCH", "DELETE", roles={"PUT": [ADMIN], "PATCH": [ADMIN], "DELETE": [ADMIN]})
def class_detail(request, pk):
    obj = get_or_404(SchoolClass.objects, pk, "Class")
    if request.method == "GET":
        obj = SchoolClass.objects.annotate(student_count=Count("students", distinct=True),
                                           course_count=Count("courses", distinct=True)).get(pk=obj.pk)
        data = class_dict(obj)
        data["students"] = [student_dict(s) for s in obj.students.select_related("school_class")]
        return JsonResponse(data)
    if request.method == "DELETE":
        obj.delete()                      # blocked (409) while the class still has courses
        return JsonResponse({"detail": "Class deleted. Its students are now unassigned."})

    body = read_json(request)
    if "name" in body:
        name = require_text(body, "name")
        if SchoolClass.objects.filter(name__iexact=name).exclude(pk=obj.pk).exists():
            raise ApiError("A class with that name already exists.", 409)
        obj.name = name
    for field in ("academic_year", "description"):
        if field in body:
            setattr(obj, field, str(body[field] or "").strip())
    obj.save()
    return JsonResponse(class_dict(obj))


def _student_ids(body):
    ids = body.get("student_ids")
    if not isinstance(ids, list) or not ids:
        raise ApiError("student_ids must be a non-empty list.")
    try:
        return [int(i) for i in ids]
    except (TypeError, ValueError):
        raise ApiError("student_ids must be numbers.")


@endpoint("POST", roles=[ADMIN])
def class_enroll(request, pk):
    """Enrollment: put students into a class (so they join all of its courses)."""
    obj = get_or_404(SchoolClass.objects, pk, "Class")
    updated = Student.objects.filter(pk__in=_student_ids(read_json(request))).update(school_class=obj)
    return JsonResponse({"enrolled": updated, "class": obj.name})


@endpoint("POST", roles=[ADMIN])
def class_unenroll(request, pk):
    obj = get_or_404(SchoolClass.objects, pk, "Class")
    updated = Student.objects.filter(pk__in=_student_ids(read_json(request)), school_class=obj)\
        .update(school_class=None)
    return JsonResponse({"removed": updated, "class": obj.name})


# ---------------------------------------------------------------------------- subjects
@endpoint("GET", "POST", roles={"POST": [ADMIN]})
def subjects(request):
    if request.method == "POST":
        body = read_json(request)
        code, name = require_text(body, "code"), require_text(body, "name")
        if Subject.objects.filter(code__iexact=code).exists():
            raise ApiError("A subject with that code already exists.", 409)
        return JsonResponse(subject_dict(Subject.objects.create(code=code, name=name)), status=201)
    return JsonResponse({"items": [subject_dict(s) for s in Subject.objects.all()]})


@endpoint("PUT", "PATCH", "DELETE", roles=[ADMIN])
def subject_detail(request, pk):
    obj = get_or_404(Subject.objects, pk, "Subject")
    if request.method == "DELETE":
        obj.delete()
        return JsonResponse({"detail": "Subject deleted."})
    body = read_json(request)
    if "code" in body:
        code = require_text(body, "code")
        if Subject.objects.filter(code__iexact=code).exclude(pk=obj.pk).exists():
            raise ApiError("A subject with that code already exists.", 409)
        obj.code = code
    if "name" in body:
        obj.name = require_text(body, "name")
    obj.save()
    return JsonResponse(subject_dict(obj))


# ---------------------------------------------------------------------------- courses
def scoped_courses(user):
    """Admin: all courses. Teacher: own courses. Student: courses of their class."""
    qs = Course.objects.select_related("school_class", "subject", "teacher")
    role = role_of(user)
    if role == ADMIN:
        return qs
    if role == TEACHER:
        return qs.filter(teacher=user)
    student = getattr(user, "student_profile", None)
    return qs.filter(school_class=student.school_class_id) if student and student.school_class_id else qs.none()


def _teacher_or_none(value):
    if value in (None, ""):
        return None
    from django.contrib.auth import get_user_model
    user = get_or_404(get_user_model().objects.filter(profile__role=TEACHER), value, "Teacher")
    return user


@endpoint("GET", "POST", roles={"POST": [ADMIN]})
def courses(request):
    if request.method == "POST":
        body = read_json(request)
        school_class = get_or_404(SchoolClass.objects, body.get("class_id"), "Class")
        subject = get_or_404(Subject.objects, body.get("subject_id"), "Subject")
        if Course.objects.filter(school_class=school_class, subject=subject).exists():
            raise ApiError("That class already has this subject.", 409)
        course = Course.objects.create(school_class=school_class, subject=subject,
                                       teacher=_teacher_or_none(body.get("teacher_id")),
                                       schedule=str(body.get("schedule", "")).strip())
        return JsonResponse(course_dict(course), status=201)

    qs = scoped_courses(request.api_user)
    if request.GET.get("class"):
        qs = qs.filter(school_class_id=int_param(request.GET["class"], "class"))
    return JsonResponse({"items": [course_dict(c) for c in qs]})


@endpoint("PUT", "PATCH", "DELETE", roles=[ADMIN])
def course_detail(request, pk):
    course = get_or_404(Course.objects.select_related("school_class", "subject", "teacher"), pk, "Course")
    if request.method == "DELETE":
        course.delete()                  # blocked (409) while attendance exists for it
        return JsonResponse({"detail": "Course deleted."})
    body = read_json(request)
    if "teacher_id" in body:
        course.teacher = _teacher_or_none(body["teacher_id"])
    if "schedule" in body:
        course.schedule = str(body["schedule"] or "").strip()
    course.save()
    return JsonResponse(course_dict(course))
