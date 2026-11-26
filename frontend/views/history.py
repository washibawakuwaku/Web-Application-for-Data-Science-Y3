"""Feature 5 – view, search, filter and update attendance records."""
import pandas as pd
import streamlit as st

import api_client
import components as ui
import theme

ui.page_header("Attendance History" if ui.is_staff() else "My Attendance History",
               "Search, filter and (for staff) correct attendance records.",
               icon=theme.mi("history"))

params = ui.filter_bar("hist", default_days=30, status=True, search=ui.is_staff())
limit = st.slider("Maximum rows to load", min_value=50, max_value=1000, value=200, step=50)

data = ui.load(api_client.get, "/api/attendance", limit=limit, **params)
items = data["items"]
st.caption(f"Showing **{len(items)}** of **{data['total']}** records")
if not items:
    ui.empty_state("No attendance records match these filters.")
    st.stop()

df = pd.DataFrame(items)
table = df[["date", "student_code", "student_name", "class_name", "subject_name", "status", "remark"]].copy()
table["status"] = table["status"].map(ui.status_tag)
table.columns = ["Date", "Student ID", "Student", "Class", "Subject", "Status", "Remark"]
st.dataframe(table, width="stretch", hide_index=True)

if ui.is_staff():
    with st.expander("✏️  Update or delete a record"):
        labels = {r["id"]: f"{r['date']} · {r['student_name']} · {r['subject_name']} · "
                           f"{ui.status_tag(r['status'])}" for r in items}
        rec_id = st.selectbox("Record", list(labels), format_func=labels.get)
        record = next(r for r in items if r["id"] == rec_id)
        options = ["present", "late", "absent"]
        col1, col2 = st.columns(2)
        new_status = col1.selectbox("Status", options, index=options.index(record["status"]),
                                    format_func=ui.status_tag)
        new_remark = col2.text_input("Remark", value=record["remark"])

        b1, b2, _ = st.columns([1, 1, 3])
        if b1.button("Update", type="primary", icon=theme.mi("edit"), width="stretch"):
            ui.run_action(lambda: api_client.put(f"/api/attendance/{rec_id}",
                                                 {"status": new_status, "remark": new_remark}),
                          "Record updated")
        if b2.button("Delete", icon=theme.mi("delete"), width="stretch"):
            ui.confirm_dialog("Delete this record?",
                              f"Delete the attendance record for **{record['student_name']}** "
                              f"on **{record['date']}**?",
                              "Delete", lambda: api_client.delete(f"/api/attendance/{rec_id}"),
                              "Record deleted", key=f"delrec_{rec_id}")
