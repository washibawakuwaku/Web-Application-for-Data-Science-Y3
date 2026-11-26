"""
Create demo accounts, classes, students and ~8 weeks of realistic attendance.

    python backend_django/manage.py seed_demo            # add demo data
    python backend_django/manage.py seed_demo --reset    # wipe attendance data first
"""
import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from api.models import Attendance, Course, Profile, Role, SchoolClass, Student, Subject

User = get_user_model()

FIRST = ["Sokha", "Dara", "Vanna", "Sreyneath", "Rithy", "Chanthou", "Vireak", "Sophea", "Kosal", "Maly",
         "Pich", "Theary", "Bunthoeun", "Sreymom", "Visal", "Channary", "Piseth", "Sovanna", "Ratana", "Kunthea",
         "Makara", "Leakena", "Sambath", "Chenda"]
LAST = ["Chan", "Sok", "Lim", "Kim", "Heng", "Ouk", "Meas", "Ly", "Chea", "Sao", "Prak", "Noun"]
# (class, subject code, teacher username, weekdays 0=Mon, schedule text)
COURSES = [
    ("M1-A", "PY", "teacher1", (0, 2), "Mon & Wed 08:00-10:00"),
    ("M1-A", "DB", "teacher1", (1, 3), "Tue & Thu 08:00-10:00"),
    ("M1-A", "MATH", "teacher2", (4,), "Fri 08:00-11:00"),
    ("M1-B", "PY", "teacher1", (1, 3), "Tue & Thu 13:00-15:00"),
    ("M1-B", "WEB", "teacher2", (0, 2), "Mon & Wed 13:00-15:00"),
    ("M1-B", "MATH", "teacher2", (4,), "Fri 13:00-16:00"),
]
DEMO_USERS = ["admin", "teacher1", "teacher2", "student1", "student2"]


class Command(BaseCommand):
    help = "Create demo data for the Student Attendance Management System."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="delete existing demo data first")
        parser.add_argument("--weeks", type=int, default=8, help="weeks of attendance history (default 8)")

    @transaction.atomic
    def handle(self, *args, **opts):
        rng = random.Random(2026)
        if opts["reset"]:
            Attendance.objects.all().delete()
            Course.objects.all().delete()
            Student.objects.all().delete()
            SchoolClass.objects.all().delete()
            Subject.objects.all().delete()
            User.objects.filter(username__in=DEMO_USERS).delete()

        def make_user(username, password, name, role, **extra):
            user, created = User.objects.get_or_create(username=username, defaults={"first_name": name, **extra})
            if created:
                user.set_password(password)
                user.save()
            Profile.objects.update_or_create(user=user, defaults={"role": role})
            return user

        make_user("admin", "admin12345", "System Admin", Role.ADMIN, is_staff=True, is_superuser=True)
        teachers = {
            "teacher1": make_user("teacher1", "teacher12345", "Chan Vireak", Role.TEACHER),
            "teacher2": make_user("teacher2", "teacher12345", "Srey Neath", Role.TEACHER),
        }

        classes = {n: SchoolClass.objects.get_or_create(name=n, defaults={"academic_year": "2026-2027"})[0]
                   for n in ("M1-A", "M1-B")}
        subjects = {code: Subject.objects.get_or_create(code=code, defaults={"name": name})[0] for code, name in
                    [("PY", "Python Programming"), ("DB", "Database Systems"),
                     ("WEB", "Web Development"), ("MATH", "Mathematics")]}

        courses = []
        for cls, code, teacher, days, schedule in COURSES:
            course, _ = Course.objects.get_or_create(
                school_class=classes[cls], subject=subjects[code],
                defaults={"teacher": teachers[teacher], "schedule": schedule})
            courses.append((course, days))

        # 12 students per class
        students, n = [], 0
        for cls in classes.values():
            for _ in range(12):
                n += 1
                name = f"{FIRST[(n - 1) % len(FIRST)]} {LAST[(n * 5) % len(LAST)]}"
                student, _ = Student.objects.get_or_create(
                    student_code=f"S2026{n:03d}",
                    defaults={"name": name, "school_class": cls,
                              "email": f"{name.lower().replace(' ', '.')}@school.edu"})
                students.append(student)
        for username, student in (("student1", students[0]), ("student2", students[12])):
            if student.user_id is None:
                student.user = make_user(username, "student12345", student.name, Role.STUDENT)
                student.save(update_fields=["user"])

        # each student gets a behaviour: most attend well, a few struggle, a few get worse over time
        profile = {}
        for i, s in enumerate(students):
            roll = rng.random()
            if i in (1, 13):
                profile[s.id] = ("declining", 0.95, 0.45)
            elif roll < 0.12:
                profile[s.id] = ("poor", 0.55, 0.55)
            elif roll < 0.35:
                profile[s.id] = ("average", 0.82, 0.82)
            else:
                profile[s.id] = ("good", 0.95, 0.95)

        today = timezone.localdate()
        start = today - timedelta(days=7 * opts["weeks"])
        span = max((today - start).days, 1)
        records = []
        for course, days in courses:
            roster = [s for s in students if s.school_class_id == course.school_class_id]
            day = start
            while day <= today:
                if day.weekday() in days:
                    progress = (day - start).days / span
                    for s in roster:
                        _, p0, p1 = profile[s.id]
                        p_attend = p0 + (p1 - p0) * progress
                        if rng.random() < p_attend:
                            status = "late" if rng.random() < 0.08 else "present"
                        else:
                            status = "absent"
                        records.append(Attendance(student=s, course=course, date=day, status=status,
                                                  recorded_by=course.teacher))
                day += timedelta(days=1)
        Attendance.objects.bulk_create(records, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(f"Demo data ready: {len(students)} students, {len(courses)} courses, "
                                             f"{len(records)} attendance records."))
        self.stdout.write("Logins:  admin / admin12345   teacher1 / teacher12345   "
                          "student1 / student12345")
