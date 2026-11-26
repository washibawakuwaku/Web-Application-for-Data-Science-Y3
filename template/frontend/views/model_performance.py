import pandas as pd
import streamlit as st

import api_client

st.title("📈 Model")

with st.expander("Retrain the model"):
    st.write("Cleans the data, compares models with cross-validation, tunes the best one "
             "and evaluates it on the test set. Takes a few seconds to a few minutes.")
    if st.button("Train model", type="primary"):
        with st.spinner("Training on the backend..."):
            try:
                api_client.train()
                st.success("Model trained and saved.")
            except api_client.APIError as e:
                st.error(str(e))

try:
    report = api_client.get_metrics()
except api_client.APIError as e:
    if str(e).startswith("404"):
        st.info("No trained model yet. Open **Retrain the model** above.")
        st.stop()
    api_client.show_error_and_stop(e)

st.subheader(f"Final model: {report['best_model']}")
st.caption(f"Task: {report['task_type']} · target `{report['target']}` · "
           f"trained {report['trained_at']} · {report['n_train']} train / {report['n_test']} test rows")
st.write("Best parameters:", report["best_params"] or "default")

# --- Test metrics -----------------------------------------------------------
st.subheader("Performance on the test set")
cols = st.columns(len(report["test_metrics"]))
for col, (name, value) in zip(cols, report["test_metrics"].items()):
    col.metric(name.upper(), value)

# --- Model comparison -------------------------------------------------------
st.subheader("Model comparison (cross-validation)")
metric = report["primary_metric"]
cv = pd.DataFrame(report["cv_results"])
st.dataframe(cv, width="stretch", hide_index=True)
st.bar_chart(cv.set_index("model")[f"cv_{metric}_mean"], horizontal=True)

c1, c2 = st.columns(2)

# --- Confusion matrix -------------------------------------------------------
if report.get("confusion_matrix"):
    with c1:
        st.subheader("Confusion matrix")
        cm = report["confusion_matrix"]
        st.dataframe(pd.DataFrame(cm["matrix"],
                                  index=[f"Actual {l}" for l in cm["labels"]],
                                  columns=[f"Predicted {l}" for l in cm["labels"]]),
                     width="stretch")

# --- Feature importance -----------------------------------------------------
if report["feature_importance"]:
    with c2:
        st.subheader("Feature importance")
        st.bar_chart(pd.Series(report["feature_importance"]).head(15), horizontal=True)
