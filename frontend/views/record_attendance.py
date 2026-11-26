"""Feature 4 – record attendance for a class session."""
from datetime import date

import pandas as pd
import streamlit as st

import api_client
import components as ui
import theme

ui.page_header("Record Attendance",
               "Pick a course and date, mark each student, then save.",
               icon=theme.mi("record"))

courses = ui.load(api_client.get, "/api/courses")["items"]
if not courses:
    ui.empty_state("No courses available. An admin needs to create a course and assign it to you.")
    st.stop()

labels = {c["id"]: f"{c['subject_name']} — {c['class_name']}"
          + (f"  ({c['schedule']})" if c["schedule"] else "") for c in courses}

with st.container(border=True):
    c1, c2, c3 = st.columns([2, 1, 1])
    course_id = c1.selectbox("Course", list(labels), format_func=labels.get)
    day = c2.date_input("Date", value=date.today(), max_value=date.today())
    default_status = c3.selectbox("Default for unmarked", ["Present", "Late", "Absent"])

sheet = ui.load(api_client.get, "/api/attendance/sheet", course=course_id, date=day.isoformat())
roster = sheet["students"]
if not roster:
    st.warning("This class has no students yet. Add students in **Students** and enrol them in the class.",
               icon=":material/group_off:")
    st.stop()

already = sum(1 for s in roster if s["status"])
if already:
    st.info(f"Attendance was already saved for {already} of {len(roster)} students on this date. "
            "Saving again will update it.", icon=":material/history:")

df = pd.DataFrame([{
    "Student ID": s["student_code"], "Student": s["student_name"],
    "Status": (s["status"] or default_status.lower()).capitalize(), "Remark": s["remark"] or "",
} for s in roster])

edited = st.data_editor(
    df, key=f"sheet_{course_id}_{day}_{default_status}", hide_index=True, width="stretch",
    disabled=["Student ID", "Student"],
    column_config={
        "Status": st.column_config.SelectboxColumn("Status", options=["Present", "Late", "Absent"],
                                                   required=True, width="small"),
        "Remark": st.column_config.TextColumn("Remark", max_chars=200),
    },
)

counts = edited["Status"].value_counts()
m = st.columns(4)
m[0].metric("Present", int(counts.get("Present", 0)), icon=theme.STATUS_ICON["present"])
m[1].metric("Late", int(counts.get("Late", 0)), icon=theme.STATUS_ICON["late"])
m[2].metric("Absent", int(counts.get("Absent", 0)), icon=theme.STATUS_ICON["absent"])
m[3].metric("Total", len(edited), icon=":material/groups:")

if st.button("Save attendance", type="primary", icon=theme.mi("save"), width="stretch"):
    records = [{"student_id": roster[i]["student_id"], "status": row["Status"].lower(),
                "remark": row["Remark"] if isinstance(row["Remark"], str) else ""}
               for i, row in edited.reset_index(drop=True).iterrows()]
    try:
        result = api_client.post("/api/attendance/bulk",
                                 {"course_id": course_id, "date": day.isoformat(), "records": records})
        st.toast(f"Saved {result['saved']} records.", icon=":material/check_circle:")
        st.success(f"Saved {result['saved']} records for {result['course']} on {result['date']}.")
    except api_client.AuthExpired as e:
        api_client.show_error_and_stop(e)
    except api_client.APIError as e:
        st.error(str(e), icon=":material/error:")
