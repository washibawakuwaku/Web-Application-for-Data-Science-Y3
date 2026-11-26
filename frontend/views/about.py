import streamlit as st

import components as ui
import config
import theme

ui.page_header("About", "Project information, team and scope.", icon=theme.mi("about"))

with st.container(border=True):
    lc, tc = st.columns([1, 5], vertical_alignment="center")
    if theme.LOGO_PATH.exists():
        lc.image(str(theme.LOGO_PATH), width=100)
    with tc:
        ui.section(config.PROJECT_TITLE, icon="school")
        st.write(config.PROJECT_DESCRIPTION)
        st.write(f"**Target users:** {config.TARGET_USERS}")

c1, c2 = st.columns(2)
with c1:
    with st.container(border=True):
        ui.section("Team", icon=":material/diversity_3:")
        st.write(f"Class: **{config.CLASS_NAME}**")
        st.markdown(f"- **{config.TEAM_LEADER}** — Team Leader")
        for member in config.TEAM_MEMBERS:
            st.markdown(f"- {member}")
with c2:
    with st.container(border=True):
        ui.section("Architecture", icon=":material/account_tree:")
        st.markdown("- **Frontend:** Streamlit")
        st.markdown("- **Backend:** Django REST API")
        st.markdown("- **Database:** SQLite")
        st.markdown("- **Analytics:** pandas · Altair (shared `stats.py`)")

with st.container(border=True):
    ui.section("Out of scope (not built)", icon=":material/block:")
    cols = st.columns(2)
    for n, item in enumerate(config.OUT_OF_SCOPE):
        cols[n % 2].markdown(f"- {item}")
