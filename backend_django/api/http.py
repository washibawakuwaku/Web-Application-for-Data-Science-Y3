"""Tiny helpers shared by all views: JSON body, errors, auth decorator, pagination."""
import json
from datetime import date, timedelta
from functools import wraps

from django.conf import settings
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import AuthToken
from .permissions import role_of


class ApiError(Exception):
    def __init__(self, detail, status=400):
        super().__init__(detail)
        self.detail = detail
        self.status = status


def authenticate_request(request):
    """Return the user for `Authorization: Token <key>` or None."""
    header = request.META.get("HTTP_AUTHORIZATION", "")
    parts = header.split()
    if len(parts) != 2 or parts[0].lower() != "token":
        return None
    token = AuthToken.objects.select_related("user").filter(key=parts[1], user__is_active=True).first()
    if token is None:
        return None
    if timezone.now() - token.created_at > timedelta(hours=settings.TOKEN_TTL_HOURS):
        token.delete()
        return None
    request.api_token = token
    return token.user


def endpoint(*methods, roles=None, auth=True):
    """
    @endpoint("GET", "POST", roles={"GET": [...], "POST": [...]})
    `roles` may also be a plain list that applies to every method.
    The logged-in user is available as `request.api_user`.
    """
    def decorator(view):
        @csrf_exempt
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            try:
                if request.method not in methods:
                    raise ApiError("Method not allowed.", 405)
                if auth:
                    user = authenticate_request(request)
                    if user is None:
                        raise ApiError("Authentication required. Please log in.", 401)
                    request.api_user = user
                    allowed = roles.get(request.method) if isinstance(roles, dict) else roles
                    if allowed and role_of(user) not in allowed:
                        raise ApiError("You do not have permission to do this.", 403)
                return view(request, *args, **kwargs)
            except ApiError as e:
                return JsonResponse({"detail": e.detail}, status=e.status)
            except ProtectedError:
                return JsonResponse({"detail": "This record is still used by other records "
                                               "(e.g. a class with courses, or a course with attendance). "
                                               "Remove those first."}, status=409)
            except IntegrityError:
                return JsonResponse({"detail": "Duplicate or conflicting record."}, status=409)
        return wrapper
    return decorator


def read_json(request):
    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        raise ApiError("Request body must be valid JSON.")
    if not isinstance(body, dict):
        raise ApiError("Request body must be a JSON object.")
    return body


def get_or_404(queryset, pk, label="Record"):
    try:
        pk = int(pk)
    except (TypeError, ValueError):
        raise ApiError(f"{label}: a valid id is required.")
    obj = queryset.filter(pk=pk).first()
    if obj is None:
        raise ApiError(f"{label} not found.", 404)
    return obj


def int_param(value, name):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ApiError(f"'{name}' must be a number.")


def parse_date(value, name="date"):
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        raise ApiError(f"'{name}' must be a date like 2026-11-18.")


def paginate(request, queryset, default_limit=100, max_limit=1000):
    limit = min(max(int_param(request.GET.get("limit", default_limit), "limit"), 1), max_limit)
    offset = max(int_param(request.GET.get("offset", 0), "offset"), 0)
    return queryset.count(), queryset[offset:offset + limit]


def require_text(body, field, label=None):
    value = str(body.get(field, "")).strip()
    if not value:
        raise ApiError(f"{label or field} is required.")
    return value
