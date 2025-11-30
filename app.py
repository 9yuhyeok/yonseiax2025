import streamlit as st
from datetime import datetime, date

st.set_page_config(page_title="시간표", layout="centered")

# ------------------ 데이터 구조 ------------------
class TimeSlot:
    def __init__(self, day: str, start: str, end: str, title: str, kind: str = "class"):
        self.day = day          # '월' ~ '일'
        self.start = start      # 'HH:MM'
        self.end = end          # 'HH:MM'
        self.title = title
        self.kind = kind        # 'class' | 'task' | 'personal'


def time_to_minutes(t: str) -> int:
    h, m = map(int, t.split(":"))
    return h * 60 + m


# 테스트용 기본 시간표 (질문에서 준 패턴 그대로)
DEFAULT_SLOTS = [
    TimeSlot('월', '09:00', '10:00', '데이터구조', 'class'),
    TimeSlot('월', '10:00', '11:00', '데이터구조 과제 - 연결 리스트 구현', 'task'),
    TimeSlot('월', '11:00', '12:00', '알고리즘', 'class'),
    TimeSlot('월', '13:00', '14:00', '알고리즘 숙제 - 정렬 알고리즘 분석', 'task'),
    TimeSlot('화', '09:00', '10:00', '운영체제', 'class'),
    TimeSlot('화', '14:00', '15:00', '데이터베이스', 'class'),
    TimeSlot('수', '10:00', '11:00', '네트워크', 'class'),
    TimeSlot('목', '09:00', '10:00', '소프트웨어공학', 'class'),
    TimeSlot('금', '13:00', '14:00', '인공지능', 'class'),
]

if "slots" not in st.session_state:
    st.session_state.slots = DEFAULT_SLOTS

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "home"

slots = st.session_state.slots
active_tab = st.session_state.active_tab

# ------------------ 공통 스타일 ------------------
st.markdown(
    """
    <style>
    body { background:#f3f4fb; }
    .main { padding-bottom:80px; }  /* 하단 탭 자리 확보 */

    .bottom-nav {
        position:fixed;
        left:0;
        right:0;
        bottom:0;
        height:60px;
        background:white;
        border-top:1px solid #e5e7eb;
        display:flex;
        justify-content:space-around;
        align-items:center;
        font-family:-apple-system,BlinkMacSystemFont,"Helvetica Neue",sans-serif;
        z-index:100;
    }
    .bottom-nav-item {
        text-align:center;
        font-size:11px;
        color:#6b7280;
    }
    .bottom-nav-icon {
        font-size:20px;
        margin-bottom:2px;
    }
    .bottom-nav-active {
        color:#4f46e5;
        font-weight:600;
    }

    /* Streamlit 버튼을 투명하게 해서 클릭만 맡기고, 실제 아이콘/텍스트는 HTML로 표현 */
    .nav-btn > button {
        background:transparent !important;
        border:none !important;
        color:transparent !important;
        height:60px;
        width:100%;
        cursor:pointer;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------ 뷰 함수들 ------------------
def render_weekly_view(slots):
    days = ['월', '화', '수', '목', '금']
    start_hour = 9
    end_hour = 16          # 9시 ~ 16시만
    num_rows = end_hour - start_hour + 1  # 9,10,11,12,13,14,15,16 = 8줄

    html = """
    <style>
    .week-wrapper {
        background:#f5f5fb;
        padding:16px 12px 24px 12px;
        border-radius:24px;
        box-shadow:0 8px 24px rgba(15,23,42,0.08);
        font-family:-apple-system,BlinkMacSystemFont,"Helvetica Neue",sans-serif;
    }
    .week-header-row {
        display:grid;
        grid-template-columns:60px repeat(5,1fr);
        margin-bottom:8px;
        font-size:12px;
        color:#9ca3af;
        text-align:center;
    }
    .week-body {
        position:relative;
        display:grid;
        grid-template-columns:60px repeat(5,1fr);
        grid-template-rows:repeat(""" + str(num_rows) + """,72px);
        background:white;
        border-radius:18px;
        overflow:hidden;
        border:1px solid #e5e7eb;
    }
    .hour-label {
        font-size:11px;
        color:#9ca3af;
        padding-top:8px;
        text-align:center;
        border-bottom:1px solid #f3f4f6;
        background:#fcfcff;
    }
    .grid-cell {
        border-bottom:1px solid #f3f4f6;
        border-left:1px solid #f9fafb;
    }
    .event {
        font-size:11px;
        border-radius:10px;
        padding:6px 8px;
        margin:3px 6px;
        overflow:hidden;
        line-height:1.3;
        box-shadow:0 1px 3px rgba(15,23,42,0.12);
        display:flex;
        align-items:flex-start;
    }
    .event.class {
        background:#e7f7eb;
        border:1px solid #bbf7d0;
        color:#14532d;
    }
    .event.task {
        background:#fff7d1;
        border:1px solid #fde68a;
        color:#854d0e;
    }
    .event.personal {
        background:#fce7f3;
        border:1px solid #f9a8d4;
        color:#9d174d;
    }
    .legend {
        margin-top:10px;
        font-size:11px;
        color:#6b7280;
        display:flex;
        gap:16px;
        align-items:center;
    }
    .dot {
        width:10px;height:10px;border-radius:999px;display:inline-block;margin-right:4px;
    }
    .dot.class {background:#86efac;}
    .dot.task {background:#fde68a;}
    .dot.personal {background:#f9a8d4;}
    </style>
    """

    html += "<div class='week-wrapper'>"

    # 헤더
    html += "<div class='week-header-row'>"
    html += "<div></div>"
    for d in days:
        html += f"<div style='font-weight:500;'>{d}</div>"
    html += "</div>"

    # 그리드 베이스
    html += "<div class='week-body'>"
    for row, hour in enumerate(range(start_hour, end_hour + 1), start=1):
        html += (
            f"<div class='hour-label' style='grid-column:1;grid-row:{row};'>{hour}</div>"
        )
        for col in range(2, 7):
            html += (
                f"<div class='grid-cell' style='grid-column:{col};grid-row:{row};'></div>"
            )

    # 블록 배치
    day_index = {d: i for i, d in enumerate(days)}  # '월'->0 ...
    for ev in slots:
        if ev.day not in day_index:
            continue
        col = day_index[ev.day] + 2  # 1은 시간축
        start_min = time_to_minutes(ev.start)
        end_min = time_to_minutes(ev.end)
        base_min = start_hour * 60
        # 9시 이전 / 16시 이후는 잘라냄
        if end_min <= base_min or start_min >= (end_hour + 1) * 60:
            continue
        start_min = max(start_min, base_min)
        end_min = min(end_min, (end_hour + 1) * 60)

        start_slot = int((start_min - base_min) / 60) + 1
        span = max(1, int((end_min - start_min) / 60))

        kind = ev.kind if ev.kind in ["class", "task", "personal"] else "class"

        html += f"""
        <div class="event {kind}"
             style="grid-column:{col};
                    grid-row:{start_slot}/span {span};">
            {ev.title}
        </div>
        """

    html += "</div>"  # week-body

    # 범례
    html += """
    <div class="legend">
      <span><span class="dot class"></span>수업</span>
      <span><span class="dot task"></span>학교 과제</span>
      <span><span class="dot personal"></span>개인 일정</span>
    </div>
    """

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_monthly_view(slots, year=2025, month=11):
    days_kr = ["월", "화", "수", "목", "금", "토", "일"]
    first_day = date(year, month, 1)
    start_weekday = first_day.weekday()  # 월=0
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    num_days = (next_month - first_day).days

    titles_by_day = {}
    for ev in slots:
        titles_by_day.setdefault(ev.day, [])
        if ev.title not in titles_by_day[ev.day]:
            titles_by_day[ev.day].append(ev.title)

    html = """
    <style>
    .month-wrapper{
        background:#f5f5fb;
        padding:16px 12px 24px 12px;
        border-radius:24px;
        box-shadow:0 8px 24px rgba(15,23,42,0.08);
        font-family:-apple-system,BlinkMacSystemFont,"Helvetica Neue",sans-serif;
    }
    .month-grid{
        display:grid;
        grid-template-columns:repeat(7,1fr);
        grid-auto-rows:100px;
        background:white;
        border-radius:18px;
        overflow:hidden;
        border:1px solid #e5e7eb;
        font-size:11px;
    }
    .month-header{
        background:#f9fafb;
        padding:6px 0;
        text-align:center;
        font-size:11px;
        font-weight:500;
        color:#6b7280;
        border-bottom:1px solid #e5e7eb;
    }
    .day-cell{
        border-bottom:1px solid #f3f4f6;
        border-right:1px solid #f3f4f6;
        padding:6px 6px 4px 6px;
        position:relative;
    }
    .day-num{
        font-size:11px;
        color:#9ca3af;
        margin-bottom:4px;
    }
    .month-tag{
        display:block;
        border-radius:8px;
        background:#e7f7eb;
        color:#166534;
        padding:3px 5px;
        margin-bottom:2px;
        overflow:hidden;
        white-space:nowrap;
        text-overflow:ellipsis;
    }
    </style>
    <div class="month-wrapper">
    """

    html += "<div class='month-grid'>"
    for d in ["월", "화", "수", "목", "금", "토", "일"]:
        html += f"<div class='month-header'>{d}</div>"

    for _ in range(start_weekday):
        html += "<div class='day-cell'></div>"

    for d in range(1, num_days + 1):
        weekday = (start_weekday + d - 1) % 7
        day_name = days_kr[weekday]
        html += "<div class='day-cell'>"
        html += f"<div class='day-num'>{d}</div>"
        titles = titles_by_day.get(day_name, [])
        for t in titles:
            html += f"<span class='month-tag'>{t}</span>"
        html += "</div>"

    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)


# ------------------ 메인 컨텐츠 ------------------
# 상단 헤더는 홈 탭에서만 (이미지처럼)
if active_tab == "home":
    col_left, col_center, col_right = st.columns([1, 1.4, 1])
    with col_left:
        st.markdown("### 시간표 1")
    with col_center:
        st.markdown(
            "<div style='text-align:center;font-weight:600;margin-top:4px;'>2025년 11월 5주차</div>",
            unsafe_allow_html=True,
        )

    view_mode = st.radio(
        "view_mode",
        options=["주간", "월간"],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )

    if view_mode == "주간":
        render_weekly_view(slots)
    else:
        render_monthly_view(slots)

elif active_tab == "task":
    st.subheader("과제")
    st.write("여기에 과제 관리 화면 넣으면 됨 (지금은 자리만 잡아둔 상태).")

elif active_tab == "ai":
    st.subheader("AI")
    st.write("여기에 AI 추천 화면 넣으면 됨 (지금은 자리만 잡아둔 상태).")

elif active_tab == "settings":
    st.subheader("설정")
    st.write("여기에 설정 화면 넣으면 됨.")

# ------------------ 하단 탭 네비게이션 ------------------
# 버튼은 클릭 이벤트만 담당, 실제 모양은 아래 HTML이 담당
nav_container = st.container()
with nav_container:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("home", key="nav_home", help="홈", type="secondary"):
            st.session_state.active_tab = "home"
    with c2:
        if st.button("task", key="nav_task", help="과제", type="secondary"):
            st.session_state.active_tab = "task"
    with c3:
        if st.button("ai", key="nav_ai", help="AI", type="secondary"):
            st.session_state.active_tab = "ai"
    with c4:
        if st.button("settings", key="nav_settings", help="설정", type="secondary"):
            st.session_state.active_tab = "settings"

# 실제 하단 바 UI (아이콘/텍스트)
st.markdown(
    f"""
    <div class="bottom-nav">
      <div class="bottom-nav-item {'bottom-nav-active' if active_tab=='home' else ''}">
        <div class="bottom-nav-icon">🏠</div>
        홈
      </div>
      <div class="bottom-nav-item {'bottom-nav-active' if active_tab=='task' else ''}">
        <div class="bottom-nav-icon">✅</div>
        과제
      </div>
      <div class="bottom-nav-item {'bottom-nav-active' if active_tab=='ai' else ''}">
        <div class="bottom-nav-icon">✨</div>
        AI
      </div>
      <div class="bottom-nav-item {'bottom-nav-active' if active_tab=='settings' else ''}">
        <div class="bottom-nav-icon">⚙️</div>
        설정
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
