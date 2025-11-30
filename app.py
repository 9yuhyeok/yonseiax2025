import streamlit as st
from datetime import date, datetime

# -------------------------------------------------
# 기본 설정
# -------------------------------------------------
st.set_page_config(page_title="AI Timetable", layout="centered")

# -------------------------------------------------
# 유틸
# -------------------------------------------------
def time_to_minutes(t: str) -> int:
    h, m = map(int, t.split(":"))
    return h * 60 + m


def time_overlaps(s1, e1, s2, e2) -> bool:
    s1, e1, s2, e2 = map(time_to_minutes, [s1, e1, s2, e2])
    return s1 < e2 and e1 > s2


# -------------------------------------------------
# 초기 상태
# -------------------------------------------------
def init_state():
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "home"

    if "home_view_mode" not in st.session_state:
        st.session_state.home_view_mode = "주간"

    if "timetable" not in st.session_state:
        st.session_state.timetable = [
            dict(day="월", start="09:00", end="10:00", title="데이터구조", kind="class"),
            dict(day="월", start="10:00", end="11:00",
                 title="데이터구조 과제 - 연결 리스트 구현", kind="task"),
            dict(day="월", start="11:00", end="12:00", title="알고리즘", kind="class"),
            dict(day="월", start="13:00", end="14:00",
                 title="알고리즘 숙제 - 정렬 알고리즘 분석", kind="task"),
            dict(day="화", start="09:00", end="10:00", title="운영체제", kind="class"),
            dict(day="화", start="14:00", end="15:00", title="데이터베이스", kind="class"),
            dict(day="수", start="10:00", end="11:00", title="네트워크", kind="class"),
            dict(day="목", start="09:00", end="10:00", title="소프트웨어공학", kind="class"),
            dict(day="금", start="13:00", end="14:00", title="인공지능", kind="class"),
        ]

    if "assignments" not in st.session_state:
        st.session_state.assignments = [
            dict(
                id="a1",
                title="데이터구조 과제 - 연결 리스트 구현",
                due="2025-12-05",
                minutes=60,
                priority="높음",
                type="학교",
                memo="도서관에서 하기",
                added_to_ai=True,
                completed=False,
                progress=0,
            ),
            dict(
                id="a2",
                title="알고리즘 숙제 - 정렬 알고리즘 분석",
                due="2025-12-07",
                minutes=50,
                priority="보통",
                type="학교",
                memo="",
                added_to_ai=True,
                completed=False,
                progress=0,
            ),
        ]

    if "task_filter" not in st.session_state:
        st.session_state.task_filter = "전체 할일"

    if "task_select_mode" not in st.session_state:
        st.session_state.task_select_mode = False

    if "task_selected_ids" not in st.session_state:
        st.session_state.task_selected_ids = set()

    if "preferences" not in st.session_state:
        st.session_state.preferences = dict(
            preferred_times=[dict(start="09:00", end="12:00")],
            avoid_times=[dict(start="18:00", end="20:00")],
            hide_classes_monthly=False,
        )

    if "recommendations" not in st.session_state:
        st.session_state.recommendations = []


init_state()

timetable = st.session_state.timetable
assignments = st.session_state.assignments
prefs = st.session_state.preferences

# -------------------------------------------------
# 공통 CSS (하단 탭 포함)
# -------------------------------------------------
st.markdown(
    """
<style>
body { background:#f3f4fb; }
.main { padding-bottom:80px; }

/* 카드/버튼 공통 */
.section-card {
    background:white;
    border-radius:18px;
    padding:16px;
    border:1px solid #e5e7eb;
    box-shadow:0 4px 16px rgba(15,23,42,0.04);
    margin-bottom:16px;
}
.section-title {
    font-weight:600;
    font-size:18px;
    margin-bottom:8px;
}

/* 과제 카드 */
.task-card {
    background:#f5f7ff;
    border-radius:16px;
    padding:12px 14px;
    border:1px solid #d1ddff;
    margin-bottom:10px;
    font-size:13px;
}
.task-header {
    display:flex;
    justify-content:space-between;
    align-items:flex-start;
    margin-bottom:6px;
}
.task-title { font-weight:600; }
.tag-type {
    font-size:11px;
    padding:2px 6px;
    border-radius:999px;
    background:#e0ebff;
    color:#1d4ed8;
}
.tag-ai {
    font-size:11px;
    padding:2px 6px;
    border-radius:999px;
    background:#eef2ff;
    color:#4f46e5;
}
.tag-priority-high {
    font-size:11px;
    padding:2px 6px;
    border-radius:999px;
    background:#fee2e2;
    color:#b91c1c;
}
.tag-priority-mid {
    font-size:11px;
    padding:2px 6px;
    border-radius:999px;
    background:#fef3c7;
    color:#92400e;
}

/* AI 카드 */
.ai-card {
    background:#ffffff;
    border-radius:16px;
    padding:12px 14px;
    border:1px solid #e5e7eb;
    margin-bottom:10px;
    font-size:13px;
}
.ai-header {
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:4px;
    font-size:12px;
    color:#4b5563;
}
.ai-badge-day {
    font-weight:600;
    color:#1d4ed8;
}

/* 설정 박스 */
.pref-box {
    border-radius:16px;
    padding:12px 14px;
    border:1px solid #bbf7d0;
    background:#ecfdf3;
    margin-bottom:12px;
}
.pref-box-avoid {
    border-color:#fecaca;
    background:#fef2f2;
}

/* 홈 – 주간 뷰 */
</style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------
# 홈 – 주간/월간 시간표
# -------------------------------------------------
def render_weekly_view():
    days = ["월", "화", "수", "목", "금"]
    start_hour = 9
    end_hour = 16
    num_rows = end_hour - start_hour + 1

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
    html += "<div class='week-header-row'><div></div>"
    for d in days:
        html += f"<div style='font-weight:500;'>{d}</div>"
    html += "</div>"

    html += "<div class='week-body'>"
    for row, hour in enumerate(range(start_hour, end_hour + 1), start=1):
        html += f"<div class='hour-label' style='grid-column:1;grid-row:{row};'>{hour}</div>"
        for col in range(2, 7):
            html += f"<div class='grid-cell' style='grid-column:{col};grid-row:{row};'></div>"

    day_index = {d: i for i, d in enumerate(days)}
    for ev in timetable:
        if ev["day"] not in day_index:
            continue
        col = day_index[ev["day"]] + 2
        start_min = time_to_minutes(ev["start"])
        end_min = time_to_minutes(ev["end"])
        base_min = start_hour * 60
        if end_min <= base_min or start_min >= (end_hour + 1) * 60:
            continue
        start_min = max(start_min, base_min)
        end_min = min(end_min, (end_hour + 1) * 60)
        start_slot = int((start_min - base_min) / 60) + 1
        span = max(1, int((end_min - start_min) / 60))
        kind = ev.get("kind", "class")
        html += f"""
        <div class="event {kind}"
             style="grid-column:{col};grid-row:{start_slot}/span {span};">
            {ev["title"]}
        </div>
        """

    html += "</div>"
    html += """
      <div class="legend">
        <span><span class="dot class"></span>수업</span>
        <span><span class="dot task"></span>학교 과제</span>
        <span><span class="dot personal"></span>개인 일정</span>
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_monthly_view():
    days_kr = ["월", "화", "수", "목", "금", "토", "일"]
    year, month = 2025, 11
    first_day = date(year, month, 1)
    start_weekday = first_day.weekday()
    next_month = date(year + (month == 12), (month % 12) + 1, 1)
    num_days = (next_month - first_day).days

    titles_by_day = {}
    for ev in timetable:
        if prefs.get("hide_classes_monthly") and ev.get("kind") == "class":
            continue
        titles_by_day.setdefault(ev["day"], [])
        if ev["title"] not in titles_by_day[ev["day"]]:
            titles_by_day[ev["day"]].append(ev["title"])

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
    <div class='month-wrapper'>
    <div class='month-grid'>
    """
    for d in ["월", "화", "수", "목", "금", "토", "일"]:
        html += f"<div class='month-header'>{d}</div>"
    for _ in range(start_weekday):
        html += "<div class='day-cell'></div>"
    for day in range(1, num_days + 1):
        weekday = (start_weekday + day - 1) % 7
        dname = days_kr[weekday]
        html += "<div class='day-cell'>"
        html += f"<div class='day-num'>{day}</div>"
        for t in titles_by_day.get(dname, []):
            html += f"<span class='month-tag'>{t}</span>"
        html += "</div>"
    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)


# -------------------------------------------------
# 과제 탭 / AI 탭 / 설정 탭 – (이전 답변 코드 그대로)
# -------------------------------------------------
# 길어서 생략 안 하고 그대로 둠; 네가 이미 붙여넣은 이전 코드와 동일.
# 아래 세 함수는 내용 그대로 유지.

def render_task_tab():
    st.markdown("<div class='section-title'>과제 관리</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("오늘의 할일", use_container_width=True):
            st.session_state.task_filter = "오늘의 할일"
    with c2:
        if st.button("전체 할일", use_container_width=True):
            st.session_state.task_filter = "전체 할일"

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("**과제 URL로 추가**  🔗", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:12px;color:#6b7280;margin-bottom:8px;'>학교 과제 스케줄 URL을 입력하면 자동으로 과제를 분석해드립니다.</div>",
        unsafe_allow_html=True,
    )
    url = st.text_input("url_input", "https://...", label_visibility="collapsed")
    cols = st.columns([3, 1])
    with cols[1]:
        if st.button("분석", use_container_width=True):
            if url and url != "https://...":
                new_id = f"url-{len(assignments)+1}"
                assignments.append(
                    dict(
                        id=new_id,
                        title="URL에서 가져온 과제",
                        due=datetime.today().strftime("%Y-%m-%d"),
                        minutes=40,
                        priority="보통",
                        type="학교",
                        memo="URL 분석으로 생성됨",
                        added_to_ai=False,
                        completed=False,
                        progress=0,
                    )
                )
                st.success("과제를 분석하여 목록에 추가했어.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("**직접 추가**", unsafe_allow_html=True)
    with st.form("direct_add_form", clear_on_submit=True):
        title = st.text_input("과제 제목")
        col1, col2 = st.columns(2)
        with col1:
            due = st.date_input("마감일", datetime.today())
        with col2:
            minutes = st.number_input("예상 소요 시간(분)", 10, 300, 60, 10)
        col3, col4 = st.columns(2)
        with col3:
            priority = st.selectbox("우선순위", ["높음", "보통", "낮음"])
        with col4:
            atype = st.selectbox("종류", ["학교", "개인"])
        memo = st.text_input("메모 (선택)")
        submitted = st.form_submit_button("추가")
        if submitted and title:
            new_id = f"new-{len(assignments)+1}"
            assignments.append(
                dict(
                    id=new_id,
                    title=title,
                    due=due.strftime("%Y-%m-%d"),
                    minutes=int(minutes),
                    priority=priority,
                    type=atype,
                    memo=memo,
                    added_to_ai=False,
                    completed=False,
                    progress=0,
                )
            )
            st.success("새 과제를 추가했어.")
    st.markdown("</div>", unsafe_allow_html=True)

    top_cols = st.columns([5, 1])
    with top_cols[0]:
        st.markdown("#### 할일", unsafe_allow_html=True)
    with top_cols[1]:
        if st.button("선택", use_container_width=True):
            st.session_state.task_select_mode = not st.session_state.task_select_mode
            st.session_state.task_selected_ids = set()

    if st.session_state.task_filter == "오늘의 할일":
        today_str = datetime.today().strftime("%Y-%m-%d")
        shown = [a for a in assignments if a["due"] == today_str]
    else:
        shown = list(assignments)

    shown.sort(key=lambda x: x["due"])
    grouped = {}
    for a in shown:
        grouped.setdefault(a["due"], []).append(a)

    for due, items in grouped.items():
        d = datetime.strptime(due, "%Y-%m-%d").date()
        weekday = ["월", "화", "수", "목", "금", "토", "일"][d.weekday()]
        st.markdown(f"**{d.month}월 {d.day}일 ({weekday})**", unsafe_allow_html=True)
        for a in items:
            selected = a["id"] in st.session_state.task_selected_ids
            col_sel, col_card = st.columns([0.4, 9.6])
            with col_sel:
                if st.session_state.task_select_mode:
                    chk = st.checkbox("", key=f"sel_{a['id']}", value=selected)
                    if chk:
                        st.session_state.task_selected_ids.add(a["id"])
                    else:
                        st.session_state.task_selected_ids.discard(a["id"])
            with col_card:
                pr_tag = (
                    "tag-priority-high"
                    if a["priority"] == "높음"
                    else "tag-priority-mid"
                    if a["priority"] == "보통"
                    else ""
                )
                ai_tag = "<span class='tag-ai'>AI 추가됨</span>" if a["added_to_ai"] else ""
                html = f"""
                <div class='task-card'>
                  <div class='task-header'>
                    <div>
                      <div class='task-title'>{a["title"]}</div>
                      <div style='margin-top:4px;font-size:12px;color:#6b7280;'>
                        <span class='tag-type'>{a["type"]}</span>
                        &nbsp;
                        <span class='{pr_tag}'>{a["priority"]}</span>
                        &nbsp;
                        {ai_tag}
                      </div>
                    </div>
                    <div style='font-size:18px;color:#9ca3af;'>✓</div>
                  </div>
                  <div style='font-size:12px;color:#6b7280;margin-top:4px;'>
                    📅 {d.month}월 {d.day}일 ({weekday})  ·  ⏱ {a["minutes"]}분
                  </div>
                  <div style='font-size:12px;color:#6b7280;margin-top:2px;'>
                    {'📂 ' + a["memo"] if a["memo"] else ''}
                  </div>
                </div>
                """
                st.markdown(html, unsafe_allow_html=True)

    if st.session_state.task_select_mode and st.session_state.task_selected_ids:
        st.write("")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("AI에 추가"):
                for a in assignments:
                    if a["id"] in st.session_state.task_selected_ids:
                        a["added_to_ai"] = True
                st.success("선택한 과제를 AI에 추가했어.")
        with c2:
            if st.button("AI에서 제외"):
                for a in assignments:
                    if a["id"] in st.session_state.task_selected_ids:
                        a["added_to_ai"] = False
                st.success("선택한 과제를 AI에서 제외했어.")
        with c3:
            if st.button("삭제"):
                st.session_state.assignments = [
                    a for a in assignments if a["id"] not in st.session_state.task_selected_ids
                ]
                st.session_state.task_selected_ids = set()
                st.success("선택한 과제를 삭제했어.")


def generate_recommendations():
    days = ["월", "화", "수", "목", "금"]
    school_hours = [
        ("09:00", "10:00"),
        ("10:00", "11:00"),
        ("11:00", "12:00"),
        ("13:00", "14:00"),
        ("14:00", "15:00"),
        ("15:00", "16:00"),
    ]
    free_slots = []
    for d in days:
        day_slots = [s for s in timetable if s["day"] == d]
        for s, e in school_hours:
            has_class = any(time_overlaps(s, e, t["start"], t["end"]) for t in day_slots)
            if not has_class:
                free_slots.append(dict(day=d, start=s, end=e))

    pending = [a for a in assignments if (not a["completed"]) and a["added_to_ai"]]
    order = {"높음": 0, "보통": 1, "낮음": 2}
    pending.sort(key=lambda a: (order.get(a["priority"], 3), a["due"]))

    recs, used_ids = [], set()
    for slot in free_slots:
        skip = False
        for avoid in prefs.get("avoid_times", []):
            if time_overlaps(slot["start"], slot["end"], avoid["start"], avoid["end"]):
                skip = True
                break
        if skip:
            continue
        pref_list = prefs.get("preferred_times", [])
        if pref_list and not any(
            time_overlaps(slot["start"], slot["end"], p["start"], p["end"])
            for p in pref_list
        ):
            continue
        slot_minutes = time_to_minutes(slot["end"]) - time_to_minutes(slot["start"])
        chosen = None
        for a in pending:
            if a["id"] in used_ids:
                continue
            if a["minutes"] <= slot_minutes:
                chosen = a
                break
        if chosen:
            used_ids.add(chosen["id"])
            recs.append(
                dict(
                    slot=slot,
                    assignment=chosen,
                    reason=f"{chosen['minutes']}분 소요 예상 - {slot['day']}요일 {slot['start']}~{slot['end']} 공강 시간 활용",
                )
            )
    st.session_state.recommendations = recs


def render_ai_tab():
    st.markdown("<div class='section-title'>AI 추천</div>", unsafe_allow_html=True)
    top_cols = st.columns([6, 1])
    with top_cols[0]:
        st.markdown(
            "<div style='font-size:13px;color:#6b7280;'>AI가 공강 시간과 과제를 분석하여 최적의 일정을 추천합니다.</div>",
            unsafe_allow_html=True,
        )
    with top_cols[1]:
        if st.button("재생성", use_container_width=True):
            generate_recommendations()
            st.success("추천 일정을 다시 만들었어.")

    added = [a for a in assignments if a["added_to_ai"]]
    recs = st.session_state.recommendations
    st.markdown(
        f"""
        <div class='section-card' style='background:#eef2ff;border-color:#c7d2fe;'>
          <div style='font-size:13px;color:#1d4ed8;'>
            📊 AI에 추가된 과제: {len(added)}개 | 생성된 추천: {len(recs)}개
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("일정 재생성", use_container_width=True):
            generate_recommendations()
    with c2:
        st.button("목록 보기", use_container_width=True)
    with c3:
        st.button("시간표 보기", use_container_width=True)

    st.markdown("#### AI 추천 결과", unsafe_allow_html=True)
    if not recs:
        st.info("아직 추천 일정이 없어. 과제를 AI에 추가하고 시간표를 설정하면 일정이 만들어져.")
        return

    for idx, r in enumerate(recs):
        slot = r["slot"]
        a = r["assignment"]
        d = datetime.strptime(a["due"], "%Y-%m-%d").date()
        weekday = ["월", "화", "수", "목", "금", "토", "일"][d.weekday()]
        html = f"""
        <div class='ai-card'>
          <div class='ai-header'>
            <span class='ai-badge-day'>{slot['day']}요일  {slot['start']} - {slot['end']}</span>
            <span style='color:#dc2626;font-weight:600;font-size:11px;'>긴급</span>
          </div>
          <div style='margin-bottom:4px;'>
            <div style='font-weight:600;'>{a["title"]}</div>
            <div style='font-size:12px;color:#6b7280;margin-top:2px;'>
              📅 마감: {d.year}-{d.month:02d}-{d.day:02d} ({weekday}) · ⏱ {a["minutes"]}분
            </div>
          </div>
          <div style='font-size:12px;color:#4b5563;margin-top:4px;'>
            💡 {r["reason"]}
          </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            prog = st.slider(
                f"진도율 체크_{idx}",
                0, 100, a["progress"], 10,
                label_visibility="collapsed",
            )
            a["progress"] = prog
        with col2:
            if st.button("완료", key=f"done_{idx}", use_container_width=True):
                a["completed"] = True
                a["progress"] = 100
                st.success("과제를 완료로 표시했어.")
        st.write("")


def render_settings_tab():
    st.markdown("<div class='section-title'>설정</div>", unsafe_allow_html=True)
    st.markdown("**과제 선호 설정**", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:13px;color:#6b7280;margin-bottom:12px;'>과제할 때 선호하는 시간대를 설정하면 더 맞춤화된 추천을 받을 수 있어.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='pref-box'>", unsafe_allow_html=True)
    st.markdown("🕒 선호하는 시간대", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        p_start = st.time_input(
            "pref_start",
            datetime.strptime("09:00", "%H:%M").time(),
            label_visibility="collapsed",
        )
    with col2:
        p_end = st.time_input(
            "pref_end",
            datetime.strptime("12:00", "%H:%M").time(),
            label_visibility="collapsed",
        )
    with col3:
        if st.button("추가", key="add_pref", use_container_width=True):
            prefs["preferred_times"].append(
                dict(start=p_start.strftime("%H:%M"), end=p_end.strftime("%H:%M"))
            )
    if prefs["preferred_times"]:
        chips = [f"{t['start']}~{t['end']}" for t in prefs["preferred_times"]]
        st.markdown(
            "<div style='font-size:12px;color:#374151;margin-top:6px;'>"
            + " · ".join(chips)
            + "</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='pref-box pref-box-avoid'>", unsafe_allow_html=True)
    st.markdown("⛔ 피하고 싶은 시간대", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        a_start = st.time_input(
            "avoid_start",
            datetime.strptime("18:00", "%H:%M").time(),
            label_visibility="collapsed",
        )
    with col2:
        a_end = st.time_input(
            "avoid_end",
            datetime.strptime("20:00", "%H:%M").time(),
            label_visibility="collapsed",
        )
    with col3:
        if st.button("추가", key="add_avoid", use_container_width=True):
            prefs["avoid_times"].append(
                dict(start=a_start.strftime("%H:%M"), end=a_end.strftime("%H:%M"))
            )
    if prefs["avoid_times"]:
        chips = [f"{t['start']}~{t['end']}" for t in prefs["avoid_times"]]
        st.markdown(
            "<div style='font-size:12px;color:#374151;margin-top:6px;'>"
            + " · ".join(chips)
            + "</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<div style='margin-top:12px;padding:12px 14px;border-radius:16px;background:#f5f3ff;border:1px solid #ddd6fe;'>",
        unsafe_allow_html=True,
    )
    st.markdown("**월간 캘린더 설정**", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:12px;color:#6b7280;margin-bottom:8px;'>월간 뷰에서 고정 학교 수업 표시 여부</div>",
        unsafe_allow_html=True,
    )
    hide = st.toggle(
        "월간 뷰에서 학교 수업 숨기기",
        value=prefs.get("hide_classes_monthly", False),
    )
    prefs["hide_classes_monthly"] = hide
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("설정 저장", use_container_width=True):
        st.success("설정을 저장했어.")


# -------------------------------------------------
# 메인 컨텐츠 (active_tab 기준)
# -------------------------------------------------
tab = st.session_state.active_tab

if tab == "home":
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c1:
        st.markdown("### 시간표 1")
    with c2:
        st.markdown(
            "<div style='text-align:center;font-weight:600;margin-top:4px;'>2025년 11월 5주차</div>",
            unsafe_allow_html=True,
        )

    view = st.session_state.home_view_mode
    t1, t2, t3 = st.columns(3)
    with t1:
        st.button("일간", use_container_width=True, disabled=True)
    with t2:
        if st.button("주간", use_container_width=True):
            st.session_state.home_view_mode = "주간"
            view = "주간"
    with t3:
        if st.button("월간", use_container_width=True):
            st.session_state.home_view_mode = "월간"
            view = "월간"

    if view == "주간":
        render_weekly_view()
    else:
        render_monthly_view()

elif tab == "task":
    render_task_tab()

elif tab == "ai":
    render_ai_tab()

elif tab == "settings":
    render_settings_tab()

# -------------------------------------------------
# 하단 탭 (실제로 이걸 눌러서 이동)
# -------------------------------------------------
# CSS: radio를 하단 고정 바처럼 보이게
st.markdown(
    """
<style>
#bottom-nav {
  position:fixed;
  left:0; right:0; bottom:0;
  background:white;
  padding:6px 12px 8px;
  box-shadow:0 -2px 12px rgba(15,23,42,0.08);
  z-index:50;
}
#bottom-nav [role="radiogroup"] {
  width:100%;
  justify-content:space-around;
}
#bottom-nav label {
  flex:1;
  text-align:center;
  padding:2px 0 4px;
  border-radius:999px;
  font-size:11px;
}
#bottom-nav label div {
  display:flex;
  flex-direction:column;
  align-items:center;
  gap:2px;
}
</style>
""",
    unsafe_allow_html=True,
)

tab_to_label = {"home": "🏠 홈", "task": "✅ 과제", "ai": "✨ AI", "settings": "⚙️ 설정"}
label_to_tab = {v: k for k, v in tab_to_label.items()}
labels = ["🏠 홈", "✅ 과제", "✨ AI", "⚙️ 설정"]
current_label = tab_to_label[st.session_state.active_tab]

st.markdown("<div id='bottom-nav'>", unsafe_allow_html=True)
selected_label = st.radio(
    "bottom_nav",
    labels,
    index=labels.index(current_label),
    horizontal=True,
    label_visibility="collapsed",
)
st.markdown("</div>", unsafe_allow_html=True)

st.session_state.active_tab = label_to_tab[selected_label]
