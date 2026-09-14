import os
from dotenv import load_dotenv


load_dotenv()


DB_CONFIG = {
    "host": os.getenv("SKILL_EXCHANGE_DB_HOST", "localhost"),
    "port": int(os.getenv("SKILL_EXCHANGE_DB_PORT", "3306")),
    "user": os.getenv("SKILL_EXCHANGE_DB_USER", "root"),
    "password": os.getenv("SKILL_EXCHANGE_DB_PASSWORD", "12345678"),
    "database": os.getenv(
        "SKILL_EXCHANGE_DB_NAME",
        "skill_exchange_hub"
    )
}