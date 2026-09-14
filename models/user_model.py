import bcrypt

from database.connection import get_connection


def create_user(full_name, email, password, role="user"):
    connection = get_connection()

    if connection is None:
        return False, "Database connection failed."

    cursor = None

    try:
        cursor = connection.cursor()

        check_query = """
            SELECT user_id
            FROM users
            WHERE email = %s
        """

        cursor.execute(check_query, (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return False, "An account with this email already exists."

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        query = """
            INSERT INTO users (
                full_name,
                email,
                password,
                role
            )
            VALUES (%s, %s, %s, %s)
        """

        values = (
            full_name.strip(),
            email.strip(),
            hashed_password,
            role
        )

        cursor.execute(query, values)
        connection.commit()

        return True, "User registered successfully!"

    except Exception as e:
        connection.rollback()
        return False, f"Registration failed: {e}"

    finally:
        if cursor:
            cursor.close()

        connection.close()


def login_user(email, password):
    connection = get_connection()

    if connection is None:
        return None

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                user_id,
                full_name,
                email,
                password,
                role
            FROM users
            WHERE email = %s
        """

        cursor.execute(query, (email.strip(),))
        user = cursor.fetchone()

        if not user:
            return None

        password_correct = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password"].encode("utf-8")
        )

        if not password_correct:
            return None

        cursor.execute(
            """
                UPDATE users
                SET last_active_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
            """,
            (user["user_id"],)
        )

        connection.commit()

        return {
            "user_id": user["user_id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "role": user.get("role", "user")
        }

    except Exception:
        if connection:
            connection.rollback()

        return None

    finally:
        if cursor:
            cursor.close()

        connection.close()


def update_last_active(user_id):
    connection = get_connection()

    if connection is None:
        return False

    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            UPDATE users
            SET last_active_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
        """

        cursor.execute(query, (user_id,))
        connection.commit()

        return True

    except Exception:
        connection.rollback()
        return False

    finally:
        if cursor:
            cursor.close()

        connection.close()