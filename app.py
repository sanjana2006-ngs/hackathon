import streamlit as st
import sqlite3
from datetime import date

# ---------------- PAGE CONFIG ----------------
st.set_page_config("Smart College Portal", "🎓", layout="centered")

# ---------------- CSS ----------------
st.markdown("""
<style>
.stApp { background:#0f172a; color:white; }
.stButton>button { background:#6366f1; color:white; border-radius:8px; }
input, textarea, select { background:#020617 !important; color:white !important; }
</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("college.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    role TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS notifications(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    message TEXT,
    receiver_role TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    student TEXT,
    status TEXT,
    date TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS timetable(
    staff TEXT,
    subject TEXT,
    day TEXT,
    time TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS login_log(
    username TEXT,
    role TEXT,
    date TEXT
)
""")

conn.commit()

# ---------------- TITLE ----------------
st.title("🎓 Smart College Portal")

# ---------------- REGISTRATION ----------------
st.subheader("📝 User Registration")

reg_role = st.selectbox("Register As", ["Student", "Staff", "Placement Officer"])
reg_user = st.text_input("Choose Username")

if st.button("Register"):
    if reg_user:
        cur.execute("INSERT OR IGNORE INTO users VALUES (?,?)", (reg_user, reg_role))
        conn.commit()
        st.success("Registration successful")

# ---------------- LOGIN ----------------
st.subheader("🔐 Login")

login_role = st.selectbox("Login As", ["Admin", "Student", "Staff", "Placement Officer"])
login_user = st.text_input("Enter Username")

if st.button("Login"):
    if login_role == "Admin" or cur.execute(
        "SELECT * FROM users WHERE username=? AND role=?",
        (login_user, login_role)
    ).fetchone():
        st.session_state.role = login_role
        st.session_state.user = login_user
        cur.execute("INSERT INTO login_log VALUES (?,?,?)",
                    (login_user, login_role, str(date.today())))
        conn.commit()
    else:
        st.error("Invalid credentials")

# ---------------- DASHBOARDS ----------------
if "role" in st.session_state:

    st.success(f"Logged in as {st.session_state.role}")

    # -------- ADMIN --------
    if st.session_state.role == "Admin":
        st.subheader("👑 Admin Dashboard")

        st.write("👥 Logged-in Users")
        logs = cur.execute("SELECT * FROM login_log").fetchall()
        for l in logs:
            st.info(f"{l[0]} ({l[1]}) on {l[2]}")

        st.write("🗑 Manage Notifications")
        notes = cur.execute("SELECT * FROM notifications").fetchall()
        for n in notes:
            if st.button(f"Delete: {n[2]}"):
                cur.execute("DELETE FROM notifications WHERE id=?", (n[0],))
                conn.commit()
                st.experimental_rerun()

    # -------- STAFF --------
    elif st.session_state.role == "Staff":
        st.subheader("👨‍🏫 Staff Dashboard")

        st.write("📊 Attendance")
        stu = st.text_input("Student Name")
        status = st.selectbox("Status", ["Present", "Absent"])

        if st.button("Update Attendance"):
            cur.execute("INSERT INTO attendance VALUES (?,?,?)",
                        (stu, status, str(date.today())))
            conn.commit()
            st.success("Attendance updated")

        st.write("📅 Class Schedule")
        subject = st.text_input("Subject")
        day = st.text_input("Day")
        time = st.text_input("Time")

        if st.button("Add Schedule"):
            cur.execute("INSERT INTO timetable VALUES (?,?,?,?)",
                        (st.session_state.user, subject, day, time))
            conn.commit()
            st.success("Schedule added")

        st.write("📢 Send Notification to Students")
        msg = st.text_input("Message")
        if st.button("Send"):
            cur.execute("INSERT INTO notifications VALUES (NULL,?,?,?)",
                        (st.session_state.user, msg, "Student"))
            conn.commit()
            st.success("Notification sent")

    # -------- PLACEMENT OFFICER --------
    elif st.session_state.role == "Placement Officer":
        st.subheader("💼 Placement Dashboard")

        msg = st.text_input("Placement Notification")
        if st.button("Send Placement Update"):
            cur.execute("INSERT INTO notifications VALUES (NULL,?,?,?)",
                        (st.session_state.user, msg, "Student"))
            conn.commit()
            st.success("Placement notification sent")

    # -------- STUDENT --------
    elif st.session_state.role == "Student":
        st.subheader("🎓 Student Dashboard")

        st.write("📢 Notifications (From Staff & Placement)")
        notes = cur.execute("""
        SELECT sender,message FROM notifications
        WHERE receiver_role='Student'
        """).fetchall()

        for n in notes:
            st.warning(f"{n[0]} : {n[1]}")

        st.write("📊 Attendance")
        att = cur.execute(
            "SELECT status,date FROM attendance WHERE student=?",
            (st.session_state.user,)
        ).fetchall()

        for a in att:
            st.info(f"{a[1]} - {a[0]}")
