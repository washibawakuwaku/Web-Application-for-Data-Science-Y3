import streamlit as st

import api_client
import config

st.title(f"{config.PROJECT_ICON} {config.PROJECT_TITLE}")
st.write(config.PROJECT_DESCRIPTION)

try:
    data = api_client.get_data(limit=1)
    schema = api_client.get_schema()
except api_client.APIError as e:
    api_client.show_error_and_stop(e)

c1, c2, c3 = st.columns(3)
c1.metric("Rows in dataset", f"{data['total_rows']:,}")
c2.metric("Input features", len(schema["features"]))
c3.metric("Model", "Trained ✅" if schema["model_trained"] else "Not trained")

st.divider()
st.subheader("How it works")
st.markdown(
    """
**Streamlit (frontend)** ➜ sends requests to ➜ **API (FastAPI or Django)** ➜ uses ➜ **ML model**

1. **Data Explorer** – look at the dataset and charts.
2. **Prediction** – enter values and get a prediction from the model.
3. **History** – see previous predictions.
4. **Model** – train the model and check how well it performs.
"""
)
# TODO: replace with a short introduction to YOUR project (problem, users, goal).
