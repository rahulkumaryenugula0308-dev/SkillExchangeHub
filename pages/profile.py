import streamlit as st

from database.connection import get_connection
from utils.ui import (
    apply_platform_style,
    render_sidebar,
    render_page_header
)


st.set_page_config(
    page_title="My Profile | Skill Exchange",
    page_icon="👤",
    layout="wide"
)

apply_platform_style()


# Make sure the user is logged in
if (
    "logged_in" not in st.session_state
    or not st.session_state["logged_in"]
):
    st.switch_page("pages/login.py")


# Get current user information
user_id = st.session_state["user_id"]

full_name = st.session_state.get(
    "full_name",
    "User"
)

render_sidebar(full_name=full_name)


# Connect to the database
connection = get_connection()

if connection is None:
    st.error("❌ Database connection failed.")
    st.stop()

cursor = connection.cursor(dictionary=True)


# Get current user information
cursor.execute(
    """
    SELECT
        user_id,
        full_name,
        email,
        created_at
    FROM users
    WHERE user_id = %s
    """,
    (user_id,)
)

user = cursor.fetchone()


# Get the user's selected skills
cursor.execute(
    """
    SELECT
        s.skill_id,
        s.skill_name,
        us.skill_type
    FROM user_skills us
    JOIN skills s
        ON us.skill_id = s.skill_id
    WHERE us.user_id = %s
    ORDER BY s.skill_name
    """,
    (user_id,)
)

skills = cursor.fetchall()


# Get pending request count
cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM exchange_requests
    WHERE receiver_id = %s
      AND status = 'pending'
    """,
    (user_id,)
)

pending = cursor.fetchone()["total"]


# Get accepted exchange count
cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM exchange_requests
    WHERE (sender_id = %s OR receiver_id = %s)
      AND status = 'accepted'
    """,
    (user_id, user_id)
)

accepted = cursor.fetchone()["total"]


# Get all available skills
cursor.execute(
    """
    SELECT
        skill_id,
        skill_name
    FROM skills
    ORDER BY skill_name
    """
)

available_skills = cursor.fetchall()


cursor.close()
connection.close()


# Separate teaching and learning skills
teach_skills = [
    skill
    for skill in skills
    if skill["skill_type"] == "teach"
]

learn_skills = [
    skill
    for skill in skills
    if skill["skill_type"] == "learn"
]


# Page header
render_page_header(
    "👤 My Profile",
    "Manage your information and keep your teaching "
    "and learning skills updated."
)


# Calculate profile completion
completion = 0

if user and user["full_name"]:
    completion += 25

if user and user["email"]:
    completion += 25

if teach_skills:
    completion += 25

if learn_skills:
    completion += 25


st.markdown("### 📊 Profile Completion")

st.progress(completion / 100)

st.write(
    f"Your profile is **{completion}% complete**."
)


# Profile metrics
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("🎓 Teaching", len(teach_skills))

with m2:
    st.metric("📖 Learning", len(learn_skills))

with m3:
    st.metric("📨 Pending", pending)

with m4:
    st.metric("✅ Accepted", accepted)


st.divider()


# Personal information
st.markdown(
    '<div class="platform-section-title">'
    '👤 Personal Information'
    '</div>',
    unsafe_allow_html=True
)

with st.container(border=True):
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Full Name**")
        st.info(user["full_name"])

    with col2:
        st.write("**Email**")
        st.info(user["email"])


# Edit profile information
with st.expander("✏️ Edit Profile"):

    new_name = st.text_input(
        "Full Name",
        value=user["full_name"]
    )

    new_email = st.text_input(
        "Email",
        value=user["email"]
    )

    if st.button(
        "💾 Save Changes",
        type="primary"
    ):
        if not new_name.strip():
            st.error("❌ Name cannot be empty.")

        elif not new_email.strip():
            st.error("❌ Email cannot be empty.")

        else:
            connection = get_connection()

            if connection is None:
                st.error("❌ Database connection failed.")

            else:
                cursor = connection.cursor()

                try:
                    cursor.execute(
                        """
                        UPDATE users
                        SET
                            full_name = %s,
                            email = %s
                        WHERE user_id = %s
                        """,
                        (
                            new_name.strip(),
                            new_email.strip(),
                            user_id
                        )
                    )

                    connection.commit()

                    # Update session values so the UI
                    # immediately shows the new information.
                    st.session_state["full_name"] = (
                        new_name.strip()
                    )

                    st.session_state["email"] = (
                        new_email.strip()
                    )

                    st.success("✅ Profile updated.")
                    st.rerun()

                except Exception as e:
                    connection.rollback()
                    st.error(
                        f"❌ Could not update profile: {e}"
                    )

                finally:
                    cursor.close()
                    connection.close()


st.divider()


# Display current teaching and learning skills
st.markdown(
    '<div class="platform-section-title">'
    '📚 My Skills'
    '</div>',
    unsafe_allow_html=True
)

teach_col, learn_col = st.columns(2)


with teach_col:

    with st.container(border=True):
        st.subheader("🎓 I Can Teach")

        if teach_skills:
            for skill in teach_skills:
                skill_name = skill["skill_name"]

                row1, row2 = st.columns([4, 1])

                with row1:
                    st.write(f"✅ {skill_name}")

                with row2:
                    if st.button(
                        "🗑️",
                        key=f"remove_teach_{skill['skill_id']}"
                    ):
                        connection = get_connection()

                        if connection:
                            cursor = connection.cursor()

                            try:
                                cursor.execute(
                                    """
                                    DELETE FROM user_skills
                                    WHERE user_id = %s
                                      AND skill_id = %s
                                      AND skill_type = 'teach'
                                    """,
                                    (
                                        user_id,
                                        skill["skill_id"]
                                    )
                                )

                                connection.commit()

                                st.success(
                                    "Teaching skill removed."
                                )
                                st.rerun()

                            except Exception as e:
                                connection.rollback()
                                st.error(str(e))

                            finally:
                                cursor.close()
                                connection.close()

        else:
            st.info(
                "No teaching skills added yet."
            )


with learn_col:

    with st.container(border=True):
        st.subheader("📖 I Want To Learn")

        if learn_skills:
            for skill in learn_skills:
                skill_name = skill["skill_name"]

                row1, row2 = st.columns([4, 1])

                with row1:
                    st.write(f"📖 {skill_name}")

                with row2:
                    if st.button(
                        "🗑️",
                        key=f"remove_learn_{skill['skill_id']}"
                    ):
                        connection = get_connection()

                        if connection:
                            cursor = connection.cursor()

                            try:
                                cursor.execute(
                                    """
                                    DELETE FROM user_skills
                                    WHERE user_id = %s
                                      AND skill_id = %s
                                      AND skill_type = 'learn'
                                    """,
                                    (
                                        user_id,
                                        skill["skill_id"]
                                    )
                                )

                                connection.commit()

                                st.success(
                                    "Learning skill removed."
                                )
                                st.rerun()

                            except Exception as e:
                                connection.rollback()
                                st.error(str(e))

                            finally:
                                cursor.close()
                                connection.close()

        else:
            st.info(
                "No learning skills added yet."
            )


st.divider()


# Add new teaching and learning skills
st.markdown(
    '<div class="platform-section-title">'
    '➕ Add Skills'
    '</div>',
    unsafe_allow_html=True
)

if available_skills:

    skill_names = [
        item["skill_name"]
        for item in available_skills
    ]

    add_col1, add_col2 = st.columns(2)

    with add_col1:

        st.subheader("🎓 Add Teaching Skill")

        selected_teach = st.selectbox(
            "Select a skill",
            skill_names,
            key="profile_teach_select"
        )

        if st.button(
            "➕ Add Teaching Skill",
            use_container_width=True
        ):
            skill_id = next(
                item["skill_id"]
                for item in available_skills
                if item["skill_name"] == selected_teach
            )

            connection = get_connection()

            if connection:
                cursor = connection.cursor()

                try:
                    cursor.execute(
                        """
                        INSERT INTO user_skills (
                            user_id,
                            skill_id,
                            skill_type
                        )
                        VALUES (%s, %s, 'teach')
                        """,
                        (
                            user_id,
                            skill_id
                        )
                    )

                    connection.commit()

                    st.success(
                        f"✅ {selected_teach} added."
                    )
                    st.rerun()

                except Exception as e:
                    connection.rollback()

                    if "Duplicate" in str(e):
                        st.warning(
                            "⚠️ You already have this skill."
                        )
                    else:
                        st.error(str(e))

                finally:
                    cursor.close()
                    connection.close()

    with add_col2:

        st.subheader("📖 Add Learning Skill")

        selected_learn = st.selectbox(
            "Select a skill",
            skill_names,
            key="profile_learn_select"
        )

        if st.button(
            "➕ Add Learning Skill",
            use_container_width=True
        ):
            skill_id = next(
                item["skill_id"]
                for item in available_skills
                if item["skill_name"] == selected_learn
            )

            connection = get_connection()

            if connection:
                cursor = connection.cursor()

                try:
                    cursor.execute(
                        """
                        INSERT INTO user_skills (
                            user_id,
                            skill_id,
                            skill_type
                        )
                        VALUES (%s, %s, 'learn')
                        """,
                        (
                            user_id,
                            skill_id
                        )
                    )

                    connection.commit()

                    st.success(
                        f"✅ {selected_learn} added."
                    )
                    st.rerun()

                except Exception as e:
                    connection.rollback()

                    if "Duplicate" in str(e):
                        st.warning(
                            "⚠️ You already have this skill."
                        )
                    else:
                        st.error(str(e))

                finally:
                    cursor.close()
                    connection.close()


# Next step for the user
st.divider()

st.markdown(
    '<div class="platform-section-title">'
    '🚀 Continue Your Journey'
    '</div>',
    unsafe_allow_html=True
)

if teach_skills and learn_skills:

    st.success(
        "🎉 Your profile has teaching and learning skills."
    )

    if st.button(
        "🔍 Find My Matches",
        type="primary",
        use_container_width=True
    ):
        st.switch_page("pages/matches.py")

else:

    st.info(
        "Add both teaching and learning skills "
        "to unlock better matches."
    )