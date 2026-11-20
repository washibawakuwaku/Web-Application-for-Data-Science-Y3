<<<<<<< HEAD
# Web-Application-for-Data-Science-Y3

=======
# Student Attendance Management System

A web-based system for recording and analysing student attendance – built with **Django** (REST API + SQLite)
and **Streamlit** (web interface), following the same structure as the `ds_project` template.

```
┌──────────────┐   HTTP / JSON   ┌────────────────────┐        ┌──────────────┐
│  Streamlit   │ ──────────────▶ │  Django  (api/)    │ ─────▶ │  SQLite DB   │
│  frontend/   │ ◀────────────── │  backend_django/   │ ◀───── │  db.sqlite3  │
└──────────────┘  token in header└────────────────────┘        └──────────────┘
```

**Team (class M1):** Thypheap Sachak Ponleu Pragna (leader) · Leang Serminh · Ty Kimhong
Full scope sheet: [`docs/project_scope.md`](docs/project_scope.md)

---

## Features

| # | Feature | Priority | Backend | Frontend page |
|---|---|---|---|---|
| 1 | User Authentication & Role Management | Must | `auth_views.py` | Sign in / Users & Roles |
| 2 | Student Management | Must | `resources.py` | Students |
| 3 | Class Management (classes, subjects, courses, enrollment) | Must | `resources.py` | Classes & Courses |
| 4 | Attendance Recording (Present / Absent / Late) | Must | `attendance_views.py` | Record Attendance |
| 5 | Attendance History (view, search, filter, update) | Must | `attendance_views.py` | Attendance History |
| 6 | Analytics Dashboard | Must | `stats.py` | Dashboard |
| 7 | Reports & Export (CSV / PDF) | Should | `reporting.py` | Reports & Export |
| 8 | Low Attendance Alerts | Should | `stats.py` | Low Attendance Alerts |
| 9 | Attendance Trend Analysis | Should | `stats.py` | Trend Analysis |

### Roles

| | Admin | Teacher | Student |
|---|---|---|---|
| Users & roles | manage | – | – |
| Students | add / edit / delete | view | – |
| Classes, subjects, courses, enrollment | manage | view own courses | view own class courses |
| Record / edit attendance | any course | **own courses only** | – |
| History, dashboard, alerts, trends, reports | all data | own courses' data | **own data only** |

### How the data fits together
`Class` ─has many─ `Student`  ·  `Course` = `Class` + `Subject` + `Teacher`  ·  `Attendance` = `Student` + `Course` + `date` + status.
A student belongs to one class and is therefore enrolled in all of that class's courses. There can be only one
attendance record per student, course and day – saving again updates it.

**Attendance rate** = (present + late) ÷ all records × 100. Change `LATE_COUNTS_AS_ATTENDED` and
`LOW_ATTENDANCE_THRESHOLD` (default 75 %) in `backend_django/config/settings.py`.
An alert is *critical* when the rate is below 80 % of the threshold, otherwise *warning*.

---

## Project structure

```
student_attendance_system/
├── backend_django/
│   ├── config/                 # settings.py ⭐ (threshold, token lifetime, …), urls.py
│   └── api/
│       ├── models.py           # Profile, Class, Subject, Course, Student, Attendance
│       ├── http.py             # auth decorator, JSON + error helpers
│       ├── auth_views.py       # 1  register / login / logout / users
│       ├── resources.py        # 2, 3  students, classes, subjects, courses, enrollment
│       ├── attendance_views.py # 4, 5  record + history
│       ├── analytics_views.py  # 6, 8, 9
│       ├── report_views.py     # 7
│       ├── stats.py            # analytics maths (pure Python, unit-tested)
│       ├── reporting.py        # CSV + PDF writers (no extra libraries)
│       ├── management/commands/seed_demo.py
│       └── tests/
├── frontend/                   # Streamlit: app.py, api_client.py, components.py, views/
├── docs/project_scope.md
└── requirements.txt
```

---

## 1. Setup

```bash
python -m venv .venv
# Windows:      .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Prepare the database (from the project root)

```bash
python backend_django/manage.py makemigrations api
python backend_django/manage.py migrate
python backend_django/manage.py seed_demo       # demo users, 2 classes, 24 students, 8 weeks of attendance
```

Demo logins: `admin / admin12345` · `teacher1 / teacher12345` · `student1 / student12345`.
For real use skip `seed_demo` and run `python backend_django/manage.py createsuperuser`
(a superuser is treated as an admin).

## 3. Run the app (two terminals)

```bash
# Terminal 1 – backend (project root)
python backend_django/manage.py runserver 8000        # Django admin: http://localhost:8000/admin

# Terminal 2 – frontend
cd frontend
streamlit run app.py                                  # http://localhost:8501
```

## 4. Tests

```bash
python backend_django/manage.py test api              # API + analytics + CSV/PDF tests
```

---

## API endpoints

Send `Authorization: Token <token>` (returned by login/register). Errors are `{"detail": "..."}`.

| Method | URL | Who | Purpose |
|---|---|---|---|
| GET | `/api/health` | – | Backend is running |
| POST | `/api/auth/register` | – | `{username, password, name, email, role: student\|teacher, student_code}` |
| POST | `/api/auth/login` · `/api/auth/logout` | – / any | Log in (returns token) · log out |
| GET | `/api/auth/me` | any | Current user and role |
| GET POST | `/api/users` · PATCH DELETE `/api/users/<id>` | admin | Role management |
| GET POST | `/api/students` · GET PUT DELETE `/api/students/<id>` | admin, teacher (read) | Student CRUD, `?search=&class=` |
| GET | `/api/students/me` | student | Own student record |
| GET POST | `/api/classes` · GET PUT DELETE `/api/classes/<id>` | any (write: admin) | Class CRUD |
| POST | `/api/classes/<id>/enroll` · `/unenroll` | admin | `{student_ids: [...]}` |
| GET POST PUT DELETE | `/api/subjects`, `/api/courses` (+ `/<id>`) | any (write: admin) | Subjects and courses |
| GET | `/api/attendance/sheet?course=&date=` | admin, teacher | Class list for one session |
| POST | `/api/attendance/bulk` | admin, teacher | `{course_id, date, records:[{student_id, status, remark}]}` |
| GET | `/api/attendance` | any (scoped) | History: `student, course, class, subject, date_from, date_to, status, search, limit, offset` |
| PUT DELETE | `/api/attendance/<id>` | admin, teacher | Update status/remark, delete |
| GET | `/api/analytics/summary` | any (scoped) | Dashboard numbers (same filters) |
| GET | `/api/analytics/low-attendance?threshold=75` | any (scoped) | Students below threshold |
| GET | `/api/analytics/trends?period=week\|month` | any (scoped) | Trends, weekday pattern, frequent absentees, drops |
| GET | `/api/reports/export?type=&format=csv\|pdf` | any (scoped) | `type`: attendance, student_summary, class_summary, low_attendance |

---

## Notes and limitations

- **Teacher self-registration** is on for convenience. Set `ALLOW_TEACHER_SELF_REGISTER = False` in `settings.py`
  and create teachers from **Users & Roles** before real use. Also set a real `DJANGO_SECRET_KEY` and `DJANGO_DEBUG=0`.
- **PDF export** uses built-in Latin fonts, so Khmer characters show as `?` in PDFs. CSV keeps all characters
  (UTF-8, opens correctly in Excel).
- Login tokens last 72 hours (`TOKEN_TTL_HOURS`). SQLite is fine for a class project; switch `DATABASES` for production.
- Deleting a class or course that still has data is blocked; deleting a student also deletes their attendance.

## Deploy (optional)

- Backend ➜ Render / Railway: `gunicorn config.wsgi` from `backend_django/` (add `gunicorn` and a production database).
- Frontend ➜ Streamlit Community Cloud, set the secret/env `API_URL` to your backend URL.
>>>>>>> b6349bd (Initial commit)
