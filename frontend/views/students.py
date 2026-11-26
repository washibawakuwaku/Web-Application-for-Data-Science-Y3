"""Feature 2 – student management (admin: full control, teacher: read-only)."""
import pandas as pd
import streamlit as st

import api_client
import components as ui
<<<<<<< HEAD
import theme

ui.page_header("Students", "Add, find and manage student records.", icon=theme.mi("students"))
=======

st.title("🧑‍🎓 Students")
>>>>>>> e0f63b6cca91b78fdafa627e46b3ae3140f1b1b5
admin = ui.is_admin()

classes = ui.load(api_client.get, "/api/classes")["items"]
class_names = {c["id"]: c["name"] for c in classes}
class_options = [None] + list(class_names)


def class_label(x):
    return "— none —" if x is None else class_names[x]


<<<<<<< HEAD
tabs = st.tabs(["📋  Student list", "➕  Add student", "✏️  Edit / delete"] if admin
               else ["📋  Student list"])

# ---------------------------------------------------------------- list
with tabs[0]:
    c1, c2 = st.columns(2)
    search = c1.text_input("Search", placeholder="name, ID or email", icon=theme.mi("search"))
    class_filter = c2.selectbox("Class", class_options,
                                format_func=lambda x: "All classes" if x is None else class_names[x])
    data = ui.load(api_client.get, "/api/students", search=search,
                   **{"class": class_filter}, limit=1000)
    st.caption(f"**{data['total']}** student(s)")
    if data["items"]:
        df = pd.DataFrame(data["items"])[["student_code", "name", "email", "class_name", "has_account"]]
        df.columns = ["Student ID", "Name", "Email", "Class", "Has login"]
        st.dataframe(df, width="stretch", hide_index=True, column_config={
            "Has login": st.column_config.CheckboxColumn("Has login", disabled=True)})
    else:
        ui.empty_state("No students found.")

if not admin:
    st.stop()

# ---------------------------------------------------------------- add
with tabs[1]:
    with st.form("add_student", clear_on_submit=True):
        c1, c2 = st.columns(2)
        code = c1.text_input("Student ID *")
        name = c2.text_input("Full name *")
        c3, c4 = st.columns(2)
        email = c3.text_input("Email")
        class_id = c4.selectbox("Class", class_options, format_func=class_label)
        if st.form_submit_button("Add student", type="primary", icon=theme.mi("add")):
            ui.run_action(lambda: api_client.post("/api/students", {
                "student_code": code, "name": name, "email": email, "class_id": class_id}),
                "Student added")

# ---------------------------------------------------------------- edit / delete
with tabs[2]:
    everyone = ui.load(api_client.get, "/api/students", limit=1000)["items"]
    if not everyone:
        ui.empty_state("No students to edit yet.")
    else:
        labels = {s["id"]: f"{s['student_code']} – {s['name']}" for s in everyone}
        sid = st.selectbox("Student", list(labels), format_func=labels.get)
        s = next(x for x in everyone if x["id"] == sid)
        with st.form(f"edit_student_{sid}"):
            c1, c2 = st.columns(2)
            code = c1.text_input("Student ID", value=s["student_code"])
            name = c2.text_input("Full name", value=s["name"])
            c3, c4 = st.columns(2)
            email = c3.text_input("Email", value=s["email"])
            class_id = c4.selectbox("Class", class_options, index=class_options.index(s["class_id"]),
                                    format_func=class_label)
            if st.form_submit_button("Save changes", type="primary", icon=theme.mi("save")):
                ui.run_action(lambda: api_client.put(f"/api/students/{sid}", {
                    "student_code": code, "name": name, "email": email, "class_id": class_id}),
                    "Student updated")
        st.divider()
        if st.button("Delete student", icon=theme.mi("delete")):
            ui.confirm_dialog("Delete student?",
                              f"Delete **{s['name']}** ({s['student_code']})? This also deletes "
                              "all of their attendance records.",
                              "Delete", lambda: api_client.delete(f"/api/students/{sid}"),
                              "Student deleted", key=f"delstu_{sid}")
=======
def run(action, success):
    try:
        action()
        st.toast(success)
        st.rerun()
    except api_client.AuthExpired as e:
        api_client.show_error_and_stop(e)
    except api_client.APIError as e:
        st.error(str(e))


tabs = st.tabs(["📋 Student list", "➕ Add student", "✏️ Edit / delete"] if admin else ["📋 Student list"])

with tabs[0]:
    c1, c2 = st.columns(2)
    search = c1.text_input("Search", placeholder="name, ID or email")
    class_filter = c2.selectbox("Class", class_options, format_func=lambda x: "All" if x is None else class_names[x])
    data = ui.load(api_client.get, "/api/students", search=search, **{"class": class_filter}, limit=1000)
    st.caption(f"{data['total']} student(s)")
    if data["items"]:
        df = pd.DataFrame(data["items"])[["student_code", "name", "email", "class_name", "has_account"]]
        df.columns = ["Student ID", "Name", "Email", "Class", "Has login"]
        st.dataframe(df, width="stretch", hide_index=True)
    else:
        st.info("No students found.")

if admin:
    with tabs[1]:
        with st.form("add_student", clear_on_submit=True):
            code = st.text_input("Student ID *")
            name = st.text_input("Full name *")
            email = st.text_input("Email")
            class_id = st.selectbox("Class", class_options, format_func=class_label)
            if st.form_submit_button("Add student", type="primary"):
                run(lambda: api_client.post("/api/students", {"student_code": code, "name": name,
                                                              "email": email, "class_id": class_id}),
                    "Student added")

    with tabs[2]:
        everyone = ui.load(api_client.get, "/api/students", limit=1000)["items"]
        if not everyone:
            st.info("No students to edit yet.")
        else:
            labels = {s["id"]: f"{s['student_code']} – {s['name']}" for s in everyone}
            sid = st.selectbox("Student", list(labels), format_func=labels.get)
            s = next(x for x in everyone if x["id"] == sid)
            with st.form(f"edit_student_{sid}"):
                code = st.text_input("Student ID", value=s["student_code"])
                name = st.text_input("Full name", value=s["name"])
                email = st.text_input("Email", value=s["email"])
                class_id = st.selectbox("Class", class_options, index=class_options.index(s["class_id"]),
                                        format_func=class_label)
                if st.form_submit_button("Save changes", type="primary"):
                    run(lambda: api_client.put(f"/api/students/{sid}", {
                        "student_code": code, "name": name, "email": email, "class_id": class_id}),
                        "Student updated")
            st.divider()
            confirm = st.checkbox("I understand this also deletes all of this student's attendance records.")
            if st.button("🗑️ Delete student", disabled=not confirm):
                run(lambda: api_client.delete(f"/api/students/{sid}"), "Student deleted")
>>>>>>> e0f63b6cca91b78fdafa627e46b3ae3140f1b1b5
