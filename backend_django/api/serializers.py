"""Turn model objects into plain dicts for JSON responses."""
from .permissions import role_of


def user_dict(user):
    student = getattr(user, "student_profile", None)
    return {
        "id": user.id,
        "username": user.username,
        "name": user.first_name or user.username,
        "email": user.email,
        "role": role_of(user),
        "is_active": user.is_active,
        "student_id": student.id if student else None,
        "student_code": student.student_code if student else None,
    }


def student_dict(s):
    return {
        "id": s.id, "student_code": s.student_code, "name": s.name, "email": s.email,
        "class_id": s.school_class_id,
        "class_name": s.school_class.name if s.school_class_id else None,
        "has_account": s.user_id is not None,
    }


def class_dict(c):
    return {
        "id": c.id, "name": c.name, "academic_year": c.academic_year, "description": c.description,
        "student_count": getattr(c, "student_count", None), "course_count": getattr(c, "course_count", None),
    }


def subject_dict(s):
    return {"id": s.id, "code": s.code, "name": s.name}


def course_dict(c):
    return {
        "id": c.id, "label": str(c), "schedule": c.schedule,
        "class_id": c.school_class_id, "class_name": c.school_class.name,
        "subject_id": c.subject_id, "subject_name": c.subject.name, "subject_code": c.subject.code,
        "teacher_id": c.teacher_id,
        "teacher_name": (c.teacher.first_name or c.teacher.username) if c.teacher_id else None,
    }


def attendance_dict(a):
    return {
        "id": a.id, "date": a.date.isoformat(), "status": a.status, "remark": a.remark,
        "student_id": a.student_id, "student_code": a.student.student_code, "student_name": a.student.name,
        "course_id": a.course_id, "subject_name": a.course.subject.name,
        "class_name": a.course.school_class.name,
        "course_label": str(a.course),
    }
