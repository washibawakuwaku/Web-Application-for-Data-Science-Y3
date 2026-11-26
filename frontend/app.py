"""
Streamlit frontend — entry point.  Run from the frontend/ folder:

    cd frontend
    streamlit run app.py
"""
import streamlit as st

import api_client
import config
import theme

st.set_page_config(
    page_title=config.PROJECT_TITLE,
    page_icon=str(theme.LOGO_SM_PATH) if theme.LOGO_SM_PATH.exists() else config.PROJECT_ICON,
    layout="wide", initial_sidebar_state="expanded")
theme.inject_css()

# Keep the user signed in across page refreshes (token saved in a browser cookie).
api_client.init_cookies()
api_client.restore_session()

user = st.session_state.get("user")

# ---------------------------------------------------------------- not signed in
if not user:
    st.navigation([st.Page("views/login.py", title="Sign in", icon=theme.mi("login"))]).run()
    st.stop()

role = user["role"]

# ---------------------------------------------------------------- sidebar: brand + user
with st.sidebar:
    _logo = theme.logo_data_uri()
    _logo_html = (f'<img class="brand-logo" src="{_logo}" alt="logo">' if _logo
                  else f'<div class="logo">{config.PROJECT_ICON}</div>')
    st.markdown(
        f"""<div class="app-brand">{_logo_html}
              <div><div class="name">Attendance System</div>
                   <div class="tag">Class {config.CLASS_NAME}</div></div>
            </div>""", unsafe_allow_html=True)
    st.markdown(
        f"""<div class="user-card">
              <div class="u-name">{user['name']}</div>
              <span class="u-role">{role}</span>
            </div>""", unsafe_allow_html=True)

# ---------------------------------------------------------------- navigation (grouped by role)
P = st.Page
dashboard = P("views/dashboard.py", title="Dashboard", icon=theme.mi("dashboard"), default=True)
alerts = P("views/alerts.py", title="Low Attendance Alerts", icon=theme.mi("alerts"))
trends = P("views/trends.py", title="Trend Analysis", icon=theme.mi("trends"))
record = P("views/record_attendance.py", title="Record Attendance", icon=theme.mi("record"))
history = P("views/history.py", title="Attendance History", icon=theme.mi("history"))
reports = P("views/reports.py", title="Reports & Export", icon=theme.mi("reports"))
students = P("views/students.py", title="Students", icon=theme.mi("students"))
classes = P("views/classes.py", title="Classes & Courses", icon=theme.mi("classes"))
users = P("views/users.py", title="Users & Roles", icon=theme.mi("users"))
about = P("views/about.py", title="About", icon=theme.mi("about"))

if role == "admin":
    pages = {"Overview": [dashboard, alerts, trends],
             "Attendance": [record, history, reports],
             "Management": [students, classes, users],
             "Info": [about]}
elif role == "teacher":
    pages = {"Overview": [dashboard, alerts, trends],
             "Attendance": [record, history, reports],
             "Management": [students],
             "Info": [about]}
else:  # student
    pages = {"My attendance": [dashboard, history, alerts, trends, reports],
             "Info": [about]}

nav = st.navigation(pages)

# ---------------------------------------------------------------- sidebar: status + logout
with st.sidebar:
    st.divider()
    theme.theme_selector()
    if st.button("Log out", width="stretch", icon=theme.mi("logout")):
        api_client.logout()
        st.rerun()
    try:
        api_client.health()
        st.caption("🟢 Backend connected")
    except api_client.APIError:
        st.caption("🔴 Backend offline")
    st.caption(f"API · {api_client.API_URL}")

nav.run()
