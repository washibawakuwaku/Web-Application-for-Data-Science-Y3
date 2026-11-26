import streamlit as st

import api_client
import theme

# --------------------------------------------------------------------------- dark login theme
# Only injected on the login page, so the rest of the app keeps its light theme.
st.markdown(
    """
    <style>
    #MainMenu, header, footer,
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] { display: none !important; }

    .stApp { background:
        radial-gradient(1100px 620px at 78% 16%, #16263f 0%, #0b1526 44%, #060a13 100%) !important; }
    .block-container { padding-top: 2.4rem !important; max-width: 1180px !important; }
    .stApp, .stMarkdown, [data-testid="stMarkdownContainer"] { color: #e6e9f2; }

    /* top brand */
    .login-brand { display:flex; align-items:center; gap:.8rem; margin-bottom: 2.4rem; }
    .login-brand img { width:48px; height:48px; border-radius:50%; background:#fff; padding:2px;
        box-shadow:0 6px 16px rgba(0,0,0,.4); }
    .login-brand .u1 { font-weight:800; color:#f1f5f9; font-size:1.02rem; line-height:1.12; letter-spacing:.2px; }
    .login-brand .u2 { color:#8ea3c4; font-size:.82rem; }

    /* left hero */
    .ll-badge { display:inline-block; padding:.32rem .75rem; border:1px solid #2a3550; border-radius:999px;
        color:#a7bbdb; font-size:.78rem; font-weight:600; background:rgba(255,255,255,.03); }
    .ll-head { font-size:2.9rem; line-height:1.08; font-weight:800; color:#f8fafc !important;
        margin:1.1rem 0 .85rem; letter-spacing:-.025em; }
    .ll-sub { color:#93a3bd !important; font-size:1.02rem; max-width:31rem; margin-bottom:1.5rem; }
    .ll-features { display:flex; flex-direction:column; gap:.7rem; max-width:34rem; }
    .lf-card { display:flex; align-items:center; gap:.85rem; background:rgba(255,255,255,.035);
        border:1px solid #1f2a40; border-radius:14px; padding:.82rem 1rem; }
    .lf-ic { width:40px; height:40px; border-radius:11px; flex:0 0 40px; display:flex;
        align-items:center; justify-content:center; background:rgba(59,130,246,.14);
        border:1px solid rgba(59,130,246,.32); color:#60a5fa; }
    .lf-ic .msr { font-size:1.25rem; }
    .lf-t { font-weight:600; color:#e7edf7; font-size:.96rem; }
    .lf-s { color:#8092ac; font-size:.82rem; margin-top:.1rem; }
    .ll-foot { color:#5f6f8c; font-size:.8rem; margin-top:1.7rem; }

    /* right card (the bordered container) */
    [data-testid="stVerticalBlockBorderWrapper"] { background: rgba(14,20,33,.74) !important;
        border:1px solid #212c43 !important; border-radius:18px !important;
        box-shadow: 0 32px 64px -32px rgba(0,0,0,.85) !important; backdrop-filter: blur(6px); }
    .card-head .ch-k { color:#60a5fa; font-weight:700; font-size:.85rem; letter-spacing:.02em; }
    .card-head .ch-t { color:#f8fafc; font-weight:800; font-size:1.5rem; margin-top:.1rem; }
    .card-head .ch-s { color:#8ea0ba; font-size:.9rem; margin:.15rem 0 .2rem; }

    /* flatten the inner form box (keep only the outer card) */
    [data-testid="stForm"] { border:none !important; padding:0 !important; box-shadow:none !important;
        background:transparent !important; }
    [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"] {
        background:transparent !important; border:none !important; box-shadow:none !important; }

    /* inputs -> dark */
    [data-testid="stTextInput"] label, [data-testid="stWidgetLabel"] p,
    [data-testid="stRadio"] label { color:#cbd5e1 !important; font-weight:600 !important; }
    [data-testid="stTextInput"] div[data-baseweb="input"],
    [data-testid="stTextInput"] div[data-baseweb="base-input"],
    [data-testid="stTextInputRootElement"] { background-color:#0c1322 !important;
        border:1px solid #273350 !important; border-radius:10px !important; }
    [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within { border-color:#3b82f6 !important;
        box-shadow:0 0 0 2px rgba(59,130,246,.25) !important; }
    [data-testid="stTextInput"] input { background-color:#0c1322 !important; color:#e8edf7 !important;
        -webkit-text-fill-color:#e8edf7 !important; }
    [data-testid="stTextInput"] input::placeholder { color:#5b6b86 !important; }
    [data-testid="stTextInput"] input:-webkit-autofill {
        -webkit-box-shadow:0 0 0 1000px #0c1322 inset !important; -webkit-text-fill-color:#e8edf7 !important; }
    [data-baseweb="input"] [data-testid="stIconMaterial"] { color:#7183a0 !important; }
    [data-testid="stTextInput"] button { color:#7183a0 !important; }

    /* tabs */
    [data-baseweb="tab-list"] { border-bottom:1px solid #212c43 !important; gap:.3rem; }
    [data-baseweb="tab"] { color:#8ea0ba !important; }
    [data-baseweb="tab"][aria-selected="true"] { color:#f8fafc !important; }

    /* sign-in button -> solid blue */
    button[kind="primaryFormSubmit"], button[kind="primary"] { background:#2563eb !important;
        background-image:none !important; border:none !important;
        box-shadow:0 12px 26px -12px rgba(37,99,235,.85) !important; }
    button[kind="primaryFormSubmit"]:hover { background:#1d4ed8 !important; }

    [data-testid="stCaptionContainer"] p, small { color:#7c8aa5 !important; }
    [data-testid="stCaptionContainer"] code { color:#9fb3d6 !important; background:rgba(255,255,255,.05) !important; }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------------------------------- brand row
logo = theme.logo_data_uri()
logo_img = f'<img src="{logo}" alt="logo">' if logo else ""
st.markdown(
    f"""<div class="login-brand">{logo_img}
          <div><div class="u1">Royal University of Phnom Penh</div></div>
        </div>""", unsafe_allow_html=True)

left, right = st.columns([1.12, 0.88], gap="large", vertical_alignment="center")

# --------------------------------------------------------------------------- left hero
FEATURES = [
    ("verified_user", "Secure role-based access", "Admin, teacher and student roles"),
    ("fact_check", "Fast attendance recording", "Mark a whole class in one click"),
    ("insights", "Analytics, alerts & reports", "Trends, low-attendance alerts, CSV / PDF"),
]
cards = "".join(
    f'<div class="lf-card"><div class="lf-ic">{theme.msr(ic)}</div>'
    f'<div><div class="lf-t">{t}</div><div class="lf-s">{s}</div></div></div>'
    for ic, t, s in FEATURES)

with left:
    st.markdown(
        f"""<div>
              <span class="ll-badge">Student Attendance Management System</span>
              <h1 class="ll-head">Attendance, analytics,<br>and insight in one place.</h1>
              <p class="ll-sub">Record attendance, monitor trends, and follow up on
                 low-attendance students — all in one secure place.</p>
              <div class="ll-features">{cards}</div>
            </div>""", unsafe_allow_html=True)

# --------------------------------------------------------------------------- right sign-in card
with right:
    with st.container(border=True):
        st.markdown(
            """<div class="card-head">
                 <div class="ch-k">Welcome back</div>
                 <div class="ch-t">Sign in to continue</div>
                 <div class="ch-s">Use your account to access the system.</div>
               </div>""", unsafe_allow_html=True)

        if st.session_state.get("flash"):
            st.warning(st.session_state.pop("flash"), icon=":material/info:")

        login_tab, register_tab = st.tabs(["Log in", "Create account"])

        with login_tab:
            with st.form("login_form"):
                username = st.text_input("Username", icon=":material/person:")
                password = st.text_input("Password", type="password", icon=":material/lock:")
                if st.form_submit_button("Sign in", type="primary", width="stretch",
                                         icon=":material/arrow_forward:"):
                    try:
                        api_client.login(username, password)
                        st.rerun()
                    except api_client.APIError as e:
                        st.error(str(e), icon=":material/error:")

        with register_tab:
            st.caption("Students register with the **Student ID** the school gave them. "
                       "Admin accounts are created by an administrator.")
            role = st.radio("I am a", ["student", "teacher"], horizontal=True, format_func=str.capitalize)
            with st.form("register_form"):
                name = st.text_input("Full name", icon=":material/badge:")
                email = st.text_input("Email (optional)", icon=":material/mail:")
                student_code = st.text_input("Student ID", icon=":material/tag:") if role == "student" else ""
                new_username = st.text_input("Choose a username", icon=":material/person:")
                new_password = st.text_input("Choose a password (min. 6 characters)", type="password",
                                             icon=":material/lock:")
                if st.form_submit_button("Create account", type="primary", width="stretch",
                                         icon=":material/person_add:"):
                    try:
                        api_client.register({"name": name, "email": email, "role": role,
                                             "student_code": student_code,
                                             "username": new_username, "password": new_password})
                        st.rerun()
                    except api_client.APIError as e:
                        st.error(str(e), icon=":material/error:")

        st.markdown(
            '<div style="color:#64748b;font-size:.8rem;margin-top:.4rem;">'
            f'{theme.msr("verified_user", size=0.95, color="#64748b")} '
            'Secure sign-in for authorized users.</div>', unsafe_allow_html=True)
