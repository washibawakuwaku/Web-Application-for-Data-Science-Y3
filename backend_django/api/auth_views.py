"""Feature 1 – User authentication & role management."""
import secrets

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.http import JsonResponse

from .http import (ApiError, endpoint, get_or_404, read_json, require_text)
from .models import AuthToken, Profile, Role, Student
from .permissions import role_of
from .serializers import user_dict

User = get_user_model()
MIN_PASSWORD = 6


def _issue_token(user):
    token = AuthToken.objects.create(key=secrets.token_hex(20), user=user)
    return JsonResponse({"token": token.key, "user": user_dict(user)})


def _create_user(body, role):
    """Shared by self-registration and admin user creation."""
    username = require_text(body, "username")
    password = str(body.get("password", ""))
    name = require_text(body, "name")
    if len(password) < MIN_PASSWORD:
        raise ApiError(f"Password must be at least {MIN_PASSWORD} characters.")
    if User.objects.filter(username__iexact=username).exists():
        raise ApiError("That username is already taken.", 409)
    email = str(body.get("email", "")).strip()
    if email and "@" not in email:
        raise ApiError("Email is not valid.")

    student = None
    if role == Role.STUDENT:
        code = require_text(body, "student_code", "Student ID")
        student = Student.objects.filter(student_code=code).first()
        if student is None:
            raise ApiError("No student with that Student ID. Ask an admin to add you first.", 404)
        if student.user_id is not None:
            raise ApiError("That Student ID already has an account.", 409)

    with transaction.atomic():
        user = User.objects.create_user(username=username, password=password, email=email, first_name=name)
        Profile.objects.create(user=user, role=role)
        if student:
            student.user = user
            student.save(update_fields=["user"])
    return user


@endpoint("POST", auth=False)
def register(request):
    body = read_json(request)
    role = body.get("role", Role.STUDENT)
    if role == Role.TEACHER and not settings.ALLOW_TEACHER_SELF_REGISTER:
        raise ApiError("Teacher accounts are created by an admin.", 403)
    if role not in (Role.STUDENT, Role.TEACHER):
        raise ApiError("You can register as a student or a teacher.")
    return _issue_token(_create_user(body, role))


@endpoint("POST", auth=False)
def login(request):
    body = read_json(request)
    user = authenticate(username=str(body.get("username", "")).strip(), password=str(body.get("password", "")))
    if user is None or not user.is_active or role_of(user) is None:
        raise ApiError("Wrong username or password.", 401)
    return _issue_token(user)


@endpoint("POST")
def logout(request):
    request.api_token.delete()
    return JsonResponse({"detail": "Logged out."})


@endpoint("GET")
def me(request):
    return JsonResponse(user_dict(request.api_user))


# ----------------------------------------------------------------- admin: user & role management
@endpoint("GET", "POST", roles=[Role.ADMIN])
def users(request):
    if request.method == "GET":
        qs = User.objects.select_related("profile", "student_profile").order_by("username")
        role = request.GET.get("role")
        if role:
            qs = qs.filter(profile__role=role)
        return JsonResponse({"items": [user_dict(u) for u in qs]})

    body = read_json(request)
    role = body.get("role")
    if role not in Role.values:
        raise ApiError("role must be admin, teacher or student.")
    return JsonResponse(user_dict(_create_user(body, role)), status=201)


@endpoint("PATCH", "PUT", "DELETE", roles=[Role.ADMIN])
def user_detail(request, pk):
    user = get_or_404(User.objects.select_related("profile"), pk, "User")
    if user.id == request.api_user.id:
        raise ApiError("You cannot change or delete your own account here.", 400)

    if request.method == "DELETE":
        user.delete()
        return JsonResponse({"detail": "User deleted."})

    body = read_json(request)
    if "role" in body:
        if body["role"] not in Role.values:
            raise ApiError("role must be admin, teacher or student.")
        Profile.objects.update_or_create(user=user, defaults={"role": body["role"]})
    if "is_active" in body:
        user.is_active = bool(body["is_active"])
    if "name" in body:
        user.first_name = require_text(body, "name")
    if body.get("password"):
        if len(str(body["password"])) < MIN_PASSWORD:
            raise ApiError(f"Password must be at least {MIN_PASSWORD} characters.")
        user.set_password(str(body["password"]))
        AuthToken.objects.filter(user=user).delete()
    user.save()
    user.refresh_from_db()
    return JsonResponse(user_dict(user))
