from django.http import JsonResponse
from django.urls import path

from . import analytics_views, attendance_views, auth_views, report_views, resources


def health(request):
    return JsonResponse({"status": "ok", "backend": "django"})


urlpatterns = [
    path("health", health),

    # 1. authentication & roles
    path("auth/register", auth_views.register),
    path("auth/login", auth_views.login),
    path("auth/logout", auth_views.logout),
    path("auth/me", auth_views.me),
    path("users", auth_views.users),
    path("users/<int:pk>", auth_views.user_detail),

    # 2. students
    path("students", resources.students),
    path("students/me", resources.student_me),
    path("students/<int:pk>", resources.student_detail),

    # 3. classes, subjects, courses, enrollment
    path("classes", resources.classes),
    path("classes/<int:pk>", resources.class_detail),
    path("classes/<int:pk>/enroll", resources.class_enroll),
    path("classes/<int:pk>/unenroll", resources.class_unenroll),
    path("subjects", resources.subjects),
    path("subjects/<int:pk>", resources.subject_detail),
    path("courses", resources.courses),
    path("courses/<int:pk>", resources.course_detail),

    # 4 & 5. attendance
    path("attendance/sheet", attendance_views.attendance_sheet),
    path("attendance/bulk", attendance_views.attendance_bulk),
    path("attendance", attendance_views.attendance_list),
    path("attendance/<int:pk>", attendance_views.attendance_detail),

    # 6, 8, 9. analytics
    path("analytics/summary", analytics_views.summary),
    path("analytics/low-attendance", analytics_views.low_attendance),
    path("analytics/trends", analytics_views.trends),

    # 7. reports
    path("reports/export", report_views.export),
]
