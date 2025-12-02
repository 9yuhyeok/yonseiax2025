import streamlit as st
from streamlit_option_menu import option_menu

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
    styles={
        "container": {
            "padding": "0",
            "background-color": "#ffffff"
        },
        "icon": {"font-size": "20px"},
        "nav-link": {
            "font-size": "16px",
            "padding": "10px 5px",
            "color": "#555",
            "text-align": "center",
        },
        "nav-link-selected": {
            "color": "black",
            "background-color": "#e0e0e0"
        },
    },
)

# 각 탭 화면
if selected == "시간표":
    st.markdown("### 시간표")
elif selected == "과제":
    st.markdown("### 과제")
elif selected == "성적":
    st.markdown("### 성적")
elif selected == "설정":
    st.markdown("### 설정")
