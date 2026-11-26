"""Reusable UI building blocks shared by every page (built on theme.py)."""
from datetime import date, timedelta

import streamlit as st

import api_client
import theme


# --------------------------------------------------------------------------- session / roles
def current_user() -> dict:
    return st.session_state["user"]


def is_staff() -> bool:
    return current_user()["role"] in ("admin", "teacher")


def is_admin() -> bool:
    return current_user()["role"] == "admin"


# --------------------------------------------------------------------------- API helpers
def load(fn, *args, **kwargs):
    """Call the API; on failure show a friendly error and stop the page."""
    try:
        return fn(*args, **kwargs)
    except api_client.APIError as e:
        api_client.show_error_and_stop(e)


def run_action(action, success: str):
    """Run an API mutation, toast on success, surface errors, then rerun."""
    try:
        action()
        st.toast(success, icon=":material/check_circle:")
        st.rerun()
    except api_client.AuthExpired as e:
        api_client.show_error_and_stop(e)
    except api_client.APIError as e:
        st.error(str(e), icon=":material/error:")


def confirm_dialog(title, message, confirm_label, action, success, *, key, danger=True):
    """Open a modal that asks before running a destructive action."""
    @st.dialog(title)
    def _dlg():
        st.warning(message, icon=":material/warning:") if danger else st.info(message)
        c1, c2 = st.columns(2)
        if c1.button("Cancel", width="stretch", key=f"{key}_cancel"):
            st.rerun()
        if c2.button(confirm_label, type="primary", width="stretch", key=f"{key}_ok",
                     icon=theme.mi("delete") if danger else None):
            run_action(action, success)
    _dlg()


# --------------------------------------------------------------------------- layout pieces
def page_header(title, subtitle=None, icon=None):
    chip = f'<div class="ph-icon">{theme.msr(icon)}</div>' if icon else ""
    sub = f'<div class="ph-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(f'<div class="page-head">{chip}<div><div class="ph-title">{title}</div>{sub}</div></div>',
                unsafe_allow_html=True)


def section(title, icon=None):
    ic = theme.msr(icon) if icon else ""
    st.markdown(f'<div class="panel-head">{ic}<span class="pt">{title}</span></div>',
                unsafe_allow_html=True)


def hero(title, label, sub, rate, chips=()):
    chip_html = "".join(
        f'<span class="chip">{theme.msr(ic)} {txt}</span>' for ic, txt in chips)
    st.markdown(
        f"""<div class="hero">
              <div>
                <div class="h-label">{label}</div>
                <div class="h-title">{title}</div>
                <div class="h-sub">{sub}</div>
                <div class="h-chips">{chip_html}</div>
              </div>
              <div class="ring-wrap">{theme.ring_svg(rate)}</div>
            </div>""", unsafe_allow_html=True)


def kpi_row(cards):
    """cards = list of dict(label, value, icon, accent, delta=None)."""
    html = ['<div class="kpi-row">']
    for c in cards:
        delta = f'<div class="k-delta">{c["delta"]}</div>' if c.get("delta") else ""
        html.append(
            f'<div class="kpi"><div class="k-chip" style="background:{c["accent"]}">'
            f'{theme.msr(c["icon"])}</div>'
            f'<div class="k-label">{c["label"]}</div>'
            f'<div class="k-value">{c["value"]}</div>{delta}</div>')
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def status_tag(status: str) -> str:
    """'present' -> '🟢 Present' for use inside dataframes / selectboxes."""
    return f"{theme.STATUS_EMOJI.get(status, '')} {status.capitalize()}"


def badge(status: str) -> str:
    return f'<span class="badge b-{status}">{status.capitalize()}</span>'


def empty_state(message, icon=":material/inbox:"):
    st.info(message, icon=icon)


# --------------------------------------------------------------------------- formatting
def fmt_rate(value) -> str:
    return "–" if value is None else f"{value:.1f}%"


# --------------------------------------------------------------------------- filters
def date_range(label: str, key: str, default_days: int):
    today = date.today()
    value = st.date_input(label, value=(today - timedelta(days=default_days), today),
                          max_value=today, key=key)
    if isinstance(value, (tuple, list)):
        if len(value) == 2:
            return value[0], value[1]
        if len(value) == 1:
            return value[0], today
    return value, value


def _pick(col, label, items, label_fn, key):
    labels = {i["id"]: label_fn(i) for i in items}
    return col.selectbox(label, [None] + list(labels), key=key,
                         format_func=lambda x: "All" if x is None else labels[x])


def filter_bar(key: str, default_days: int = 60, status: bool = False, search: bool = False) -> dict:
    """Class / course / date range (and optionally status / search). Returns API query params."""
    classes = load(api_client.get, "/api/classes")["items"]
    courses = load(api_client.get, "/api/courses")["items"]
    with st.container(border=True):
        st.markdown(f'<div class="filter-label">{theme.msr("search", size=1.0)} Filters</div>',
                    unsafe_allow_html=True)
        cols = st.columns([1, 1.4, 1.6] + ([1] if status else []) + ([1.4] if search else []))
        params = {
            "class": _pick(cols[0], "Class", classes, lambda c: c["name"], f"{key}_class"),
            "course": _pick(cols[1], "Course", courses,
                            lambda c: f"{c['subject_name']} ({c['class_name']})", f"{key}_course"),
        }
        with cols[2]:
            start, end = date_range("Date range", f"{key}_dates", default_days)
        params["date_from"], params["date_to"] = start.isoformat(), end.isoformat()
        i = 3
        if status:
            params["status"] = cols[i].selectbox(
                "Status", [None, "present", "late", "absent"], key=f"{key}_status",
                format_func=lambda x: "All" if x is None else status_tag(x))
            i += 1
        if search:
            params["search"] = cols[i].text_input("Search student", key=f"{key}_search",
                                                  placeholder="name or ID")
    return params
