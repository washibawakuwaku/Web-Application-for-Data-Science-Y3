"""
Streamlit frontend.  Run from the frontend/ folder:

    cd frontend
    streamlit run app.py
"""
import streamlit as st

import api_client
import config

st.set_page_config(page_title=config.PROJECT_TITLE, page_icon=config.PROJECT_ICON, layout="wide")

# Backend status in the sidebar
with st.sidebar:
    try:
        info = api_client.health()
        st.success(f"Backend connected ({info.get('backend', '?')})")
    except api_client.APIError:
        st.error("Backend not connected")
    st.caption(f"API: {api_client.API_URL}")

# TODO: add, remove or rename pages to match the features in your scope sheet.
pages = [
    st.Page("views/home.py", title="Home", icon="🏠", default=True),
    st.Page("views/data_explorer.py", title="Data Explorer", icon="📊"),
    st.Page("views/prediction.py", title="Prediction", icon="🔮"),
    st.Page("views/history.py", title="History", icon="🕘"),
    st.Page("views/model_performance.py", title="Model", icon="📈"),
    st.Page("views/about.py", title="About", icon="ℹ️"),
]
st.navigation(pages).run()
