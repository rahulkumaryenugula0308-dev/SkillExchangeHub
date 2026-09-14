import streamlit as st

from models.exchange_model import (
    get_incoming_requests,
    get_sent_requests,
    update_request_status
)

from utils.ui import (
    apply_platform_style,
    render_sidebar,
    render_page_header
)


st.set_page_config(
    page_title="Requests | Skill Exchange",
    page_icon="📨",
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
    "📨 Exchange Requests",
    "Manage your skill exchange connections and "
    "continue your learning journey."
)


# Load incoming and sent requests
incoming_requests = get_incoming_requests(user_id)
sent_requests = get_sent_requests(user_id)


# Calculate request counts
incoming_pending = sum(
    1
    for request in incoming_requests
    if request["status"] == "pending"
)

sent_pending = sum(
    1
    for request in sent_requests
    if request["status"] == "pending"
)

accepted_count = (
    sum(
        1
        for request in incoming_requests
        if request["status"] == "accepted"
    )
    +
    sum(
        1
        for request in sent_requests
        if request["status"] == "accepted"
    )
)


# Request metrics
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(
        "📥 Incoming",
        len(incoming_requests)
    )

with m2:
    st.metric(
        "⏳ Pending",
        incoming_pending + sent_pending
    )

with m3:
    st.metric(
        "✅ Accepted",
        accepted_count
    )

with m4:
    st.metric(
        "📤 Sent",
        len(sent_requests)
    )


st.write("")


# Separate incoming and sent requests
incoming_tab, sent_tab = st.tabs(
    [
        "📥 Incoming Requests",
        "📤 Sent Requests"
    ]
)


# Incoming requests
with incoming_tab:

    if not incoming_requests:

        st.info(
            "📭 You don't have any incoming requests yet."
        )

        if st.button(
            "🔍 Find Matches",
            use_container_width=True
        ):
            st.switch_page("pages/matches.py")

    else:

        for request in incoming_requests:

            status = request["status"]

            with st.container(border=True):

                left, right = st.columns([4, 1])

                with left:

                    st.markdown(
                        f"## 👤 {request['full_name']}"
                    )

                    st.caption(
                        f"📧 {request['email']}"
                    )

                    st.caption(
                        f"📅 Requested: "
                        f"{request['requested_at']}"
                    )

                with right:

                    if status == "pending":
                        st.warning("⏳ Pending")

                    elif status == "accepted":
                        st.success("✅ Accepted")

                    else:
                        st.error("❌ Rejected")

                # Pending requests can be accepted or rejected
                if status == "pending":

                    st.info(
                        "This person is waiting for your response."
                    )

                    c1, c2 = st.columns(2)

                    with c1:

                        if st.button(
                            "✅ Accept",
                            key=f"accept_{request['request_id']}",
                            use_container_width=True
                        ):

                            success, message = (
                                update_request_status(
                                    request["request_id"],
                                    user_id,
                                    "accepted"
                                )
                            )

                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)

                    with c2:

                        if st.button(
                            "❌ Reject",
                            key=f"reject_{request['request_id']}",
                            use_container_width=True
                        ):

                            success, message = (
                                update_request_status(
                                    request["request_id"],
                                    user_id,
                                    "rejected"
                                )
                            )

                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)

                # Accepted requests allow the user to open Chat
                elif status == "accepted":

                    st.success(
                        "🎉 You are now connected!"
                    )

                    if st.button(
                        "💬 Chat Now",
                        key=f"chat_in_{request['request_id']}",
                        use_container_width=True
                    ):

                        st.query_params["user_id"] = (
                            request["sender_id"]
                        )

                        st.switch_page(
                            "pages/chat.py"
                        )


# Sent requests
with sent_tab:

    if not sent_requests:

        st.info(
            "📭 You haven't sent any exchange requests yet."
        )

        if st.button(
            "🔍 Find Matches",
            key="sent_find_matches",
            use_container_width=True
        ):
            st.switch_page("pages/matches.py")

    else:

        for request in sent_requests:

            status = request["status"]

            with st.container(border=True):

                left, right = st.columns([4, 1])

                with left:

                    st.markdown(
                        f"## 👤 {request['full_name']}"
                    )

                    st.caption(
                        f"📧 {request['email']}"
                    )

                    st.caption(
                        f"📅 Requested: "
                        f"{request['requested_at']}"
                    )

                with right:

                    if status == "pending":
                        st.warning("⏳ Pending")

                    elif status == "accepted":
                        st.success("✅ Accepted")

                    else:
                        st.error("❌ Rejected")

                if request["responded_at"]:

                    st.caption(
                        f"🕒 Responded: "
                        f"{request['responded_at']}"
                    )

                else:

                    st.caption(
                        "🕒 Waiting for response..."
                    )

                # Accepted sent requests can open Chat
                if status == "accepted":

                    st.success(
                        "🎉 Your exchange has been accepted!"
                    )

                    if st.button(
                        "💬 Chat Now",
                        key=f"chat_sent_{request['request_id']}",
                        use_container_width=True
                    ):

                        st.query_params["user_id"] = (
                            request["receiver_id"]
                        )

                        st.switch_page(
                            "pages/chat.py"
                        )


st.divider()


# Navigation to other parts of the application
st.subheader(
    "🚀 Continue Your Skill Journey"
)

c1, c2, c3 = st.columns(3)

with c1:

    if st.button(
        "🔍 Find Matches",
        use_container_width=True
    ):
        st.switch_page("pages/matches.py")

with c2:

    if st.button(
        "👤 My Profile",
        use_container_width=True
    ):
        st.switch_page("pages/profile.py")

with c3:

    if st.button(
        "💬 Chat & Share",
        use_container_width=True
    ):
        st.switch_page("pages/chat.py")