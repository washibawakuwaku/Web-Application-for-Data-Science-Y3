"""
All calls from Streamlit to the backend go through this file.
The frontend never loads the model itself – it asks the API.
"""
import os

import requests
import streamlit as st

# Change with an environment variable, e.g.  API_URL=https://my-api.onrender.com
API_URL = os.environ.get("API_URL", "http://localhost:8000").rstrip("/")
TIMEOUT = 30


class APIError(Exception):
    pass


def _request(method: str, path: str, **kwargs):
    url = f"{API_URL}{path}"
    try:
        r = requests.request(method, url, timeout=TIMEOUT, **kwargs)
    except requests.ConnectionError:
        raise APIError(f"Cannot connect to the backend at {API_URL}. Is it running?")
    if not r.ok:
        try:
            detail = r.json().get("detail", r.text)
        except ValueError:
            detail = r.text
        raise APIError(f"{r.status_code}: {detail}")
    return r.json()


def health():
    return _request("GET", "/api/health")


@st.cache_data(ttl=60)
def get_schema():
    return _request("GET", "/api/schema")


@st.cache_data(ttl=60)
def get_data(limit: int = 1000):
    return _request("GET", "/api/data", params={"limit": limit})


def get_metrics():
    return _request("GET", "/api/metrics")


def train():
    st.cache_data.clear()
    return _request("POST", "/api/train")


def predict(features: dict):
    return _request("POST", "/api/predict", json={"features": features})


def get_history():
    return _request("GET", "/api/predictions")


def show_error_and_stop(err: Exception):
    """Show a friendly error message and stop the page."""
    st.error(str(err))
    st.info("Start the backend first – see README.md, step 3.")
    st.stop()
