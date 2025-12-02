import streamlit as st
import datetime

# -------------------------------------------------
# 1. 페이지 기본 설정
# -------------------------------------------------
st.set_page_config(page_title="AI Timetable", layout="centered")

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "홈"

# -------------------------------------------------
# 2. CSS 스타일
# -------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
        margin-bottom: 80px;
    }
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 5rem;
        max-width: 100%;
    }

    /* 하단 탭 네비게이션 */
    div[data-testid="stRadio"] {
        position: fixed; bottom: 0; left: 0;
        width: 100%; background-color: white;
        border-top: 1px solid #e5e7eb;
        z-index: 9999;
        padding: 8px 0 12px 0;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
    }
    div[data-testid="stRadio"] > label { display: none !important; }
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex; justify-content: space-around;
        width: 100%;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        flex: 1; background: white !important;
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
    }
    div[data-testid="stRadio"] p {
        font-size: 10px; margin: 0;
        color: #9ca3af; text-align: center;
    }
    div[data-testid="stRadio"] label[data-checked="true"] p {
        color: #4f46e5 !important; font-weight: 700;
    }
    div[data-testid="stRadio"] p span {
        font-size: 20px; margin-bottom: 2px;
    }

    /* 시간표 */
    .timetable-wrapper {
        background: white;
        border-radius: 15px;
        border: 1px solid #e5e7eb;
        overflow: hidden;
        margin-top: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .timetable-header {
        display: grid;
        grid-template-columns: 40px repeat(5, 1fr);
        background: #f9fafb;
        border-bottom: 1px solid #e5e7eb;
        text-align: center;
        font-size: 12px; font-weight: 600;
        color: #6b7280; padding: 8px 0;
    }
    .timetable-body {
        display: grid;
        grid-template-columns: 40px repeat(5, 1fr);
        grid-template-rows: repeat(42, 10px);
        position: relative;
    }
    .time-label {
        font-size: 10px; color: #9ca3af;
        text-align: center;
        border-right: 1px solid #f3f4f6;
        border-bottom: 1px solid #f3f4f6;
        display: flex; align-items: start;
        justify-content: center; padding-top: 2px;
    }
    .grid-bg-cell {
        border-right: 1px solid #f3f4f6;
        border-bottom: 1px solid #f3f4f6;
    }

    .event-item {
        margin: 1px; padding: 4px 6px;
        border-radius: 6px;
        font-size: 11px;
        line-height: 1.2;
        display: flex; flex-direction: column;
        justify-content: center;
        overflow: hidden;
        z-index: 10;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    .evt-class {
        background-color: #dcfce7;
        border-left: 3px solid #22c55e;
        color: #14532d;
    }
    .evt-task {
        background-color: #fef9c3;
        border-left: 3px solid #eab308;
        color: #854d0e;
    }

    .evt-title { font-weight: 700; margin-bottom: 2px; }
    .evt-time { font-size: 9px; opacity: 0.8; }

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 3. 기본 시간표 데이터
# -------------------------------------------------

timetable_data = [
    {"day": "월", "start": "09:00", "end": "10:00", "title": "데이터구조", "kind": "class"},
    {"day": "월", "start": "10:00", "end": "11:00", "title": "데이터구조 과제", "kind": "task", "sub": "연결리스트 구현"},
    {"day": "월", "start": "11:00", "end": "12:00", "title": "알고리즘", "kind": "class"},
    {"day": "월", "start": "13:00", "end": "13:50", "title": "알고리즘 숙제", "kind": "task", "sub": "50분"},
    {"day": "화", "start": "09:00", "end": "10:00", "title": "운영체제", "kind": "class"},
    {"day": "화", "start": "14:00", "end": "15:00", "title": "데이터베이스", "kind": "class"},
    {"day": "수", "start": "10:00", "end": "11:00", "title": "네트워크", "kind": "class"},
    {"day": "목", "start": "09:00", "end": "10:00", "title": "소프트웨어공학", "kind": "class"},
    {"day": "금", "start": "09:00", "end": "10:00", "title": "데이터구조 과제", "kind": "task", "sub": "스택/큐 구현"},
    {"day": "금", "start": "13:00", "end": "14:00", "title": "인공지능", "kind": "class"},
]


# -------------------------------------------------
# 시간표 렌더 함수
# -------------------------------------------------
def render_timetable():
    days = ["월", "화", "수", "목", "금"]
    day_map = {d: i for i, d in enumerate(days)}

    html = '<div class="timetable-wrapper">'
    html += '<div class="timetable-header"><div></div>'
    for d in days:
        html += f"<div>{d}</div>"
    html += "</div>"

    html += '<div class="timetable-body">'

    for h in range(9, 17):
        row_start = (h - 9) * 6 + 1
        html += f'<div class="time-label" style="grid-column: 1; grid-row: {row_start} / span 6;">{h}</div>'
        for col in range(2, 7):
            html += f'<div class="grid-bg-cell" style="grid-column: {col}; grid-row: {row_start} / span 6;"></div>'

    for item in timetable_data:
        d_idx = day_map[item["day"]]
        sh, sm = map(int, item["start"].split(":"))
        eh, em = map(int, item["end"].split(":"))
        start_min = (sh - 9) * 60 + sm
        duration = eh * 60 + em - (sh * 60 + sm)
        g_row = start_min // 10 + 1
        g_span = duration // 10
        g_col = d_idx + 2
        cls = "evt-class" if item["kind"] == "class" else "evt-task"
        sub = item.get("sub", "")

        html += f"""
        <div class="event-item {cls}" style="grid-column:{g_col}; grid-row:{g_row}/span {g_span};">
            <div class='evt-title'>{item['title']}</div>
            <div class='evt-time'>{sub}</div>
        </div>
        """

    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)


# -------------------------------------------------
# 4. HOMEPAGE UI
# -------------------------------------------------
if st.session_state.active_tab == "홈":

    # 시간표 리스트 초기화
    if "timetables" not in st.session_state:
        st.session_state.timetables = ["시간표 1"]
        st.session_state.current_tt = "시간표 1"
    if "rename_mode" not in st.session_state:
        st.session_state.rename_mode = False

    # 상단 UI
    c1, c2, c3 = st.columns([5, 1, 1])

    with c1:
        selected = st.selectbox(
            "시간표 선택",
            st.session_state.timetables,
            index=st.session_state.timetables.index(st.session_state.current_tt),
            label_visibility="collapsed",
        )
        if selected != st.session_state.current_tt:
            st.session_state.current_tt = selected
            st.rerun()

    with c2:
        if st.button("✏️"):
            st.session_state.rename_mode = True

    with c3:
        if st.button("➕"):
            new_name = f"시간표 {len(st.session_state.timetables) + 1}"
            st.session_state.timetables.append(new_name)
            st.session_state.current_tt = new_name
            st.rerun()

    # 이름 변경 폼
    if st.session_state.rename_mode:
        with st.form("rename"):
            new = st.text_input("새 이름", st.session_state.current_tt)
            ok = st.form_submit_button("변경")
            if ok and new:
                idx = st.session_state.timetables.index(st.session_state.current_tt)
                st.session_state.timetables[idx] = new
                st.session_state.current_tt = new
                st.session_state.rename_mode = False
                st.rerun()

    # 날짜 이동
    if "current_date" not in st.session_state:
        st.session_state.current_date = datetime.date(2025, 12, 1)

    colA, colB, colC = st.columns([1, 3, 1])

    with colA:
        if st.button("◀"):
            st.session_state.current_date -= datetime.timedelta(weeks=1)

    with colB:
        wk = st.session_state.current_date.isocalendar()[1] % 4 + 1
        st.markdown(
            f"<div style='text-align:center; font-size:18px; font-weight:600;'>"
            f"{st.session_state.current_date.year}년 "
            f"{st.session_state.current_date.month}월 {wk}주차</div>",
            unsafe_allow_html=True,
        )

    with colC:
        if st.button("▶"):
            st.session_state.current_date += datetime.timedelta(weeks=1)

    # 시간표 스크롤 가능 영역
    st.markdown("<div style='height:550px; overflow-y:scroll;'>", unsafe_allow_html=True)
    render_timetable()
    st.markdown("</div>", unsafe_allow_html=True)

    # 카테고리 표시
    st.markdown("""
    <div style="display:flex; gap:18px; margin-top:14px; font-size:13px;">
        <div style="display:flex; align-items:center;">
            <div style="width:10px; height:10px; background:#22c55e; 
                        border-radius:5px; margin-right:6px;"></div>
            수업
        </div>
        <div style="display:flex; align-items:center;">
            <div style="width:10px; height:10px; background:#eab308; 
                        border-radius:5px; margin-right:6px;"></div>
            학교 과제
        </div>
        <div style="display:flex; align-items:center;">
            <div style="width:10px; height:10px; background:#60a5fa;
                        border-radius:5px; margin-right:6px;"></div>
            개인 일정
        </div>
    </div>
    """, unsafe_allow_html=True)


# -------------------------------------------------
# Other Tabs
# -------------------------------------------------
elif st.session_state.active_tab == "과제":
    st.title("📘 과제")
    st.info("과제 목록이 여기에 표시됩니다.")

elif st.session_state.active_tab == "AI":
    st.title("✨ AI 추천")
    st.write("AI 추천 로직은 추후 연결됩니다.")

elif st.session_state.active_tab == "설정":
    st.title("⚙️ 설정")


# -------------------------------------------------
# 하단 네비게이션
# -------------------------------------------------
tabs = ["🏠\n홈", "✅\n과제", "✨\nAI", "⚙️\n설정"]

selected = st.radio(
    "bottom_nav",
    tabs,
    index=tabs.index(f"🏠\n{st.session_state.active_tab}") 
        if f"🏠\n{st.session_state.active_tab}" in tabs else 0,
    horizontal=True,
    label_visibility="collapsed",
    key="nav",
)

new_tab = selected.split("\n")[1]
if new_tab != st.session_state.active_tab:
    st.session_state.active_tab = new_tab
    st.rerun()
