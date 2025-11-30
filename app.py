import streamlit as st
from datetime import datetime, timedelta

# ---------- 데이터 구조 ----------
class TimeSlot:
    def __init__(self, day, start, end, subject=None):
        self.day = day
        self.start = start
        self.end = end
        self.subject = subject

class Assignment:
    def __init__(self, id, title, due, spend, priority, added=True):
        self.id = id
        self.title = title
        self.due = due
        self.spend = spend
        self.priority = priority
        self.added = added
        self.completed = False
        self.progress = 0

# ---------- 초기 데이터 ----------
st.session_state.setdefault("timetable", [
    TimeSlot("월", "09:00", "10:00", "데이터구조"),
    TimeSlot("월", "11:00", "12:00", "알고리즘"),
    TimeSlot("화", "09:00", "10:00", "운영체제"),
    TimeSlot("화", "14:00", "15:00", "데이터베이스"),
    TimeSlot("수", "10:00", "11:00", "네트워크"),
    TimeSlot("목", "09:00", "10:00", "소프트웨어공학"),
    TimeSlot("금", "13:00", "14:00", "인공지능"),
])

st.session_state.setdefault("assignments", [
    Assignment("1", "데이터구조 과제 - 연결 리스트 구현", "2025-12-05", 60, "high"),
    Assignment("2", "알고리즘 숙제 - 정렬 알고리즘 분석", "2025-12-07", 50, "medium")
])

TAB_HOME, TAB_TASK, TAB_AI, TAB_SET = st.tabs(["🏠 홈", "📝 과제", "✨ AI", "⚙️ 설정"])

# -----------------------------------------------------------
# 1️⃣ 홈 탭
# -----------------------------------------------------------
with TAB_HOME:
    st.subheader("시간표 1")
    st.write("2025년 11월 5주차")

    days = ["월", "화", "수", "목", "금"]
    timetable = st.session_state.timetable

    cols = st.columns(len(days))
    for i, day in enumerate(days):
        with cols[i]:
            st.markdown(f"**{day}**")
            for t in timetable:
                if t.day == day:
                    st.success(f"{t.start}-{t.end}\n\n**{t.subject}**")

# -----------------------------------------------------------
# 2️⃣ 과제 탭
# -----------------------------------------------------------
with TAB_TASK:
    st.subheader("과제 관리")

    for a in st.session_state.assignments:
        st.write(f"📌 {a.title}")
        st.write(f"📅 마감일: {a.due} | ⏱ {a.spend}분 | 🔥 우선순위: {a.priority}")
        done = st.checkbox("완료", key=f"done_{a.id}")
        if done:
            a.completed = True
            a.progress = 100

# -----------------------------------------------------------
# 3️⃣ AI 추천 탭
# -----------------------------------------------------------
with TAB_AI:
    st.subheader("AI 추천 일정")

    free_slots = []
    school_hours = [("09:00", "10:00"), ("10:00", "11:00"),
                    ("11:00", "12:00"), ("13:00", "14:00"),
                    ("14:00", "15:00")]

    busy = {(t.day, t.start, t.end) for t in timetable}

    for day in days:
        for s, e in school_hours:
            if not any(t.day == day and t.start == s for t in timetable):
                free_slots.append((day, s, e))

    pending = [a for a in st.session_state.assignments if not a.completed]

    if free_slots and pending:
        slot = free_slots[0]
        assign = pending[0]
        st.info(f"""
        🧠 추천 일정

        - 📅 {slot[0]}요일 {slot[1]} - {slot[2]}
        - 과제: **{assign.title}**
        - 예상: {assign.spend}분
        """)
    else:
        st.warning("추천할 일정이 없습니다.")

# -----------------------------------------------------------
# 4️⃣ 설정 탭
# -----------------------------------------------------------
with TAB_SET:
    st.subheader("과제 선호 설정")
    st.time_input("선호 시작 시간", datetime.strptime("09:00", "%H:%M"))
    st.time_input("선호 종료 시간", datetime.strptime("12:00", "%H:%M"))
    st.button("설정 저장")
