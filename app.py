import streamlit as st
import sqlite3
from datetime import date

# ---------------- DATABASE ----------------
conn = sqlite3.connect("college.db", check_same_thread=False)
cur = conn.cursor()

# Users table
cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT,
    role TEXT
)
""")

# Notifications table
cur.execute("""
CREATE TABLE IF NOT EXISTS notifications(
    sender TEXT,
    message TEXT,
    receiver_role TEXT
)
""")

# Attendance table
cur.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    student TEXT,
    status TEXT,
    date TEXT
)
""")

conn.commit()

# ---------------- PAGE CONFIG ----------------
st.set_page_config("Smart College Portal", "🎓", layout="centered")

# ---------------- LOAD CSS ----------------
with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------- LOGIN ----------------
st.title("🎓 Smart College Portal")

role = st.selectbox(
    "Login as",
    ["Admin", "Staff", "Placement Officer", "Student"]
)

username = st.text_input("Enter Username")

if st.button("Login"):
    st.session_state.role = role
    st.session_state.user = username

# ---------------- DASHBOARDS ----------------
if "role" in st.session_state:

    st.success(f"Logged in as {st.session_state.role}")

    # ---------- ADMIN ----------
    if st.session_state.role == "Admin":
        st.subheader("👑 Admin Dashboard")

        users = cur.execute("SELECT role, COUNT(*) FROM users GROUP BY role").fetchall()
        for u in users:
            st.info(f"{u[0]} count : {u[1]}")

        msg = st.text_input("Send Notification")
        target = st.selectbox("Send to", ["Student", "Staff", "Placement Officer"])

        if st.button("Send"):
            cur.execute("INSERT INTO notifications VALUES (?,?,?)",
                        ("Admin", msg, target))
            conn.commit()
            st.success("Notification sent")

    # ---------- STAFF ----------
    elif st.session_state.role == "Staff":
        st.subheader("👨‍🏫 Staff Dashboard")

        student = st.text_input("Student Name")
        status = st.selectbox("Attendance", ["Present", "Absent"])

        if st.button("Update Attendance"):
            cur.execute("INSERT INTO attendance VALUES (?,?,?)",
                        (student, status, str(date.today())))
            conn.commit()
            st.success("Attendance updated")

    # ---------- PLACEMENT OFFICER ----------
    elif st.session_state.role == "Placement Officer":
        st.subheader("💼 Placement Dashboard")

        notice = st.text_input("Placement Notification")

        if st.button("Send Placement Update"):
            cur.execute("INSERT INTO notifications VALUES (?,?,?)",
                        ("Placement Officer", notice, "Student"))
            conn.commit()
            st.success("Placement notification sent")

    # ---------- STUDENT ----------
    elif st.session_state.role == "Student":
        st.subheader("🎓 Student Dashboard")

        st.write("📢 Notifications:")
        notes = cur.execute(
            "SELECT sender, message FROM notifications WHERE receiver_role='Student'"
        ).fetchall()

        for n in notes:
            st.warning(f"{n[0]} : {n[1]}")

        st.write("📊 Attendance:")
        att = cur.execute(
            "SELECT status, date FROM attendance WHERE student=?",
            (st.session_state.user,)
        ).fetchall()

        for a in att:
            st.info(f"{a[1]} - {a[0]}")

# ---------------- ABOUT & CONTACT ----------------
st.divider()
st.write("📘 About | 📞 Contact")
st.write("Smart College Portal – Built using Streamlit, Python, and SQL")
