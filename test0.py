from dataclasses import dataclass, field
from typing import List, Optional, Literal
from datetime import datetime
import math

Priority = Literal["high", "medium", "low"]

@dataclass
class TimeSlot:
    day: str               # '월', '화' ...
    startTime: str         # '09:00'
    endTime: str           # '10:00'
    subject: Optional[str] = None
    isBlocked: bool = False

@dataclass
class Assignment:
    id: str
    title: str
    dueDate: str           # 'YYYY-MM-DD'
    estimatedTime: int     # 분 단위
    priority: Priority     # 'high' | 'medium' | 'low'
    completed: bool
    type: Literal["school", "personal"]
    progress: int = 0      # 0~100
    addedToAI: bool = False
    memo: str = ""
    repeat: str = "none"
    reminder: str = "none"

@dataclass
class Recommendation:
    timeSlot: TimeSlot
    assignment: Assignment
    reason: str

@dataclass
class PreferenceSlot:
    startTime: str
    endTime: str

@dataclass
class Preferences:
    preferredTimeSlots: List[PreferenceSlot] = field(default_factory=list)
    avoidTimeSlots: List[PreferenceSlot] = field(default_factory=list)
    hideClassesInMonthly: bool = False


# ----- 시간 관련 유틸 -----

def normalize_time(time_str: str) -> str:
    # "9:00", "09:00", "9시", "09시 00분", "900" 등 → "09:00"
    s = time_str.replace("시", "").replace("분", "").replace(" ", "")
    if ":" in s:
        parts = s.split(":")
        hour = parts[0].zfill(2)
        minute = (parts[1] if len(parts) > 1 and parts[1] else "00").zfill(2)
    else:
        if len(s) <= 2:
            hour = s.zfill(2)
            minute = "00"
        else:
            hour = s[:-2].zfill(2)
            minute = s[-2:]
    return f"{hour}:{minute}"

def time_to_minutes(time_str: str) -> int:
    t = normalize_time(time_str)
    h, m = t.split(":")
    return int(h) * 60 + int(m)

def time_overlaps(start1: str, end1: str, start2: str, end2: str) -> bool:
    s1, e1 = time_to_minutes(start1), time_to_minutes(end1)
    s2, e2 = time_to_minutes(start2), time_to_minutes(end2)
    return s1 < e2 and e1 > s2

def calculate_duration(start: str, end: str) -> float:
    # 시간 단위 (시간)
    return (time_to_minutes(end) - time_to_minutes(start)) / 60.0


# ----- 공강 찾기 -----

def find_free_slots(schedule: List[TimeSlot]) -> List[TimeSlot]:
    days = ["월", "화", "수", "목", "금"]
    school_hours = [
        ("09:00", "10:00"),
        ("10:00", "11:00"),
        ("11:00", "12:00"),
        ("13:00", "14:00"),
        ("14:00", "15:00"),
        ("15:00", "16:00"),
        ("16:00", "17:00"),
    ]
    free: List[TimeSlot] = []
    for day in days:
        day_schedule = [s for s in schedule if s.day == day]
        for start, end in school_hours:
            has_class = any(
                time_overlaps(start, end, slot.startTime, slot.endTime)
                for slot in day_schedule
            )
            if not has_class:
                free.append(TimeSlot(day=day, startTime=start, endTime=end))
    return free


# ----- 추천 생성 -----

def parse_date(d: str) -> datetime:
    return datetime.strptime(d, "%Y-%m-%d")

def generate_recommendations(
    schedule: List[TimeSlot],
    assignments: List[Assignment],
    preferences: Optional[Preferences] = None,
) -> List[Recommendation]:
    if not schedule or not assignments:
        return []

    free_slots = find_free_slots(schedule)

    # React 코드처럼: addedToAI = true, completed = false, remainingTime > 0 만 대상으로
    pending: List[Assignment] = []
    for a in assignments:
        if a.completed or not a.addedToAI:
            continue
        progress = a.progress or 0
        remaining = math.ceil(a.estimatedTime * (100 - progress) / 100)
        if remaining <= 0:
            continue
        tmp = Assignment(**{**a.__dict__})
        tmp.estimatedTime = remaining  # remainingTime을 estimatedTime 자리에 넣어서 사용
        pending.append(tmp)

    if not pending:
        return []

    priority_order = {"high": 0, "medium": 1, "low": 2}
    pending.sort(
        key=lambda a: (
            priority_order.get(a.priority, 1),
            parse_date(a.dueDate),
        )
    )

    recs: List[Recommendation] = []
    used_ids = set()

    def slot_allowed(slot: TimeSlot) -> bool:
        if not preferences:
            return True

        # 피하고 싶은 시간대
        for av in preferences.avoidTimeSlots:
            if time_overlaps(slot.startTime, slot.endTime, av.startTime, av.endTime):
                return False

        # 선호 시간대가 설정되어 있으면, 그 안에 들어가는 슬롯만 허용
        if preferences.preferredTimeSlots:
            return any(
                time_overlaps(slot.startTime, slot.endTime, pf.startTime, pf.endTime)
                for pf in preferences.preferredTimeSlots
            )
        return True

    for slot in free_slots:
        if not slot_allowed(slot):
            continue
        duration_min = calculate_duration(slot.startTime, slot.endTime) * 60
        chosen: Optional[Assignment] = None
        for a in pending:
            if a.id in used_ids:
                continue
            if a.estimatedTime <= duration_min:
                chosen = a
                break
        if chosen:
            reason = (
                f"{chosen.estimatedTime}분 소요 예상 - "
                f"{slot.day}요일 {slot.startTime}-{slot.endTime} 공강 시간 활용"
            )
            recs.append(
                Recommendation(
                    timeSlot=slot,
                    assignment=chosen,
                    reason=reason,
                )
            )
            used_ids.add(chosen.id)
    return recs


# ----- 간단 테스트 -----

if __name__ == "__main__":
    schedule = [
        TimeSlot(day="월", startTime="09:00", endTime="10:00", subject="데이터구조"),
        TimeSlot(day="월", startTime="11:00", endTime="12:00", subject="알고리즘"),
        TimeSlot(day="화", startTime="09:00", endTime="10:00", subject="운영체제"),
    ]
    assignments = [
        Assignment(
            id="test-1",
            title="데이터구조 과제 - 연결 리스트 구현",
            dueDate="2025-12-05",
            estimatedTime=60,
            priority="high",
            completed=False,
            type="school",
            addedToAI=True,
        ),
        Assignment(
            id="test-2",
            title="알고리즘 숙제 - 정렬 알고리즘 분석",
            dueDate="2025-12-07",
            estimatedTime=50,
            priority="medium",
            completed=False,
            type="school",
            addedToAI=True,
        ),
    ]
    prefs = Preferences(
        preferredTimeSlots=[PreferenceSlot(startTime="13:00", endTime="17:00")],
        avoidTimeSlots=[PreferenceSlot(startTime="09:00", endTime="11:00")],
    )
    recs = generate_recommendations(schedule, assignments, prefs)
    for r in recs:
        print(
            f"{r.timeSlot.day} {r.timeSlot.startTime}-{r.timeSlot.endTime} -> "
            f"{r.assignment.title} ({r.reason})"
        )
