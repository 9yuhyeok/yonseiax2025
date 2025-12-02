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

# 시간표 데이터 생성
timetable_data = {
    "": ["9", "10", "11", "12", "13", "14", "15", "16"],
    "월": ["", "", "", "", "", "", "", ""],
    "화": ["", "", "", "", "", "", "", ""],
    "수": ["", "", "", "", "", "", "", ""],
    "목": ["", "", "", "", "", "", "", ""],
    "금": ["", "", "", "", "", "", "", ""],
}
timetable_df = pd.DataFrame(timetable_data)

# 탭 화면
if selected == "시간표":
    st.markdown("### 시간표")
    st.table(timetable_df)

elif selected == "과제":
    st.markdown("### 과제")

elif selected == "성적":
    st.markdown("### 성적")

elif selected == "설정":
    st.markdown("### 설정")
