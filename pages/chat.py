import os
from datetime import datetime
from turtle import done

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from models.chat_model import (
    get_user_conversations,
    get_messages,
    send_message,
    mark_messages_as_read,
    user_has_conversation_access
)
from models.user_model import update_last_active
from models.resource_model import (
    share_link,
    get_shared_links,
    save_shared_file,
    get_shared_files,
    format_file_size
)
from utils.ui import (
    apply_platform_style,
    render_sidebar,
    render_page_header
)


st.set_page_config(
    page_title="Chat & Share | Skill Exchange",
    page_icon="💬",
    layout="wide"
)

apply_platform_style()


# Refresh the chat automatically every 5 seconds
st_autorefresh(
    interval=5000,
    key="chat_auto_refresh"
)


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


# Update the user's last-active time
update_last_active(user_id)


# Load user's conversations
conversations = get_user_conversations(user_id)


# Page header
render_page_header(
    "💬 Chat & Share",
    "Chat with your skill partners and exchange learning resources."
)


# Show a message when there are no conversations
if not conversations:

    render_sidebar(
        full_name=full_name
    )

    st.info(
        "💬 You don't have any conversations yet. "
        "Accept a skill exchange request to start chatting."
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "📨 Manage Requests",
            use_container_width=True
        ):
            st.switch_page("pages/request.py")

    with c2:

        if st.button(
            "🔍 Find Matches",
            use_container_width=True
        ):
            st.switch_page("pages/matches.py")

    st.stop()


# Get optional user_id from the request page
requested_user_id = st.query_params.get("user_id")

default_index = 0

if requested_user_id:

    try:
        requested_user_id = int(requested_user_id)

        for index, conversation in enumerate(conversations):

            if (
                conversation["other_user_id"]
                == requested_user_id
            ):
                default_index = index
                break

    except (ValueError, TypeError):
        default_index = 0


# Create labels for the conversation list
conversation_labels = []

for conversation in conversations:

    name = conversation["full_name"]
    unread_count = conversation["unread_count"]
    last_message = conversation["last_message"]

    if last_message:
        preview = last_message[:30]

        if len(last_message) > 30:
            preview += "..."
    else:
        preview = "No messages yet"

    if unread_count > 0:
        label = f"🔴 {name} ({unread_count})"
    else:
        label = f"👤 {name}"

    # Preview is calculated for future UI use
    # and keeps the conversation data easy to extend.
    _ = preview

    conversation_labels.append(label)


# Show the common sidebar and conversation list
selected_index = render_sidebar(
    full_name=full_name,
    show_conversations=True,
    conversation_labels=conversation_labels,
    default_index=default_index
)


# Get the selected conversation
selected_conversation = conversations[selected_index]

conversation_id = selected_conversation["conversation_id"]
other_user_id = selected_conversation["other_user_id"]
other_user_name = selected_conversation["full_name"]
other_user_email = selected_conversation["email"]
other_user_last_active = selected_conversation["last_active_at"]


# Security check:
# Only participants can access a conversation.
if not user_has_conversation_access(
    conversation_id,
    user_id
):
    st.error(
        "🚫 You don't have permission to access "
        "this conversation."
    )
    st.stop()


# Calculate the partner's activity status
activity_text = "⚪ Offline"

if other_user_last_active:

    now = datetime.now()

    difference = (
        now - other_user_last_active
    ).total_seconds()

    if difference <= 120:

        activity_text = "🟢 Active now"

    elif difference <= 3600:

        minutes = max(
            1,
            int(difference // 60)
        )

        activity_text = (
            f"🟡 Last active "
            f"{minutes} minute(s) ago"
        )

    elif difference <= 86400:

        hours = max(
            1,
            int(difference // 3600)
        )

        activity_text = (
            f"⚪ Last active "
            f"{hours} hour(s) ago"
        )

    else:

        days = max(
            1,
            int(difference // 86400)
        )

        activity_text = (
            f"⚪ Last active "
            f"{days} day(s) ago"
        )


# Conversation partner header
header_left, header_right = st.columns([5, 1])

with header_left:

    with st.container(border=True):

        st.markdown(
            f"## 👤 {other_user_name}"
        )

        st.caption(
            f"📧 {other_user_email}"
        )

        st.write(activity_text)


with header_right:

    st.write("")

    if st.button(
        "🔄 Refresh",
        use_container_width=True
    ):
        st.rerun()


# Mark received messages as read
mark_messages_as_read(
    conversation_id,
    user_id
)


# Load conversation messages
messages = get_messages(
    conversation_id,
    user_id
)


if not messages:

    with st.container(border=True):

        st.markdown("### 👋 Start the Conversation")

        st.write(
            "Ask a question, share your knowledge, "
            "or help your partner learn."
        )

else:

    for message in messages:

        sender_id = message["sender_id"]
        sender_name = message["full_name"]
        message_text = message["message_text"]
        sent_at = message["sent_at"]

        formatted_time = ""

        if sent_at:
            formatted_time = sent_at.strftime(
                "%d %b %Y, %I:%M %p"
            )

        if sender_id == user_id:

            with st.chat_message(
                "user",
                avatar="🧑"
            ):

                st.markdown("**You**")
                st.write(message_text)

                if formatted_time:
                    st.caption(
                        f"🕐 {formatted_time}"
                    )

        else:

            with st.chat_message(
                "assistant",
                avatar="👤"
            ):

                st.markdown(
                    f"**{sender_name}**"
                )

                st.write(message_text)

                if formatted_time:
                    st.caption(
                        f"🕐 {formatted_time}"
                    )


# Message input
message_text = st.chat_input(
    "Write a message..."
)

if message_text:

    success = send_message(
        conversation_id,
        user_id,
        message_text
    )

    if success:

        update_last_active(user_id)
        st.rerun()

    else:

        st.error(
            "❌ Message could not be sent."
        )


# Learning resources
st.divider()

st.markdown(
    '<div class="platform-section-title">'
    '📚 Learning Resources'
    '</div>',
    unsafe_allow_html=True
)

links_tab, files_tab = st.tabs(
    [
        "🔗 Shared Links",
        "📎 Shared Files"
    ]
)


# Shared links
with links_tab:

    shared_links = get_shared_links(
        conversation_id,
        user_id
    )

    if shared_links:

        for link in shared_links:

            with st.container(border=True):

                st.markdown(
                    f"### 🔗 {link['full_name']}"
                )

                st.markdown(
                    f"[{link['url']}]({link['url']})"
                )

                if link["created_at"]:

                    st.caption(
                        "🕐 "
                        + link["created_at"].strftime(
                            "%d %b %Y, %I:%M %p"
                        )
                    )

    else:

        st.info(
            "📚 No learning links shared yet."
        )

    st.write("")

    st.subheader("➕ Share a Learning Link")

    with st.form(
        "share_link_form",
        clear_on_submit=True
    ):

        link_url = st.text_input(
            "Learning URL",
            placeholder="https://example.com/python"
        )

        submitted = st.form_submit_button(
            "🔗 Share Link",
            use_container_width=True
        )

        if submitted:

            success, message = share_link(
                conversation_id,
                user_id,
                link_url
            )

            if success:

                st.success(message)
                update_last_active(user_id)
                st.rerun()

            else:

                st.error(message)


# Shared files
with files_tab:

    shared_files = get_shared_files(
        conversation_id,
        user_id
    )

    if shared_files:

        for shared_file in shared_files:

            with st.container(border=True):

                left, right = st.columns([4, 1])

                with left:

                    st.markdown(
                        f"### 📄 "
                        f"{shared_file['original_filename']}"
                    )

                    st.caption(
                        f"👤 Shared by "
                        f"{shared_file['full_name']}"
                    )

                    st.caption(
                        f"📏 "
                        f"{format_file_size(shared_file['file_size'])}"
                    )

                    if shared_file["created_at"]:

                        st.caption(
                            "🕐 "
                            + shared_file["created_at"].strftime(
                                "%d %b %Y, %I:%M %p"
                            )
                        )

                with right:

                    file_path = shared_file["file_path"]

                    if os.path.exists(file_path):

                        with open(
                            file_path,
                            "rb"
                        ) as file:

                            data = file.read()

                        st.download_button(
                            "⬇️ Download",
                            data=data,
                            file_name=shared_file[
                                "original_filename"
                            ],
                            key=(
                                f"download_"
                                f"{shared_file['file_id']}"
                            ),
                            use_container_width=True
                        )

                    else:

                        st.error("File unavailable")

    else:

        st.info(
            "📚 No learning files shared yet."
        )

    st.write("")

    st.subheader("➕ Share a Learning File")

    uploaded_file = st.file_uploader(
        "Choose a learning file",
        type=[
            "pdf",
            "docx",
            "xlsx",
            "txt"
        ],
        help=(
            "Allowed: PDF, DOCX, XLSX, TXT. "
            "Maximum size: 10 MB."
        )
    )

    if uploaded_file:

        st.write(
            f"📄 Selected: **{uploaded_file.name}**"
        )

        st.caption(
            f"📏 {format_file_size(uploaded_file.size)}"
        )

        if st.button(
            "📎 Share File",
            use_container_width=True
        ):

            success, message = save_shared_file(
                conversation_id,
                user_id,
                uploaded_file
            )

            if success:

                st.success(message)
                update_last_active(user_id)
                st.rerun()

            else:

                st.error(message)


st.divider()


# Navigation to other parts of the application
st.subheader("🚀 Continue Your Skill Journey")

c1, c2, c3 = st.columns(3)

with c1:

    if st.button(
        "🏠 Dashboard",
        use_container_width=True
    ):
        st.switch_page("pages/dashboard.py")

with c2:

    if st.button(
        "🔍 Find Matches",
        use_container_width=True
    ):
        st.switch_page("pages/matches.py")

with c3:

    if st.button(
        "👤 My Profile",
        use_container_width=True
    ):
        st.switch_page("pages/profile.py")