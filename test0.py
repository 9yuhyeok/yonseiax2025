import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="시간표 앱", layout="wide")

# 아래 탭 메뉴
selected = option_menu(
    None,
    ["시간표", "과제", "성적", "설정"],
    icons=["calendar-week", "check2-square", "bar-chart-line", "gear"],
    menu_icon=None,
    default_index=0,
    orientation="horizontal",
)

# 시간표 데이터
timetable_data = {
    "월": [""] * 8,
    "화": [""] * 8,
    "수": [""] * 8,
    "목": [""] * 8,
    "금": [""] * 8,
}
timetable_df = pd.DataFrame(timetable_data, index=["9","10","11","12","13","14","15","16"])

# HTML + CSS 로 셀 크기 3:2 고정
def timetable_html(df):
    html = """
    <style>
        table {
            border-collapse: collapse;
            width: auto;
        }
        th, td {
            border: 1px solid #d1d1d1;
            width: 150px;   /* 가로 */
            height: 100px;  /* 세로 (3:2 비율) */
            text-align: center;
            font-size: 16px;
        }
        th {
            background-color: #f4f4f4;
        }
    </style>
    """
    html += df.to_html(escape=False)
    return html

# 탭 화면 표시
if selected == "시간표":
    st.markdown("### 시간표")
    st.markdown(timetable_html(timetable_df), unsafe_allow_html=True)

elif selected == "과제":
    st.markdown("### 과제")

elif selected == "성적":
    st.markdown("### 성적")

elif selected == "설정":
    st.markdown("### 설정")
