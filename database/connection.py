import mysql.connector
from mysql.connector import Error

from config import DB_CONFIG


def get_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )

        if connection.is_connected():
            return connection

    except Error:
        return None

    return None