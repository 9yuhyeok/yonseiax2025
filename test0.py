import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

st.set_page_config(page_title="시간표 앱", layout="wide")

selected = option_menu(
    None,
    ["시간표", "과제", "성적", "설정"],
    icons=["calendar-week", "check2-square", "bar-chart-line", "gear"],
    menu_icon=None,
    default_index=0,
    orientation="horizontal",
)

# ---- 시간표 데이터 ----
timetable_data = {
    "월": ["", "", "", "", "", "", "", ""],
    "화": ["", "", "", "", "", "", "", ""],
    "수": ["", "", "", "", "", "", "", ""],
    "목": ["", "", "", "", "", "", "", ""],
    "금": ["", "", "", "", "", "", "", ""],
}
timetable_df = pd.DataFrame(
    timetable_data,
    index=["9", "10", "11", "12", "13", "14", "15", "16"]
)

# ---- 공통 CSS: 셀 가로:세로 = 5:3 ----
cell_width = 150      # px
cell_height = 90      # px  (150 * 3/5)

st.markdown(
    f"""
    <style>
    /* st.table 전체에 적용 */
    [data-testid="stTable"] table {{
        border-collapse: collapse;
    }}
    [data-testid="stTable"] table th,
    [data-testid="stTable"] table td {{
        width: {cell_width}px;
        height: {cell_height}px;
        text-align: center;
        vertical-align: middle;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- 탭별 화면 ----
if selected == "시간표":
    st.markdown("### 시간표")
    st.table(timetable_df)

elif selected == "과제":
    st.markdown("### 과제")

elif selected == "성적":
    st.markdown("### 성적")

elif selected == "설정":
    st.markdown("### 설정")
