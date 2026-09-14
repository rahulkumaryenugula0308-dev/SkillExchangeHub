import os
import uuid
from urllib.parse import urlparse

from database.connection import get_connection


# Folder where shared files are stored
UPLOAD_FOLDER = "uploads"

# Maximum allowed file size: 10 MB
MAX_FILE_SIZE = 10 * 1024 * 1024

# File types allowed for sharing
ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".xlsx",
    ".txt"
}


# Create the upload folder if it does not already exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def validate_url(url):
    """Check whether the URL is a valid HTTP or HTTPS URL."""

    if not url:
        return False

    url = url.strip()

    try:
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            return False

        if not parsed.netloc:
            return False

        return True

    except Exception:
        return False


def share_link(conversation_id, sender_id, url):
    """Share a learning link inside a conversation."""

    if not validate_url(url):
        return (
            False,
            "❌ Please enter a valid HTTP or HTTPS URL."
        )

    connection = get_connection()

    if connection is None:
        return (
            False,
            "❌ Database connection failed."
        )

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        # Security check:
        # The sender must belong to the conversation.
        access_query = """
            SELECT conversation_id
            FROM conversations
            WHERE conversation_id = %s
              AND (
                  user1_id = %s
                  OR user2_id = %s
              )
        """

        cursor.execute(
            access_query,
            (conversation_id, sender_id, sender_id)
        )

        conversation = cursor.fetchone()

        if not conversation:
            return (
                False,
                "🚫 You don't have permission "
                "to share a link here."
            )

        # Save the link in the database
        insert_query = """
            INSERT INTO shared_links (
                conversation_id,
                sender_id,
                url
            )
            VALUES (%s, %s, %s)
        """

        cursor.execute(
            insert_query,
            (
                conversation_id,
                sender_id,
                url.strip()
            )
        )

        connection.commit()

        return (
            True,
            "✅ Learning link shared successfully!"
        )

    except Exception as e:
        connection.rollback()

        return (
            False,
            f"❌ Could not share link: {e}"
        )

    finally:
        if cursor:
            cursor.close()

        connection.close()


def get_shared_links(conversation_id, user_id):
    """Get all learning links shared in a conversation."""

    connection = get_connection()

    if connection is None:
        return []

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        # Security check:
        # Only conversation participants can view shared links.
        access_query = """
            SELECT conversation_id
            FROM conversations
            WHERE conversation_id = %s
              AND (
                  user1_id = %s
                  OR user2_id = %s
              )
        """

        cursor.execute(
            access_query,
            (conversation_id, user_id, user_id)
        )

        conversation = cursor.fetchone()

        if not conversation:
            return []

        # Get all links from this conversation
        query = """
            SELECT
                sl.link_id,
                sl.conversation_id,
                sl.sender_id,
                sl.url,
                sl.created_at,
                u.full_name
            FROM shared_links sl
            JOIN users u
                ON sl.sender_id = u.user_id
            WHERE sl.conversation_id = %s
            ORDER BY sl.created_at ASC
        """

        cursor.execute(query, (conversation_id,))

        return cursor.fetchall()

    except Exception:
        return []

    finally:
        if cursor:
            cursor.close()

        connection.close()


def validate_file(uploaded_file):
    """Validate file type and size before saving."""

    if uploaded_file is None:
        return (
            False,
            "❌ No file selected."
        )

    original_filename = uploaded_file.name

    # Check file extension
    extension = os.path.splitext(
        original_filename
    )[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(
            sorted(ALLOWED_EXTENSIONS)
        )

        return (
            False,
            f"❌ Unsupported file type. "
            f"Allowed: {allowed}"
        )

    # Check file size
    file_size = uploaded_file.size

    if file_size > MAX_FILE_SIZE:
        return (
            False,
            "❌ File is too large. "
            "Maximum size is 10 MB."
        )

    if file_size <= 0:
        return (
            False,
            "❌ The selected file is empty."
        )

    return True, "✅ File is valid."


def save_shared_file(
    conversation_id,
    sender_id,
    uploaded_file
):
    """Validate and save a file shared in a conversation."""

    # Validate the file before saving it
    valid, message = validate_file(uploaded_file)

    if not valid:
        return False, message

    connection = get_connection()

    if connection is None:
        return (
            False,
            "❌ Database connection failed."
        )

    cursor = None
    stored_path = None

    try:
        cursor = connection.cursor(dictionary=True)

        # Security check:
        # The sender must belong to the conversation.
        access_query = """
            SELECT conversation_id
            FROM conversations
            WHERE conversation_id = %s
              AND (
                  user1_id = %s
                  OR user2_id = %s
              )
        """

        cursor.execute(
            access_query,
            (conversation_id, sender_id, sender_id)
        )

        conversation = cursor.fetchone()

        if not conversation:
            return (
                False,
                "🚫 You don't have permission "
                "to upload a file here."
            )

        # Get file information
        original_filename = uploaded_file.name

        extension = os.path.splitext(
            original_filename
        )[1].lower()

        file_size = uploaded_file.size

        file_type = (
            uploaded_file.type
            or "application/octet-stream"
        )

        # Create a unique internal filename
        # so uploaded files do not overwrite each other.
        unique_name = f"{uuid.uuid4().hex}{extension}"

        stored_path = os.path.join(
            UPLOAD_FOLDER,
            unique_name
        )

        # Save the actual file to the uploads folder
        with open(stored_path, "wb") as file:
            file.write(uploaded_file.getbuffer())

        # Save file information to MySQL
        insert_query = """
            INSERT INTO shared_files (
                conversation_id,
                sender_id,
                original_filename,
                stored_filename,
                file_path,
                file_size,
                file_type
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            insert_query,
            (
                conversation_id,
                sender_id,
                original_filename,
                unique_name,
                stored_path,
                file_size,
                file_type
            )
        )

        connection.commit()

        return (
            True,
            "✅ File shared successfully!"
        )

    except Exception as e:
        connection.rollback()

        # Delete the physical file if database saving fails
        try:
            if stored_path and os.path.exists(stored_path):
                os.remove(stored_path)
        except Exception:
            pass

        return (
            False,
            f"❌ Could not share file: {e}"
        )

    finally:
        if cursor:
            cursor.close()

        connection.close()


def get_shared_files(conversation_id, user_id):
    """Get all files shared in a conversation."""

    connection = get_connection()

    if connection is None:
        return []

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        # Security check:
        # Only conversation participants can view shared files.
        access_query = """
            SELECT conversation_id
            FROM conversations
            WHERE conversation_id = %s
              AND (
                  user1_id = %s
                  OR user2_id = %s
              )
        """

        cursor.execute(
            access_query,
            (conversation_id, user_id, user_id)
        )

        conversation = cursor.fetchone()

        if not conversation:
            return []

        # Get files shared in this conversation
        query = """
            SELECT
                sf.file_id,
                sf.conversation_id,
                sf.sender_id,
                sf.original_filename,
                sf.stored_filename,
                sf.file_path,
                sf.file_size,
                sf.file_type,
                sf.created_at,
                u.full_name
            FROM shared_files sf
            JOIN users u
                ON sf.sender_id = u.user_id
            WHERE sf.conversation_id = %s
            ORDER BY sf.created_at ASC
        """

        cursor.execute(query, (conversation_id,))

        return cursor.fetchall()

    except Exception:
        return []

    finally:
        if cursor:
            cursor.close()

        connection.close()


def format_file_size(file_size):
    """Convert a file size in bytes into a readable format."""

    if file_size < 1024:
        return f"{file_size} B"

    if file_size < 1024 * 1024:
        return f"{file_size / 1024:.1f} KB"

    return f"{file_size / (1024 * 1024):.1f} MB"