import streamlit as st
import math

# ---------- 초기 설정 ----------
st.set_page_config(
    page_title="Mobile Calculator",
    layout="wide"
)

# ---------- 세션 상태 기본값 ----------
if "language" not in st.session_state:
    st.session_state.language = "ko"   # ko / en
if "theme" not in st.session_state:
    st.session_state.theme = "light"   # light / dark

# ---------- 다국어 텍스트 ----------
TEXTS = {
    "title": {
        "ko": "📱 모바일 계산기",
        "en": "📱 Mobile Calculator",
    },
    "basic_tab": {
        "ko": "일반 계산기",
        "en": "Basic",
    },
    "sci_tab": {
        "ko": "공학용 계산기",
        "en": "Scientific",
    },
    "settings_tab": {
        "ko": "설정",
        "en": "Settings",
    },
    "basic_desc": {
        "ko": "사칙연산 위주 일반 계산기야. 예: 1+2*3/4",
        "en": "Basic calculator for +, -, ×, ÷. e.g., 1+2*3/4",
    },
    "sci_desc": {
        "ko": "공학용 함수 사용 가능: sin, cos, tan, log, sqrt, pi, e 등.",
        "en": "Scientific functions: sin, cos, tan, log, sqrt, pi, e, etc.",
    },
    "expr_label": {
        "ko": "계산식 입력",
        "en": "Enter expression",
    },
    "calc_button": {
        "ko": "계산하기",
        "en": "Calculate",
    },
    "result": {
        "ko": "결과",
        "en": "Result",
    },
    "error": {
        "ko": "계산할 수 없는 식이야. 수식과 함수 이름을 확인해줘.",
        "en": "Invalid expression. Please check operators and function names.",
    },
    "settings_language": {
        "ko": "언어",
        "en": "Language",
    },
    "settings_theme": {
        "ko": "화면 모드",
        "en": "Theme",
    },
    "settings_saved": {
        "ko": "설정이 적용되었어. 상단 탭이 마음에 안 들면 언어/모드 다시 바꿔봐.",
        "en": "Settings applied. If you don’t like it, change language/theme again.",
    },
    "theme_light": {
        "ko": "라이트",
        "en": "Light",
    },
    "theme_dark": {
        "ko": "다크",
        "en": "Dark",
    },
    "available_funcs": {
        "ko": "사용 가능 함수: sin, cos, tan, log, sqrt, abs, round, pi, e",
        "en": "Available: sin, cos, tan, log, sqrt, abs, round, pi, e",
    },
}

def t(key: str) -> str:
    lang = st.session_state.language
    return TEXTS[key][lang]

# ---------- 테마 적용 ----------
def apply_theme():
    theme = st.session_state.theme
    if theme == "dark":
        bg = "#020617"
        card = "#0f172a"
        text = "#e5e7eb"
        accent = "#22c55e"
    else:
        bg = "#f9fafb"
        card = "#ffffff"
        text = "#0f172a"
        accent = "#2563eb"

    st.markdown(
        f"""
        <style>
        body {{
            background-color: {bg};
        }}
        .stApp {{
            background-color: {bg};
            color: {text};
        }}
        .stTabs [data-baseweb="tab"] {{
            font-size: 0.9rem;
        }}
        .stButton>button {{
            border-radius: 999px;
            padding: 0.5rem 1.2rem;
            font-weight: 600;
        }}
        .calc-card {{
            background-color: {card};
            padding: 1rem;
            border-radius: 1rem;
            box-shadow: 0 10px 30px rgba(15,23,42,0.18);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    return accent

accent_color = apply_theme()

# ---------- 안전한 계산 함수 ----------
allowed_names = {
    k: getattr(math, k) for k in dir(math) if not k.startswith("_")
}
allowed_names.update({
    "abs": abs,
    "round": round,
})

def safe_eval(expr: str):
    """
    숫자, 기본 연산자(+-*/**), math 함수만 허용.
    """
    expr = expr.strip()
    if not expr:
        return ""
    code = compile(expr, "<string>", "eval")
    for name in code.co_names:
        if name not in allowed_names:
            raise NameError(f"사용 불가 이름: {name}")
    return eval(code, {"__builtins__": {}}, allowed_names)

# ---------- 메인 UI ----------
st.markdown(f"<h2 style='margin-bottom:0.5rem;'>{t('title')}</h2>", unsafe_allow_html=True)
st.caption("Streamlit · Mobile first")

# 탭 생성 (언어에 따라 라벨 바뀜)
tab_basic, tab_sci, tab_settings = st.tabs(
    [t("basic_tab"), t("sci_tab"), t("settings_tab")]
)

# ----- 1) 일반 계산기 탭 -----
with tab_basic:
    st.markdown("<div class='calc-card'>", unsafe_allow_html=True)
    st.write(t("basic_desc"))
    expr_basic = st.text_input(t("expr_label"), key="expr_basic", placeholder="1+2*3/4")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(t("calc_button"), key="btn_basic"):
            try:
                result = safe_eval(expr_basic)
                st.session_state.basic_result = result
            except Exception:
                st.session_state.basic_result = None

    result = st.session_state.get("basic_result", "")
    if result == "":
        pass
    elif result is None:
        st.error(t("error"))
    else:
        st.success(f"{t('result')}: {result}")
    st.markdown("</div>", unsafe_allow_html=True)

# ----- 2) 공학용 계산기 탭 -----
with tab_sci:
    st.markdown("<div class='calc-card'>", unsafe_allow_html=True)
    st.write(t("sci_desc"))
    st.info(t("available_funcs"))
    expr_sci = st.text_input(
        t("expr_label"),
        key="expr_sci",
        placeholder="sin(pi/2) + log(10) - sqrt(2)"
    )
    if st.button(t("calc_button"), key="btn_sci"):
        try:
            result = safe_eval(expr_sci)
            st.session_state.sci_result = result
        except Exception:
            st.session_state.sci_result = None

    result_sci = st.session_state.get("sci_result", "")
    if result_sci == "":
        pass
    elif result_sci is None:
        st.error(t("error"))
    else:
        st.success(f"{t('result')}: {result_sci}")
    st.markdown("</div>", unsafe_allow_html=True)

# ----- 3) 설정 탭 -----
with tab_settings:
    st.markdown("<div class='calc-card'>", unsafe_allow_html=True)

    # 언어
    lang_label = st.radio(
        t("settings_language"),
        options=["한국어", "English"],
        index=0 if st.session_state.language == "ko" else 1,
        horizontal=True,
    )
    st.session_state.language = "ko" if lang_label == "한국어" else "en"

    # 테마
    theme_label = st.radio(
        t("settings_theme"),
        options=[TEXTS["theme_light"]["ko"], TEXTS["theme_dark"]["ko"]],
        index=0 if st.session_state.theme == "light" else 1,
        horizontal=True,
    )
    # 라벨이 한글 기준이니까 라이트/다크로 비교
    if theme_label == TEXTS["theme_light"]["ko"]:
        st.session_state.theme = "light"
    else:
        st.session_state.theme = "dark"

    st.success(t("settings_saved"))
    st.markdown("</div>", unsafe_allow_html=True)

    st.caption("※ 진짜 스트림릿 공식 다크 테마는 config로 바꾸는 거고, "
               "여긴 데모라 CSS로 느낌만 바꾸는 방식이야.")
