import math
import re
from dataclasses import dataclass, field
from typing import List, Optional, Literal, Dict, Set

# ==========================================
# 1. 데이터 구조 정의 (Interfaces -> Data Classes)
# ==========================================

@dataclass
class TimeSlot:
    day: str
    startTime: str
    endTime: str
    subject: Optional[str] = None
    isBlocked: bool = False

@dataclass
class Assignment:
    id: str
    title: str
    dueDate: str
    estimatedTime: int  # 분 단위
    priority: Literal['high', 'medium', 'low']
    completed: bool
    type: Literal['school', 'personal']
    addedToAI: bool
    memo: str
    progress: int = 0
    repeat: Literal['none', 'daily', 'weekly', 'monthly'] = 'none'
    reminder: Literal['none', '10min', '30min', '1hour', '1day'] = 'none'
    # 로직 내부 계산용
    remainingTime: int = 0

@dataclass
class Recommendation:
    timeSlot: TimeSlot
    assignment: Assignment
    reason: str

@dataclass
class Preferences:
    avoidTimeSlots: List[TimeSlot] = field(default_factory=list)
    preferredTimeSlots: List[TimeSlot] = field(default_factory=list)
    hideClassesInMonthly: bool = False

# ==========================================
# 2. 메인 로직 클래스
# ==========================================

class ScheduleOptimizer:
    def __init__(self):
        # 학교 수업 시간 정의 (고정값)
        self.school_hours = [
            {'start': '09:00', 'end': '10:00'},
            {'start': '10:00', 'end': '11:00'},
            {'start': '11:00', 'end': '12:00'},
            {'start': '13:00', 'end': '14:00'},
            {'start': '14:00', 'end': '15:00'},
            {'start': '15:00', 'end': '16:00'},
            {'start': '16:00', 'end': '17:00'}
        ]
        self.days = ['월', '화', '수', '목', '금']

    # --- 헬퍼 함수들 ---

    def normalize_time(self, time_str: str) -> str:
        """시간 형식 정규화 (예: '9시' -> '09:00')"""
        # "9:00", "09:00", "9시", "09시 00분" 등을 "09:00" 형식으로 변환
        clean_str = re.sub(r'시|분|\s', '', time_str)
        match = re.match(r'^(\d{1,2}):?(\d{2})?$', clean_str)
        
        if not match:
            return time_str
        
        hour = match.group(1).zfill(2)
        minute = match.group(2) if match.group(2) else '00'
        return f"{hour}:{minute}"

    def time_to_minutes(self, time_str: str) -> int:
        """HH:MM 문자열을 00:00 기준 분(minute)으로 변환"""
        normalized = self.normalize_time(time_str)
        hour, minute = map(int, normalized.split(':'))
        return hour * 60 + minute

    def time_overlaps(self, start1: str, end1: str, start2: str, end2: str) -> bool:
        """두 시간 구간이 겹치는지 확인"""
        s1 = self.time_to_minutes(start1)
        e1 = self.time_to_minutes(end1)
        s2 = self.time_to_minutes(start2)
        e2 = self.time_to_minutes(end2)
        return s1 < e2 and e1 > s2

    def calculate_duration(self, start_time: str, end_time: str) -> float:
        """두 시간 사이의 간격을 시간(hour) 단위로 반환"""
        start = self.time_to_minutes(start_time)
        end = self.time_to_minutes(end_time)
        return (end - start) / 60.0

    # --- 핵심 알고리즘 ---

    def find_free_slots(self, schedule_data: List[TimeSlot]) -> List[TimeSlot]:
        """현재 시간표를 기반으로 공강 시간(Free Slots)을 찾음"""
        print('🔍 [findFreeSlots] 시작')
        free_slots: List[TimeSlot] = []

        for day in self.days:
            # 해당 요일의 수업들 필터링
            day_schedule = [s for s in schedule_data if s.day == day]
            day_free_count = 0

            for hour in self.school_hours:
                # 해당 시간(hour)에 수업이 있는지 확인
                has_class = False
                for slot in day_schedule:
                    if self.time_overlaps(hour['start'], hour['end'], slot.startTime, slot.endTime):
                        has_class = True
                        break
                
                if not has_class:
                    free_slots.append(TimeSlot(
                        day=day,
                        startTime=hour['start'],
                        endTime=hour['end']
                    ))
                    day_free_count += 1
            
            print(f"  ➡️ {day}요일 공강 시간: {day_free_count}개")

        print(f'✨ 총 공강 슬롯: {len(free_slots)}개')
        return free_slots

    def generate_recommendations(self, schedule_data: List[TimeSlot], assignment_data: List[Assignment], preferences: Optional[Preferences] = None) -> List[Recommendation]:
        """공강 시간과 과제 목록을 매칭하여 추천 일정 생성"""
        print('\n🚀 ========== generateRecommendations 시작 ==========')
        
        if not schedule_data:
            print('❌ 중단: scheduleData가 비어있음')
            return []
        
        if not assignment_data:
            print('❌ 중단: assignmentData가 비어있음')
            return []

        # 1. 공강 시간 찾기
        free_slots = self.find_free_slots(schedule_data)
        
        # 2. 과제 필터링 및 우선순위 정렬
        pending_assignments = []
        for a in assignment_data:
            if not a.completed and a.addedToAI:
                # 남은 시간 계산
                remaining_time = math.ceil(a.estimatedTime * (100 - a.progress) / 100)
                # 데이터클래스는 불변이 아니므로 복사본을 만드는 것이 좋지만, 
                # 여기선 편의상 객체에 속성을 업데이트합니다. (파이썬에서는 동적 속성 할당 가능하나 dataclass 필드 사용 권장)
                a.remainingTime = remaining_time 
                
                if remaining_time > 0:
                    pending_assignments.append(a)

        # 정렬 로직 (Priority -> DueDate)
        priority_map = {'high': 0, 'medium': 1, 'low': 2}
        pending_assignments.sort(key=lambda x: (priority_map[x.priority], x.dueDate))

        print(f'📋 pendingAssignments: {len(pending_assignments)}개')

        new_recommendations: List[Recommendation] = []
        used_assignment_ids: Set[str] = set()
        
        skipped_by_preferences = 0
        skipped_by_avoid = 0
        slot_index = 0

        # 3. 매칭 알고리즘
        for free_slot in free_slots:
            slot_index += 1
            print(f"\n  🕒 슬롯 {slot_index}/{len(free_slots)}: {free_slot.day} {free_slot.startTime}-{free_slot.endTime}")

            skip_slot = False

            # 선호도 설정(Preferences) 체크
            if preferences:
                # Avoid Time Slots
                if preferences.avoidTimeSlots:
                    for avoid in preferences.avoidTimeSlots:
                        if self.time_overlaps(free_slot.startTime, free_slot.endTime, avoid.startTime, avoid.endTime):
                            print(f"    ⛔ avoidTimeSlots 필터링됨")
                            skipped_by_avoid += 1
                            skip_slot = True
                            break
                
                # Preferred Time Slots
                if not skip_slot and preferences.preferredTimeSlots:
                    is_preferred = False
                    for preferred in preferences.preferredTimeSlots:
                        if self.time_overlaps(free_slot.startTime, free_slot.endTime, preferred.startTime, preferred.endTime):
                            is_preferred = True
                            break
                    
                    if not is_preferred:
                        print("    ⚠️ 건너뜀: 선호 시간대 아님")
                        skipped_by_preferences += 1
                        skip_slot = True

            if skip_slot:
                continue

            # 슬롯 길이 계산 (시간 단위)
            slot_duration_hours = self.calculate_duration(free_slot.startTime, free_slot.endTime)
            slot_duration_minutes = slot_duration_hours * 60

            # 적절한 과제 찾기
            suitable_assignment = None
            for assignment in pending_assignments:
                not_used = assignment.id not in used_assignment_ids
                fits = assignment.remainingTime <= slot_duration_minutes

                if not_used and fits:
                    suitable_assignment = assignment
                    print(f"      ✅ \"{assignment.title}\": 매칭 성공!")
                    break
                elif not not_used:
                    pass # 이미 사용됨
                else:
                    # 시간 부족
                    pass

            if suitable_assignment:
                reason = (f"진도율 {suitable_assignment.progress}%, 남은 시간 {suitable_assignment.remainingTime}분" 
                          if suitable_assignment.progress > 0 
                          else f"{suitable_assignment.estimatedTime}분 소요 예상")
                reason += f" - {free_slot.day}요일 {free_slot.startTime}-{free_slot.endTime} 공강 시간 활용"

                new_recommendations.append(Recommendation(
                    timeSlot=free_slot,
                    assignment=suitable_assignment,
                    reason=reason
                ))
                used_assignment_ids.add(suitable_assignment.id)
            else:
                print("    ⚪ 적합한 과제 없음")

        print(f"\n🎉 최종 추천 수: {len(new_recommendations)}개")
        return new_recommendations

# ==========================================
# 3. 실행 테스트 코드 (React의 초기 상태값 사용)
# ==========================================

if __name__ == "__main__":
    optimizer = ScheduleOptimizer()

    # 테스트용 시간표 데이터
    test_schedule = [
        TimeSlot(day='월', startTime='09:00', endTime='10:00', subject='데이터구조'),
        TimeSlot(day='월', startTime='11:00', endTime='12:00', subject='알고리즘'),
        TimeSlot(day='화', startTime='09:00', endTime='10:00', subject='운영체제'),
        TimeSlot(day='화', startTime='14:00', endTime='15:00', subject='데이터베이스'),
        TimeSlot(day='수', startTime='10:00', endTime='11:00', subject='네트워크'),
        TimeSlot(day='목', startTime='09:00', endTime='10:00', subject='소프트웨어공학'),
        TimeSlot(day='금', startTime='13:00', endTime='14:00', subject='인공지능')
    ]

    # 테스트용 과제 데이터
    test_assignments = [
        Assignment(
            id='test-1',
            title='데이터구조 과제 - 연결 리스트 구현',
            dueDate='2025-12-05',
            estimatedTime=60,
            priority='high',
            completed=False,
            type='school',
            progress=0,
            addedToAI=True,
            memo='도서관에서 하기',
            repeat='none',
            reminder='none'
        ),
        Assignment(
            id='test-2',
            title='알고리즘 숙제 - 정렬 알고리즘 분석',
            dueDate='2025-12-07',
            estimatedTime=50,
            priority='medium',
            completed=False,
            type='school',
            progress=0,
            addedToAI=True,
            memo='',
            repeat='none',
            reminder='1day'
        )
    ]

    # 테스트용 선호도 설정 (옵션)
    test_preferences = Preferences(
        avoidTimeSlots=[],  # 피하고 싶은 시간 없음
        preferredTimeSlots=[] # 선호 시간 없음 (전체 허용)
    )

    # 추천 생성 실행
    recommendations = optimizer.generate_recommendations(test_schedule, test_assignments, test_preferences)

    # 결과 출력
    print("\n[최종 추천 결과]")
    for idx, rec in enumerate(recommendations, 1):
        print(f"{idx}. [{rec.timeSlot.day} {rec.timeSlot.startTime}~{rec.timeSlot.endTime}] {rec.assignment.title}")
        print(f"   - 이유: {rec.reason}")
