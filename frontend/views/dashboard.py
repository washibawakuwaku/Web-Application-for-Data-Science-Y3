"""Feature 6 – attendance statistics and charts."""
import pandas as pd
import streamlit as st

import api_client
import components as ui
<<<<<<< HEAD
import theme

ui.page_header("Attendance Dashboard" if ui.is_staff() else "My Attendance",
               "Overall attendance, broken down by class, course and time.",
               icon="dashboard")

params = ui.filter_bar("dash", default_days=60)
data = ui.load(api_client.get, "/api/analytics/summary", **params)
o = data["overall"]
if o["total"] == 0:
    ui.empty_state("No attendance records match these filters yet.")
    st.stop()

# low-attendance banner + threshold (staff only)
threshold, low_total = None, 0
if ui.is_staff():
    alerts = ui.load(api_client.get, "/api/analytics/low-attendance", **params)
    threshold, low_total = alerts["threshold"], alerts["total"]

# ---------------------------------------------------------------- hero
chips = [("event_available", f"{o['total']:,} records"),
         ("groups", f"{o['students']:,} students" if ui.is_staff() else f"{o['total']:,} sessions")]
if ui.is_staff() and low_total:
    chips.append(("notification_important", f"{low_total} below {threshold:.0f}%"))
ui.hero(title="Attendance Overview", label=f"{params['date_from']}  →  {params['date_to']}",
        sub="Attendance rate = (present + late) ÷ all records. Late counts as attended.",
        rate=o["rate"], chips=chips)

if ui.is_staff() and low_total:
    st.warning(f"**{low_total} student(s)** are below {threshold:.0f}% attendance — "
               "see **Low Attendance Alerts**.", icon=":material/notification_important:")

# ---------------------------------------------------------------- KPI cards
share = lambda n: f"{100 * n / o['total']:.0f}% of records"   # noqa: E731
ui.kpi_row([
    {"label": "Present", "value": f"{o['present']:,}", "icon": "check_circle",
     "accent": theme.PRESENT, "delta": share(o["present"])},
    {"label": "Late", "value": f"{o['late']:,}", "icon": "schedule",
     "accent": theme.LATE, "delta": share(o["late"])},
    {"label": "Absent", "value": f"{o['absent']:,}", "icon": "cancel",
     "accent": theme.ABSENT, "delta": share(o["absent"])},
    {"label": "Students" if ui.is_staff() else "Records",
     "value": f"{(o['students'] if ui.is_staff() else o['total']):,}", "icon": "groups",
     "accent": "linear-gradient(135deg,#4f46e5,#7c3aed)",
     "delta": f"{len(data['by_class'])} class(es)" if ui.is_staff() else "all time"},
])

# ---------------------------------------------------------------- charts
daily = pd.DataFrame(data["daily"])
left, right = st.columns([1.35, 1])
with left:
    with st.container(border=True):
        ui.section("Attendance rate over time", icon="trending_up")
        st.altair_chart(theme.line_rate(daily, "date", "Date", threshold=threshold), width="stretch")
with right:
    with st.container(border=True):
        ui.section("Present / Late / Absent", icon="donut_small")
        st.altair_chart(theme.donut_status(o["present"], o["late"], o["absent"]), width="stretch")

left, right = st.columns(2)
with left:
    with st.container(border=True):
        ui.section("Rate by class", icon="library_books")
        st.altair_chart(theme.bar_category(pd.DataFrame(data["by_class"]), "class_name", "Class"),
                        width="stretch")
with right:
    with st.container(border=True):
        ui.section("Rate by course", icon="menu_book")
        by_course = pd.DataFrame(data["by_course"])
        st.altair_chart(theme.bar_category(by_course, "course", "Course"), width="stretch")

with st.expander("Show the numbers"):
    st.dataframe(
        by_course.rename(columns={"course": "Course", "total": "Records", "present": "Present",
                                  "late": "Late", "absent": "Absent", "rate": "Rate %"}),
        width="stretch", hide_index=True,
        column_config={"Rate %": st.column_config.NumberColumn(format="%.1f%%")})
=======

st.title("📊 Attendance Dashboard" if ui.is_staff() else "📊 My Attendance")
params = ui.filter_bar("dash", default_days=60)

data = ui.load(api_client.get, "/api/analytics/summary", **params)
o = data["overall"]
if o["total"] == 0:
    st.info("No attendance records match these filters yet.")
    st.stop()

c = st.columns(5)
c[0].metric("Attendance rate", ui.fmt_rate(o["rate"]))
c[1].metric("Present", o["present"])
c[2].metric("Late", o["late"])
c[3].metric("Absent", o["absent"])
c[4].metric("Students" if ui.is_staff() else "Records", o["students"] if ui.is_staff() else o["total"])
st.caption("Attendance rate = (present + late) ÷ all records. Late counts as attended.")

if ui.is_staff():
    alerts = ui.load(api_client.get, "/api/analytics/low-attendance", **params)
    if alerts["total"]:
        st.warning(f"🚨 {alerts['total']} student(s) are below {alerts['threshold']:.0f}% attendance "
                   "– see **Low Attendance Alerts**.")

left, right = st.columns(2)
with left:
    st.subheader("Attendance rate over time")
    daily = pd.DataFrame(data["daily"]).set_index("date")
    st.line_chart(daily["rate"])
with right:
    st.subheader("Present / Late / Absent")
    st.bar_chart(pd.Series({"Present": o["present"], "Late": o["late"], "Absent": o["absent"]}))

left, right = st.columns(2)
with left:
    st.subheader("Rate by class")
    by_class = pd.DataFrame(data["by_class"])
    st.bar_chart(by_class.set_index("class_name")["rate"])
with right:
    st.subheader("Rate by course")
    by_course = pd.DataFrame(data["by_course"])
    st.bar_chart(by_course.set_index("course")["rate"])

with st.expander("Show the numbers"):
    st.dataframe(by_course.rename(columns={"course": "Course", "total": "Records", "present": "Present",
                                           "late": "Late", "absent": "Absent", "rate": "Rate %"}),
                 width="stretch", hide_index=True)
>>>>>>> e0f63b6cca91b78fdafa627e46b3ae3140f1b1b5
