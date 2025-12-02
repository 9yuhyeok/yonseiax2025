import streamlit as st
from streamlit_option_menu import option_menu

# 페이지 기본 설정
st.set_page_config(page_title="Tabs Example", layout="wide")

# 아래 하단 탭 메뉴
selected = option_menu(
    None,
    ["탭1", "탭2", "탭3", "탭4"],
    icons=["house", "list-task", "stars", "gear"],
    menu_icon=None,
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0", "background-color": "#ffffff"},
        "icon": {"font-size": "20px"},
        "nav-link": {
            "font-size": "16px",
            "padding": "10px 5px",
            "color": "#555",
            "text-align": "center",
        },
        "nav-link-selected": {"color": "black", "background-color": "#e0e0e0"},
    }
)

# 탭별 컨텐츠
if selected == "탭1":
    st.markdown("### 탭1")
elif selected == "탭2":
    st.markdown("### 탭2")
elif selected == "탭3":
    st.markdown("### 탭3")
elif selected == "탭4":
    st.markdown("### 탭4")
