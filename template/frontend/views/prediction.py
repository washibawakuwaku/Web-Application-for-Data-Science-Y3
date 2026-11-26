"""
The form is built automatically from GET /api/schema,
then the values are sent to POST /api/predict.
"""
import pandas as pd
import streamlit as st

import api_client

st.title("🔮 Prediction")

try:
    schema = api_client.get_schema()
except api_client.APIError as e:
    api_client.show_error_and_stop(e)

if not schema["model_trained"]:
    st.warning("The model is not trained yet. Go to the **Model** page and click **Train model**.")
    st.stop()

with st.form("predict_form"):
    cols = st.columns(2)
    values = {}
    for i, field in enumerate(schema["features"]):
        box = cols[i % 2]
        label = field["name"].replace("_", " ").capitalize()
        if field["type"] == "category":
            opts = field["options"]
            values[field["name"]] = box.selectbox(label, opts, index=opts.index(field["default"]))
        elif field["type"] == "integer":
            values[field["name"]] = box.number_input(label, value=int(field["default"]), step=1)
        else:
            values[field["name"]] = box.number_input(label, value=float(field["default"]), step=0.1)
    submitted = st.form_submit_button("Predict", type="primary")

if submitted:
    try:
        result = api_client.predict(values)
    except api_client.APIError as e:
        st.error(str(e))
        st.stop()

    st.subheader("Result")
    st.success(f"**{schema['target']}: {result['prediction']}**")
    if result.get("probabilities"):
        probs = pd.Series(result["probabilities"], name="probability")
        st.bar_chart(probs)

    # TODO: explain the result to the user in plain words.
