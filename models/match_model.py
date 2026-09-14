from database.connection import get_connection


def find_matches(user_id):
    connection = get_connection()

    if connection is None:
        return []

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        # Get current user's learning skills
        cursor.execute(
            """
            SELECT skill_id
            FROM user_skills
            WHERE user_id = %s
              AND skill_type = 'learn'
            """,
            (user_id,)
        )

        learning_skill_ids = {
            row["skill_id"]
            for row in cursor.fetchall()
        }

        # Get current user's teaching skills
        cursor.execute(
            """
            SELECT skill_id
            FROM user_skills
            WHERE user_id = %s
              AND skill_type = 'teach'
            """,
            (user_id,)
        )

        teaching_skill_ids = {
            row["skill_id"]
            for row in cursor.fetchall()
        }

        # Get all other users
        cursor.execute(
            """
            SELECT user_id, full_name, email
            FROM users
            WHERE user_id != %s
            """,
            (user_id,)
        )

        users = cursor.fetchall()
        matches = []

        for user in users:
            other_user_id = user["user_id"]

            # Skills the other user can teach
            cursor.execute(
                """
                SELECT skill_id
                FROM user_skills
                WHERE user_id = %s
                  AND skill_type = 'teach'
                """,
                (other_user_id,)
            )

            other_teach = {
                row["skill_id"]
                for row in cursor.fetchall()
            }

            # Skills the other user wants to learn
            cursor.execute(
                """
                SELECT skill_id
                FROM user_skills
                WHERE user_id = %s
                  AND skill_type = 'learn'
                """,
                (other_user_id,)
            )

            other_learn = {
                row["skill_id"]
                for row in cursor.fetchall()
            }

            # Find two-way matches
            learn_from_them = (
                learning_skill_ids & other_teach
            )

            teach_to_them = (
                teaching_skill_ids & other_learn
            )

            # Get skill names
            learn_from_them_names = []
            teach_to_them_names = []

            for skill_id in learn_from_them:
                cursor.execute(
                    """
                    SELECT skill_name
                    FROM skills
                    WHERE skill_id = %s
                    """,
                    (skill_id,)
                )

                result = cursor.fetchone()

                if result:
                    learn_from_them_names.append(
                        result["skill_name"]
                    )

            for skill_id in teach_to_them:
                cursor.execute(
                    """
                    SELECT skill_name
                    FROM skills
                    WHERE skill_id = %s
                    """,
                    (skill_id,)
                )

                result = cursor.fetchone()

                if result:
                    teach_to_them_names.append(
                        result["skill_name"]
                    )

            # Match counts
            total_matches = (
                len(learn_from_them)
                + len(teach_to_them)
            )

            # Learning match score
            if learning_skill_ids:
                learning_match_score = (
                    len(learn_from_them)
                    / len(learning_skill_ids)
                ) * 100
            else:
                learning_match_score = 0

            # Teaching match score
            if teaching_skill_ids:
                teaching_match_score = (
                    len(teach_to_them)
                    / len(teaching_skill_ids)
                ) * 100
            else:
                teaching_match_score = 0

            # Final score
            score = round(
                (
                    learning_match_score
                    + teaching_match_score
                ) / 2
            )

            # Add only users with at least one match
            if total_matches > 0:
                matches.append(
                    {
                        "user_id": other_user_id,
                        "full_name": user["full_name"],
                        "email": user["email"],
                        "score": score,
                        "learning_match_score": round(
                            learning_match_score
                        ),
                        "teaching_match_score": round(
                            teaching_match_score
                        ),
                        "learn_from_them_names":
                            learn_from_them_names,
                        "teach_to_them_names":
                            teach_to_them_names,
                        "teach_matches": len(
                            teach_to_them
                        ),
                        "learn_matches": len(
                            learn_from_them
                        ),
                        "total_matches": total_matches
                    }
                )

        # Highest score first
        matches.sort(
            key=lambda match: match["score"],
            reverse=True
        )

        return matches

    except Exception:
        return []

    finally:
        if cursor:
            cursor.close()

        connection.close()