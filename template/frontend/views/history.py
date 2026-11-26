import pandas as pd
import streamlit as st

import api_client

st.title("🕘 Prediction History")

try:
    items = api_client.get_history()["items"]
except api_client.APIError as e:
    api_client.show_error_and_stop(e)

if not items:
    st.info("No predictions yet. Try the **Prediction** page.")
    st.stop()

rows = [{"time": it["created_at"], "prediction": it["prediction"], **it["input"]} for it in items]
st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
