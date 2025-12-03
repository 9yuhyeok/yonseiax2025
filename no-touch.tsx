import { useState, useEffect } from 'react';
import { MobileLayout } from './components/MobileLayout';
import { HomeTab, ViewMode } from './components/HomeTab';
import { TaskTab } from './components/TaskTab';
import { GradesTab } from './components/GradesTab';
import { WeeklyView } from './components/WeeklyView';
import { DailyView } from './components/DailyView';
import { MonthlyView } from './components/MonthlyView';
import { TimeTableUpload } from './components/TimeTableUpload';
import { AssignmentSchedule } from './components/AssignmentSchedule';
import { PreferencesForm, Preferences } from './components/PreferencesForm';
import { Toaster } from './components/ui/sonner';
import { toast } from 'sonner@2.0.3';

export interface TimeSlot {
  day: string;
  startTime: string;
  endTime: string;
  subject?: string;
  isBlocked?: boolean;
}

export interface Assignment {
  id: string;
  title: string;
  dueDate: string;
  estimatedTime: number;
  priority: 'high' | 'medium' | 'low';
  completed: boolean;
  type: 'school' | 'personal';
  progress?: number;
  addedToAI: boolean;
  memo: string;
  repeat?: 'none' | 'daily' | 'weekly' | 'monthly';
  reminder?: 'none' | '10min' | '30min' | '1hour' | '1day';
}

export interface Recommendation {
  timeSlot: TimeSlot;
  assignment: Assignment;
  reason: string;
}

interface Timetable {
  id: string;
  name: string;
  schedule: TimeSlot[];
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'home' | 'task' | 'grades' | 'settings'>('home');
  const [viewMode, setViewMode] = useState<ViewMode>('weekly');
  const [currentDate, setCurrentDate] = useState(new Date());
  
  // 시간표 관리
  const [timetables, setTimetables] = useState<Timetable[]>([
    { 
      id: '1', 
      name: '시간표 1', 
      schedule: [
        // 테스트용 초기 시간표
        { day: '월', startTime: '09:00', endTime: '10:00', subject: '데이터구조' },
        { day: '월', startTime: '11:00', endTime: '12:00', subject: '알고리즘' },
        { day: '화', startTime: '09:00', endTime: '10:00', subject: '운영체제' },
        { day: '화', startTime: '14:00', endTime: '15:00', subject: '데이터베이스' },
        { day: '수', startTime: '10:00', endTime: '11:00', subject: '네트워크' },
        { day: '목', startTime: '09:00', endTime: '10:00', subject: '소프트웨어공학' },
        { day: '금', startTime: '13:00', endTime: '14:00', subject: '인공지능' }
      ]
    }
  ]);
  const [currentTimetableId, setCurrentTimetableId] = useState('1');
  
  const [assignments, setAssignments] = useState<Assignment[]>([
    // 테스트용 초기 과제
    {
      id: 'test-1',
      title: '데이터구조 과제 - 연결 리스트 구현',
      dueDate: '2025-12-05',
      estimatedTime: 60,
      priority: 'high',
      completed: false,
      type: 'school',
      progress: 0,
      addedToAI: true, // 테스트를 위해 AI에 추가된 상태로 시작
      memo: '도서관에서 하기',
      repeat: 'none',
      reminder: 'none'
    },
    {
      id: 'test-2',
      title: '알고리즘 숙제 - 정렬 알고리즘 분석',
      dueDate: '2025-12-07',
      estimatedTime: 50,
      priority: 'medium',
      completed: false,
      type: 'school',
      progress: 0,
      addedToAI: true, // 테스트를 위해 AI에 추가된 상태로 시작
      memo: '',
      repeat: 'none',
      reminder: '1day'
    }
  ]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [preferences, setPreferences] = useState<Preferences | null>(null);

  // 현재 시간표
  const currentTimetable = timetables.find(t => t.id === currentTimetableId);
  const schedule = currentTimetable?.schedule || [];

  // 시간표 또는 과제가 변경될 때마다 추천 재생성
  useEffect(() => {
    console.log('🔄 [시간표/과제 변경] useEffect 실행');
    console.log('  - currentTimetable:', currentTimetable);
    console.log('  - schedule.length:', schedule.length);
    console.log('  - schedule:', schedule);
    console.log('  - assignments.length:', assignments.length);
    console.log('  - assignments with addedToAI:', assignments.filter(a => a.addedToAI).length);
    
    // 타이머를 사용하여 초기 렌더링 이후에 실행
    const timer = setTimeout(() => {
      if (schedule.length > 0 && assignments.length > 0) {
        const aiAssignments = assignments.filter(a => a.addedToAI && !a.completed);
        if (aiAssignments.length > 0) {
          console.log('✅ 조건 충족, 추천 생성 시작');
          generateRecommendations(schedule, assignments);
        } else {
          console.log('⚠️ AI에 추가된 미완료 과제가 없음 - 추천 초기화');
          setRecommendations([]);
        }
      } else {
        console.log('❌ 조건 미충족 - 추천 초기화');
        if (schedule.length === 0) {
          console.log('  ❌ schedule이 비어있음 - currentTimetable 확인 필요');
        }
        if (assignments.length === 0) {
          console.log('  ❌ assignments가 비어있음');
        }
        setRecommendations([]);
      }
    }, 100);
    
    return () => clearTimeout(timer);
  }, [schedule, assignments]); // 시간표와 과제가 변경될 때마다 실행

  const handlePreferencesSaved = (prefs: Preferences) => {
    console.log('💾 선호 설정 저장:', prefs);
    setPreferences(prefs);
    toast.success('선호 설정이 저장되었습니다!');
    setActiveTab('home');
  };

  const handleScheduleAnalyzed = (analyzedSchedule: TimeSlot[]) => {
    console.log('📅 시간표 분석 완료:', analyzedSchedule);
    
    // 현재 시간표 업데이트 (useEffect에서 자동으로 추천 재생성)
    setTimetables(prev => 
      prev.map(t => 
        t.id === currentTimetableId 
          ? { ...t, schedule: analyzedSchedule } 
          : t
      )
    );
    toast.success('시간표가 분석되었습니다!');
    setActiveTab('home');
  };

  const handleAssignmentsUpdated = (updatedAssignments: Assignment[]) => {
    setAssignments(updatedAssignments);
    // useEffect에서 자동으로 재생성되므로 여기서는 호출하지 않음
  };

  const handleAddToAI = (assignmentIds: string[]) => {
    console.log('\n📌 ========== handleAddToAI 호출 ==========');
    console.log('🎯 선택된 과제 IDs:', assignmentIds);
    console.log('📝 선택된 과제 상세:', assignmentIds.map(id => {
      const assignment = assignments.find(a => a.id === id);
      return assignment ? `${assignment.title} (${assignment.estimatedTime}분)` : id;
    }));
    
    const updated = assignments.map(a => 
      assignmentIds.includes(a.id) 
        ? { ...a, addedToAI: true }
        : a
    );
    
    const addedCount = updated.filter(a => a.addedToAI).length;
    console.log('✅ 업데이트 후 AI에 추가된 전체 과제 수:', addedCount);
    console.log('📊 업데이트된 assignments:', updated.map(a => ({
      title: a.title,
      addedToAI: a.addedToAI,
      completed: a.completed,
      estimatedTime: a.estimatedTime
    })));
    
    setAssignments(updated);
    
    if (schedule.length === 0) {
      console.log('⚠️ 시간표가 없어서 추천 생성 안 함');
      toast.warning(`${assignmentIds.length}개 과제가 AI에 추가되었습니다!\n시간표를 업로드하면 추천 일정이 생성됩니다.`, {
        duration: 4000
      });
    } else {
      console.log('✅ 시간표 있음, useEffect에서 자동으로 추천 재생성됨');
      toast.success(`${assignmentIds.length}개 과제가 AI에 추가되었습니다!\nAI 탭에서 추천 일정을 확인하세요.`, {
        duration: 3000
      });
    }
    console.log('========== handleAddToAI 완료 ==========\n');
  };

  const handleProgressUpdate = (assignmentId: string, completed: boolean, progress: number) => {
    const updated = assignments.map(a => 
      a.id === assignmentId 
        ? { ...a, completed, progress } 
        : a
    );
    handleAssignmentsUpdated(updated);
    
    if (completed) {
      toast.success('과제가 완료되었습니다! 🎉');
    } else {
      toast.info(`진도율이 ${progress}%로 업데이트되었습니다`);
    }
    
    // useEffect에서 자동으로 재생성되므로 여기서는 호출하지 않음
  };

  const handleRegenerateRecommendations = () => {
    // 현재 시간표와 과제를 사용하여 추천 재생성
    const currentSchedule = currentTimetable?.schedule || [];
    generateRecommendations(currentSchedule, assignments);
    toast.success('추천 일정이 재생성되었습니다!');
  };

  const handleAddTimetable = () => {
    const newId = String(Date.now());
    const newTimetable: Timetable = {
      id: newId,
      name: `시간표 ${timetables.length + 1}`,
      schedule: []
    };
    setTimetables(prev => [...prev, newTimetable]);
    setCurrentTimetableId(newId);
    toast.success('새 시간표가 추가되었습니다!');
  };

  const handleRenameTimetable = (id: string, name: string) => {
    setTimetables(prev => 
      prev.map(t => t.id === id ? { ...t, name } : t)
    );
    toast.success('시간표 이름이 변경되었습니다!');
  };

  const handleDeleteTimetable = (id: string) => {
    if (timetables.length <= 1) {
      toast.error('최소 1개의 시간표는 필요합니다.');
      return;
    }
    
    setTimetables(prev => prev.filter(t => t.id !== id));
    
    if (currentTimetableId === id) {
      const remaining = timetables.filter(t => t.id !== id);
      setCurrentTimetableId(remaining[0].id);
    }
    
    toast.success('시간표가 삭제되었습니다!');
  };

  const generateRecommendations = (scheduleData: TimeSlot[], assignmentData: Assignment[]) => {
    console.log('\n🚀 ========== generateRecommendations 시작 ==========');
    console.log('📊 입력 데이터:');
    console.log('  - scheduleData 개수:', scheduleData.length);
    console.log('  - assignmentData 개수:', assignmentData.length);
    console.log('  - assignmentData 상세:', assignmentData.map(a => ({
      title: a.title,
      addedToAI: a.addedToAI,
      completed: a.completed,
      estimatedTime: a.estimatedTime
    })));
    
    if (scheduleData.length === 0) {
      console.log('❌ 중단: scheduleData가 비어있음');
      return;
    }
    
    if (assignmentData.length === 0) {
      console.log('❌ 중단: assignmentData가 비어있음');
      return;
    }

    const freeSlots = findFreeSlots(scheduleData);
    console.log('📌 [디버깅 1] freeSlots.length:', freeSlots.length);
    console.log('📌 [디버깅 2] assignmentData.length:', assignmentData.length);
    
    const pendingAssignments = assignmentData
      .filter(a => !a.completed && a.addedToAI)
      .map(a => {
        const progress = a.progress || 0;
        const remainingTime = Math.ceil(a.estimatedTime * (100 - progress) / 100);
        console.log(`  �� 과제: "${a.title}" - estimatedTime: ${a.estimatedTime}분, progress: ${progress}%, remainingTime: ${remainingTime}분`);
        return { ...a, remainingTime };
      })
      .filter(a => a.remainingTime > 0)
      .sort((a, b) => {
        if (a.priority !== b.priority) {
          const priorityOrder = { high: 0, medium: 1, low: 2 };
          return priorityOrder[a.priority] - priorityOrder[b.priority];
        }
        return a.dueDate.localeCompare(b.dueDate);
      });
    
    console.log('📌 [디버깅 3] pendingAssignments.length:', pendingAssignments.length);
    console.log('📋 pendingAssignments (addedToAI=true, completed=false, remainingTime>0):', pendingAssignments);
    
    const newRecommendations: Recommendation[] = [];
    const usedAssignments = new Set<string>();
    
    console.log('🎯 추천 생성 시작 - 공강 슬롯 매칭');
    console.log('⚙️ preferences:', preferences);
    
    let slotIndex = 0;
    let skippedByPreferences = 0;
    let skippedByAvoid = 0;
    
    for (const freeSlot of freeSlots) {
      slotIndex++;
      console.log(`\n  🕒 슬롯 ${slotIndex}/${freeSlots.length}: ${freeSlot.day} ${freeSlot.startTime}-${freeSlot.endTime}`);
      
      // preferences 필터링 (설정된 경우에만)
      let skipSlot = false;
      
      if (preferences) {
        // avoidTimeSlots 체크
        if (preferences.avoidTimeSlots && preferences.avoidTimeSlots.length > 0) {
          const shouldAvoid = preferences.avoidTimeSlots.some(avoid => {
            const overlap = timeOverlaps(freeSlot.startTime, freeSlot.endTime, avoid.startTime, avoid.endTime);
            if (overlap) {
              console.log(`    ⛔ avoidTimeSlots 필터링: ${avoid.startTime}-${avoid.endTime}와 겹침`);
            }
            return overlap;
          });
          if (shouldAvoid) {
            console.log(`    ❌ 건너뜀: 피하고 싶은 시간대`);
            skippedByAvoid++;
            skipSlot = true;
          }
        }

        // preferredTimeSlots 체크 (설정된 경우에만)
        if (!skipSlot && preferences.preferredTimeSlots && preferences.preferredTimeSlots.length > 0) {
          const isPreferred = preferences.preferredTimeSlots.some(preferred => {
            const overlap = timeOverlaps(freeSlot.startTime, freeSlot.endTime, preferred.startTime, preferred.endTime);
            return overlap;
          });
          if (!isPreferred) {
            console.log(`    ⚠️ 건너뜀: preferredTimeSlots 설정 있으나 선호 시간대 아님`);
            console.log(`      설정된 선호 시간대:`, preferences.preferredTimeSlots);
            skippedByPreferences++;
            skipSlot = true;
          } else {
            console.log(`    ✅ 선호 시간대에 포함됨`);
          }
        } else if (!skipSlot) {
          console.log(`    ✅ 선호 시간대 미설정 또는 비어있음, 모든 시간 허용`);
        }
      } else {
        console.log(`    ✅ preferences 미설정, 모든 시간 허용`);
      }
      
      if (skipSlot) {
        continue;
      }

      const slotDuration = calculateDuration(freeSlot.startTime, freeSlot.endTime);
      console.log(`    ⏱️ 슬롯 길이: ${slotDuration}시간 (${slotDuration * 60}분)`);
      
      // 먼저 정확히 맞는 과제를 찾고, 없으면 더 작은 과제를 찾음
      let suitableAssignment = pendingAssignments.find(assignment => {
        const notUsed = !usedAssignments.has(assignment.id);
        const fits = assignment.remainingTime <= slotDuration * 60;
        
        if (!notUsed) {
          console.log(`      ⏭️ "${assignment.title}": 이미 사용됨`);
        } else if (!fits) {
          console.log(`      ⏭️ "${assignment.title}": 시간 부족 (필요: ${assignment.remainingTime}분 > 가능: ${slotDuration * 60}분)`);
        } else {
          console.log(`      ✅ "${assignment.title}": 매칭 성공! (필요: ${assignment.remainingTime}분 <= 가능: ${slotDuration * 60}분)`);
        }
        
        return notUsed && fits;
      });

      if (suitableAssignment) {
        const progress = suitableAssignment.progress || 0;
        let reason = progress > 0 
          ? `진도율 ${progress}%, 남은 시간 ${suitableAssignment.remainingTime}분 - ${freeSlot.day}요일 ${freeSlot.startTime}-${freeSlot.endTime} 공강 시간 활용`
          : `${suitableAssignment.estimatedTime}분 소요 예상 - ${freeSlot.day}요일 ${freeSlot.startTime}-${freeSlot.endTime} 공강 시간 활용`;

        newRecommendations.push({
          timeSlot: freeSlot,
          assignment: suitableAssignment,
          reason
        });
        usedAssignments.add(suitableAssignment.id);
        console.log(`    ➕ 추천에 추가됨 (총 ${newRecommendations.length}개)`);
      } else {
        console.log(`    ⚪ 적합한 과제 없음`);
      }
    }
    
    console.log(`\n🎉 최종 추천 수: ${newRecommendations.length}개`);
    if (newRecommendations.length === 0) {
      console.log('⚠️ 추천이 생성되지 않은 이유 요약:');
      console.log('  1. 공강 슬롯 수:', freeSlots.length);
      console.log('  2. 대기 중인 과제 수:', pendingAssignments.length);
      console.log('  3. preferences 설정:', preferences);
      console.log('  4. 피하고 싶은 시간대로 건너뛴 슬롯:', skippedByAvoid);
      console.log('  5. 선호 시간대 필터로 건너뛴 슬롯:', skippedByPreferences);
      
      if (freeSlots.length === 0) {
        console.log('  ❌ 문제: 공강 슬롯이 없습니다. 시간표를 확인하세요.');
      } else if (pendingAssignments.length === 0) {
        console.log('  ❌ 문제: AI에 추가된 미완료 과제가 없습니다.');
      } else if (skippedByPreferences > 0 && skippedByPreferences === freeSlots.length) {
        console.log('  ❌ 문제: 모든 공강 슬롯이 선호 시간대 필터로 제외되었습니다.');
        console.log('  💡 해결방법: 설정에서 선호 시간대를 조정하거나 제거하세요.');
      } else if (skippedByAvoid === freeSlots.length) {
        console.log('  ❌ 문제: 모든 공강 슬롯이 피하고 싶은 시간대로 제외되었습니다.');
        console.log('  💡 해결방법: 설정에서 피하고 싶은 시간대를 조정하세요.');
      } else {
        console.log('  ⚠️ 문제: 공강 슬롯과 과제가 있지만 매칭되지 않습니다.');
        console.log('  💡 가능한 원인:');
        console.log('     - 모든 과제의 소요 시간이 공강 슬롯보다 김');
        console.log('     - 필터 설정이 너무 엄격함');
        
        // 추가 분석: 최소/최대 슬롯 길이와 과제 시간 비교
        if (freeSlots.length > 0 && pendingAssignments.length > 0) {
          const slotDurations = freeSlots.map(slot => calculateDuration(slot.startTime, slot.endTime) * 60);
          const maxSlotDuration = Math.max(...slotDurations);
          const minAssignmentTime = Math.min(...pendingAssignments.map(a => a.remainingTime));
          
          console.log(`  📊 가장 긴 공강 슬롯: ${maxSlotDuration}분`);
          console.log(`  📊 가장 짧은 과제 시간: ${minAssignmentTime}분`);
          
          if (minAssignmentTime > maxSlotDuration) {
            console.log('  ❌ 원인 확인: 모든 과제가 가장 긴 공강 슬롯보다 깁니다.');
            console.log('  💡 해결방법: 과제를 더 작은 단위로 나누거나, 예상 시간을 줄이세요.');
          }
        }
      }
    } else {
      console.log('✅ 생성된 추천:', newRecommendations);
    }
    console.log('========== generateRecommendations 완료 ==========\n');
    setRecommendations(newRecommendations);
  };

  const findFreeSlots = (scheduleData: TimeSlot[]): TimeSlot[] => {
    console.log('🔍 [findFreeSlots] 시작');
    console.log('📅 scheduleData:', scheduleData);
    
    const days = ['월', '화', '수', '목', '금'];
    const freeSlots: TimeSlot[] = [];
    const schoolHours = [
      { start: '09:00', end: '10:00' },
      { start: '10:00', end: '11:00' },
      { start: '11:00', end: '12:00' },
      { start: '13:00', end: '14:00' },
      { start: '14:00', end: '15:00' },
      { start: '15:00', end: '16:00' },
      { start: '16:00', end: '17:00' }
    ];

    days.forEach(day => {
      const daySchedule = scheduleData.filter(s => s.day === day);
      console.log(`  📌 ${day}요일 수업:`, daySchedule);
      
      let dayFreeCount = 0;
      schoolHours.forEach(hour => {
        const hasClass = daySchedule.some(slot => {
          const overlap = timeOverlaps(hour.start, hour.end, slot.startTime, slot.endTime);
          if (overlap) {
            console.log(`    ❌ ${hour.start}-${hour.end}: ${slot.subject}와 겹침`);
          }
          return overlap;
        });
        
        if (!hasClass) {
          freeSlots.push({
            day,
            startTime: hour.start,
            endTime: hour.end
          });
          dayFreeCount++;
          console.log(`    ✅ ${hour.start}-${hour.end}: 공강`);
        }
      });
      console.log(`  ➡️ ${day}요일 공강 시간: ${dayFreeCount}개`);
    });

    console.log('✨ 총 공강 슬롯:', freeSlots.length, freeSlots);
    return freeSlots;
  };

  // 시간 문자열을 분 단위 숫자로 변환 (HH:MM -> 분)
  const timeToMinutes = (time: string): number => {
    const [hour, min] = time.split(':').map(Number);
    return hour * 60 + min;
  };

  // 시간 형식 정규화 (다양한 형식을 HH:MM으로 통일)
  const normalizeTime = (time: string): string => {
    // "9:00", "09:00", "9시", "09시 00분" 등을 "09:00" 형식으로 변환
    const timeStr = time.replace(/시|분|\s/g, '');
    const match = timeStr.match(/^(\d{1,2}):?(\d{2})?$/);
    
    if (!match) return time; // 파싱 실패 시 원본 반환
    
    const hour = match[1].padStart(2, '0');
    const minute = match[2] || '00';
    return `${hour}:${minute}`;
  };

  const timeOverlaps = (start1: string, end1: string, start2: string, end2: string): boolean => {
    // 시간을 분 단위 숫자로 변환하여 정확히 비교
    const s1 = timeToMinutes(normalizeTime(start1));
    const e1 = timeToMinutes(normalizeTime(end1));
    const s2 = timeToMinutes(normalizeTime(start2));
    const e2 = timeToMinutes(normalizeTime(end2));
    
    const result = s1 < e2 && e1 > s2;
    // 디버깅이 필요한 경우에만 주석 해제
    // console.log(`    🔄 timeOverlaps(${start1}[${s1}], ${end1}[${e1}], ${start2}[${s2}], ${end2}[${e2}]) = ${result}`);
    return result;
  };

  const calculateDuration = (startTime: string, endTime: string): number => {
    const start = timeToMinutes(normalizeTime(startTime));
    const end = timeToMinutes(normalizeTime(endTime));
    const duration = (end - start) / 60;
    // 디버깅이 필요한 경우에만 주석 해제
    // console.log(`    ⏰ calculateDuration(${startTime}, ${endTime}) = ${duration}시간`);
    return duration;
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'home':
        return (
          <HomeTab
            viewMode={viewMode}
            onViewModeChange={setViewMode}
            currentDate={currentDate}
            onDateChange={setCurrentDate}
            timetables={timetables}
            currentTimetableId={currentTimetableId}
            onTimetableChange={setCurrentTimetableId}
            onAddTimetable={handleAddTimetable}
            onRenameTimetable={handleRenameTimetable}
            onDeleteTimetable={handleDeleteTimetable}
          >
            {viewMode === 'daily' && (
              <DailyView
                schedule={schedule}
                recommendations={recommendations}
                currentDate={currentDate}
                assignments={assignments}
              />
            )}
            {viewMode === 'weekly' && (
              <WeeklyView
                schedule={schedule}
                recommendations={recommendations}
                currentDate={currentDate}
                assignments={assignments}
              />
            )}
            {viewMode === 'monthly' && (
              <MonthlyView
                schedule={schedule}
                recommendations={recommendations}
                currentDate={currentDate}
                hideClasses={preferences?.hideClassesInMonthly || false}
                assignments={assignments}
              />
            )}
          </HomeTab>
        );

      case 'task':
        return (
          <TaskTab>
            <AssignmentSchedule
              assignments={assignments}
              onAssignmentsUpdated={handleAssignmentsUpdated}
              onApplyAI={handleAddToAI}
            />
          </TaskTab>
        );

      case 'grades':
        return <GradesTab />;

      case 'settings':
        return (
          <div className="p-4">
            <h2 className="mb-4">설정</h2>
            <PreferencesForm 
              onSave={handlePreferencesSaved}
              initialPreferences={preferences || undefined}
            />
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <>
      <Toaster />
      <MobileLayout
        activeTab={activeTab}
        onTabChange={setActiveTab}
      >
        {renderContent()}
      </MobileLayout>
    </>
  );
}
