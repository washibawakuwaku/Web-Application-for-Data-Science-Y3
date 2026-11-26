from django.contrib import admin

from .models import Attendance, Course, Profile, SchoolClass, Student, Subject

for model in (Profile, SchoolClass, Subject, Course, Student, Attendance):
    admin.site.register(model)
