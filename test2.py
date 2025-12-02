<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>시간표 1</title>
    <style>
        /* 기본 스타일 초기화 */
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #fff;
            color: #333;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }

        /* ---------------------------------------------------- */
        /* 헤더 (상단) */
        /* ---------------------------------------------------- */

        .header {
            padding: 10px 15px;
            border-bottom: 1px solid #eee;
        }

        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .title-section {
            font-size: 1.2em;
            font-weight: bold;
            display: flex;
            align-items: center;
        }

        .date-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: bold;
            padding: 10px 0;
        }

        .date-nav .arrow {
            font-size: 1.5em;
            cursor: pointer;
            padding: 0 10px;
        }
        
        .view-toggle {
            display: flex;
            background-color: #f0f0f0;
            border-radius: 8px;
            padding: 3px;
            font-size: 0.9em;
        }

        .view-toggle button {
            background: none;
            border: none;
            padding: 5px 15px;
            cursor: pointer;
            border-radius: 6px;
            font-weight: 500;
        }

        .view-toggle .active {
            background-color: #fff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            font-weight: bold;
        }

        /* ---------------------------------------------------- */
        /* 시간표 그리드 (메인) */
        /* ---------------------------------------------------- */

        .grid-view-container {
            flex-grow: 1;
            overflow-y: auto;
            display: grid;
            /* 첫 번째 컬럼(시간) 너비 고정, 나머지 5개 요일 균등 분할 */
            grid-template-columns: 50px repeat(5, 1fr); 
            /* 첫 번째 행(요일 헤더) 높이 고정 */
            grid-template-rows: 40px repeat(7, 1fr); 
            min-height: 500px;
        }

        /* 요일 헤더 스타일 (월, 화, 수, 목, 금) */
        .day-header {
            grid-row: 1;
            text-align: center;
            line-height: 40px;
            border-bottom: 1px solid #ddd;
            border-right: 1px solid #eee;
            font-size: 0.9em;
            font-weight: bold;
            color: #777;
        }

        /* 시간 컬럼 스타일 */
        .time-label {
            grid-column: 1;
            text-align: right;
            padding-right: 5px;
            font-size: 0.8em;
            color: #999;
            border-bottom: 1px solid #eee;
            border-right: 1px solid #ddd;
            line-height: 1;
            display: flex;
            align-items: flex-start;
            justify-content: flex-end;
        }

        /* 시간표 셀 (그리드 영역) */
        .grid-cell {
            border-bottom: 1px solid #eee;
            border-right: 1px solid #eee;
            box-sizing: border-box;
            position: relative;
        }
        .grid-view-container .grid-cell:nth-child(5n+1) {
             /* 월요일 컬럼의 왼쪽 경계 */
             border-left: 1px solid #ddd; 
        }
        .grid-view-container .grid-cell:nth-last-child(-n+5) {
            /* 마지막 행의 하단 경계 제거 (footer와 겹치지 않게) */
            border-bottom: none; 
        }


        /* 과목 블록 스타일 */
        .class-block {
            position: absolute;
            width: calc(100% - 2px); /* 100%에서 경계선 제외 */
            box-sizing: border-box;
            margin: 1px;
            padding: 5px;
            border-radius: 6px;
            font-size: 0.9em;
            font-weight: bold;
            color: #333;
            overflow: hidden;
            z-index: 10;
        }

        /* 색상 지정 */
        .green { background-color: #a8e6cf; } /* 운영체제, 네트워크, 소프트웨어 공학, 데이터베이스 */
        .light-green { background-color: #dcf2e3; } /* 데이터구조, 알고리즘 */
        .yellow { background-color: #fce8a9; } /* 과제 블록 */
        .pink { background-color: #ffb7c5; } /* 인공지능 */

        .assignment-text {
            font-size: 0.8em;
            font-weight: normal;
            margin-top: 3px;
        }
        
        /* ---------------------------------------------------- */
        /* 하단 네비게이션 (Footer) */
        /* ---------------------------------------------------- */

        .bottom-nav {
            display: flex;
            justify-content: space-around;
            padding: 10px 0;
            border-top: 1px solid #eee;
            background-color: #fff;
            position: sticky;
            bottom: 0;
        }

        .nav-item {
            text-align: center;
            font-size: 0.7em;
            color: #999;
        }
        .nav-item.active {
            color: #007bff; /* 활성화된 항목 색상 (파란색 예시) */
        }
        .nav-item div {
            font-size: 1.5em;
            margin-bottom: 3px;
        }
    </style>
</head>
<body>

    <header class="header">
        <div class="top-bar">
            <div class="title-section">
                시간표 1 
                <span style="font-size: 0.8em; color: #aaa; margin-left: 5px;">&#9998;</span>
            </div>
            <div style="font-size: 1.5em;">+</div>
        </div>
        <div class="date-nav">
            <span class="arrow">&lt;</span>
            <span>**2025년 12월 1주차**</span>
            <span class="arrow">&gt;</span>
        </div>
        <div class="view-toggle">
            <button>일간</button>
            <button class="active">주간</button>
            <button>월간</button>
        </div>
    </header>

    <div class="grid-view-container" id="timetableGrid">
        <div class="time-label" style="grid-row: 2;">9</div>
        <div class="time-label" style="grid-row: 3;">10</div>
        <div class="time-label" style="grid-row: 4;">11</div>
        <div class="time-label" style="grid-row: 5;">12</div>
        <div class="time-label" style="grid-row: 6;">13</div>
        <div class="time-label" style="grid-row: 7;">14</div>
        <div class="time-label" style="grid-row: 8;">15</div>

        <div class="day-header" style="grid-column: 2;">월</div>
        <div class="day-header" style="grid-column: 3;">화</div>
        <div class="day-header" style="grid-column: 4;">수</div>
        <div class="day-header" style="grid-column: 5;">목</div>
        <div class="day-header" style="grid-column: 6;">금</div>

        <script>
            const gridContainer = document.getElementById('timetableGrid');
            for (let r = 2; r <= 8; r++) { // 9시(2행)부터 15시(8행)까지
                for (let c = 2; c <= 6; c++) { // 월(2열)부터 금(6열)까지
                    const cell = document.createElement('div');
                    cell.className = 'grid-cell';
                    cell.style.gridRow = r;
                    cell.style.gridColumn = c;
                    cell.dataset.row = r;
                    cell.dataset.col = c;
                    gridContainer.appendChild(cell);
                }
            }
        </script>
        
        <div class="class-block light-green" style="grid-column: 2; grid-row: 2;">
            데이터구조
        </div>
        <div class="class-block yellow" style="grid-column: 2; grid-row: 3 / span 1;">
            데이터구조 과제 ...
            <div class="assignment-text">60분</div>
        </div>
        <div class="class-block light-green" style="grid-column: 2; grid-row: 4;">
            알고리즘
        </div>
        <div class="class-block yellow" style="grid-column: 2; grid-row: 6 / span 1;">
            알고리즘 숙제 ...
            <div class="assignment-text">50분</div>
        </div>

        <div class="class-block green" style="grid-column: 3; grid-row: 2;">
            운영체제
        </div>
        <div class="class-block light-green" style="grid-column: 3; grid-row: 7;">
            데이터베이스
        </div>

        <div class="class-block green" style="grid-column: 4; grid-row: 3;">
            네트워크
        </div>

        <div class="class-block green" style="grid-column: 5; grid-row: 2;">
            소프트웨어 공학
        </div>
        
        <div class="class-block yellow" style="grid-column: 6; grid-row: 3;">
            데이터구조 과제 ...
            <div class="assignment-text">60분</div>
        </div>
        <div class="class-block pink" style="grid-column: 6; grid-row: 6;">
            인공지능
        </div>
    </div>

    <footer class="bottom-nav">
        <div class="nav-item active">
            <div>&#127968;</div> 홈
        </div>
        <div class="nav-item">
            <div>&#9989;</div> 과제
        </div>
        <div class="nav-item">
            <div>&#10024;</div> AI
        </div>
        <div class="nav-item">
            <div>&#9881;</div> 설정
        </div>
    </footer>

</body>
</html>
