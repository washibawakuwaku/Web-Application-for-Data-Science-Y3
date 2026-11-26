# Project Scope – Student Attendance Management System

| | |
|---|---|
| **Class** | M1 |
| **Project topic** | Student Attendance Management System |
| **Target users** | Teachers, lecturers, school administrators, and students |
| **Team leader** | Thypheap Sachak Ponleu Pragna |
| **Team members** | Leang Serminh, Ty Kimhong |

## Problem statement
Managing student attendance manually using paper records or spreadsheets is time-consuming and prone to human
errors. It can lead to inaccurate attendance records, missing data, difficulties tracking student attendance, and
limited insights into attendance patterns. A web-based Student Attendance Management System is needed to automate
attendance management, store attendance records efficiently, and provide data analytics to help teachers and
administrators monitor student attendance and identify students with low attendance rates.

## Out of scope (will NOT build)
Facial recognition, camera-based attendance detection, GPS tracking, biometric authentication, advanced AI-based
prediction, and mobile application development.

## Features (9 total – 6 must have, 3 should have)

| # | Feature | Priority | User can… | Where it lives | Status |
|---|---|---|---|---|---|
| 1 | User Authentication & Role Management | Must | Register, log in, log out, and access the system based on role (Admin, Teacher, Student) | `api/auth_views.py`, `views/login.py`, `views/users.py` | Implemented |
| 2 | Student Management | Must | Add, view, update, delete, and manage student information (ID, name, email, class) | `api/resources.py`, `views/students.py` | Implemented |
| 3 | Class Management | Must | Create, view, update, delete and manage classes, courses, subjects, and student enrollment | `api/resources.py`, `views/classes.py` | Implemented |
| 4 | Attendance Recording | Must | Record attendance per class session with status Present, Absent or Late | `api/attendance_views.py`, `views/record_attendance.py` | Implemented |
| 5 | Attendance History Management | Must | View, search, filter and update attendance records by student, class, subject and date | `api/attendance_views.py`, `views/history.py` | Implemented |
| 6 | Attendance Analytics Dashboard | Must | View statistics, percentages, present/absent counts and trends through charts | `api/stats.py`, `views/dashboard.py` | Implemented |
| 7 | Attendance Reports & Export | Should | Generate reports by student, class, subject and date range; export CSV or PDF | `api/reporting.py`, `views/reports.py` | Implemented |
| 8 | Low Attendance Alerts | Should | Identify students whose attendance rate is below a threshold and show warnings | `api/stats.py`, `views/alerts.py` | Implemented |
| 9 | Attendance Trend Analysis | Should | Analyse historical data: patterns, frequently absent students, changes over time | `api/stats.py`, `views/trends.py` | Implemented |

*Owner (team member) and Teacher-feedback columns from the scope sheet are left for the team to fill in.*
