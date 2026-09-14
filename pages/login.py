import streamlit as st

from models.user_model import login_user
from utils.ui import apply_platform_style, render_page_header


st.set_page_config(
    page_title="Login | Skill Exchange",
    page_icon="🔐",
    layout="wide"
)

apply_platform_style()


# Center the login page
left, center, right = st.columns([1, 2, 1])


with center:
    st.write("")

    render_page_header(
        "🤝 Skill Exchange Hub",
        "Connect with people, exchange skills, and learn together."
    )

    with st.container(border=True):
        st.markdown("### 🔐 Welcome Back")

        st.caption(
            "Login to continue to your Skill Exchange Hub."
        )

        st.write("")

        email = st.text_input(
            "📧 Email",
            placeholder="Enter your email",
            key="login_email"
        )

        password = st.text_input(
            "🔑 Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )

        st.write("")

        if st.button(
            "🚀 Login",
            type="primary",
            use_container_width=True
        ):
            # Validate login fields
            if not email.strip():
                st.error("❌ Please enter your email.")

            elif not password:
                st.error("❌ Please enter your password.")

            else:
                user = login_user(
                    email.strip(),
                    password
                )

                if user:
                    # Store logged-in user information
                    st.session_state["logged_in"] = True
                    st.session_state["user_id"] = user["user_id"]
                    st.session_state["full_name"] = user["full_name"]
                    st.session_state["email"] = user["email"]
                    st.session_state["role"] = user.get(
                        "role",
                        "user"
                    )

                    st.success("✅ Login successful!")

                    st.switch_page(
                        "pages/dashboard.py"
                    )

                else:
                    st.error(
                        "❌ Invalid email or password."
                    )

    st.write("")
    st.divider()

    st.write("Don't have an account?")

    if st.button(
        "📝 Create New Account",
        use_container_width=True
    ):
        st.switch_page(
            "pages/register.py"
        )