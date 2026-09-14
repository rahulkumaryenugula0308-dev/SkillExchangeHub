import streamlit as st

from models.user_model import create_user
from utils.ui import apply_platform_style, render_page_header


st.set_page_config(
    page_title="Register | Skill Exchange",
    page_icon="📝",
    layout="wide"
)

apply_platform_style()


# Center the registration form
left, center, right = st.columns([1, 2, 1])


with center:
    render_page_header(
        "🤝 Join Skill Exchange",
        "Create your account and start exchanging skills."
    )

    st.markdown("### 📝 Create Account")

    full_name = st.text_input(
        "👤 Full Name",
        placeholder="Enter your full name"
    )

    email = st.text_input(
        "📧 Email",
        placeholder="Enter your email"
    )

    password = st.text_input(
        "🔑 Password",
        type="password",
        placeholder="Create a password"
    )

    confirm_password = st.text_input(
        "🔐 Confirm Password",
        type="password",
        placeholder="Re-enter your password"
    )

    st.write("")

    if st.button(
        "🚀 Create Account",
        type="primary",
        use_container_width=True
    ):
        # Validate the registration form
        if not full_name.strip():
            st.error("❌ Please enter your name.")

        elif not email.strip():
            st.error("❌ Please enter your email.")

        elif not password:
            st.error("❌ Please create a password.")

        elif password != confirm_password:
            st.error("❌ Passwords do not match.")

        else:
            success, message = create_user(
                full_name.strip(),
                email.strip(),
                password
            )

            if success:
                st.success("✅ " + message)

                st.info(
                    "You can now login with your account."
                )

                if st.button(
                    "🔐 Go to Login",
                    use_container_width=True
                ):
                    st.switch_page("pages/login.py")

            else:
                st.error(message)

    st.divider()

    if st.button(
        "🔐 Already have an account? Login",
        use_container_width=True
    ):
        st.switch_page("pages/login.py")