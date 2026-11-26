import pandas as pd
import streamlit as st

import api_client

st.title("📊 Data Explorer")

try:
    data = api_client.get_data(limit=1000)
    schema = api_client.get_schema()
except api_client.APIError as e:
    api_client.show_error_and_stop(e)

df = pd.DataFrame(data["rows"], columns=data["columns"])
target = schema["target"]
numeric = [f["name"] for f in schema["features"] if f["type"] in ("integer", "number")]
categorical = [f["name"] for f in schema["features"] if f["type"] == "category"]

st.caption(f"Showing {len(df):,} of {data['total_rows']:,} rows")
st.dataframe(df.head(20), width="stretch")

c1, c2 = st.columns(2)
with c1:
    st.subheader("Statistics")
    st.dataframe(df[numeric].describe().T.round(2), width="stretch")
with c2:
    st.subheader(f"Target: `{target}`")
    if schema["task_type"] == "classification":
        st.bar_chart(df[target].value_counts())
    else:
        st.bar_chart(df[target].value_counts(bins=20).sort_index())

st.subheader("Explore a column")
col = st.selectbox("Column", numeric + categorical)
if col in numeric:
    st.bar_chart(df[col].value_counts(bins=20).sort_index())
elif schema["task_type"] == "classification":
    st.bar_chart(df.groupby(col)[target].value_counts().unstack(fill_value=0))
else:
    st.bar_chart(df.groupby(col)[target].mean())

# TODO: add charts that tell the story of YOUR data.
