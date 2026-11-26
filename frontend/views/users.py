"""Feature 1 – role management (admin only)."""
import pandas as pd
import streamlit as st

import api_client
import components as ui
import theme

ui.page_header("Users & Roles", "Create accounts and manage roles and access.",
               icon=theme.mi("users"))

users = ui.load(api_client.get, "/api/users")["items"]
df = pd.DataFrame(users)[["username", "name", "email", "role", "student_code", "is_active"]]
df.columns = ["Username", "Name", "Email", "Role", "Student ID", "Active"]
st.dataframe(df, width="stretch", hide_index=True, column_config={
    "Active": st.column_config.CheckboxColumn("Active", disabled=True)})

with st.expander("➕  Create a user"):
    with st.form("create_user", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Full name *")
        username = c2.text_input("Username *")
        c3, c4 = st.columns(2)
        email = c3.text_input("Email")
        password = c4.text_input("Password * (min. 6 characters)", type="password")
        c5, c6 = st.columns(2)
        role = c5.selectbox("Role", ["teacher", "admin", "student"])
        student_code = c6.text_input("Student ID (student role only; must already exist)")
        if st.form_submit_button("Create user", type="primary", icon=theme.mi("add")):
            ui.run_action(lambda: api_client.post("/api/users", {
                "name": name, "username": username, "email": email, "password": password,
                "role": role, "student_code": student_code}), "User created")

others = [u for u in users if u["id"] != ui.current_user()["id"]]
if others:
    with st.expander("✏️  Change a user's role / status / password"):
        labels = {u["id"]: f"{u['username']} ({u['role']})" for u in others}
        uid = st.selectbox("User", list(labels), format_func=labels.get)
        u = next(x for x in others if x["id"] == uid)
        roles = ["admin", "teacher", "student"]
        c1, c2 = st.columns(2)
        new_role = c1.selectbox("Role", roles, index=roles.index(u["role"]) if u["role"] in roles else 2,
                                key=f"role_{uid}")
        active = c2.checkbox("Account is active", value=u["is_active"], key=f"active_{uid}")
        new_password = st.text_input("New password (leave empty to keep)", type="password", key=f"pw_{uid}")

        b1, b2, _ = st.columns([1, 1, 3])
        if b1.button("Save", type="primary", icon=theme.mi("save"), width="stretch"):
            payload = {"role": new_role, "is_active": active}
            if new_password:
                payload["password"] = new_password
            ui.run_action(lambda: api_client.put(f"/api/users/{uid}", payload), "User updated")
        if b2.button("Delete user", icon=theme.mi("delete"), width="stretch"):
            ui.confirm_dialog("Delete user?", f"Delete the account **{u['username']}** ({u['role']})?",
                              "Delete", lambda: api_client.delete(f"/api/users/{uid}"),
                              "User deleted", key=f"deluser_{uid}")
