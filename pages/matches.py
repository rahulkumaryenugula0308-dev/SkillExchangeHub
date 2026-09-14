import streamlit as st

from models.match_model import find_matches
from models.exchange_model import send_exchange_request
from utils.ui import (
    apply_platform_style,
    render_sidebar,
    render_page_header
)


st.set_page_config(
    page_title="Find Matches | Skill Exchange",
    page_icon="🔍",
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


# Page header
render_page_header(
    "🔍 Find Skill Matches",
    "Discover people who can teach you and learn from you."
)


# Load matches when the page opens or refresh is clicked
if (
    "matches" not in st.session_state
    or st.button(
        "🔄 Refresh Matches",
        use_container_width=True
    )
):
    st.session_state["matches"] = find_matches(user_id)


matches = st.session_state.get("matches", [])


# Show a message when no matches are available
if not matches:

    st.markdown(
        """
        ### 🔍 No Matches Yet

        Complete your profile with at least one
        teaching skill and one learning skill.
        """
    )

    if st.button(
        "👤 Complete Profile",
        type="primary",
        use_container_width=True
    ):
        st.switch_page("pages/profile.py")

    st.stop()


st.metric(
    "🎯 Available Matches",
    len(matches)
)

st.write("")


# Filters
filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    search_text = st.text_input(
        "🔎 Search",
        placeholder="Name or email"
    )

with filter_col2:
    minimum_score = st.slider(
        "Minimum Match Score",
        min_value=0,
        max_value=100,
        value=0
    )

with filter_col3:
    sort_option = st.selectbox(
        "Sort",
        [
            "Best Match First",
            "Lowest Match First",
            "Name A → Z",
            "Name Z → A"
        ]
    )


# Filter matches based on search text and score
filtered_matches = []

for match in matches:
    name = match.get("full_name", "")
    email = match.get("email", "")
    score = match.get("score", 0)

    if score < minimum_score:
        continue

    if search_text:
        search_value = search_text.lower()

        if (
            search_value not in name.lower()
            and search_value not in email.lower()
        ):
            continue

    filtered_matches.append(match)


# Sort filtered matches
if sort_option == "Best Match First":

    filtered_matches.sort(
        key=lambda item: item.get("score", 0),
        reverse=True
    )

elif sort_option == "Lowest Match First":

    filtered_matches.sort(
        key=lambda item: item.get("score", 0)
    )

elif sort_option == "Name A → Z":

    filtered_matches.sort(
        key=lambda item: item.get(
            "full_name",
            ""
        ).lower()
    )

else:

    filtered_matches.sort(
        key=lambda item: item.get(
            "full_name",
            ""
        ).lower(),
        reverse=True
    )


st.write("")


# Display filtered matches
if not filtered_matches:

    st.warning(
        "No matches found with the selected filters."
    )

else:

    for match in filtered_matches:

        name = match.get("full_name", "User")
        email = match.get("email", "")
        score = match.get("score", 0)

        learning_score = match.get(
            "learning_match_score",
            0
        )

        teaching_score = match.get(
            "teaching_match_score",
            0
        )

        learn_names = match.get(
            "learn_from_them_names",
            []
        )

        teach_names = match.get(
            "teach_to_them_names",
            []
        )

        with st.container(border=True):

            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"## 👤 {name}")
                st.caption(f"📧 {email}")

            with col2:

                if score >= 80:
                    st.success(f"🔥 {score}% Match")

                elif score >= 60:
                    st.warning(f"⭐ {score}% Match")

                else:
                    st.info(f"💡 {score}% Match")

            st.progress(
                min(max(score, 0), 100) / 100
            )

            m1, m2, m3 = st.columns(3)

            with m1:
                st.metric(
                    "📖 Learning",
                    f"{learning_score}%"
                )

            with m2:
                st.metric(
                    "🎓 Teaching",
                    f"{teaching_score}%"
                )

            with m3:
                st.metric(
                    "🤝 Total Match",
                    score
                )

            skill_col1, skill_col2 = st.columns(2)

            with skill_col1:

                st.subheader(
                    "📖 They Can Teach You"
                )

                if learn_names:

                    for skill in learn_names:
                        st.write(f"✅ {skill}")

                else:

                    st.info(
                        "No direct learning match."
                    )

            with skill_col2:

                st.subheader(
                    "🎓 You Can Teach Them"
                )

                if teach_names:

                    for skill in teach_names:
                        st.write(f"✅ {skill}")

                else:

                    st.info(
                        "No direct teaching match."
                    )

            st.write("")

            if st.button(
                "📨 Send Exchange Request",
                key=f"request_{match['user_id']}",
                use_container_width=True
            ):

                success, message = send_exchange_request(
                    user_id,
                    match["user_id"]
                )

                if success:

                    st.success(message)

                    # Refresh matches after sending a request
                    st.session_state["matches"] = (
                        find_matches(user_id)
                    )

                    st.rerun()

                else:

                    st.warning(message)


st.divider()


# Navigation to the next parts of the application
st.subheader("🚀 Continue Your Skill Journey")

c1, c2, c3 = st.columns(3)

with c1:

    if st.button(
        "👤 My Profile",
        use_container_width=True
    ):
        st.switch_page("pages/profile.py")

with c2:

    if st.button(
        "📨 Manage Requests",
        use_container_width=True
    ):
        st.switch_page("pages/request.py")

with c3:

    if st.button(
        "💬 Chat & Share",
        use_container_width=True
    ):
        st.switch_page("pages/chat.py")