import streamlit as st
import datetime

# -------------------------------------------------
# 1. 기본 페이지 설정
# -------------------------------------------------
st.set_page_config(page_title="AI Timetable", layout="centered")

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "홈"

# -------------------------------------------------
# 2. 전역 상태 초기화 (여기가 핵심 수정!)
# -------------------------------------------------
# timetables 가 없거나, 이전 버전(list)이라면 새 구조(dict)로 초기화
if (
    "timetables" not in st.session_state
    or not isinstance(st.session_state.timetables, dict)
):
    st.session_state.timetables = {"시간표 1": []}  # 각 시간표 이름: 일정 리스트
    st.session_state.current_tt = "시간표 1"

# current_tt 가 혹시 빠져 있거나, timetables 키에 없으면 안전하게 초기화
if "current_tt" not in st.session_state or \
   st.session_state.current_tt not in st.session_state.timetables:
    st.session_state.current_tt = list(st.session_state.timetables.keys())[0]

if "rename_mode" not in st.session_state:
    st.session_state.rename_mode = False

if "current_date" not in st.session_state:
    st.session_state.current_date = datetime.date(2025, 12, 1)

# -------------------------------------------------
# 3. CSS
# -------------------------------------------------
st.markdown("""
<style>

    .stApp {
        background-color:#f8f9fa;
        margin-bottom:80px;
    }

    /* 위쪽 공백 줄이기 */
    .main .block-container {
        padding-top:0.5rem !important;
        padding-bottom:4rem !important;
        max-width:100%;
    }

    /* selectbox 기본 화살표 숨기기 */
    select {
        -webkit-appearance:none !important;
        -moz-appearance:none !important;
        appearance:none !important;
        background-image:none !important;
        padding-right:0 !important;
    }

    /* 시간표 카드 */
    .timetable-wrapper {
        background:white;
        border-radius:15px;
        border:1px solid #e5e7eb;
        margin-top:0px;
        box-shadow:0 4px 6px rgba(0,0,0,0.02);
    }

    .timetable-header {
        display:grid;
        grid-template-columns:40px repeat(5, 1fr);
        background:#f9fafb;
        border-bottom:1px solid #e5e7eb;
        font-size:12px;
        font-weight:600;
        color:#6b7280;
        padding:8px 0;
        text-align:center;
    }

    .timetable-body {
        display:grid;
        grid-template-columns:40px repeat(5, 1fr);
        grid-template-rows:repeat(42, 10px);  /* 9~16시, 7시간 × 6칸 = 42 */
        position:relative;
    }

    .time-label {
        font-size:10px;
        color:#9ca3af;
        text-align:center;
        border-right:1px solid #f3f4f6;
        border-bottom:1px solid #f3f4f6;
        padding-top:2px;
    }

    .grid-bg-cell {
        border-right:1px solid #f3f4f6;
        border-bottom:1px solid #f3f4f6;
    }

    .event-item {
        margin:1px;
        padding:4px 6px;
        border-radius:6px;
        font-size:11px;
        overflow:hidden;
        z-index:10;
        box-shadow:0 1px 2px rgba(0,0,0,0.1);
        display:flex;
        flex-direction:column;
        justify-content:center;
    }

    .evt-class {
        background-color:#dcfce7;
        border-left:3px solid #22c55e;
    }

    .evt-task {
        background-color:#fef9c3;
        border-left:3px solid #eab308;
    }

    .evt-personal {
        background-color:#dbeafe;
        border-left:3px solid #3b82f6;
    }

    /* 하단 네비게이션 */
    div[data-testid="stRadio"] {
        position:fixed;
        bottom:0; left:0;
        width:100%;
        background:white;
        border-top:1px solid #e5e7eb;
        padding:6px 0;
        box-shadow:0 -2px 8px rgba(0,0,0,0.05);
        z-index:9999;
    }

    div[data-testid="stRadio"] > label {display:none !important;}
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display:flex;
        justify-content:space-around;
        width:100%;
    }
    div[data-testid="stRadio"] p {
        font-size:10px;
        margin:0;
        color:#9ca3af;
        text-align:center;
    }
    div[data-testid="stRadio"] label[data-checked="true"] p {
        color:#4f46e5 !important;
        font-weight:700;
    }
    div[data-testid="stRadio"] p span {
        font-size:20px;
        margin-bottom:2px;
    }

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 4. 시간표 렌더링 함수
# -------------------------------------------------
def render_timetable():
    data = st.session_state.timetables[st.session_state.current_tt]
    days = ["월", "화", "수", "목", "금"]
    day_idx = {d: i for i, d in enumerate(days)}

    html = '<div class="timetable-wrapper">'
    html += '<div class="timetable-header"><div></div>'
    for d in days:
        html += f"<div>{d}</div>"
    html += "</div>"

    html += '<div class="timetable-body">'

    # 배경 그리드
    for h in range(9, 17):
        base = (h - 9) * 6 + 1
        html += f'<div class="time-label" style="grid-row:{base}/span 6;">{h}</div>'
        for col in range(2, 7):
            html += f'<div class="grid-bg-cell" style="grid-column:{col}; grid-row:{base}/span 6;"></div>'

    # 일정 렌더링
    for item in data:
        col = day_idx[item["day"]] + 2
        sh, sm = map(int, item["start"].split(":"))
        eh, em = map(int, item["end"].split(":"))
        start = (sh - 9) * 60 + sm
        duration = (eh * 60 + em) - (sh * 60 + sm)

        row = start // 10 + 1
        span = max(1, duration // 10)  # 10분 단위

        cls = {
            "class": "evt-class",
            "task": "evt-task",
            "personal": "evt-personal"
        }.get(item.get("kind", "class"), "evt-class")

        sub = item.get("sub", "")

        html += f"""
        <div class="event-item {cls}" style="grid-column:{col}; grid-row:{row}/span {span};">
            <div class="evt-title">{item['title']}</div>
            <div class="evt-time">{sub}</div>
        </div>
        """

    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)

# -------------------------------------------------
# 5. 홈 탭
# -------------------------------------------------
if st.session_state.active_tab == "홈":

    c1, c2, c3 = st.columns([5, 1, 1])

    # 시간표 선택
    with c1:
        tt_names = list(st.session_state.timetables.keys())
        selected = st.selectbox(
            "",
            tt_names,
            index=tt_names.index(st.session_state.current_tt),
            label_visibility="collapsed",
        )
        if selected != st.session_state.current_tt:
            st.session_state.current_tt = selected
            st.rerun()

    # 이름 변경
    with c2:
        if st.button("✏️"):
            st.session_state.rename_mode = True

    # 새 시간표 추가 (빈 시간표)
    with c3:
        if st.button("➕"):
            new_name = f"시간표 {len(st.session_state.timetables) + 1}"
            st.session_state.timetables[new_name] = []   # 복제 X, 완전 빈 시간표
            st.session_state.current_tt = new_name
            st.session_state.rename_mode = False
            st.rerun()

    # 이름 변경 모달
    if st.session_state.rename_mode:
        with st.form("rename_form"):
            new_name = st.text_input("새 이름", st.session_state.current_tt)
            ok = st.form_submit_button("변경")
            if ok and new_name.strip():
                data = st.session_state.timetables.pop(st.session_state.current_tt)
                st.session_state.timetables[new_name] = data
                st.session_state.current_tt = new_name
                st.session_state.rename_mode = False
                st.rerun()

    # 날짜 이동
    colL, colM, colR = st.columns([1, 3, 1])

    with colL:
        if st.button("◀"):
            st.session_state.current_date -= datetime.timedelta(weeks=1)

    with colM:
        wk = st.session_state.current_date.isocalendar()[1] % 4 + 1
        st.markdown(
            f"<div style='text-align:center; font-size:17px; margin-top:-6px;'>"
            f"{st.session_state.current_date.year}년 "
            f"{st.session_state.current_date.month}월 {wk}주차"
            f"</div>",
            unsafe_allow_html=True,
        )

    with colR:
        if st.button("▶"):
            st.session_state.current_date += datetime.timedelta(weeks=1)

    # 시간표 (스크롤 영역)
    st.markdown("<div style='height:520px; overflow-y:auto;'>", unsafe_allow_html=True)
    render_timetable()
    st.markdown("</div>", unsafe_allow_html=True)

    # 카테고리 범례
    st.markdown("""
    <div style="display:flex; gap:18px; margin-top:10px; font-size:12px;">
        <div style="display:flex; align-items:center;">
            <div style="width:10px; height:10px; background:#22c55e; border-radius:5px; margin-right:6px;"></div>
            수업
        </div>
        <div style="display:flex; align-items:center;">
            <div style="width:10px; height:10px; background:#eab308; border-radius:5px; margin-right:6px;"></div>
            학교 과제
        </div>
        <div style="display:flex; align-items:center;">
            <div style="width:10px; height:10px; background:#60a5fa; border-radius:5px; margin-right:6px;"></div>
            개인 일정
        </div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# 6. (임시) 다른 탭 placeholder
# -------------------------------------------------
elif st.session_state.active_tab == "과제":
    st.title("📘 과제")
    st.info("과제 탭은 추후 구현 예정입니다.")

elif st.session_state.active_tab == "AI":
    st.title("✨ AI 추천")
    st.info("AI 추천 탭은 추후 구현 예정입니다.")

elif st.session_state.active_tab == "설정":
    st.title("⚙️ 설정")
    st.info("설정 탭은 추후 구현 예정입니다.")

# -------------------------------------------------
# 7. 하단 네비게이션
# -------------------------------------------------
tabs = ["🏠\n홈", "✅\n과제", "✨\nAI", "⚙️\n설정"]

selected_tab = st.radio(
    "bottom_nav",
    tabs,
    horizontal=True,
    label_visibility="collapsed",
    key="nav",
)

new_tab = selected_tab.split("\n")[1]
if new_tab != st.session_state.active_tab:
    st.session_state.active_tab = new_tab
    st.rerun()
