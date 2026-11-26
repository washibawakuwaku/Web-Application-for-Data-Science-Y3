"""
All calls from Streamlit to the Django backend go through this file.
The login token is kept in st.session_state and sent on every request.
"""
import os

import requests
import streamlit as st

# Change with an environment variable, e.g.  API_URL=https://my-api.onrender.com
API_URL = os.environ.get("API_URL", "http://localhost:8000").rstrip("/")
TIMEOUT = 30


class APIError(Exception):
    pass


class AuthExpired(APIError):
    pass


def _clean(params: dict) -> dict:
    return {k: v for k, v in params.items() if v not in (None, "")}


def _request(method: str, path: str, **kwargs):
    headers = {}
    if st.session_state.get("token"):
        headers["Authorization"] = f"Token {st.session_state['token']}"
    try:
        r = requests.request(method, f"{API_URL}{path}", headers=headers, timeout=TIMEOUT, **kwargs)
    except requests.ConnectionError:
        raise APIError(f"Cannot connect to the backend at {API_URL}. Is it running?")
    except requests.Timeout:
        raise APIError("The backend took too long to answer.")
    if r.status_code == 401 and headers:
        raise AuthExpired("Your session has expired. Please log in again.")
    if not r.ok:
        try:
            detail = r.json().get("detail", r.text)
        except ValueError:
            detail = r.text
        raise APIError(str(detail))
    return r


# ---------------------------------------------------------------- session
# The login token is also saved in a browser cookie so a page refresh keeps the
# user signed in (st.session_state alone is wiped on a hard refresh).
COOKIE_NAME = "attn_token"
COOKIE_MAX_AGE = 72 * 3600          # keep in step with TOKEN_TTL_HOURS
_cookie_ctl = None


def init_cookies():
    """Create the cookie controller for this run. Call once, early in app.py."""
    global _cookie_ctl
    try:
        from streamlit_cookies_controller import CookieController
        _cookie_ctl = CookieController()
    except Exception:
        _cookie_ctl = None
    return _cookie_ctl


def _save_token_cookie(token: str):
    if _cookie_ctl is not None:
        try:
            _cookie_ctl.set(COOKIE_NAME, token, max_age=COOKIE_MAX_AGE, same_site="strict")
        except Exception:
            pass


def _clear_token_cookie():
    if _cookie_ctl is not None:
        try:
            _cookie_ctl.remove(COOKIE_NAME)
        except Exception:
            pass


def restore_session():
    """Rebuild the session from the saved cookie after a fresh page load / refresh."""
    if st.session_state.get("user"):
        return
    try:
        token = st.context.cookies.get(COOKIE_NAME)
    except Exception:
        token = None
    if not token:
        return
    st.session_state["token"] = token
    try:
        st.session_state["user"] = _request("GET", "/api/auth/me").json()
    except AuthExpired:
        st.session_state.pop("token", None)       # token no longer valid -> forget it
        _clear_token_cookie()
    except APIError:
        st.session_state.pop("token", None)       # backend down -> keep cookie, retry next load


def start_session(response: dict):
    st.session_state["token"] = response["token"]
    st.session_state["user"] = response["user"]
    _save_token_cookie(response["token"])


def clear_session():
    st.session_state.pop("token", None)
    st.session_state.pop("user", None)
    _clear_token_cookie()


def health():
    return _request("GET", "/api/health").json()


def login(username: str, password: str):
    start_session(_request("POST", "/api/auth/login", json={"username": username, "password": password}).json())


def register(payload: dict):
    start_session(_request("POST", "/api/auth/register", json=payload).json())


def logout():
    try:
        _request("POST", "/api/auth/logout")
    except APIError:
        pass
    clear_session()


# ---------------------------------------------------------------- generic verbs
def get(path: str, **params):
    return _request("GET", path, params=_clean(params)).json()


def post(path: str, payload: dict | None = None):
    return _request("POST", path, json=payload or {}).json()


def put(path: str, payload: dict):
    return _request("PUT", path, json=payload).json()


def delete(path: str):
    return _request("DELETE", path).json()


def download(path: str, **params):
    """Returns (bytes, filename, mime) for CSV / PDF exports."""
    r = _request("GET", path, params=_clean(params))
    disposition = r.headers.get("Content-Disposition", "")
    filename = disposition.split("filename=")[-1].strip('"') if "filename=" in disposition else "report"
    return r.content, filename, r.headers.get("Content-Type", "application/octet-stream").split(";")[0]


def show_error_and_stop(err: Exception):
    """Show a friendly error message and stop the page."""
    if isinstance(err, AuthExpired):
        clear_session()
        st.session_state["flash"] = str(err)
        st.rerun()
    st.error(str(err))
    st.info("Start the backend first – see README.md, step 3.")
    st.stop()
