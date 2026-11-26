"""
Central design system: colour tokens, icons, global CSS, the light/dark theme
switch and the Altair chart builders. Import this everywhere for one shared look.
"""
import base64
import math
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

# --------------------------------------------------------------------------- assets
ASSETS = Path(__file__).resolve().parent / "assets"
LOGO_PATH = ASSETS / "logo.png"
LOGO_SM_PATH = ASSETS / "logo_sm.png"
_LOGO_URI = None


def logo_data_uri() -> str:
    global _LOGO_URI
    if _LOGO_URI is None:
        try:
            _LOGO_URI = "data:image/png;base64," + base64.b64encode(LOGO_SM_PATH.read_bytes()).decode()
        except OSError:
            _LOGO_URI = ""
    return _LOGO_URI


# --------------------------------------------------------------------------- colours
BRAND = "#4f46e5"
BRAND2 = "#7c3aed"
INK = "#0f172a"
MUTED = "#64748b"
BORDER = "#e8ebf2"
CANVAS = "#f4f6fb"

PRESENT = "#0ca30c"
LATE = "#fab219"
ABSENT = "#d03b3b"

STATUS_COLOR = {"present": PRESENT, "late": LATE, "absent": ABSENT}
STATUS_EMOJI = {"present": "🟢", "late": "🟡", "absent": "🔴"}
STATUS_ICON = {"present": ":material/check_circle:", "late": ":material/schedule:",
               "absent": ":material/cancel:"}

ICON = {
    "dashboard": "space_dashboard", "alerts": "notification_important", "trends": "trending_up",
    "record": "fact_check", "history": "history", "reports": "summarize", "students": "groups",
    "classes": "library_books", "users": "manage_accounts", "about": "info", "save": "save",
    "delete": "delete", "edit": "edit", "add": "add_circle", "download": "download",
    "logout": "logout", "login": "login", "search": "search",
}

CHART_HEIGHT = 300


def _name(x: str) -> str:
    if not x:
        return ""
    if x.startswith(":material/"):
        return x.strip(":").split("/", 1)[1]
    return ICON.get(x, x)


def mi(name: str) -> str:
    return f":material/{_name(name)}:"


def msr(name: str, size: float = None, color: str = None) -> str:
    style = (f"font-size:{size}rem;" if size else "") + (f"color:{color};" if color else "")
    return f'<span class="msr" style="{style}">{_name(name)}</span>'


# --------------------------------------------------------------------------- theme state
def current_theme() -> str:
    """'light' | 'dark' | 'system' — what the user picked (default: system)."""
    return st.session_state.get("ui_theme", "system")


THEME_OPTIONS = {"light": "Light", "dark": "Dark", "system": "System"}


def theme_selector():
    """Sidebar appearance switch: one even row of text segments (Light / Dark / System)."""
    current = current_theme()
    choice = st.segmented_control(
        "Appearance", list(THEME_OPTIONS), format_func=THEME_OPTIONS.get,
        default=current, required=True, width="stretch", key="theme_picker")
    if choice and choice != current:
        st.session_state["ui_theme"] = choice
        st.rerun()


TOKENS_LIGHT = {
    "canvas": "#f4f6fb", "card": "#ffffff", "soft": "#f1f5f9", "border": "#e8ebf2",
    "ink": "#0f172a", "muted": "#64748b", "shadow": "rgba(15,23,42,.05)",
    "hover": "rgba(15,23,42,.16)", "input-bg": "#ffffff", "input-border": "#e2e8f0",
}
TOKENS_DARK = {
    "canvas": "#0b1220", "card": "#111a2e", "soft": "#0f1829", "border": "#223049",
    "ink": "#e6e9f2", "muted": "#93a3bd", "shadow": "rgba(0,0,0,.5)",
    "hover": "rgba(0,0,0,.6)", "input-bg": "#0c1322", "input-border": "#2a3650",
}


def _vars(tokens):
    return ";".join(f"--{k}:{v}" for k, v in tokens.items())


def inject_css():
    """Set the theme tokens for the chosen mode, then the static stylesheet.

    'system' emits the light tokens plus a prefers-color-scheme:dark override, so it
    follows the viewer's operating-system setting.
    """
    mode = current_theme()
    if mode == "dark":
        root = f":root{{{_vars(TOKENS_DARK)}}}"
    elif mode == "system":
        root = (f":root{{{_vars(TOKENS_LIGHT)}}}"
                f"@media (prefers-color-scheme:dark){{:root{{{_vars(TOKENS_DARK)}}}}}")
    else:
        root = f":root{{{_vars(TOKENS_LIGHT)}}}"
    st.markdown(f"<style>{root}</style>", unsafe_allow_html=True)
    st.markdown(STATIC_CSS, unsafe_allow_html=True)


# Static stylesheet (plain string – references the tokens via var()).
STATIC_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0&display=swap');

html, body, .stApp, .stMarkdown, [data-testid="stMarkdownContainer"],
button, input, textarea, select, h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}
.stApp { background: var(--canvas); }
.block-container { padding-top: 1.7rem; padding-bottom: 3rem; max-width: 1320px; }
#MainMenu, footer, [data-testid="stStatusWidget"] { display: none; }
header[data-testid="stHeader"] { background: transparent; }
/* the hidden cookie-persistence component leaves no gap */
iframe[title*="cookie_controller"] { display: none !important; height: 0 !important; }
[data-testid="stElementContainer"]:has(iframe[title*="cookie_controller"]) { display: none !important; }
h1, h2, h3, h4 { letter-spacing: -0.01em; }

/* main-content text colour follows the theme (sidebar keeps its own dark colours) */
[data-testid="stMain"], [data-testid="stMain"] p, [data-testid="stMain"] li,
[data-testid="stMain"] label, [data-testid="stMain"] h1, [data-testid="stMain"] h2,
[data-testid="stMain"] h3, [data-testid="stMain"] h4, [data-testid="stMain"] h5,
[data-testid="stMain"] [data-testid="stMarkdownContainer"] { color: var(--ink); }
[data-testid="stMain"] [data-testid="stCaptionContainer"],
[data-testid="stMain"] [data-testid="stCaptionContainer"] p { color: var(--muted) !important; }

.msr { font-family: 'Material Symbols Rounded'; font-weight: normal; font-style: normal;
       font-size: 1.3rem; line-height: 1; letter-spacing: normal; text-transform: none;
       display: inline-block; white-space: nowrap; direction: ltr;
       -webkit-font-smoothing: antialiased; font-feature-settings: 'liga'; vertical-align: middle; }
span[data-testid="stIconMaterial"], .material-symbols-rounded, .material-symbols-outlined,
[class*="material-symbols"], .material-icons, .msr {
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    font-weight: normal !important; font-style: normal !important;
    letter-spacing: normal !important; text-transform: none !important; }

/* page header */
.page-head { display: flex; align-items: center; gap: .85rem; margin: .1rem 0 1.1rem; }
.page-head .ph-icon { width: 46px; height: 46px; border-radius: 13px; flex: 0 0 46px;
    background: linear-gradient(135deg, #4f46e5, #7c3aed); color: #fff;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 6px 16px rgba(79,70,229,.32); }
.page-head .ph-icon .msr { font-size: 1.5rem; }
.page-head .ph-title { font-size: 1.5rem; font-weight: 800; color: var(--ink); line-height: 1.1; }
.page-head .ph-sub { color: var(--muted); font-size: .9rem; margin-top: .12rem; }
.filter-label { font-size:.78rem; font-weight:700; color: var(--muted); text-transform:uppercase;
    letter-spacing:.05em; margin-bottom:.1rem; display:flex; align-items:center; gap:.3rem; }

/* hero */
.hero { position: relative; overflow: hidden; border-radius: 20px; padding: 1.5rem 1.8rem;
    background: linear-gradient(120deg, #4f46e5 0%, #6d28d9 55%, #7c3aed 100%); color: #fff;
    display: flex; justify-content: space-between; align-items: center; gap: 1rem;
    box-shadow: 0 18px 40px -16px rgba(79,70,229,.6); margin-bottom: 1.1rem; }
.hero::before, .hero::after { content: ''; position: absolute; border-radius: 50%; }
.hero::before { width: 240px; height: 240px; right: -70px; top: -95px; background: rgba(255,255,255,.09); }
.hero::after { width: 150px; height: 150px; right: 130px; bottom: -80px; background: rgba(255,255,255,.06); }
.hero .h-label { font-size: .78rem; font-weight: 600; letter-spacing: .07em; text-transform: uppercase; opacity: .85; }
.hero .h-title { font-size: 1.55rem; font-weight: 800; margin: .15rem 0 .4rem; color:#fff; }
.hero .h-sub { opacity: .9; font-size: .92rem; }
.hero .h-chips { display: flex; gap: .5rem; margin-top: .95rem; flex-wrap: wrap; }
.hero .chip { background: rgba(255,255,255,.16); border: 1px solid rgba(255,255,255,.24);
    padding: .32rem .72rem; border-radius: 999px; font-size: .82rem; font-weight: 600;
    display: inline-flex; align-items: center; gap: .35rem; }
.hero .ring-wrap { position: relative; z-index: 2; flex: 0 0 auto; }

/* KPI cards */
.kpi-row { display: flex; gap: .85rem; margin: .1rem 0 .4rem; flex-wrap: wrap; }
.kpi { flex: 1 1 0; min-width: 155px; background: var(--card); border: 1px solid var(--border);
    border-radius: 16px; padding: 1rem 1.1rem; box-shadow: 0 1px 2px var(--shadow);
    transition: transform .16s ease, box-shadow .16s ease; }
.kpi:hover { transform: translateY(-2px); box-shadow: 0 14px 26px -14px var(--hover); }
.kpi .k-chip { width: 38px; height: 38px; border-radius: 11px; display: flex;
    align-items: center; justify-content: center; color: #fff; }
.kpi .k-chip .msr { font-size: 1.25rem; }
.kpi .k-label { color: var(--muted); font-size: .8rem; font-weight: 600; margin-top: .75rem; }
.kpi .k-value { font-size: 1.75rem; font-weight: 800; color: var(--ink); line-height: 1.15; }
.kpi .k-delta { font-size: .76rem; font-weight: 600; color: var(--muted); margin-top: .1rem; }

/* panels & cards */
.panel-head { display: flex; align-items: center; gap: .5rem; margin: .1rem 0 .5rem; }
.panel-head .msr { color: #6366f1; font-size: 1.2rem; }
.panel-head .pt { font-weight: 700; font-size: 1rem; color: var(--ink); }
[data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"] { background: var(--card);
    border-radius: 16px; box-shadow: 0 1px 2px var(--shadow); }
[data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"] { border-color: var(--border) !important; }
[data-testid="stMetric"] { background: var(--card); border: 1px solid var(--border); border-radius: 16px;
    padding: 1rem 1.1rem; box-shadow: 0 1px 2px var(--shadow); }
[data-testid="stMetricValue"] { color: var(--ink); }
[data-testid="stMetricLabel"] p { font-weight: 600; color: var(--muted); }

/* buttons */
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
    font-weight: 600; border-radius: .6rem; transition: transform .05s ease, box-shadow .15s ease; }
.stButton > button:hover, .stFormSubmitButton > button:hover,
.stDownloadButton > button:hover { transform: translateY(-1px); }
button[kind="primary"], button[kind="primaryFormSubmit"] {
    background-image: linear-gradient(135deg, #4f46e5, #7c3aed) !important; border: none !important;
    box-shadow: 0 8px 18px -8px rgba(79,70,229,.7) !important; color:#fff !important; }
[data-testid="stMain"] button[kind="secondary"] { background: var(--soft) !important;
    color: var(--ink) !important; border: 1px solid var(--border) !important; }

/* sidebar */
[data-testid="stSidebar"] { background: linear-gradient(185deg, #0f1222 0%, #1a1b3a 100%);
    border-right: 1px solid #232842; }
[data-testid="stSidebarNav"] a { border-radius: 9px; margin: 1px 8px; }
[data-testid="stSidebarNav"] a:hover { background: rgba(129,140,248,.14); }
[data-testid="stSidebarNav"] a[aria-current="page"] { background: rgba(129,140,248,.22); }
.app-brand { display: flex; align-items: center; gap: .6rem; padding: .2rem .2rem 1rem; }
.app-brand .logo { width: 40px; height: 40px; border-radius: 11px; flex: 0 0 40px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6); display: flex; align-items: center;
    justify-content: center; font-size: 21px; box-shadow: 0 6px 14px rgba(99,102,241,.4); }
.app-brand .brand-logo { width: 42px; height: 42px; border-radius: 50%; flex: 0 0 42px;
    background: #fff; padding: 2px; object-fit: contain; box-shadow: 0 4px 12px rgba(0,0,0,.35); }
.app-brand .name { font-weight: 700; font-size: 1rem; color: #f1f2f8; line-height: 1.1; }
.app-brand .tag { font-size: .72rem; color: #9aa0bd; }
.user-card { background: rgba(255,255,255,.05); border: 1px solid #2a2f4d; border-radius: 12px;
    padding: .7rem .85rem; margin-bottom: .4rem; }
.user-card .u-name { font-weight: 700; color: #f1f2f8; font-size: .92rem; }
.user-card .u-role { display: inline-block; margin-top: .3rem; font-size: .66rem; font-weight: 700;
    letter-spacing: .04em; text-transform: uppercase; color: #c7d2fe;
    background: rgba(99,102,241,.3); border: 1px solid rgba(129,140,248,.4);
    border-radius: 999px; padding: .1rem .55rem; }

/* appearance switch (sidebar) — a quiet track with an equal-width text segment per mode */
.st-key-theme_picker [data-testid="stWidgetLabel"] p { font-size: .7rem !important;
    font-weight: 700 !important; letter-spacing: .08em; text-transform: uppercase;
    color: #8a90ad !important; }
.st-key-theme_picker [role="radiogroup"] { display: flex; flex-wrap: nowrap; gap: 2px;
    width: 100%; padding: 3px; border-radius: 10px;
    background: rgba(255,255,255,.04); border: 1px solid #2a2f4d; }
.st-key-theme_picker button { flex: 1 1 0; min-width: 0; min-height: 2rem !important;
    padding: .25rem .4rem !important; margin: 0 !important; border: none !important;
    border-radius: 7px !important; background: transparent !important; box-shadow: none !important;
    color: #9aa0bd !important; transition: background .15s, color .15s; }
.st-key-theme_picker button p { font-size: .8rem !important; font-weight: 600 !important; }
.st-key-theme_picker button:hover { background: rgba(255,255,255,.06) !important;
    color: #e6e9f2 !important; }
.st-key-theme_picker button[aria-checked="true"],
.st-key-theme_picker button[aria-checked="true"]:hover { background: rgba(129,140,248,.24) !important;
    color: #ffffff !important; box-shadow: inset 0 0 0 1px rgba(129,140,248,.45) !important; }

/* status badges */
.badge { display: inline-flex; align-items: center; gap: .25rem; padding: .12rem .55rem;
    border-radius: 999px; font-size: .78rem; font-weight: 700; }
.b-present { background: #dcfce7; color: #166534; }
.b-late { background: #fef9c3; color: #854d0e; }
.b-absent { background: #fee2e2; color: #991b1b; }

/* Streamlit's own inputs, selects and tables are JS-themed and can't be darkened via CSS,
   so in dark mode they stay light and read as clean controls on the dark surface.
   Only the labels (which sit on the dark page) follow the theme. */
[data-testid="stMain"] [data-testid="stWidgetLabel"] p,
[data-testid="stMain"] [data-testid="stWidgetLabel"] label { color: var(--ink); }
[data-testid="stMain"] [data-baseweb="tab"] { color: var(--muted) !important; }
[data-testid="stMain"] [data-baseweb="tab"][aria-selected="true"] { color: var(--ink) !important; }

/* frame tables as clean cards */
[data-testid="stDataFrame"], [data-testid="stDataEditor"] {
    border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }

/* expander */
[data-testid="stExpander"] { border: 1px solid var(--border) !important; background: var(--card) !important;
    border-radius: 12px !important; }
[data-testid="stExpander"] summary { color: var(--ink) !important; }
[data-testid="stExpander"] summary:hover { color: #6366f1 !important; }
</style>
"""


# --------------------------------------------------------------------------- progress ring
def ring_svg(pct, size=128, stroke=13):
    pct = max(0.0, min(100.0, float(pct or 0)))
    r = (size - stroke) / 2
    circ = 2 * math.pi * r
    off = circ * (1 - pct / 100)
    cx = size / 2
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
      <circle cx="{cx}" cy="{cx}" r="{r:.1f}" fill="none" stroke="rgba(255,255,255,.22)" stroke-width="{stroke}"/>
      <circle cx="{cx}" cy="{cx}" r="{r:.1f}" fill="none" stroke="#ffffff" stroke-width="{stroke}"
        stroke-linecap="round" stroke-dasharray="{circ:.1f}" stroke-dashoffset="{off:.1f}"
        transform="rotate(-90 {cx} {cx})"/>
      <text x="50%" y="48%" text-anchor="middle" dy=".35em" fill="#fff"
        font-size="{size * 0.25:.0f}" font-weight="800" font-family="Inter">{pct:.0f}%</text>
      <text x="50%" y="66%" text-anchor="middle" fill="rgba(255,255,255,.82)"
        font-size="{size * 0.09:.0f}" font-family="Inter">attendance</text>
    </svg>"""


# --------------------------------------------------------------------------- Altair charts
def _ink():
    m = current_theme()
    return INK if m == "light" else "#e6e9f2" if m == "dark" else "#6b7686"


def _muted():
    m = current_theme()
    return MUTED if m == "light" else "#9aa7bd" if m == "dark" else "#7c879b"


def _grid():
    m = current_theme()
    return "#eef1f7" if m == "light" else "#1b2740" if m == "dark" else "rgba(124,135,155,.22)"


def _axisc():
    m = current_theme()
    return BORDER if m == "light" else "#2a3a57" if m == "dark" else "rgba(124,135,155,.45)"


def _style(chart):
    return (chart
            .configure_view(strokeWidth=0, fill=None)
            .configure(background="transparent")
            .configure_axis(labelColor=_muted(), titleColor=_muted(), labelFontSize=12, titleFontSize=12,
                            grid=True, gridColor=_grid(), domainColor=_axisc(), tickColor=_axisc(),
                            labelFont="Inter", titleFont="Inter")
            .configure_axisX(grid=False)
            .configure_legend(labelFont="Inter", titleFont="Inter", labelColor=_ink())
            .properties(height=CHART_HEIGHT, background="transparent"))


def line_rate(data, x_field, x_title, threshold=None):
    df = data.copy()
    x = (alt.X(f"{x_field}:T", title=x_title, axis=alt.Axis(labelAngle=0, format="%b %d"))
         if x_field == "date" else alt.X(f"{x_field}:N", title=x_title, axis=alt.Axis(labelAngle=0)))
    base = alt.Chart(df).encode(
        x=x, y=alt.Y("rate:Q", title="Attendance rate (%)", scale=alt.Scale(domain=[0, 100])))
    area = base.mark_area(line=False, opacity=0.14, color=BRAND)
    line = base.mark_line(color=BRAND, strokeWidth=3,
                          point=alt.OverlayMarkDef(color=BRAND, size=60, filled=True, stroke="#fff",
                                                   strokeWidth=1.5))
    layers = [area, line]
    if threshold is not None:
        layers.append(alt.Chart(df).mark_rule(color=ABSENT, strokeDash=[5, 4], strokeWidth=1.5)
                      .encode(y=alt.datum(threshold)))
    layers.append(base.mark_point(size=80, opacity=0).encode(tooltip=[
        alt.Tooltip(f"{x_field}:T" if x_field == "date" else f"{x_field}:N", title=x_title),
        alt.Tooltip("rate:Q", title="Rate %"), alt.Tooltip("total:Q", title="Records")]))
    return _style(alt.layer(*layers))


def donut_status(present, late, absent):
    df = pd.DataFrame({"Status": ["Present", "Late", "Absent"], "Count": [present, late, absent]})
    df = df[df["Count"] > 0]
    total = int(df["Count"].sum())
    base = alt.Chart(df).encode(
        theta=alt.Theta("Count:Q", stack=True),
        color=alt.Color("Status:N", scale=alt.Scale(domain=["Present", "Late", "Absent"],
                        range=[PRESENT, LATE, ABSENT]),
                        legend=alt.Legend(orient="bottom", title=None, labelFontSize=12)),
        tooltip=["Status:N", "Count:Q"])
    arc = base.mark_arc(innerRadius=72, outerRadius=108, cornerRadius=4,
                        stroke="#111a2e" if current_theme() == "dark" else "#ffffff", strokeWidth=2)
    center = (alt.Chart(pd.DataFrame({"t": [f"{total:,}"]}))
              .mark_text(align="center", fontWeight="bold", fontSize=26, color=_ink(), font="Inter", dy=-6)
              .encode(text="t:N"))
    sub = (alt.Chart(pd.DataFrame({"l": ["records"]}))
           .mark_text(align="center", fontSize=12, color=_muted(), font="Inter", dy=16).encode(text="l:N"))
    return (alt.layer(arc, center, sub).configure_view(strokeWidth=0, fill=None)
            .configure(background="transparent").configure_legend(labelFont="Inter", labelColor=_ink())
            .properties(height=CHART_HEIGHT, background="transparent"))


def bar_category(df, cat_field, cat_title, value_field="rate", value_title="Rate (%)",
                 color=BRAND, domain=(0, 100), sort="-x"):
    base = alt.Chart(df).encode(
        y=alt.Y(f"{cat_field}:N", sort=sort, title=cat_title),
        x=alt.X(f"{value_field}:Q", title=value_title,
                scale=alt.Scale(domain=list(domain)) if domain else alt.Undefined),
        tooltip=[alt.Tooltip(f"{cat_field}:N", title=cat_title),
                 alt.Tooltip(f"{value_field}:Q", title=value_title)])
    bars = base.mark_bar(color=color, cornerRadiusEnd=6, height=24)
    labels = base.mark_text(align="left", dx=6, color=_ink(), fontWeight="bold", font="Inter").encode(
        text=alt.Text(f"{value_field}:Q", format=".1f"))
    return _style(alt.layer(bars, labels)).properties(height=max(150, 48 * len(df)))
