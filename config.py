import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "Game_play@123")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)

    # Email супер-админа
    SUPER_ADMIN_EMAIL = os.getenv("SUPER_ADMIN_EMAIL", "admin@gmail.com")

    # Лимит агентов на одного пользователя
    AGENT_LIMIT = int(os.getenv("AGENT_LIMIT", 1))
