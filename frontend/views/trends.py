"""Feature 9 – attendance patterns over time."""
import pandas as pd
import streamlit as st

import api_client
import components as ui
<<<<<<< HEAD
import theme

WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

ui.page_header("Attendance Trend Analysis",
               "How attendance changes over time, by weekday, and who is slipping.",
               icon=theme.mi("trends"))

period = st.segmented_control("Group by", ["week", "month"], default="week",
                              format_func=str.capitalize, selection_mode="single") or "week"
=======

st.title("📈 Attendance Trend Analysis")
period = st.radio("Group by", ["week", "month"], horizontal=True, format_func=str.capitalize)
>>>>>>> e0f63b6cca91b78fdafa627e46b3ae3140f1b1b5
params = ui.filter_bar("trends", default_days=90)

data = ui.load(api_client.get, "/api/analytics/trends", period=period, **params)
if not data["series"]:
<<<<<<< HEAD
    ui.empty_state("No attendance records match these filters yet.")
    st.stop()

for note in data["insights"]:
    st.info(note, icon=":material/lightbulb:")

# ---------------------------------------------------------------- rate over time
series = pd.DataFrame(data["series"])
series["date"] = pd.to_datetime(series["period"])
with st.container(border=True):
    ui.section(f"Attendance rate per {period}", icon="trending_up")
    st.altair_chart(theme.line_rate(series, "date", period.capitalize()), width="stretch")
    with st.expander("Show the numbers"):
        show = series[["period", "total", "present", "late", "absent", "rate", "change"]].rename(
            columns={"period": period.capitalize(), "total": "Records", "present": "Present",
                     "late": "Late", "absent": "Absent", "rate": "Rate %", "change": "Change"})
        st.dataframe(show, width="stretch", hide_index=True)

# ---------------------------------------------------------------- weekday + frequent absentees
left, right = st.columns(2)
with left:
    with st.container(border=True):
        ui.section("Absence rate by weekday", icon="calendar_month")
        weekday = pd.DataFrame(data["weekday"]).dropna(subset=["absent_rate"])
        st.altair_chart(
            theme.bar_category(weekday, "weekday", "Weekday", value_field="absent_rate",
                               value_title="Absent %", color=theme.ABSENT, domain=None,
                               sort=WEEKDAY_ORDER), width="stretch")
with right:
    with st.container(border=True):
        ui.section("Most frequently absent", icon="person_alert")
        frequent = pd.DataFrame(data["frequent_absentees"])
        if frequent.empty:
            st.success("Nobody has been absent. 🎉")
        else:
            st.dataframe(frequent[["student_code", "student_name", "absent", "total", "absent_rate"]].rename(
                columns={"student_code": "Student ID", "student_name": "Student", "absent": "Absences",
                         "total": "Records", "absent_rate": "Absent %"}), width="stretch", hide_index=True)

# ---------------------------------------------------------------- declining
with st.container(border=True):
    ui.section(f"Attendance dropped (latest {period} vs previous)", icon="trending_down")
    declining = pd.DataFrame(data["declining"])
    if declining.empty:
        st.success("No sharp drops found.", icon=":material/thumb_up:")
    else:
        st.dataframe(declining[["student_code", "student_name", "previous_rate", "current_rate", "change"]].rename(
            columns={"student_code": "Student ID", "student_name": "Student", "previous_rate": "Previous %",
                     "current_rate": "Current %", "change": "Change"}), width="stretch", hide_index=True)
=======
    st.info("No attendance records match these filters yet.")
    st.stop()

for note in data["insights"]:
    st.info(note)

st.subheader(f"Attendance rate per {period}")
series = pd.DataFrame(data["series"]).set_index("period")
st.line_chart(series["rate"])
with st.expander("Show the numbers"):
    st.dataframe(series[["total", "present", "late", "absent", "rate", "change"]].rename(
        columns={"total": "Records", "present": "Present", "late": "Late", "absent": "Absent",
                 "rate": "Rate %", "change": "Change vs previous"}), width="stretch")

left, right = st.columns(2)
with left:
    st.subheader("Absence rate by weekday")
    weekday = pd.DataFrame(data["weekday"])
    st.bar_chart(weekday.set_index("weekday")["absent_rate"])
with right:
    st.subheader("Most frequently absent")
    frequent = pd.DataFrame(data["frequent_absentees"])
    if frequent.empty:
        st.success("Nobody has been absent.")
    else:
        st.dataframe(frequent[["student_code", "student_name", "absent", "total", "absent_rate"]].rename(
            columns={"student_code": "Student ID", "student_name": "Student", "absent": "Absences",
                     "total": "Records", "absent_rate": "Absent %"}), width="stretch", hide_index=True)

st.subheader(f"Students whose attendance dropped (latest {period} vs previous)")
declining = pd.DataFrame(data["declining"])
if declining.empty:
    st.success("No sharp drops found.")
else:
    st.dataframe(declining[["student_code", "student_name", "previous_rate", "current_rate", "change"]].rename(
        columns={"student_code": "Student ID", "student_name": "Student", "previous_rate": "Previous %",
                 "current_rate": "Current %", "change": "Change"}), width="stretch", hide_index=True)
>>>>>>> e0f63b6cca91b78fdafa627e46b3ae3140f1b1b5
