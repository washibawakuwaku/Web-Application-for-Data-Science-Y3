import streamlit as st

import config

st.title("ℹ️ About")

st.subheader("Project")
st.write(f"**{config.PROJECT_TITLE}**")
st.write(config.PROJECT_DESCRIPTION)

st.subheader("Team")
st.write(f"Class: **{config.CLASS_NAME}**")
for member in config.TEAM_MEMBERS:
    st.markdown(f"- {member}")

st.subheader("Dataset")
st.write(config.DATA_SOURCE)

st.subheader("Architecture")
st.write("Streamlit (frontend) · FastAPI or Django (backend API) · scikit-learn (ML)")
