import math
from datetime import datetime, date
from typing import List, Dict, Any, Optional

import streamlit as st
import pandas as pd


st.set_page_config(page_title="시간표 기반 과제 추천기", layout="wide")


# ---- 시간 관련 유틸 ----
def normalize_time(t: str) -> str:
    """다양한 형식의 시간을 HH:MM 문자열로 통일."""
    if t is None:
        return "00:00"
    t = str(t).strip()
    if not t:
        return "00:00"
    # "9시 30분" 같은 형태 처리
    t = t.replace("시", ":").replace("분", "")
    t = t.replace(" ", "")
    if ":" in t:
        parts = t.split(":")
        h = parts[0] if parts[0] else "0"
        m = parts[1] if len(parts) > 1 and parts[1] else "00"
    else:
        # "930" -> "9:30", "9" -> "9:00"
        if len(t) <= 2:
            h, m = t, "00"
        else:
            h, m = t[:-2], t[-2:]
    h = h.zfill(2)
    m = m.zfill(2)
    return f"{h}:{m}"


def time_to_minutes(t: str) -> int:
    h, m = normalize_time(t).split(":")
    return int(h) * 60 + int(m)


def time_overlaps(start1: str, end1: str, start2: str, end2: str) -> bool:
    s1 = time_to_minutes(start1)
    e1 = time_to_minutes(end1)
    s2 = time_to_minutes(start2)
    e2 = time_to_minutes(end2)
    return s1 < e2 and e1 > s2


def calculate_duration(start_time: str, end_time: str) -> float:
    """시간 길이(시간 단위)."""
    start = time_to_minutes(start_time)
    end = time_to_minutes(end_time)
    return max(0, (end - start) / 60.0)


# ---- 추천 로직 ----
def parse_date_str(s: Any) -> date:
    try:
        # 이미 date 객체인 경우
        if isinstance(s, date):
            return s
        return datetime.strptime(str(s), "%Y-%m-%d").date()
    except Exception:
        # 실패 시 아주 먼 미래로
        return date(9999, 12, 31)


def find_free_slots(schedule_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    days = ["월", "화", "수", "목", "금"]
    school_hours = [
        {"start": "09:00", "end": "10:00"},
        {"start": "10:00", "end": "11:00"},
        {"start": "11:00", "end": "12:00"},
        {"start": "13:00", "end": "14:00"},
        {"start": "14:00", "end": "15:00"},
        {"start": "15:00", "end": "16:00"},
        {"start": "16:00", "end": "17:00"},
    ]

    free_slots: List[Dict[str, Any]] = []

    for day in days:
        day_schedule = [s for s in schedule_data if s.get("day") == day]
        for h in school_hours:
            has_class = False
            for slot in day_schedule:
                if time_overlaps(
                    h["start"],
                    h["end"],
                    slot.get("startTime", ""),
                    slot.get("endTime", ""),
                ):
                    has_class = True
                    break
            if not has_class:
                free_slots.append(
                    {
                        "day": day,
                        "startTime": h["start"],
                        "endTime": h["end"],
                    }
                )
    return free_slots


def generate_recommendations(
    schedule_data: List[Dict[str, Any]],
    assignment_data: List[Dict[str, Any]],
    preferences: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    if not schedule_data or not assignment_data:
        return []

    free_slots = find_free_slots(schedule_data)
    if not free_slots:
        return []

    pending = []
    for a in assignment_data:
        if a.get("completed"):
            continue
        if not a.get("addedToAI"):
            continue
        est = a.get("estimatedTime")
        if est is None:
            continue
        try:
            est_val = int(est)
        except Exception:
            continue

        progress = a.get("progress") or 0
        try:
            progress_val = int(progress)
        except Exception:
            progress_val = 0

        remaining = math.ceil(est_val * (100 - progress_val) / 100)
        if remaining <= 0:
            continue

        copy = a.copy()
        copy["remainingTime"] = remaining
        pending.append(copy)

    if not pending:
        return []

    priority_order = {"high": 0, "medium": 1, "low": 2}

    def sort_key(a: Dict[str, Any]):
        return (
            priority_order.get(a.get("priority", "medium"), 1),
            parse_date_str(a.get("dueDate")),
        )

    pending.sort(key=sort_key)

    recommendations: List[Dict[str, Any]] = []
    used_ids = set()

    for free in free_slots:
        # preferences 처리
        if preferences:
            avoid = preferences.get("avoidTimeSlots") or []
            preferred = preferences.get("preferredTimeSlots") or []

            # 피하고 싶은 시간대
            if avoid:
                skip = False
                for avoid_slot in avoid:
                    if time_overlaps(
                        free["startTime"],
                        free["endTime"],
                        avoid_slot.get("startTime", ""),
                        avoid_slot.get("endTime", ""),
                    ):
                        skip = True
                        break
                if skip:
                    continue

            # 선호 시간대가 설정돼 있으면, 그 안에 들어가는 슬롯만 사용
            if preferred:
                is_pref = any(
                    time_overlaps(
                        free["startTime"],
                        free["endTime"],
                        p.get("startTime", ""),
                        p.get("endTime", ""),
                    )
                    for p in preferred
                )
                if not is_pref:
                    continue

        slot_minutes = calculate_duration(
            free["startTime"], free["endTime"]
        ) * 60.0

        chosen = None
        for a in pending:
            if a["id"] in used_ids:
                continue
            if a["remainingTime"] <= slot_minutes:
                chosen = a
                break

        if chosen:
            progress_val = int(chosen.get("progress") or 0)
            if progress_val > 0:
                reason = (
                    f"진도율 {progress_val}%, 남은 시간 {chosen['remainingTime']}분 - "
                    f"{free['day']}요일 {free['startTime']}-{free['endTime']} 공강 시간 활용"
                )
            else:
                reason = (
                    f"{chosen['estimatedTime']}분 소요 예상 - "
                    f"{free['day']}요일 {free['startTime']}-{free['endTime']} 공강 시간 활용"
                )

            recommendations.append(
                {
                    "timeSlot": free,
                    "assignment": chosen,
                    "reason": reason,
                }
            )
            used_ids.add(chosen["id"])

    return recommendations


# ---- 세션 초기값 ----
if "timetables" not in st.session_state:
    st.session_state.timetables = [
        {
            "id": "1",
            "name": "시간표 1",
            "schedule": [
                {"day": "월", "startTime": "09:00", "endTime": "10:00", "subject": "데이터구조"},
                {"day": "월", "startTime": "11:00", "endTime": "12:00", "subject": "알고리즘"},
                {"day": "화", "startTime": "09:00", "endTime": "10:00", "subject": "운영체제"},
                {"day": "화", "startTime": "14:00", "endTime": "15:00", "subject": "데이터베이스"},
                {"day": "수", "startTime": "10:00", "endTime": "11:00", "subject": "네트워크"},
                {"day": "목", "startTime": "09:00", "endTime": "10:00", "subject": "소프트웨어공학"},
                {"day": "금", "startTime": "13:00", "endTime": "14:00", "subject": "인공지능"},
            ],
        }
    ]

if "current_timetable_id" not in st.session_state:
    st.session_state.current_timetable_id = "1"

if "assignments" not in st.session_state:
    st.session_state.assignments = [
        {
            "id": "test-1",
            "title": "데이터구조 과제 - 연결 리스트 구현",
            "dueDate": "2025-12-05",
            "estimatedTime": 60,
            "priority": "high",
            "completed": False,
            "type": "school",
            "progress": 0,
            "addedToAI": True,
            "memo": "도서관에서 하기",
            "repeat": "none",
            "reminder": "none",
        },
        {
            "id": "test-2",
            "title": "알고리즘 숙제 - 정렬 알고리즘 분석",
            "dueDate": "2025-12-07",
            "estimatedTime": 50,
            "priority": "medium",
            "completed": False,
            "type": "school",
            "progress": 0,
            "addedToAI": True,
            "memo": "",
            "repeat": "none",
            "reminder": "1day",
        },
    ]

if "preferences" not in st.session_state:
    st.session_state.preferences = {
        "avoidTimeSlots": [],
        "preferredTimeSlots": [],
        "hideClassesInMonthly": False,
    }

if "recommendations" not in st.session_state:
    st.session_state.recommendations = []

st.title("📅 시간표 기반 과제 추천기 (Streamlit 버전)")


# ---- 공통 상태 ----
timetables: List[Dict[str, Any]] = st.session_state.timetables
assignments: List[Dict[str, Any]] = st.session_state.assignments
preferences: Dict[str, Any] = st.session_state.preferences

# 현재 시간표 찾기
current_id = st.session_state.current_timetable_id
current_timetable = next(
    (t for t in timetables if t["id"] == current_id), timetables[0]
)
schedule = current_timetable.get("schedule", [])


# ---- 탭 선택 ----
tab = st.sidebar.radio("탭", ["홈", "과제", "AI 추천", "설정"])


# ---- 홈 탭 ----
if tab == "홈":
    st.subheader("시간표 관리")

    # 시간표 선택
    labels = [f"{t['name']} ({t['id']})" for t in timetables]
    id_by_label = {labels[i]: timetables[i]["id"] for i in range(len(timetables))}
    current_label = next(
        (lbl for lbl, tid in id_by_label.items() if tid == current_id), labels[0]
    )
    chosen_label = st.selectbox("시간표 선택", labels, index=labels.index(current_label))
    new_id = id_by_label[chosen_label]
    if new_id != current_id:
        st.session_state.current_timetable_id = new_id
        current_timetable = next(
            (t for t in timetables if t["id"] == new_id), timetables[0]
        )
        schedule = current_timetable.get("schedule", [])

    # 시간표 이름 변경
    new_name = st.text_input("현재 시간표 이름", value=current_timetable["name"])
    if new_name != current_timetable["name"]:
        current_timetable["name"] = new_name

    # 새 시간표 추가
    if st.button("새 시간표 추가"):
        new_tid = str(int(datetime.now().timestamp()))
        timetables.append(
            {
                "id": new_tid,
                "name": f"시간표 {len(timetables) + 1}",
                "schedule": [],
            }
        )
        st.session_state.current_timetable_id = new_tid
        st.success("새 시간표가 추가되었습니다.")

    st.markdown("### 시간표 편집")

    if schedule:
        schedule_df = pd.DataFrame(schedule)
    else:
        schedule_df = pd.DataFrame(
            {"day": [], "startTime": [], "endTime": [], "subject": []}
        )

    edited_schedule_df = st.data_editor(
        schedule_df,
        num_rows="dynamic",
        use_container_width=True,
        key="schedule_editor",
    )

    if st.button("시간표 저장"):
        current_timetable["schedule"] = edited_schedule_df.to_dict("records")
        st.success("시간표가 저장되었습니다.")

    st.markdown("### 간단 뷰 모드")
    view_mode = st.radio(
        "보기 모드",
        ["weekly", "daily", "monthly"],
        key="view_mode",
        horizontal=True,
    )

    today = st.date_input("기준 날짜", value=date.today(), key="current_date")

    weekday_map = {0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"}
    today_day = weekday_map[today.weekday()]

    if view_mode == "weekly":
        st.write("이번 주 수업")
        st.table(pd.DataFrame(schedule))
    elif view_mode == "daily":
        st.write(f"{today_day}요일 수업")
        daily_slots = [s for s in schedule if s.get("day") == today_day]
        st.table(pd.DataFrame(daily_slots))
    else:  # monthly
        hide_classes = preferences.get("hideClassesInMonthly", False)
        if hide_classes:
            st.info("월간 보기에서 수업은 숨기고 추천만 봅니다. (AI 탭에서 추천 생성 필요)")
        else:
            st.info("월간 요약은 간단히 주·일간 뷰를 참고해줘. (필요하면 여기서 더 확장 가능)")


# ---- 과제 탭 ----
elif tab == "과제":
    st.subheader("과제 목록")

    if not assignments:
        st.info("현재 등록된 과제가 없습니다.")
    else:
        for idx, a in enumerate(assignments):
            with st.expander(
                f"{a['title']} (마감: {a['dueDate']}, 우선순위: {a['priority']})",
                expanded=False,
            ):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.write(f"타입: {a.get('type', 'school')}")
                    st.write(f"예상 시간: {a.get('estimatedTime', 0)}분")
                    st.write(f"메모: {a.get('memo', '') or '-'}")
                with c2:
                    completed = st.checkbox(
                        "완료",
                        value=a.get("completed", False),
                        key=f"completed_{a['id']}",
                    )
                    added = st.checkbox(
                        "AI에 사용",
                        value=a.get("addedToAI", False),
                        key=f"ai_{a['id']}",
                    )
                with c3:
                    progress_val = int(a.get("progress") or 0)
                    progress_new = st.slider(
                        "진도(%)",
                        0,
                        100,
                        progress_val,
                        key=f"progress_{a['id']}",
                    )

                # 상태 업데이트
                a["completed"] = completed
                a["addedToAI"] = added
                a["progress"] = progress_new

    st.markdown("---")
    st.subheader("새 과제 추가")

    with st.form("add_assignment"):
        title = st.text_input("제목")
        due = st.date_input("마감일", value=date.today())
        est = st.number_input(
            "예상 소요 시간 (분)", min_value=10, max_value=600, step=10, value=60
        )
        priority = st.selectbox("우선순위", ["high", "medium", "low"])
        type_ = st.selectbox("타입", ["school", "personal"])
        memo = st.text_area("메모", "")
        submit = st.form_submit_button("추가")

        if submit:
            if not title:
                st.error("제목은 필수입니다.")
            else:
                new_assignment = {
                    "id": f"a{int(datetime.now().timestamp() * 1000)}",
                    "title": title,
                    "dueDate": due.isoformat(),
                    "estimatedTime": int(est),
                    "priority": priority,
                    "completed": False,
                    "type": type_,
                    "progress": 0,
                    "addedToAI": False,
                    "memo": memo,
                    "repeat": "none",
                    "reminder": "none",
                }
                assignments.append(new_assignment)
                st.success("과제가 추가되었습니다.")


# ---- AI 추천 탭 ----
elif tab == "AI 추천":
    st.subheader("AI 추천 일정 생성")

    st.write(f"- 현재 시간표 슬롯 수: **{len(schedule)}**")
    ai_candidates = [
        a
        for a in assignments
        if a.get("addedToAI") and not a.get("completed", False)
    ]
    st.write(f"- AI에 추가된 미완료 과제 수: **{len(ai_candidates)}**")

    if not schedule:
        st.warning("먼저 홈 탭에서 시간표를 입력하거나 편집해줘.")
    elif not ai_candidates:
        st.warning("과제 탭에서 'AI에 사용' 체크를 켜야 추천을 만들 수 있어.")
    else:
        if st.button("추천 생성 / 재생성"):
            st.session_state.recommendations = generate_recommendations(
                schedule, assignments, preferences
            )
            st.success("추천 일정이 생성되었습니다.")

        recs = st.session_state.recommendations
        if not recs:
            st.info("아직 생성된 추천이 없습니다. 위 버튼을 눌러 만들어줘.")
        else:
            st.markdown("### 추천 결과")
            for rec in recs:
                slot = rec["timeSlot"]
                a = rec["assignment"]
                header = (
                    f"{slot['day']} {slot['startTime']}-{slot['endTime']} · {a['title']}"
                )
                with st.expander(header, expanded=True):
                    st.write(f"마감일: {a['dueDate']}")
                    st.write(f"우선순위: {a['priority']}")
                    st.write(f"예상 시간: {a['estimatedTime']}분")
                    st.write(f"현재 진도: {int(a.get('progress') or 0)}%")
                    st.write(rec["reason"])


# ---- 설정 탭 ----
elif tab == "설정":
    st.subheader("선호 시간대 / 피하고 싶은 시간대 설정")

    hide_classes = st.checkbox(
        "월간 보기에서 수업 숨기기", value=preferences.get("hideClassesInMonthly", False)
    )

    st.markdown("### 피하고 싶은 시간대 (avoidTimeSlots)")
    avoid_slots = preferences.get("avoidTimeSlots") or []
    if avoid_slots:
        avoid_df = pd.DataFrame(avoid_slots)
    else:
        avoid_df = pd.DataFrame({"startTime": [], "endTime": []})

    edited_avoid_df = st.data_editor(
        avoid_df,
        num_rows="dynamic",
        use_container_width=True,
        key="avoid_editor",
    )

    st.markdown("### 선호 시간대 (preferredTimeSlots)")
    preferred_slots = preferences.get("preferredTimeSlots") or []
    if preferred_slots:
        preferred_df = pd.DataFrame(preferred_slots)
    else:
        preferred_df = pd.DataFrame({"startTime": [], "endTime": []})

    edited_preferred_df = st.data_editor(
        preferred_df,
        num_rows="dynamic",
        use_container_width=True,
        key="preferred_editor",
    )

    if st.button("설정 저장"):
        preferences["hideClassesInMonthly"] = hide_classes
        preferences["avoidTimeSlots"] = edited_avoid_df.to_dict("records")
        preferences["preferredTimeSlots"] = edited_preferred_df.to_dict("records")
        st.session_state.preferences = preferences
        st.success("설정이 저장되었습니다.")
