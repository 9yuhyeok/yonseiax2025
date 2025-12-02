import streamlit as st
from streamlit_option_menu import option_menu
import datetime

# -------------------------------------------------
# 1. 기본 페이지 설정
# -------------------------------------------------
st.set_page_config(page_title="AI Timetable", layout="centered")

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "시간표"

# -------------------------------------------------
# 2. 전역 상태 초기화
# -------------------------------------------------
if (
    "timetables" not in st.session_state
    or not isinstance(st.session_state.timetables, dict)
):
    st.session_state.timetables = {"시간표 1": []}
    st.session_state.current_tt = "시간표 1"

if "current_tt" not in st.session_state or \
   st.session_state.current_tt not in st.session_state.timetables:
    st.session_state.current_tt = list(st.session_state.timetables.keys())[0]

if "rename_mode" not in st.session_state:
    st.session_state.rename_mode = False

if "current_date" not in st.session_state:
    st.session_state.current_date = datetime.date(2025, 12, 1)


# -------------------------------------------------
# 3. 탭 메뉴 (요청한 그대로)
# -------------------------------------------------
selected = option_menu(
    None,
    ["시간표", "과제", "성적", "설정"],
    icons=["calendar-week", "check2-square", "bar-chart-line", "gear"],
    menu_icon=None,
    default_index=["시간표","과제","성적","설정"].index(st.session_state.active_tab),
    orientation="horizontal",
)

if selected != st.session_state.active_tab:
    st.session_state.active_tab = selected
    st.rerun()


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
        span = max(1, duration // 10)

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
# 5. 화면별 렌더링
# -------------------------------------------------
if st.session_state.active_tab == "시간표":
    st.markdown("### 시간표")

    # UI 생략 — 기존 코드 그대로 유지
    c1, c2, c3 = st.columns([5, 1, 1])

    with c1:
        tt_names = list(st.session_state.timetables.keys())
        selected_tt = st.selectbox(
            "",
            tt_names,
            index=tt_names.index(st.session_state.current_tt),
            label_visibility="collapsed",
        )
        if selected_tt != st.session_state.current_tt:
            st.session_state.current_tt = selected_tt
            st.rerun()

    with c2:
        if st.button("✏️"):
            st.session_state.rename_mode = True

    with c3:
        if st.button("➕"):
            new_name = f"시간표 {len(st.session_state.timetables) + 1}"
            st.session_state.timetables[new_name] = []
            st.session_state.current_tt = new_name
            st.session_state.rename_mode = False
            st.rerun()

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

    # 주차 이동 버튼
    colL, colM, colR = st.columns([1, 3, 1])
    with colL:
        if st.button("◀"):
            st.session_state.current_date -= datetime.timedelta(weeks=1)
    with colR:
        if st.button("▶"):
            st.session_state.current_date += datetime.timedelta(weeks=1)

    # 시간표 표시 (스크롤 영역)
    st.markdown("<div style='height:520px; overflow-y:auto;'>", unsafe_allow_html=True)
    render_timetable()
    st.markdown("</div>", unsafe_allow_html=True)


elif st.session_state.active_tab == "과제":
    st.title("📘 과제")
    st.info("과제 기능 개발 예정")

elif st.session_state.active_tab == "성적":
    st.title("📊 성적")
    st.info("성적 기능 개발 예정")

elif st.session_state.active_tab == "설정":
    st.title("⚙️ 설정")
    st.info("설정 기능 개발 예정")
