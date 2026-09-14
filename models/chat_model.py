from database.connection import get_connection


def get_or_create_conversation(user1_id, user2_id):
    connection = get_connection()

    if connection is None:
        return None

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        # Keep user IDs in a consistent order
        first_user = min(user1_id, user2_id)
        second_user = max(user1_id, user2_id)

        # Check whether the conversation already exists
        query = """
            SELECT conversation_id
            FROM conversations
            WHERE user1_id = %s
              AND user2_id = %s
        """

        cursor.execute(
            query,
            (first_user, second_user)
        )

        conversation = cursor.fetchone()

        if conversation:
            return conversation["conversation_id"]

        # Create a new conversation
        insert_query = """
            INSERT INTO conversations (
                user1_id,
                user2_id
            )
            VALUES (%s, %s)
        """

        cursor.execute(
            insert_query,
            (first_user, second_user)
        )

        conversation_id = cursor.lastrowid
        connection.commit()

        return conversation_id

    except Exception:
        connection.rollback()
        return None

    finally:
        if cursor:
            cursor.close()

        connection.close()


def user_has_conversation_access(conversation_id, user_id):
    connection = get_connection()

    if connection is None:
        return False

    cursor = None

    try:
        cursor = connection.cursor()

        # Check that the user belongs to this conversation
        query = """
            SELECT conversation_id
            FROM conversations
            WHERE conversation_id = %s
              AND (
                  user1_id = %s
                  OR user2_id = %s
              )
        """

        cursor.execute(
            query,
            (conversation_id, user_id, user_id)
        )

        conversation = cursor.fetchone()

        return conversation is not None

    except Exception:
        return False

    finally:
        if cursor:
            cursor.close()

        connection.close()


def send_message(conversation_id, sender_id, message_text):
    connection = get_connection()

    if connection is None:
        return False

    cursor = None

    try:
        # Prevent empty messages
        if not message_text.strip():
            return False

        cursor = connection.cursor()

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
            return False

        # Insert the message
        query = """
            INSERT INTO messages (
                conversation_id,
                sender_id,
                message_text,
                is_read
            )
            VALUES (%s, %s, %s, FALSE)
        """

        cursor.execute(
            query,
            (
                conversation_id,
                sender_id,
                message_text.strip()
            )
        )

        connection.commit()

        return True

    except Exception:
        connection.rollback()
        return False

    finally:
        if cursor:
            cursor.close()

        connection.close()


def get_messages(conversation_id, user_id):
    connection = get_connection()

    if connection is None:
        return []

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        # Security check:
        # The user must belong to the conversation.
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

        # Get all messages in chronological order
        query = """
            SELECT
                m.message_id,
                m.conversation_id,
                m.sender_id,
                m.message_text,
                m.sent_at,
                m.is_read,
                u.full_name
            FROM messages m
            JOIN users u
                ON m.sender_id = u.user_id
            WHERE m.conversation_id = %s
            ORDER BY m.sent_at ASC
        """

        cursor.execute(query, (conversation_id,))

        return cursor.fetchall()

    except Exception:
        return []

    finally:
        if cursor:
            cursor.close()

        connection.close()


def mark_messages_as_read(conversation_id, user_id):
    connection = get_connection()

    if connection is None:
        return False

    cursor = None

    try:
        cursor = connection.cursor()

        # Security check
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
            return False

        # Mark messages from the other user as read
        query = """
            UPDATE messages
            SET is_read = TRUE
            WHERE conversation_id = %s
              AND sender_id != %s
              AND is_read = FALSE
        """

        cursor.execute(
            query,
            (conversation_id, user_id)
        )

        connection.commit()

        return True

    except Exception:
        connection.rollback()
        return False

    finally:
        if cursor:
            cursor.close()

        connection.close()


def get_unread_count(conversation_id, user_id):
    connection = get_connection()

    if connection is None:
        return 0

    cursor = None

    try:
        cursor = connection.cursor()

        # Security check
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
            return 0

        # Count unread messages from the other user
        query = """
            SELECT COUNT(*) AS unread_count
            FROM messages
            WHERE conversation_id = %s
              AND sender_id != %s
              AND is_read = FALSE
        """

        cursor.execute(
            query,
            (conversation_id, user_id)
        )

        result = cursor.fetchone()

        return result[0]

    except Exception:
        return 0

    finally:
        if cursor:
            cursor.close()

        connection.close()


def get_user_conversations(user_id):
    connection = get_connection()

    if connection is None:
        return []

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                c.conversation_id,

                CASE
                    WHEN c.user1_id = %s
                    THEN c.user2_id
                    ELSE c.user1_id
                END AS other_user_id,

                u.full_name,
                u.email,
                u.last_active_at,
                c.created_at,

                -- Last message
                (
                    SELECT m.message_text
                    FROM messages m
                    WHERE m.conversation_id = c.conversation_id
                    ORDER BY m.sent_at DESC
                    LIMIT 1
                ) AS last_message,

                -- Last message time
                (
                    SELECT m.sent_at
                    FROM messages m
                    WHERE m.conversation_id = c.conversation_id
                    ORDER BY m.sent_at DESC
                    LIMIT 1
                ) AS last_message_at,

                -- Unread message count
                (
                    SELECT COUNT(*)
                    FROM messages m
                    WHERE m.conversation_id = c.conversation_id
                      AND m.sender_id != %s
                      AND m.is_read = FALSE
                ) AS unread_count

            FROM conversations c

            JOIN users u
                ON u.user_id = CASE
                    WHEN c.user1_id = %s
                    THEN c.user2_id
                    ELSE c.user1_id
                END

            WHERE c.user1_id = %s
               OR c.user2_id = %s

            ORDER BY COALESCE(
                (
                    SELECT MAX(m.sent_at)
                    FROM messages m
                    WHERE m.conversation_id = c.conversation_id
                ),
                c.created_at
            ) DESC
        """

        cursor.execute(
            query,
            (
                user_id,
                user_id,
                user_id,
                user_id,
                user_id
            )
        )

        return cursor.fetchall()

    except Exception:
        return []

    finally:
        if cursor:
            cursor.close()

        connection.close()