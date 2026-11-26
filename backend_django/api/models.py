from django.conf import settings
from django.db import models


class Role(models.TextChoices):
    ADMIN = "admin", "Admin"
    TEACHER = "teacher", "Teacher"
    STUDENT = "student", "Student"


class Status(models.TextChoices):
    PRESENT = "present", "Present"
    ABSENT = "absent", "Absent"
    LATE = "late", "Late"


class Profile(models.Model):
    """Adds a role to Django's built-in User (feature 1)."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class AuthToken(models.Model):
    """Simple login token sent as `Authorization: Token <key>`."""
    key = models.CharField(max_length=40, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="auth_tokens")
    created_at = models.DateTimeField(auto_now_add=True)


class SchoolClass(models.Model):
    """A group of students, e.g. "M1-A" (feature 3)."""
    name = models.CharField(max_length=50, unique=True)
    academic_year = models.CharField(max_length=20, blank=True)
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "classes"

    def __str__(self):
        return self.name


class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} – {self.name}"


class Course(models.Model):
    """A subject taught to one class by one teacher. Attendance is recorded per course."""
    school_class = models.ForeignKey(SchoolClass, on_delete=models.PROTECT, related_name="courses")
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="courses")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                on_delete=models.SET_NULL, related_name="taught_courses")
    schedule = models.CharField(max_length=100, blank=True, help_text="e.g. Mon & Wed 08:00-10:00")

    class Meta:
        ordering = ["school_class__name", "subject__name"]
        constraints = [models.UniqueConstraint(fields=["school_class", "subject"], name="unique_class_subject")]

    def __str__(self):
        return f"{self.subject.name} ({self.school_class.name})"


class Student(models.Model):
    """Feature 2. A student belongs to one class = enrolled in all of that class's courses."""
    student_code = models.CharField("Student ID", max_length=30, unique=True)
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    school_class = models.ForeignKey(SchoolClass, null=True, blank=True,
                                     on_delete=models.SET_NULL, related_name="students")
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True,
                                on_delete=models.SET_NULL, related_name="student_profile")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.student_code} {self.name}"


class Attendance(models.Model):
    """One row = one student, one course, one day (feature 4)."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance_records")
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="attendance_records")
    date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices)
    remark = models.CharField(max_length=200, blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "student__name"]
        constraints = [models.UniqueConstraint(fields=["student", "course", "date"], name="one_record_per_day")]
        indexes = [models.Index(fields=["date"]), models.Index(fields=["course", "date"])]

    def __str__(self):
        return f"{self.date} {self.student.student_code} {self.status}"
