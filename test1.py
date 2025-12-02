import streamlit as st
import datetime

# -------------------------------------------------
# 기본 설정
# -------------------------------------------------
st.set_page_config(page_title="AI Timetable", layout="wide")

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "시간표"

# -------------------------------------------------
# CSS (탭 버튼 + 시간표 공백 제거)
# -------------------------------------------------
st.markdown("""
<style>

.stApp {
    background-color: #f7f8fa;
}

/* ----- 상단 탭 버튼 스타일 ----- */
.navbar {
    display: flex;
    justify-content: space-around;
    background: #f1f2f6;
    padding: 14px 0;
    border-radius: 12px;
    margin-bottom: 5px;
}

.nav-btn {
    padding: 10px 20px;
    border-radius: 10px;
    cursor: pointer;
    font-weight: 600;
    font-size: 17px;
    color: #555;
    display: flex;
    align-items: center;
    gap: 6px;
}

.nav-btn-active {
    background: #ea5a4f;
    color: white !important;
}

/* 날짜 아래 공백 제거 */
.no-space {
    margin-top: -25px !important;
}

/* 시간표 래퍼 */
.timetable-wrapper {
    margin-top: 10px;
}

.timetable-header {
    display: grid;
    grid-template-columns: 40px repeat(5, 1fr);
    background: #f9fafb;
    text-align: center;
    font-weight: 600;
    padding: 8px 0;
    border-radius: 12px 12px 0 0;
    font-size: 14px;
    color: #555;
}

.timetable-body {
    display: grid;
    grid-template-columns: 40px repeat(5, 1fr);
    grid-template-rows: repeat(42, 12px);
    border: 1px solid #eee;
    border-top: none;
    background: white;
    border-radius: 0 0 12px 12px;
}

.time-label {
    text-align: center;
    font-size: 11px;
    padding-top: 2px;
    color: #999;
}

.grid-bg-cell {
    border-bottom: 1px solid #f1f1f1;
    border-right: 1px solid #f1f1f1;
}

/* 이벤트 */
.event-item {
    position: relative;
    font-size: 11px;
    padding: 2px 4px;
    border-radius: 6px;
    margin: 1px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.evt-class {
    background: #ddfbe0;
    border-left: 3px solid #28a745;
}

.evt-task {
    background: #fff2b3;
    border-left: 3px solid #f5c518;
}

.evt-title {
    font-weight: 600;
}

.evt-time {
    font-size: 9px;
    opacity: 0.7;
}

</style>
""", unsafe_allow_html=True)



# -------------------------------------------------
# 시간표 데이터 샘플
# -------------------------------------------------
default_timetable = [
    {"day": "월", "start": "09:00", "end": "10:00", "title": "데이터구조", "kind": "class"},
    {"day": "월", "start": "10:00", "end": "11:00", "title": "데이터구조 과제", "kind": "task", "sub": "연결리스트"},
]

if "timetables" not in st.session_state:
    st.session_state.timetables = {"시간표 1": default_timetable.copy()}

if "current_tt" not in st.session_state:
    st.session_state.current_tt = "시간표 1"

if "current_date" not in st.session_state:
    st.session_state.current_date = datetime.date(2025, 12, 1)


# -------------------------------------------------
# 시간표 렌더링 함수
# -------------------------------------------------
def render_timetable(tt_data):
    days = ["월", "화", "수", "목", "금"]
    day_index = {d: i for i, d in enumerate(days)}

    html = '<div class="timetable-wrapper">'
    html += '<div class="timetable-header"><div></div>'
    for d in days:
        html += f"<div>{d}</div>"
    html += "</div>"

    html += '<div class="timetable-body">'

    for h in range(9, 17):
        row = (h - 9) * 6 + 1
        html += f'<div class="time-label" style="grid-column:1; grid-row:{row}/span 6;">{h}</div>'
        for col in range(2, 7):
            html += f'<div class="grid-bg-cell" style="grid-column:{col}; grid-row:{row}/span 6;"></div>'

    for item in tt_data:
        d = day_index[item["day"]]
        sh, sm = map(int, item["start"].split(":"))
        eh, em = map(int, item["end"].split(":"))

        start = (sh - 9) * 60 + sm
        duration = (eh * 60 + em) - (sh * 60 + sm)

        g_row = start // 10 + 1
        g_span = duration // 10
        g_col = d + 2

        kind = "evt-class" if item["kind"] == "class" else "evt-task"
        sub = item.get("sub", "")

        html += f"""
        <div class="event-item {kind}" style="grid-column:{g_col}; grid-row:{g_row}/span {g_span};">
            <div class="evt-title">{item['title']}</div>
            <div class="evt-time">{sub}</div>
        </div>
        """

    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)



# -------------------------------------------------
# 네비게이션 바 (커스텀 버튼)
# -------------------------------------------------
tabs = ["시간표", "과제", "성적", "설정"]
icons = ["📅", "☑️", "📊", "⚙️"]

nav_html = '<div class="navbar">'
for name, icon in zip(tabs, icons):
    cls = "nav-btn nav-btn-active" if st.session_state.active_tab == name else "nav-btn"
    nav_html += f"""
    <div class="{cls}" onclick="fetch('/?nav={name}')">{icon} {name}</div>
    """
nav_html += "</div>"

st.markdown(nav_html, unsafe_allow_html=True)

# JS (Streamlit 세션 업데이트)
st.markdown("""
<script>
const url = new URL(window.location.href);
window.onclick = (e) => {
    if(e.target.innerText.includes("시간표")){
        window.location.href = "/?nav=시간표";
    } else if(e.target.innerText.includes("과제")){
        window.location.href = "/?nav=과제";
    } else if(e.target.innerText.includes("성적")){
        window.location.href = "/?nav=성적";
    } else if(e.target.innerText.includes("설정")){
        window.location.href = "/?nav=설정";
    }
}
</script>
""", unsafe_allow_html=True)

nav = st.query_params.get("nav")
if nav:
    st.session_state.active_tab = nav


# -------------------------------------------------
# 실제 페이지
# -------------------------------------------------
if st.session_state.active_tab == "시간표":

    tt_name = st.session_state.current_tt
    timetable = st.session_state.timetables[tt_name]

    # 상단: 시간표 선택 / 이름 변경 / 추가
    col1, col2, col3 = st.columns([5,1,1])

    with col1:
        new_tt = st.selectbox(
            "",
            list(st.session_state.timetables.keys()),
            index=list(st.session_state.timetables.keys()).index(tt_name)
        )
        if new_tt != tt_name:
            st.session_state.current_tt = new_tt
            st.rerun()

    with col2:
        if st.button("✏️"):
            new_name = st.text_input("새 이름", tt_name)
            if new_name:
                st.session_state.timetables[new_name] = st.session_state.timetables.pop(tt_name)
                st.session_state.current_tt = new_name
                st.rerun()

    with col3:
        if st.button("➕"):
            n = len(st.session_state.timetables) + 1
            st.session_state.timetables[f"시간표 {n}"] = []
            st.session_state.current_tt = f"시간표 {n}"
            st.rerun()

    # 날짜 네비게이터
    colL, colM, colR = st.columns([1,3,1])

    with colL:
        if st.button("◀"):
            st.session_state.current_date -= datetime.timedelta(weeks=1)

    with colM:
        week = st.session_state.current_date.isocalendar()[1] % 4 + 1
        st.markdown(f"<h4 style='text-align:center;'>{st.session_state.current_date.year}년 {st.session_state.current_date.month}월 {week}주차</h4>", unsafe_allow_html=True)

    with colR:
        if st.button("▶"):
            st.session_state.current_date += datetime.timedelta(weeks=1)

    # 날짜 바로 아래 공백 제거
    st.markdown("<div class='no-space'></div>", unsafe_allow_html=True)

    # 시간표 출력
    render_timetable(timetable)


elif st.session_state.active_tab == "과제":
    st.title("📝 과제")

elif st.session_state.active_tab == "성적":
    st.title("📊 성적 분석")

elif st.session_state.active_tab == "설정":
    st.title("⚙️ 설정")
