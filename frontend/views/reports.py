"""Feature 7 – generate attendance reports and export them as CSV or PDF."""
import streamlit as st

import api_client
import components as ui
import theme

REPORTS = {
    "attendance": "Attendance records (every entry)",
    "student_summary": "Summary by student",
    "class_summary": "Summary by class",
    "low_attendance": "Low attendance students",
}

ui.page_header("Reports & Export", "Build a report, preview it, then download CSV or PDF.",
               icon=theme.mi("reports"))

with st.container(border=True):
    c1, c2 = st.columns([2, 1])
    report_type = c1.selectbox("Report", list(REPORTS), format_func=REPORTS.get)
    fmt = c2.segmented_control("File format", ["csv", "pdf"], default="csv",
                               format_func=str.upper, selection_mode="single") or "csv"

params = ui.filter_bar("report", default_days=30, status=(report_type == "attendance"))
if report_type == "low_attendance":
    params["threshold"] = st.slider("Threshold", 40, 100, 75, step=5, format="%d%%")

if st.button("Generate report", type="primary", icon=theme.mi("reports"), width="stretch"):
    try:
        content, filename, mime = api_client.download(
            "/api/reports/export", type=report_type, format=fmt, **params)
        st.session_state["report_file"] = (content, filename, mime)
    except api_client.AuthExpired as e:
        api_client.show_error_and_stop(e)
    except api_client.APIError as e:
        st.session_state.pop("report_file", None)
        st.error(str(e), icon=":material/error:")

if "report_file" in st.session_state:
    content, filename, mime = st.session_state["report_file"]
    st.success(f"Report ready: **{filename}**", icon=":material/task_alt:")
    st.download_button("Download", data=content, file_name=filename, mime=mime,
                       icon=theme.mi("download"), type="primary")
    if filename.endswith(".csv"):
        import io

        import pandas as pd
        st.caption("Preview (first 50 rows)")
        st.dataframe(pd.read_csv(io.BytesIO(content)).head(50), width="stretch", hide_index=True)
