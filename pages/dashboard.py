import streamlit as st

from database.connection import get_connection
from utils.ui import (
    apply_platform_style,
    render_sidebar,
    render_page_header
)


st.set_page_config(
    page_title="Dashboard | Skill Exchange",
    page_icon="🏠",
    layout="wide"
)

apply_platform_style()


# Make sure the user is logged in
if (
    "logged_in" not in st.session_state
    or not st.session_state["logged_in"]
):
    st.switch_page("pages/login.py")


# Get current user information from the session
user_id = st.session_state["user_id"]

full_name = st.session_state.get(
    "full_name",
    "User"
)


# Show the common application sidebar
render_sidebar(
    full_name=full_name
)


# Connect to the database
connection = get_connection()

if connection is None:
    st.error("❌ Database connection failed.")
    st.stop()

cursor = connection.cursor(dictionary=True)


# Get the number of matching users
cursor.execute(
    """
    SELECT COUNT(
        DISTINCT other_user.user_id
    ) AS total_matches
    FROM user_skills my_skill
    JOIN user_skills other_skill
        ON my_skill.skill_id = other_skill.skill_id
        AND my_skill.skill_type = 'learn'
        AND other_skill.skill_type = 'teach'
    JOIN users other_user
        ON other_skill.user_id = other_user.user_id
    WHERE my_skill.user_id = %s
      AND other_user.user_id != %s
    """,
    (user_id, user_id)
)

total_matches = cursor.fetchone()["total_matches"]


# Get the number of pending incoming requests
cursor.execute(
    """
    SELECT COUNT(*) AS total_pending
    FROM exchange_requests
    WHERE receiver_id = %s
      AND status = 'pending'
    """,
    (user_id,)
)

pending_requests = cursor.fetchone()["total_pending"]


# Get the number of accepted exchanges
cursor.execute(
    """
    SELECT COUNT(*) AS total_accepted
    FROM exchange_requests
    WHERE (sender_id = %s OR receiver_id = %s)
      AND status = 'accepted'
    """,
    (user_id, user_id)
)

accepted_exchanges = cursor.fetchone()["total_accepted"]


# Get the user's teaching and learning skills
cursor.execute(
    """
    SELECT
        s.skill_name,
        us.skill_type
    FROM user_skills us
    JOIN skills s
        ON us.skill_id = s.skill_id
    WHERE us.user_id = %s
    ORDER BY us.skill_type, s.skill_name
    """,
    (user_id,)
)

user_skills = cursor.fetchall()


# Close the database connection
cursor.close()
connection.close()


# Separate teaching and learning skills
teach_skills = [
    skill["skill_name"]
    for skill in user_skills
    if skill["skill_type"] == "teach"
]

learn_skills = [
    skill["skill_name"]
    for skill in user_skills
    if skill["skill_type"] == "learn"
]


# Dashboard header
render_page_header(
    "🤝 Skill Exchange Hub",
    f"Welcome, {full_name}! "
    "Connect, exchange skills, and learn something new."
)


# Dashboard statistics
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("🎯 Matches", total_matches)

with col2:
    st.metric("📨 Pending", pending_requests)

with col3:
    st.metric("✅ Accepted", accepted_exchanges)

with col4:
    st.metric("🎓 Teaching", len(teach_skills))

with col5:
    st.metric("📖 Learning", len(learn_skills))


st.write("")


# Show the most useful next action for the user
st.markdown(
    '<div class="platform-section-title">🚀 Your Next Step</div>',
    unsafe_allow_html=True
)

if not teach_skills or not learn_skills:

    st.info(
        "👤 Complete your profile by adding at least "
        "one teaching skill and one learning skill."
    )

    if st.button(
        "👤 Complete My Profile",
        type="primary",
        use_container_width=True
    ):
        st.switch_page("pages/profile.py")

elif total_matches == 0:

    st.info(
        "🔍 Your profile is ready. "
        "Now discover people who match your skills."
    )

    if st.button(
        "🔍 Find My Matches",
        type="primary",
        use_container_width=True
    ):
        st.switch_page("pages/matches.py")

elif pending_requests > 0:

    st.warning(
        f"📨 You have {pending_requests} pending request(s)."
    )

    if st.button(
        "📨 Review Requests",
        type="primary",
        use_container_width=True
    ):
        st.switch_page("pages/request.py")

elif accepted_exchanges > 0:

    st.success(
        "🎉 You have active skill exchange connections."
    )

    if st.button(
        "💬 Start Chatting",
        type="primary",
        use_container_width=True
    ):
        st.switch_page("pages/chat.py")

else:

    st.info(
        "🔍 Explore your skill matches and "
        "start connecting."
    )

    if st.button(
        "🔍 Explore Matches",
        type="primary",
        use_container_width=True
    ):
        st.switch_page("pages/matches.py")


st.divider()


# Show the user's teaching and learning skills
st.markdown(
    '<div class="platform-section-title">📚 My Skills</div>',
    unsafe_allow_html=True
)

skill_col1, skill_col2 = st.columns(2)

with skill_col1:

    with st.container(border=True):
        st.subheader("🎓 I Can Teach")

        if teach_skills:
            for skill in teach_skills:
                st.write(f"✅ {skill}")
        else:
            st.info("No teaching skills added yet.")


with skill_col2:

    with st.container(border=True):
        st.subheader("📖 I Want To Learn")

        if learn_skills:
            for skill in learn_skills:
                st.write(f"📖 {skill}")
        else:
            st.info("No learning skills added yet.")


st.divider()


# Quick navigation buttons
st.markdown(
    '<div class="platform-section-title">⚡ Quick Actions</div>',
    unsafe_allow_html=True
)

q1, q2, q3, q4 = st.columns(4)

with q1:
    if st.button(
        "🔍 Find Matches",
        use_container_width=True
    ):
        st.switch_page("pages/matches.py")

with q2:
    if st.button(
        "📨 Requests",
        use_container_width=True
    ):
        st.switch_page("pages/request.py")

with q3:
    if st.button(
        "💬 My Chats",
        use_container_width=True
    ):
        st.switch_page("pages/chat.py")

with q4:
    if st.button(
        "👤 My Profile",
        use_container_width=True
    ):
        st.switch_page("pages/profile.py")