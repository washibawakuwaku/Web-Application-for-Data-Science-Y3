"""Feature 8 – students whose attendance is below a threshold."""
import pandas as pd
import streamlit as st

import api_client
import components as ui
import theme

ui.page_header("Low Attendance Alerts",
               "Students below the attendance threshold who may need follow-up.",
               icon=theme.mi("alerts"))

threshold = st.slider("Alert threshold (attendance rate below…)", 40, 100, 75, step=5, format="%d%%")
params = ui.filter_bar("alerts", default_days=30)

data = ui.load(api_client.get, "/api/analytics/low-attendance", threshold=threshold, **params)
items = data["items"]
if not items:
    st.success(f"No students are below {threshold}% in this period. 🎉", icon=":material/celebration:")
    st.stop()

critical = sum(1 for i in items if i["severity"] == "critical")
ui.kpi_row([
    {"label": "Below threshold", "value": len(items), "icon": "warning",
     "accent": theme.LATE, "delta": f"under {threshold}% attendance"},
    {"label": "Critical", "value": critical, "icon": "priority_high",
     "accent": theme.ABSENT, "delta": f"under {threshold * 0.8:.0f}% attendance"},
    {"label": "Needs a warning", "value": len(items) - critical, "icon": "flag",
     "accent": "linear-gradient(135deg,#4f46e5,#7c3aed)", "delta": "between the two"},
])

ui.section("Who to follow up first", icon="person_alert")
for i in items[:5]:
    icon = ":material/error:" if i["severity"] == "critical" else ":material/warning:"
    msg = (f"**{i['student_name']}** ({i['student_code']}) — attendance **{i['rate']}%** "
           f"· {i['absent']} absent, {i['late']} late of {i['total']}")
    (st.error if i["severity"] == "critical" else st.warning)(msg, icon=icon)

with st.container(border=True):
    ui.section("All flagged students", icon="table_view")
    df = pd.DataFrame(items)[["student_code", "student_name", "total", "present", "late", "absent",
                              "rate", "severity"]]
    df["severity"] = df["severity"].map({"critical": "🔴 Critical", "warning": "🟠 Warning"})
    df.columns = ["Student ID", "Student", "Records", "Present", "Late", "Absent", "Rate", "Level"]
    st.dataframe(df, width="stretch", hide_index=True, column_config={
        "Rate": st.column_config.ProgressColumn("Rate", min_value=0, max_value=100, format="%.1f%%")})
    st.caption("Critical = rate below 80% of the threshold.")
