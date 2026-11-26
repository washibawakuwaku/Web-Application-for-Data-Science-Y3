"""API tests. Run from the project root:  python backend_django/manage.py test api"""
import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from api.models import Attendance, Course, Profile, Role, SchoolClass, Student, Subject

User = get_user_model()


class ApiTestCase(TestCase):
    def setUp(self):
        self.admin = self.make_user("admin", Role.ADMIN)
        self.teacher = self.make_user("t1", Role.TEACHER)
        self.other_teacher = self.make_user("t2", Role.TEACHER)
        self.klass = SchoolClass.objects.create(name="M1")
        self.subject = Subject.objects.create(code="PY", name="Python")
        self.course = Course.objects.create(school_class=self.klass, subject=self.subject, teacher=self.teacher)
        self.s1 = Student.objects.create(student_code="S1", name="Alice", school_class=self.klass)
        self.s2 = Student.objects.create(student_code="S2", name="Bob", school_class=self.klass)
        self.today = timezone.localdate()

    def make_user(self, username, role):
        user = User.objects.create_user(username, password="secret123", first_name=username)
        Profile.objects.create(user=user, role=role)
        return user

    def login(self, username):
        r = self.client.post("/api/auth/login", json.dumps({"username": username, "password": "secret123"}),
                             content_type="application/json")
        self.assertEqual(r.status_code, 200, r.content)
        return {"HTTP_AUTHORIZATION": f"Token {r.json()['token']}"}

    def post(self, url, data, headers):
        return self.client.post(url, json.dumps(data), content_type="application/json", **headers)

    def record(self, headers, day=None, statuses=("present", "absent")):
        return self.post("/api/attendance/bulk", {
            "course_id": self.course.id, "date": (day or self.today).isoformat(),
            "records": [{"student_id": self.s1.id, "status": statuses[0]},
                        {"student_id": self.s2.id, "status": statuses[1], "remark": "sick"}],
        }, headers)


class AuthTests(ApiTestCase):
    def test_requires_login(self):
        self.assertEqual(self.client.get("/api/students").status_code, 401)

    def test_wrong_password(self):
        r = self.client.post("/api/auth/login", json.dumps({"username": "admin", "password": "x"}),
                             content_type="application/json")
        self.assertEqual(r.status_code, 401)

    def test_student_registration_links_to_record(self):
        r = self.client.post("/api/auth/register", json.dumps({
            "username": "alice", "password": "secret123", "name": "Alice", "role": "student", "student_code": "S1"}),
            content_type="application/json")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(r.json()["user"]["student_code"], "S1")
        # the same Student ID cannot be claimed twice
        r = self.client.post("/api/auth/register", json.dumps({
            "username": "alice2", "password": "secret123", "name": "A", "role": "student", "student_code": "S1"}),
            content_type="application/json")
        self.assertEqual(r.status_code, 409)

    def test_cannot_register_as_admin(self):
        r = self.client.post("/api/auth/register", json.dumps({
            "username": "evil", "password": "secret123", "name": "E", "role": "admin"}),
            content_type="application/json")
        self.assertEqual(r.status_code, 400)

    def test_logout_invalidates_token(self):
        h = self.login("admin")
        self.assertEqual(self.client.post("/api/auth/logout", **h).status_code, 200)
        self.assertEqual(self.client.get("/api/auth/me", **h).status_code, 401)


class RoleTests(ApiTestCase):
    def test_teacher_cannot_create_student_admin_can(self):
        data = {"student_code": "S9", "name": "New", "class_id": self.klass.id}
        self.assertEqual(self.post("/api/students", data, self.login("t1")).status_code, 403)
        self.assertEqual(self.post("/api/students", data, self.login("admin")).status_code, 201)
        self.assertEqual(self.post("/api/students", data, self.login("admin")).status_code, 409)  # duplicate ID

    def test_only_admin_manages_users(self):
        self.assertEqual(self.client.get("/api/users", **self.login("t1")).status_code, 403)
        self.assertEqual(self.client.get("/api/users", **self.login("admin")).status_code, 200)

    def test_cannot_delete_class_with_courses(self):
        r = self.client.delete(f"/api/classes/{self.klass.id}", **self.login("admin"))
        self.assertEqual(r.status_code, 409)


class AttendanceTests(ApiTestCase):
    def test_record_and_update_without_duplicates(self):
        h = self.login("t1")
        self.assertEqual(self.record(h).json()["saved"], 2)
        self.record(h, statuses=("late", "present"))                  # same day again -> update
        self.assertEqual(Attendance.objects.count(), 2)
        self.assertEqual(Attendance.objects.get(student=self.s1).status, "late")

    def test_other_teacher_cannot_record(self):
        self.assertEqual(self.record(self.login("t2")).status_code, 403)

    def test_future_date_rejected(self):
        r = self.record(self.login("t1"), day=self.today + timedelta(days=2))
        self.assertEqual(r.status_code, 400)

    def test_invalid_status_rejected(self):
        r = self.record(self.login("t1"), statuses=("present", "sleeping"))
        self.assertEqual(r.status_code, 422)

    def test_history_filter_search_and_edit(self):
        h = self.login("t1")
        self.record(h)
        r = self.client.get("/api/attendance?status=absent&search=bob", **h).json()
        self.assertEqual(r["total"], 1)
        rec_id = r["items"][0]["id"]
        r = self.client.patch(f"/api/attendance/{rec_id}", json.dumps({"status": "present"}),
                              content_type="application/json", **h)
        self.assertEqual(r.json()["status"], "present")

    def test_student_sees_only_own_records(self):
        self.record(self.login("t1"))
        user = self.make_user("alice", Role.STUDENT)
        self.s1.user = user
        self.s1.save()
        r = self.client.get("/api/attendance", **self.login("alice")).json()
        self.assertEqual({i["student_code"] for i in r["items"]}, {"S1"})
        self.assertEqual(self.post("/api/attendance/bulk", {}, self.login("alice")).status_code, 403)


class AnalyticsTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        h = self.login("t1")
        for back in range(4):                                         # Bob is always absent, Alice present
            self.record(h, day=self.today - timedelta(days=back))

    def test_summary(self):
        data = self.client.get("/api/analytics/summary", **self.login("admin")).json()
        self.assertEqual(data["overall"]["total"], 8)
        self.assertEqual(data["overall"]["rate"], 50.0)

    def test_low_attendance_alerts(self):
        data = self.client.get("/api/analytics/low-attendance?threshold=75", **self.login("admin")).json()
        self.assertEqual([i["student_code"] for i in data["items"]], ["S2"])
        self.assertEqual(self.client.get("/api/analytics/low-attendance?threshold=abc",
                                         **self.login("admin")).status_code, 400)

    def test_trends(self):
        data = self.client.get("/api/analytics/trends?period=week", **self.login("admin")).json()
        self.assertEqual(data["frequent_absentees"][0]["student_code"], "S2")

    def test_export_csv_and_pdf(self):
        h = self.login("admin")
        csv_resp = self.client.get("/api/reports/export?type=student_summary&format=csv", **h)
        self.assertEqual(csv_resp.status_code, 200)
        self.assertIn("attachment", csv_resp["Content-Disposition"])
        self.assertIn(b"Alice", csv_resp.content)
        pdf_resp = self.client.get("/api/reports/export?type=attendance&format=pdf", **h)
        self.assertTrue(pdf_resp.content.startswith(b"%PDF"))
        self.assertEqual(self.client.get("/api/reports/export?format=xml", **h).status_code, 400)
