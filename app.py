import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta

# -------------------------------
# CONFIGURATION
# -------------------------------
EXPIRY_MINUTES = 2   # QR valid for 2 minutes

st.set_page_config(page_title="Smart Attendance System", layout="wide")

st.title("📚 Smart Attendance Tracking System")
st.markdown("### QR Based | Cloud Dashboard | Analytics Enabled")

# -------------------------------
# DATABASE CONNECTION
# -------------------------------
conn = sqlite3.connect("attendance.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    student_id TEXT,
    lecture_id TEXT,
    timestamp TEXT
)
""")

# -------------------------------
# QR VALIDATION FUNCTION
# -------------------------------
def is_valid_qr(lecture_id):
    try:
        time_part = lecture_id.split("_")[1]
        qr_time = datetime.strptime(time_part, "%Y%m%d%H%M")
        if datetime.now() - qr_time <= timedelta(minutes=EXPIRY_MINUTES):
            return True
        else:
            return False
    except:
        return False

# -------------------------------
# MARK ATTENDANCE SECTION
# -------------------------------
st.header("📝 Mark Attendance")

col1, col2 = st.columns(2)

with col1:
    student_id = st.text_input("Enter Student ID")

with col2:
    lecture_id = st.text_input("Enter Lecture Code (From QR)")

if st.button("Mark Attendance"):
    if student_id and lecture_id:
        if is_valid_qr(lecture_id):
            c.execute("INSERT INTO attendance VALUES (?, ?, ?)",
                      (student_id, lecture_id, datetime.now()))
            conn.commit()
            st.success("✅ Attendance Marked Successfully!")
        else:
            st.error("❌ QR Code Expired! Please Scan Again.")
    else:
        st.warning("⚠ Please enter both Student ID and Lecture Code!")

# -------------------------------
# DASHBOARD SECTION
# -------------------------------
st.header("📊 Attendance Dashboard")

df = pd.read_sql_query("SELECT * FROM attendance", conn)

if df.empty:
    st.info("No attendance records found yet.")
else:
    st.dataframe(df, use_container_width=True)

    st.subheader("📈 Attendance Count per Student")
    st.bar_chart(df['student_id'].value_counts())

    # Attendance percentage calculation
    total_lectures = df['lecture_id'].nunique()
    student_attendance = df['student_id'].value_counts()

    percentage = (student_attendance / total_lectures) * 100

    st.subheader("📊 Attendance Percentage")
    st.dataframe(percentage.rename("Attendance %"))

    # Low attendance alert
    low = percentage[percentage < 75]

    if not low.empty:
        st.warning("⚠ Students Below 75% Attendance")
        st.dataframe(low.rename("Attendance %"))

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.markdown("🚀 Developed for Hackathon | Smart Attendance with QR Auto-Expiry Security")