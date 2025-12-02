import streamlit as st

# -------------------------------------------------
# 1. 페이지 설정 및 상태 초기화
# -------------------------------------------------
st.set_page_config(page_title="AI Timetable", layout="centered")

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "홈"  # 기본 탭

# -------------------------------------------------
# 2. CSS 스타일 (하단 탭 & 시간표 완벽 구현)
# -------------------------------------------------
st.markdown("""
<style>
    /* 전체 배경 및 여백 설정 */
    .stApp {
        background-color: #f8f9fa;
        margin-bottom: 80px; /* 하단 탭 공간 확보 */
    }
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 5rem;
        max-width: 100%;
    }

    /* --- [수정됨] 하단 탭 네비게이션 (스크린샷 스타일) --- */
    /* 라디오 버튼을 하단 고정 탭으로 변신시키는 CSS */
    div[data-testid="stRadio"] {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: white;
        border-top: 1px solid #e5e7eb;
        z-index: 9999;
        padding: 8px 0 12px 0;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
    }
    div[data-testid="stRadio"] > label {
        display: none !important; /* 라디오 라벨 숨김 */
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex;
        justify-content: space-around; /* 간격 균등 배치 */
        width: 100%;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
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
    }
    
    /* 탭 내부 텍스트/아이콘 스타일 */
    div[data-testid="stRadio"] p {
        font-size: 10px;
        margin: 0;
        line-height: 1.2;
        text-align: center;
        color: #9ca3af; /* 선택 안됨: 회색 */
    }
    
    /* 선택된 탭 스타일 */
    div[data-testid="stRadio"] label[data-checked="true"] p {
        color: #4f46e5 !important; /* 선택됨: 파란색 */
        font-weight: 700;
    }
    
    /* 아이콘 크기 키우기 (이모지) */
    div[data-testid="stRadio"] p span {
        display: block;
        font-size: 20px;
        margin-bottom: 2px;
    }

    /* --- [수정됨] 시간표 그리드 디자인 --- */
    .timetable-wrapper {
        background: white;
        border-radius: 15px;
        border: 1px solid #e5e7eb;
        overflow: hidden;
        margin-top: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .timetable-header {
        display: grid;
        grid-template-columns: 40px repeat(5, 1fr);
        background: #f9fafb;
        border-bottom: 1px solid #e5e7eb;
        text-align: center;
        font-size: 12px;
        font-weight: 600;
        color: #6b7280;
        padding: 8px 0;
    }
    .timetable-body {
        display: grid;
        grid-template-columns: 40px repeat(5, 1fr);
        /* 9시~16시 (7시간) -> 10분 단위 grid */
        grid-template-rows: repeat(42, 10px); 
        position: relative;
    }
    .time-label {
        font-size: 10px;
        color: #9ca3af;
        text-align: center;
        border-right: 1px solid #f3f4f6;
        border-bottom: 1px solid #f3f4f6;
        display: flex;
        align-items: start;
        justify-content: center;
        padding-top: 2px;
    }
    .grid-bg-cell {
        border-right: 1px solid #f3f4f6;
        border-bottom: 1px solid #f3f4f6;
    }
    
    /* 이벤트 카드 스타일 */
    .event-item {
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
    }
    .evt-class {
        background-color: #dcfce7;
        border-left: 3px solid #22c55e;
        color: #14532d;
    }
    .evt-task {
        background-color: #fef9c3;
        border-left: 3px solid #eab308;
        color: #854d0e;
    }
    .evt-title { font-weight: 700; margin-bottom: 2px; }
    .evt-time { font-size: 9px; opacity: 0.8; }
    
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 3. 데이터 및 로직
# -------------------------------------------------

# 시간표 데이터 (스크린샷과 동일)
timetable_data = [
    {"day": "월", "start": "09:00", "end": "10:00", "title": "데이터구조", "kind": "class"},
    {"day": "월", "start": "10:00", "end": "11:00", "title": "데이터구조 과제", "kind": "task", "sub": "연결리스트 구현"},
    {"day": "월", "start": "11:00", "end": "12:00", "title": "알고리즘", "kind": "class"},
    {"day": "월", "start": "13:00", "end": "13:50", "title": "알고리즘 숙제", "kind": "task", "sub": "50분"},
    
    {"day": "화", "start": "09:00", "end": "10:00", "title": "운영체제", "kind": "class"},
    {"day": "화", "start": "14:00", "end": "15:00", "title": "데이터베이스", "kind": "class"},
    
    {"day": "수", "start": "10:00", "end": "11:00", "title": "네트워크", "kind": "class"},
    
    {"day": "목", "start": "09:00", "end": "10:00", "title": "소프트웨어공학", "kind": "class"},
    
    {"day": "금", "start": "09:00", "end": "10:00", "title": "데이터구조 과제", "kind": "task", "sub": "스택/큐 구현"},
    {"day": "금", "start": "13:00", "end": "14:00", "title": "인공지능", "kind": "class"},
]

def render_timetable():
    days = ["월", "화", "수", "목", "금"]
    day_map = {d: i for i, d in enumerate(days)}
    
    # 9시부터 16시까지 (총 7시간)
    start_hour = 9
    
    # --- HTML 조립 시작 ---
    html = '<div class="timetable-wrapper">'
    
    # 1. 헤더 (요일)
    html += '<div class="timetable-header"><div></div>'
    for d in days:
        html += f'<div>{d}</div>'
    html += '</div>'
    
    # 2. 바디 (그리드)
    html += '<div class="timetable-body">'
    
    # 배경 그리드 (시간축 + 빈칸)
    # 1시간 = 6칸 (10분 단위)
    for h in range(9, 17): # 9, 10 ... 16
        # 시간 표시 (6칸 차지)
        row_start = (h - 9) * 6 + 1
        html += f'<div class="time-label" style="grid-column: 1; grid-row: {row_start} / span 6;">{h}</div>'
        
        # 나머지 요일 빈칸 (배경선 용도)
        for col in range(2, 7):
            html += f'<div class="grid-bg-cell" style="grid-column: {col}; grid-row: {row_start} / span 6;"></div>'

    # 이벤트 배치
    for item in timetable_data:
        d_idx = day_map.get(item["day"])
        if d_idx is None: continue
        
        # 시간 파싱
        sh, sm = map(int, item["start"].split(":"))
        eh, em = map(int, item["end"].split(":"))
        
        # 분 단위 변환
        start_min = (sh - 9) * 60 + sm
        duration_min = (eh * 60 + em) - (sh * 60 + sm)
        
        # 그리드 좌표 계산 (10분 = 1 row)
        g_row = int(start_min / 10) + 1
        g_span = int(duration_min / 10)
        g_col = d_idx + 2 # 1은 시간축, 2부터 월요일
        
        # 스타일링
        cls = "evt-class" if item["kind"] == "class" else "evt-task"
        sub_txt = f"<div class='evt-time'>{item['sub']}</div>" if 'sub' in item else ""
        
        # HTML 삽입 (여기가 중요: f-string 안에서 깔끔하게 처리)
        html += f"""
        <div class="event-item {cls}" style="grid-column: {g_col}; grid-row: {g_row} / span {g_span};">
            <div class="evt-title">{item['title']}</div>
            {sub_txt}
        </div>
        """
        
    html += '</div></div>' # body, wrapper 닫기
    
    # Streamlit에 렌더링 (여기가 핵심: html 변수를 한 번에 출력)
    st.markdown(html, unsafe_allow_html=True)
    
    # 범례
    st.markdown("""
    <div style="display:flex; justify-content:flex-end; gap:12px; margin-top:8px; font-size:12px; color:#6b7280;">
        <span style="display:flex; align-items:center;">
            <span style="width:8px; height:8px; background:#22c55e; border-radius:50%; margin-right:4px;"></span>수업
        </span>
        <span style="display:flex; align-items:center;">
            <span style="width:8px; height:8px; background:#eab308; border-radius:50%; margin-right:4px;"></span>과제
        </span>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# 4. 메인 화면 구성
# -------------------------------------------------
tab = st.session_state.active_tab

if tab == "홈":
    st.markdown("### 📅 2025년 12월 1주차")
    
    # 뷰 모드 버튼 (모양만 구현)
    c1, c2, c3 = st.columns(3)
    c1.button("일간", use_container_width=True, disabled=True)
    c2.button("주간", use_container_width=True, type="primary")
    c3.button("월간", use_container_width=True)
    
    render_timetable()

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
# 줄바꿈(\n)을 이용해서 아이콘을 위로, 텍스트를 아래로 배치
tabs = ["🏠\n홈", "✅\n과제", "✨\nAI", "⚙️\n설정"]

# 라디오 버튼을 그리지만 CSS로 숨기고 커스텀 탭처럼 보이게 함
selected = st.radio(
    "bottom_nav", 
    tabs, 
    index=tabs.index(f"🏠\n{st.session_state.active_tab}") if f"🏠\n{st.session_state.active_tab}" in tabs else 0, # 현재 탭 유지 로직
    horizontal=True, 
    label_visibility="collapsed",
    key="nav"
)

# 탭 전환 로직 (선택된 텍스트에서 이모지 제거하고 상태 업데이트)
new_tab = selected.split("\n")[1]
if new_tab != st.session_state.active_tab:
    st.session_state.active_tab = new_tab
    st.rerun()
