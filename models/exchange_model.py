from database.connection import get_connection


def send_exchange_request(sender_id, receiver_id):
    connection = get_connection()

    if connection is None:
        return False, "❌ Database connection failed."

    cursor = None

    try:
        cursor = connection.cursor()

        # Check whether a pending request already exists
        check_query = """
            SELECT request_id
            FROM exchange_requests
            WHERE sender_id = %s
              AND receiver_id = %s
              AND status = 'pending'
        """

        cursor.execute(
            check_query,
            (sender_id, receiver_id)
        )

        existing_request = cursor.fetchone()

        if existing_request:
            return False, "⚠️ Request already sent."

        # Insert a new exchange request
        insert_query = """
            INSERT INTO exchange_requests (
                sender_id,
                receiver_id,
                status
            )
            VALUES (%s, %s, 'pending')
        """

        cursor.execute(
            insert_query,
            (sender_id, receiver_id)
        )

        connection.commit()

        return True, "✅ Skill exchange request sent!"

    except Exception as e:
        connection.rollback()

        return False, f"❌ Request failed: {e}"

    finally:
        if cursor:
            cursor.close()

        connection.close()


def get_incoming_requests(receiver_id):
    connection = get_connection()

    if connection is None:
        return []

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                er.request_id,
                er.sender_id,
                er.receiver_id,
                er.status,
                er.requested_at,
                er.responded_at,
                u.full_name,
                u.email
            FROM exchange_requests er
            JOIN users u
                ON er.sender_id = u.user_id
            WHERE er.receiver_id = %s
            ORDER BY er.requested_at DESC
        """

        cursor.execute(query, (receiver_id,))

        return cursor.fetchall()

    except Exception:
        return []

    finally:
        if cursor:
            cursor.close()

        connection.close()


def get_sent_requests(sender_id):
    connection = get_connection()

    if connection is None:
        return []

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                er.request_id,
                er.sender_id,
                er.receiver_id,
                er.status,
                er.requested_at,
                er.responded_at,
                u.full_name,
                u.email
            FROM exchange_requests er
            JOIN users u
                ON er.receiver_id = u.user_id
            WHERE er.sender_id = %s
            ORDER BY er.requested_at DESC
        """

        cursor.execute(query, (sender_id,))

        return cursor.fetchall()

    except Exception:
        return []

    finally:
        if cursor:
            cursor.close()

        connection.close()


def create_conversation(user1_id, user2_id):
    connection = get_connection()

    if connection is None:
        return False, None

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        # Keep user IDs in a consistent order
        first_user = min(user1_id, user2_id)
        second_user = max(user1_id, user2_id)

        # Check whether the conversation already exists
        check_query = """
            SELECT conversation_id
            FROM conversations
            WHERE user1_id = %s
              AND user2_id = %s
        """

        cursor.execute(
            check_query,
            (first_user, second_user)
        )

        existing_conversation = cursor.fetchone()

        if existing_conversation:
            return True, existing_conversation["conversation_id"]

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

        return True, conversation_id

    except Exception:
        connection.rollback()
        return False, None

    finally:
        if cursor:
            cursor.close()

        connection.close()


def update_request_status(request_id, receiver_id, status):
    connection = get_connection()

    if connection is None:
        return False, "❌ Database connection failed."

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        # Only accepted and rejected are valid statuses
        if status not in ["accepted", "rejected"]:
            return False, "❌ Invalid request status."

        # Get the request and verify that this receiver owns it
        request_query = """
            SELECT
                request_id,
                sender_id,
                receiver_id,
                status
            FROM exchange_requests
            WHERE request_id = %s
              AND receiver_id = %s
        """

        cursor.execute(
            request_query,
            (request_id, receiver_id)
        )

        request = cursor.fetchone()

        if not request:
            return False, "❌ Request not found."

        # Prevent processing the same request twice
        if request["status"] != "pending":
            return False, "⚠️ Request was already processed."

        # Update request status
        update_query = """
            UPDATE exchange_requests
            SET
                status = %s,
                responded_at = CURRENT_TIMESTAMP
            WHERE request_id = %s
              AND receiver_id = %s
              AND status = 'pending'
        """

        cursor.execute(
            update_query,
            (status, request_id, receiver_id)
        )

        # When accepted, create a conversation
        if status == "accepted":
            sender_id = request["sender_id"]
            receiver_id = request["receiver_id"]

            # Keep user IDs in a consistent order
            first_user = min(sender_id, receiver_id)
            second_user = max(sender_id, receiver_id)

            conversation_query = """
                SELECT conversation_id
                FROM conversations
                WHERE user1_id = %s
                  AND user2_id = %s
            """

            cursor.execute(
                conversation_query,
                (first_user, second_user)
            )

            conversation = cursor.fetchone()

            # Create the conversation if it doesn't exist
            if not conversation:
                create_query = """
                    INSERT INTO conversations (
                        user1_id,
                        user2_id
                    )
                    VALUES (%s, %s)
                """

                cursor.execute(
                    create_query,
                    (first_user, second_user)
                )

            connection.commit()

            return (
                True,
                "✅ Request accepted! 💬 Chat is now available."
            )

        # When rejected, only the request status is changed
        if status == "rejected":
            connection.commit()

            return True, "❌ Request rejected."

    except Exception as e:
        connection.rollback()

        return False, f"❌ Update failed: {e}"

    finally:
        if cursor:
            cursor.close()

        connection.close()