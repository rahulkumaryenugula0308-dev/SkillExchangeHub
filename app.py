import streamlit as st


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Skill Exchange Hub",
    page_icon="🤝",
    layout="wide"
)


# ==========================================================
# ENTRY POINT
# ==========================================================

if (
    "logged_in" in st.session_state
    and st.session_state["logged_in"]
):

    st.switch_page(
        "pages/dashboard.py"
    )

else:

    st.switch_page(
        "pages/login.py"
    )