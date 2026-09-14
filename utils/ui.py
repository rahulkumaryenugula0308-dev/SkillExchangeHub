import streamlit as st


def apply_platform_style():
    """Apply the common styling used across the application."""

    st.markdown(
        """
        <style>

        /* Remove unnecessary space above the page */
        header[data-testid="stHeader"] {
            height: 0rem;
            background: transparent;
        }

        header[data-testid="stHeader"] > div {
            height: 0rem;
        }

        .block-container {
            padding-top: 0.7rem !important;
            padding-bottom: 2.5rem !important;
            max-width: 1400px;
        }

        /* Main application background */
        .stApp {
            background:
                linear-gradient(
                    135deg,
                    #f8fbff 0%,
                    #eef4ff 50%,
                    #faf5ff 100%
                );
        }

        /* Sidebar background */
        [data-testid="stSidebar"] {
            background:
                linear-gradient(
                    180deg,
                    #172554 0%,
                    #1e3a8a 50%,
                    #312e81 100%
                );
        }

        /* Sidebar text */
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span {
            color: white !important;
        }

        /* Sidebar page links */
        [data-testid="stSidebar"]
        [data-testid="stPageLink"] a {
            color: white !important;
            border-radius: 10px;
            padding: 10px 12px;
            font-weight: 600;
        }

        [data-testid="stSidebar"]
        [data-testid="stPageLink"] a:hover {
            background: rgba(255, 255, 255, 0.15);
        }

        /* Sidebar buttons */
        [data-testid="stSidebar"] .stButton > button {
            width: 100%;
            min-height: 42px;
            border-radius: 10px;
            border: none !important;
            background: white !important;
            color: #172554 !important;
            font-weight: 600;
        }

        [data-testid="stSidebar"]
        .stButton > button * {
            color: #172554 !important;
        }

        [data-testid="stSidebar"]
        .stButton > button:hover {
            background: #dbeafe !important;
            color: #172554 !important;
        }

        [data-testid="stSidebar"]
        .stButton > button:hover * {
            color: #172554 !important;
        }

        /* Sidebar radio buttons */
        [data-testid="stSidebar"]
        [role="radiogroup"] label,
        [data-testid="stSidebar"]
        [role="radiogroup"] label p {
            color: white !important;
        }

        /* Page title */
        .platform-title {
            font-size: 40px;
            font-weight: 800;
            color: #172554;
            margin-top: 0;
            margin-bottom: 4px;
        }

        /* Page subtitle */
        .platform-subtitle {
            font-size: 17px;
            color: #64748b;
            margin-bottom: 25px;
        }

        /* Section title */
        .platform-section-title {
            font-size: 28px;
            font-weight: 750;
            color: #1e293b;
            margin-top: 10px;
            margin-bottom: 10px;
        }

        /* Reusable card */
        .platform-card {
            background: white;
            border: 1px solid #dbe4f0;
            border-radius: 18px;
            padding: 20px;
            box-shadow:
                0 8px 25px
                rgba(15, 23, 42, 0.06);
        }

        /* Metric cards */
        [data-testid="stMetric"] {
            background: white;
            border: 1px solid #dbe4f0;
            border-radius: 16px;
            padding: 12px;
        }

        /* Buttons */
        .stButton > button {
            border-radius: 10px;
            min-height: 42px;
            font-weight: 600;
        }

        /* Text inputs */
        .stTextInput input,
        .stTextArea textarea {
            border-radius: 10px;
        }

        /* Alerts */
        [data-testid="stAlert"] {
            border-radius: 12px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


def render_sidebar(
    full_name="User",
    show_conversations=False,
    conversation_labels=None,
    default_index=0
):
    """Render the shared application sidebar."""

    selected_index = default_index

    with st.sidebar:

        st.markdown("## 🤝 Skill Exchange")

        st.caption(
            f"Welcome, {full_name}"
        )

        st.divider()

        # Main navigation
        st.subheader("🧭 Your Journey")

        st.page_link(
            "pages/dashboard.py",
            label="1️⃣ Dashboard",
            icon="🏠"
        )

        st.page_link(
            "pages/profile.py",
            label="2️⃣ Complete Profile",
            icon="👤"
        )

        st.page_link(
            "pages/matches.py",
            label="3️⃣ Find Matches",
            icon="🔍"
        )

        st.page_link(
            "pages/request.py",
            label="4️⃣ Manage Requests",
            icon="📨"
        )

        st.page_link(
            "pages/chat.py",
            label="5️⃣ Chat & Share",
            icon="💬"
        )

        st.divider()

        # Frequently used actions
        st.subheader("⚡ Quick Actions")

        if st.button(
            "🏠 Dashboard",
            key="common_dashboard_button",
            use_container_width=True
        ):
            st.switch_page("pages/dashboard.py")

        if st.button(
            "🔍 Find Matches",
            key="common_matches_button",
            use_container_width=True
        ):
            st.switch_page("pages/matches.py")

        if st.button(
            "📨 Requests",
            key="common_requests_button",
            use_container_width=True
        ):
            st.switch_page("pages/request.py")

        if st.button(
            "💬 Chat",
            key="common_chat_button",
            use_container_width=True
        ):
            st.switch_page("pages/chat.py")

        # Conversation selector used on the Chat page
        if show_conversations:

            st.divider()

            st.subheader("💬 My Conversations")

            st.caption(
                "Your accepted skill exchange partners"
            )

            if conversation_labels:

                selected_index = st.radio(
                    "Select a conversation:",
                    range(len(conversation_labels)),
                    index=default_index,
                    format_func=lambda index:
                        conversation_labels[index],
                    key="conversation_selector"
                )

            else:

                st.info("No conversations yet.")

        st.divider()

        # Clear login session and return to Login
        if st.button(
            "🚪 Logout",
            key="common_logout_button",
            use_container_width=True
        ):

            for key in [
                "logged_in",
                "user_id",
                "full_name",
                "email",
                "role"
            ]:
                st.session_state.pop(
                    key,
                    None
                )

            st.switch_page("pages/login.py")

    return selected_index


def render_page_header(title, subtitle):
    """Render a consistent title and subtitle."""

    st.markdown(
        f"""
        <div class="platform-title">
            {title}
        </div>

        <div class="platform-subtitle">
            {subtitle}
        </div>
        """,
        unsafe_allow_html=True
    )