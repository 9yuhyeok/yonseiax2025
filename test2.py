import streamlit as st
import streamlit.components.v1 as components
import json

# -------------------------------------------------
# 1. 페이지 설정 및 상태 초기화
# -------------------------------------------------
st.set_page_config(page_title="AI Timetable", layout="wide") # wide layout으로 변경
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "홈"
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "주간" # 기본 뷰 모드

# -------------------------------------------------
# 2. 데이터 (스크린샷 기반)
# -------------------------------------------------

# [새로운 데이터 추가: 월간 뷰를 위한 더미 데이터]
timetable_data = [
    {"day": "월", "date": "12-02", "start": "09:00", "end": "10:00", "title": "데이터구조", "kind": "class", "day_of_week": "월"},
    {"day": "월", "date": "12-02", "start": "10:00", "end": "11:00", "title": "데이터구조 과제", "kind": "task", "sub": "연결리스트 구현", "day_of_week": "월"},
    {"day": "월", "date": "12-02", "start": "11:00", "end": "12:00", "title": "알고리즘", "kind": "class", "day_of_week": "월"},
    {"day": "월", "date": "12-02", "start": "13:00", "end": "13:50", "title": "알고리즘 숙제", "kind": "task", "sub": "50분", "day_of_week": "월"},
    
    {"day": "화", "date": "12-03", "start": "09:00", "end": "10:00", "title": "운영체제", "kind": "class", "day_of_week": "화"},
    {"day": "화", "date": "12-03", "start": "14:00", "end": "15:00", "title": "데이터베이스", "kind": "class", "day_of_week": "화"},
    
    {"day": "수", "date": "12-04", "start": "10:00", "end": "11:00", "title": "네트워크", "kind": "class", "day_of_week": "수"},
    
    {"day": "목", "date": "12-05", "start": "09:00", "end": "10:00", "title": "소프트웨어공학", "kind": "class", "day_of_week": "목"},
    
    {"day": "금", "date": "12-06", "start": "09:00", "end": "10:00", "title": "데이터구조 과제", "kind": "task", "sub": "스택/큐 구현", "day_of_week": "금"},
    {"day": "금", "date": "12-06", "start": "13:00", "end": "14:00", "title": "인공지능", "kind": "class", "day_of_week": "금"},

    # 월간 뷰를 위한 다음 주 데이터 (더미)
    {"day": "월", "date": "12-09", "start": "10:00", "end": "11:00", "title": "AI 특강", "kind": "class", "day_of_week": "월"},
    {"day": "수", "date": "12-11", "start": "14:00", "end": "15:00", "title": "팀 프로젝트 회의", "kind": "task", "day_of_week": "수"},
]

# -------------------------------------------------
# 3. HTML/CSS 템플릿 (CSS Grid 기반 시간표)
# -------------------------------------------------

def get_timetable_html(view_mode, data):
    # Python 데이터를 JSON 문자열로 변환하여 JavaScript에서 사용
    data_json = json.dumps(data)
    
    # 시간표를 렌더링하는 HTML/CSS/JavaScript 코드 (하나의 문자열)
    # 이 코드는 Streamlit의 components.html()을 통해 안전하게 렌더링됩니다.
    html_template = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; margin: 0; padding: 0; }}
            
            /* --- 시간표 그리드 디자인 --- */
            .timetable-wrapper {{
                background: white;
                border-radius: 15px;
                border: 1px solid #e5e7eb;
                overflow: hidden;
                margin-top: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.02);
                min-height: 500px; /* 최소 높이 설정 */
            }}
            .timetable-header {{
                display: grid;
                grid-template-columns: 40px repeat({len(["월", "화", "수", "목", "금"]) if view_mode == "주간" else 1}, 1fr);
                background: #f9fafb;
                border-bottom: 1px solid #e5e7eb;
                text-align: center;
                font-size: 12px;
                font-weight: 600;
                color: #6b7280;
                padding: 8px 0;
            }}
            .timetable-body {{
                display: grid;
                /* 시간 축(40px) + 5개 요일(1fr) */
                grid-template-columns: 40px repeat({len(["월", "화", "수", "목", "금"]) if view_mode == "주간" else 1}, 1fr);
                /* 9시~16시 (7시간) -> 10분 단위 grid = 42 rows */
                grid-template-rows: repeat(42, 10px); 
                position: relative;
                overflow-y: auto;
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
                line-height: 1;
                z-index: 5;
                background-color: white;
            }}
            .grid-bg-cell {{
                border-right: 1px solid #f3f4f6;
                border-bottom: 1px solid #f3f4f6;
            }}
            
            /* 이벤트 카드 스타일 */
            .event-item {{
                position: absolute; /* 이벤트를 배경 셀 위에 절대 위치로 배치 */
                width: calc(100% - 2px);
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
            .evt-title {{ font-weight: 700; margin-bottom: 2px; }}
            .evt-time {{ font-size: 9px; opacity: 0.8; }}

            /* 일간/월간 뷰 조정 */
            {f'.timetable-header div:not(:first-child) {{ grid-column: 2; }}' if view_mode == '일간' else ''}
            {f'.timetable-body div:not(:first-child) {{ grid-column: 2; }}' if view_mode == '일간' else ''}
            
            /* 월간 뷰: 주간 뷰의 일주일만 보여주는 것으로 간주 (실제 월간 캘린더는 구현 복잡도가 높음) */
            {f'.timetable-header div:not(:first-child) {{ grid-column: 2; }}' if view_mode == '월간' else ''}
            {f'.timetable-body div:not(:first-child) {{ grid-column: 2; }}' if view_mode == '월간' else ''}

        </style>
    </head>
    <body>
        <div class="timetable-wrapper">
            <div class="timetable-header" id="header"></div>
            <div class="timetable-body" id="body"></div>
        </div>

        <script>
            const timetableData = {data_json};
            const viewMode = "{view_mode}";
            const days = ["월", "화", "수", "목", "금"];
            const startHour = 9;

            function renderGrid(data) {{
                const headerEl = document.getElementById('header');
                const bodyEl = document.getElementById('body');
                headerEl.innerHTML = '<div></div>';
                bodyEl.innerHTML = '';

                // --- 1. 헤더 렌더링 ---
                if (viewMode === '주간') {{
                    days.forEach(d => {{ headerEl.innerHTML += `<div>${{d}}</div>`; }});
                }} else if (viewMode === '일간') {{
                    headerEl.innerHTML += `<div>월</div>`; // 임시로 월요일만 표시
                }} else {{ // 월간 (주간과 동일하게 표시)
                     days.forEach(d => {{ headerEl.innerHTML += `<div>${{d}}</div>`; }});
                }}

                // --- 2. 배경 그리드 및 시간 라벨 렌더링 ---
                for (let h = startHour; h < 16; h++) {{ // 9시부터 15시까지
                    const rowStart = (h - startHour) * 6 + 1; // 10분 단위로 6칸
                    
                    // 시간 라벨 (9, 10, 11...)
                    bodyEl.innerHTML += `<div class="time-label" style="grid-column: 1; grid-row: ${{rowStart}} / span 6;">${{h}}</div>`;
                    
                    // 배경 셀 (라인)
                    const numCols = viewMode === '주간' ? 5 : 1;
                    for (let c = 0; c < numCols; c++) {{
                        const col = c + 2; // 2부터 월요일 시작
                        for (let r = 0; r < 6; r++) {{ // 1시간당 6칸 (10분 단위)
                           bodyEl.innerHTML += `<div class="grid-bg-cell" style="grid-column: ${{col}}; grid-row: ${{rowStart + r}};"></div>`;
                        }}
                    }}
                }}

                // --- 3. 이벤트 배치 ---
                data.forEach(item => {{
                    const dIdx = days.indexOf(item.day_of_week);
                    if (dIdx === -1) return;

                    const [sh, sm] = item.start.split(":").map(Number);
                    const [eh, em] = item.end.split(":").map(Number);
                    
                    const startMin = (sh - startHour) * 60 + sm;
                    const durationMin = (eh * 60 + em) - (sh * 60 + sm);
                    
                    const gRow = Math.floor(startMin / 10) + 1;
                    const gSpan = Math.ceil(durationMin / 10);
                    const gCol = (viewMode === '주간' || viewMode === '월간') ? dIdx + 2 : 2; 

                    const cls = item.kind === "class" ? "evt-class" : "evt-task";
                    const subTxt = item.sub ? `<div class='evt-time'>${{item.sub}}</div>` : "";
                    
                    const eventHTML = `
                        <div class="event-item ${{cls}}" style="
                            grid-column: ${{gCol}};
                            grid-row: ${{gRow}} / span ${{gSpan}};
                            /* Absolute positioning within the grid area */
                            top: 0; left: 0; 
                            height: 100%;
                        ">
                            <div class="evt-title">${{item.title}}</div>
                            ${{subTxt}}
                        </div>
                    `;
                    
                    // 이벤트 블록을 배경 셀 대신 바디에 직접 absolute 위치로 삽입
                    // grid-area를 사용하여 위치를 지정하고 absolute로 블록 자체를 띄워 깨짐 현상을 방지합니다.
                    const eventEl = document.createElement('div');
                    eventEl.innerHTML = eventHTML;
                    eventEl.firstChild.style.gridArea = `${gRow} / ${gCol} / span ${gSpan} / span 1`;
                    
                    // 100% 높이를 설정하여 이벤트 블록의 크기를 그리드 셀의 크기에 맞춥니다.
                    eventEl.firstChild.style.height = `${gSpan * 10}px`; 
                    eventEl.firstChild.style.width = 'calc(100% - 2px)'; // 폭 조정
                    eventEl.firstChild.style.position = 'absolute'; 
                    eventEl.firstChild.style.top = `${(gRow - 1) * 10}px`;
                    eventEl.firstChild.style.left = `${(gCol - 1) * (bodyEl.offsetWidth / (days.length + 1))}px`;

                    bodyEl.appendChild(eventEl.firstChild);
                }});
            }}

            // 렌더링 시작
            renderGrid(timetableData);
        </script>
    </body>
    </html>
    """
    return html_template

# -------------------------------------------------
# 4. Streamlit UI 렌더링
# -------------------------------------------------
tab = st.session_state.active_tab
view_mode = st.session_state.view_mode

# 하단 탭 스타일을 위해 마크다운 사용 (상단에 CSS 정의됨)
st.markdown("""
<style>
    /* Streamlit 버튼 스타일 오버라이드 (일간/주간/월간 버튼) */
    div[data-testid="stButton"] > button {
        height: 35px;
        border-radius: 8px;
        font-weight: 600;
        border: 1px solid #e5e7eb;
        background-color: white;
        color: #4b5563;
    }
    div[data-testid="stButton"] button[data-testid="stColorableButton"] {
        background-color: #f87171 !important; /* 주간: 빨간색 */
        color: white !important;
        border-color: #f87171 !important;
    }
    /* 상단 영역 padding 제거 */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
    }
</style>
""", unsafe_allow_html=True)


# --- [탭: 홈] ---
if tab == "홈":
    # 1. 상단 제목 및 날짜
    st.markdown("### 📅 2025년 12월 1주차")
    
    # 2. 뷰 모드 버튼 (클릭 가능하게 수정)
    c1, c2, c3 = st.columns(3)
    
    # 클릭 시 view_mode 세션 상태 업데이트
    if c1.button("일간", use_container_width=True, type=("primary" if view_mode == "일간" else "secondary")):
        st.session_state.view_mode = "일간"
        st.rerun()
        
    if c2.button("주간", use_container_width=True, type=("primary" if view_mode == "주간" else "secondary")):
        st.session_state.view_mode = "주간"
        st.rerun()
        
    if c3.button("월간", use_container_width=True, type=("primary" if view_mode == "월간" else "secondary")):
        st.session_state.view_mode = "월간"
        st.rerun()
    
    # 3. 시간표 데이터 필터링 (뷰 모드에 따라)
    filtered_data = []
    
    if view_mode == "주간" or view_mode == "일간":
        # 현재 주 (12월 1주차 데이터만 사용)
        filtered_data = [item for item in timetable_data if item['date'].startswith('12-0')]
    elif view_mode == "월간":
        # 월간은 모든 데이터 사용 (12월 전체)
        filtered_data = timetable_data

    # 4. 시간표 렌더링
    # 일간 뷰는 월요일만 표시하도록 데이터 필터링 (임시 구현)
    display_data = filtered_data
    if view_mode == "일간":
        display_data = [item for item in filtered_data if item['day_of_week'] == '월']

    # HTML 템플릿 호출 및 렌더링 (HTML 렌더링 깨짐 현상 방지)
    # st.markdown 대신 st.components.v1.html 사용
    html_content = get_timetable_html(view_mode, display_data)
    components.html(html_content, height=580, scrolling=True)


    # 5. 범례 (HTML 렌더링 후 별도 출력)
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

# --- [다른 탭] ---
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
# 하단 탭 로직은 이전 코드와 동일하게 유지
tabs = ["🏠\n홈", "✅\n과제", "✨\nAI", "⚙️\n설정"]
tab_icons = {"홈": "🏠", "과제": "✅", "AI": "✨", "설정": "⚙️"}

selected = st.radio(
    "bottom_nav", 
    tabs, 
    index=tabs.index(f"{tab_icons[st.session_state.active_tab]}\n{st.session_state.active_tab}"), 
    horizontal=True, 
    label_visibility="collapsed",
    key="nav"
)

new_tab = selected.split("\n")[1]
if new_tab != st.session_state.active_tab:
    st.session_state.active_tab = new_tab
    st.rerun()
