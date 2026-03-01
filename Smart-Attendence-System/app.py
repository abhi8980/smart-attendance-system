import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta

# -----------------------------
# CONFIGURATION
# -----------------------------
EXPIRY_MINUTES = 10   # QR valid for 10 minutes (safe for demo)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

st.set_page_config(page_title="Smart Attendance System", layout="wide")

# -----------------------------
# SESSION STATE
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# -----------------------------
# HEADER
# -----------------------------
st.title("📚 Smart Attendance Tracking System")
st.markdown("### QR Based | Secure | Cloud Enabled")

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
conn = sqlite3.connect("database/attendance.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    student_id TEXT,
    lecture_id TEXT,
    timestamp TEXT
)
""")

# -----------------------------
# QR VALIDATION FUNCTION
# -----------------------------
def is_valid_qr(lecture_id):
    try:
        time_part = lecture_id.split("_")[1]
        qr_time = datetime.strptime(time_part, "%Y%m%d%H%M%S")
        return datetime.now() - qr_time <= timedelta(minutes=EXPIRY_MINUTES)
    except:
        return False

# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------
menu = st.sidebar.selectbox(
    "Navigation",
    ["Student Attendance", "Admin Panel"]
)

# ==================================================
# STUDENT MODE
# ==================================================
if menu == "Student Attendance":

    st.subheader("📝 Mark Attendance")

    student_id = st.text_input("Enter Student ID")
    lecture_id = st.text_input("Enter Lecture Code (From QR)")

    if st.button("Mark Attendance"):
        if student_id and lecture_id:

            if is_valid_qr(lecture_id):

                # Check duplicate
                c.execute("""
                    SELECT * FROM attendance
                    WHERE student_id=? AND lecture_id=?
                """, (student_id, lecture_id))

                existing = c.fetchone()

                if existing:
                    st.warning("⚠ Attendance already marked!")
                else:
                    c.execute("INSERT INTO attendance VALUES (?, ?, ?)",
                              (student_id, lecture_id, datetime.now()))
                    conn.commit()
                    st.success("✅ Attendance Marked Successfully!")

            else:
                st.error("❌ QR Code Expired! Please Scan Again.")

        else:
            st.warning("⚠ Please fill all fields.")

# ==================================================
# ADMIN MODE
# ==================================================
elif menu == "Admin Panel":

    if not st.session_state.logged_in:

        st.subheader("🔐 Admin Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.success("Login Successful")
                st.rerun()
            else:
                st.error("Invalid Credentials")

    else:
        st.success("Welcome Admin 👋")

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

        df = pd.read_sql_query("SELECT * FROM attendance", conn)

        st.subheader("📊 Attendance Dashboard")

        if df.empty:
            st.info("No attendance records yet.")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Records", len(df))
            col2.metric("Total Sessions", df['lecture_id'].nunique())
            col3.metric("Unique Students", df['student_id'].nunique())

            st.dataframe(df, use_container_width=True)

            st.subheader("📈 Attendance Count per Student")
            st.bar_chart(df['student_id'].value_counts())

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.markdown("🚀 Hackathon Project | Secure QR Based Attendance System")