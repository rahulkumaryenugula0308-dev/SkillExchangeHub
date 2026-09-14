from database.connection import get_connection


def get_all_skills():
    """Get all available skills from the database."""

    connection = get_connection()

    if connection is None:
        return []

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        # Get all skills sorted alphabetically
        query = """
            SELECT skill_id, skill_name, category
            FROM skills
            ORDER BY skill_name
        """

        cursor.execute(query)

        return cursor.fetchall()

    except Exception:
        return []

    finally:
        if cursor:
            cursor.close()

        connection.close()


def save_user_skill(user_id, skill_id, skill_type):
    """Save a teaching or learning skill for a user."""

    connection = get_connection()

    if connection is None:
        return False

    cursor = None

    try:
        cursor = connection.cursor()

        # Save the user's selected skill and its type
        query = """
            INSERT INTO user_skills (
                user_id,
                skill_id,
                skill_type
            )
            VALUES (%s, %s, %s)
        """

        cursor.execute(
            query,
            (user_id, skill_id, skill_type)
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