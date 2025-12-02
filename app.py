import streamlit as st
from datetime import date, timedelta

# -------------------------------------------------
# 1. 페이지 설정 및 상태 초기화
# -------------------------------------------------
st.set_page_config(page_title="AI Timetable", layout="centered")

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "홈"  # 기본 탭

DEFAULT_TIMETABLE = [
    {"day": "월", "start": "09:00", "end": "10:00", "title": "데이터구조", "kind": "class"},
    {"day": "월", "start": "10:00", "end": "11:00", "title": "데이터구조 과제", "kind": "task", "sub": "연결리스트 구현"},
    {"day": "월", "start": "11:00", "end": "12:00", "title": "알고리즘", "kind": "class"},
    {"day": "월", "start": "13:00", "end": "13:50", "title": "알고리즘 숙제", "kind": "task", "sub": "50분"},

    {"day": "화", "start": "09:00", "end": "10:00", "title": "운영체제", "kind": "class"},
    {"day": "화", "start": "14:00", "end": "15:00", "title": "데이터베이스", "kind": "class"},

    {"day": "수", "start": "10:00", "end": "11:00", "title": "네트워크", "kind": "class"},
    {"day": "수", "start": "18:00", "end": "19:00", "title": "스터디 준비", "kind": "personal"},

    {"day": "목", "start": "09:00", "end": "10:00", "title": "소프트웨어공학", "kind": "class"},

    {"day": "금", "start": "09:00", "end": "10:00", "title": "데이터구조 과제", "kind": "task", "sub": "스택/큐 구현"},
    {"day": "금", "start": "13:00", "end": "14:00", "title": "인공지능", "kind": "class"},
    {"day": "금", "start": "20:00", "end": "21:00", "title": "운동", "kind": "personal"},
]

if "timetables" not in st.session_state:
    st.session_state.timetables = [
        {"name": "시간표 1", "data": DEFAULT_TIMETABLE.copy()},
    ]
    st.session_state.active_timetable = 0

if "editing_name" not in st.session_state:
    st.session_state.editing_name = False

if "name_input" not in st.session_state:
    st.session_state.name_input = st.session_state.timetables[0]["name"]

if "week_offset" not in st.session_state:
    st.session_state.week_offset = 0

START_HOUR = 9
END_HOUR = 22
TOTAL_ROWS = (END_HOUR - START_HOUR + 1) * 6

# -------------------------------------------------
# 2. CSS 스타일 (하단 탭 & 시간표 완벽 구현)
# -------------------------------------------------
st.markdown(f"""
<style>
    /* 전체 배경 및 여백 설정 */
    .stApp {{
        background-color: #f8f9fa;
        margin-bottom: 80px; /* 하단 탭 공간 확보 */
    }}
    .main .block-container {{
        padding-top: 1rem;
        padding-bottom: 5rem;
        max-width: 100%;
    }}

    /* 하단 탭 네비게이션 */
    div[data-testid="stRadio"] {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: white;
        border-top: 1px solid #e5e7eb;
        z-index: 9999;
        padding: 8px 0 12px 0;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
    }}
    div[data-testid="stRadio"] > label {{
        display: none !important;
    }}
    div[data-testid="stRadio"] > div[role="radiogroup"] {{
        display: flex;
        justify-content: space-around;
        width: 100%;
    }}
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {{
        flex: 1;
        background: white !important;
        border: none;
        margin: 0;
        padding: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        cursor: pointer;
    }}

    div[data-testid="stRadio"] p {{
        font-size: 10px;
        margin: 0;
        line-height: 1.2;
        text-align: center;
        color: #9ca3af;
    }}

    div[data-testid="stRadio"] label[data-checked="true"] p {{
        color: #4f46e5 !important;
        font-weight: 700;
    }}

    div[data-testid="stRadio"] p span {{
        display: block;
        font-size: 20px;
        margin-bottom: 2px;
    }}

    /* 시간표 그리드 디자인 */
    .timetable-wrapper {{
        background: white;
        border-radius: 15px;
        border: 1px solid #e5e7eb;
        overflow: hidden;
        margin-top: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }}
    .timetable-header {{
        display: grid;
        grid-template-columns: 60px repeat(5, 1fr);
        background: #f9fafb;
        border-bottom: 1px solid #e5e7eb;
        text-align: center;
        font-size: 12px;
        font-weight: 600;
        color: #6b7280;
        padding: 8px 0;
    }}
    .timetable-scroll {{
        max-height: 540px;
        overflow-y: auto;
    }}
    .timetable-body {{
        display: grid;
        grid-template-columns: 60px repeat(5, 1fr);
        grid-template-rows: repeat({TOTAL_ROWS}, 10px);
        position: relative;
        min-width: 100%;
    }}
    .time-label {{
        font-size: 10px;
        color: #9ca3af;
        text-align: center;
        border-right: 1px solid #f3f4f6;
        border-bottom: 1px solid #f3f4f6;
        display: flex;
        align-items: start;
        justify-content: center;
        padding-top: 2px;
        background: white;
    }}
    .grid-bg-cell {{
        border-right: 1px solid #f3f4f6;
        border-bottom: 1px solid #f3f4f6;
    }}

    .event-item {{
        margin: 1px;
        padding: 4px 6px;
        border-radius: 6px;
        font-size: 11px;
        line-height: 1.2;
        display: flex;
        flex-direction: column;
        justify-content: center;
        overflow: hidden;
        z-index: 10;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }}
    .evt-class {{
        background-color: #dcfce7;
        border-left: 3px solid #22c55e;
        color: #14532d;
    }}
    .evt-task {{
        background-color: #fef9c3;
        border-left: 3px solid #eab308;
        color: #854d0e;
    }}
    .evt-personal {{
        background-color: #f3e8ff;
        border-left: 3px solid #a855f7;
        color: #6b21a8;
    }}
    .evt-title {{ font-weight: 700; margin-bottom: 2px; }}
    .evt-time {{ font-size: 9px; opacity: 0.8; }}

    .legend {{
        display: flex;
        justify-content: flex-start;
        gap: 12px;
        margin-top: 8px;
        font-size: 12px;
        color: #6b7280;
    }}
    .legend-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 4px;
    }}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 3. 데이터 및 로직
# -------------------------------------------------

def add_timetable():
    new_index = len(st.session_state.timetables) + 1
    new_name = f"시간표 {new_index}"
    st.session_state.timetables.append({"name": new_name, "data": DEFAULT_TIMETABLE.copy()})
    st.session_state.active_timetable = len(st.session_state.timetables) - 1
    st.session_state.editing_name = False
    st.session_state.name_input = new_name
    for i in range(len(st.session_state.timetables)):
        st.session_state[f"ttoggle_{i}"] = i == st.session_state.active_timetable


def get_week_label(base_date: date, offset: int) -> str:
    target_date = base_date + timedelta(weeks=offset)
    week_of_month = ((target_date.day - 1) // 7) + 1
    return f"{target_date.year}년 {target_date.month}월 {week_of_month}주차"


def render_timetable(data):
    days = ["월", "화", "수", "목", "금"]
    day_map = {d: i for i, d in enumerate(days)}

    html = '<div class="timetable-wrapper">'

    html += '<div class="timetable-header"><div></div>'
    for d in days:
        html += f'<div>{d}</div>'
    html += '</div>'

    html += '<div class="timetable-scroll">'
    html += '<div class="timetable-body">'

    for h in range(START_HOUR, END_HOUR + 1):
        row_start = (h - START_HOUR) * 6 + 1
        html += f'<div class="time-label" style="grid-column: 1; grid-row: {row_start} / span 6;">{h}</div>'
        for col in range(2, 7):
            html += f'<div class="grid-bg-cell" style="grid-column: {col}; grid-row: {row_start} / span 6;"></div>'

    cls_map = {"class": "evt-class", "task": "evt-task", "personal": "evt-personal"}

    for item in data:
        d_idx = day_map.get(item["day"])
        if d_idx is None:
            continue

        sh, sm = map(int, item["start"].split(":"))
        eh, em = map(int, item["end"].split(":"))

        start_min = (sh - START_HOUR) * 60 + sm
        duration_min = (eh * 60 + em) - (sh * 60 + sm)

        g_row = int(start_min / 10) + 1
        g_span = int(duration_min / 10)
        g_col = d_idx + 2

        cls = cls_map.get(item["kind"], "evt-class")
        detail_lines = [f"<div class='evt-time'>{item['start']} - {item['end']}</div>"]
        if "sub" in item:
            detail_lines.append(f"<div class='evt-time'>{item['sub']}</div>")
        detail_html = "".join(detail_lines)

        html += f"""
        <div class="event-item {cls}" style="grid-column: {g_col}; grid-row: {g_row} / span {g_span};">
            <div class="evt-title">{item['title']}</div>
            {detail_html}
        </div>
        """

    html += '</div>'
    html += '</div>'
    html += '</div>'

    st.markdown(html, unsafe_allow_html=True)

    st.markdown(
        """
        <div class="legend">
            <span><span class="legend-dot" style="background:#22c55e;"></span>수업</span>
            <span><span class="legend-dot" style="background:#eab308;"></span>학교 과제</span>
            <span><span class="legend-dot" style="background:#a855f7;"></span>개인 일정</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------
# 4. 메인 화면 구성
# -------------------------------------------------
tab = st.session_state.active_tab

if tab == "홈":
    active_idx = st.session_state.active_timetable
    active_name = st.session_state.timetables[active_idx]["name"]

    header = st.container()
    name_col, edit_col, add_col = header.columns([6, 1, 1])

    if st.session_state.editing_name:
        st.session_state.name_input = name_col.text_input(
            "시간표 이름",
            value=st.session_state.name_input,
            label_visibility="collapsed",
            key="timetable_name_input",
        )
        if edit_col.button("💾", help="이름 저장"):
            new_name = st.session_state.name_input.strip() or active_name
            st.session_state.timetables[active_idx]["name"] = new_name
            st.session_state.editing_name = False
        if add_col.button("↩️", help="취소"):
            st.session_state.editing_name = False
            st.session_state.name_input = active_name
    else:
        name_col.markdown(f"### 시간표 {active_idx + 1} : {active_name}")
        if edit_col.button("✏️", help="이름 변경"):
            st.session_state.editing_name = True
            st.session_state.name_input = active_name
        if add_col.button("➕", help="시간표 추가"):
            add_timetable()
            st.rerun()

    st.divider()

    st.markdown("##### 내 시간표 선택")
    selection_area = st.container()
    with selection_area:
        for idx, table in enumerate(st.session_state.timetables):
            col1, col2 = st.columns([6, 1])
            col1.write(table["name"])
            default_value = st.session_state.get(f"ttoggle_{idx}", idx == st.session_state.active_timetable)
            toggled = col2.toggle("활성화", value=default_value, key=f"ttoggle_{idx}")
            if toggled and st.session_state.active_timetable != idx:
                st.session_state.active_timetable = idx
                for j in range(len(st.session_state.timetables)):
                    st.session_state[f"ttoggle_{j}"] = j == idx
                st.rerun()
            elif not toggled and idx == st.session_state.active_timetable:
                st.session_state[f"ttoggle_{idx}"] = True

    st.divider()

    base_date = date(2025, 12, 1)
    week_col_left, week_col_center, week_col_right = st.columns([1, 3, 1])
    if week_col_left.button("⬅️", help="이전 주"):
        st.session_state.week_offset -= 1
    week_col_center.markdown(
        f"### {get_week_label(base_date, st.session_state.week_offset)}",
        unsafe_allow_html=True,
    )
    if week_col_right.button("➡️", help="다음 주"):
        st.session_state.week_offset += 1

    c1, c2, c3 = st.columns(3)
    c1.button("일간", use_container_width=True)
    c2.button("주간", use_container_width=True, type="primary")
    c3.button("월간", use_container_width=True)

    render_timetable(st.session_state.timetables[st.session_state.active_timetable]["data"])

elif tab == "과제":
    st.title("✅ 과제 관리")
    st.info("등록된 과제 목록이 여기에 표시됩니다.")

elif tab == "AI":
    st.title("✨ AI 일정 추천")
    st.success("AI가 공강 시간을 분석하고 있습니다...")

elif tab == "설정":
    st.title("⚙️ 설정")
    st.write("계정 및 알림 설정")

# -------------------------------------------------
# 5. 하단 탭 네비게이션 (고정)
# -------------------------------------------------
tabs = ["🏠\n홈", "✅\n과제", "✨\nAI", "⚙️\n설정"]

selected = st.radio(
    "bottom_nav",
    tabs,
    index=tabs.index(f"🏠\n{st.session_state.active_tab}") if f"🏠\n{st.session_state.active_tab}" in tabs else 0,
    horizontal=True,
    label_visibility="collapsed",
    key="nav",
)

new_tab = selected.split("\n")[1]
if new_tab != st.session_state.active_tab:
    st.session_state.active_tab = new_tab
    st.rerun()
