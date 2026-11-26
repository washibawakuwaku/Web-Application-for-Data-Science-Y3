"""Role helpers. Roles: admin, teacher, student (feature 1)."""
from .models import Role


def role_of(user):
    if user.is_superuser:
        return Role.ADMIN
    profile = getattr(user, "profile", None)
    return profile.role if profile else None


def can_manage_course(user, course):
    """Admins can record attendance for any course, teachers only for their own."""
    role = role_of(user)
    return role == Role.ADMIN or (role == Role.TEACHER and course.teacher_id == user.id)
