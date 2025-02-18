import os
import uuid
import pickle
import hashlib
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Optional
from functools import wraps
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from config import Config
from cigs.api.schemas.user import UserSchema, UserRole, Token
from web3 import Web3
from eth_account.messages import encode_defunct
from fastapi import HTTPException
from pydantic import BaseModel

AGENT_LIMIT = int(os.getenv("AGENT_LIMIT", 1))
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
w3 = Web3(Web3.HTTPProvider(os.getenv("BASE_RPC_URL")))


def init_db():
    conn, cursor = get_db()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            username TEXT,
            name TEXT,
            email_verified BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            is_machine BOOLEAN DEFAULT FALSE,
            user_data TEXT,
            wallet_address TEXT
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            agent_name TEXT,
            main_purpose TEXT,
            work_description TEXT,
            writing_style TEXT,
            sample_content TEXT,
            common_phrases TEXT,
            model_selection TEXT,
            apikey TEXT,
            pkl_path TEXT,
            create_time TEXT,
            created_by TEXT
        )
    """)

    conn.commit()
    conn.close()


# Подключение к БД
def get_db():
    db_path = "agents.db"
    if not os.path.exists(db_path):
        raise RuntimeError(f"Database file not found: {db_path}")

    conn = sqlite3.connect(db_path)
    return conn, conn.cursor()

init_db()

class WalletAuthRequest(BaseModel):
    wallet_address: str
    signature: str
    message: str
class AgentRequest(BaseModel):
    agent_name: str
    main_purpose: str
    work_description: str
    writing_style: str
    sample_content: str
    common_phrases: str
    model_selection: str

# Модель токена
class Token(BaseModel):
    access_token: str
    token_type: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Хеширование пароля
def get_hashed_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_user(token: str = Depends(oauth2_scheme)) -> UserSchema:
    """Получение текущего пользователя по токену"""
    if not token:
        raise HTTPException(status_code=401, detail="Authentication token is missing")

    try:
        # Декодируем токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_role: str = payload.get("role")

        if not username or not user_role:
            raise HTTPException(status_code=401, detail="Invalid authentication data")

        # Подключение к БД и получение данных пользователя
        conn, cursor = get_db()
        cursor.execute("""
            SELECT id, email, name, email_verified, is_active, is_machine, user_data 
            FROM users WHERE username = ?
        """, (username,))
        user_row = cursor.fetchone()
        conn.close()

        if not user_row:
            raise HTTPException(status_code=401, detail="User not found")

        return UserSchema(
            id_user=str(user_row[0]),
            email=user_row[1],
            role=user_role,
            username=username,
            name=user_row[2],
            email_verified=bool(user_row[3]),
            is_active=bool(user_row[4]),
            is_machine=bool(user_row[5]),
            user_data=json.loads(user_row[6]) if user_row[6] else None
        )

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def is_wallet_on_base_chain(wallet_address: str) -> bool:
    """Проверяет, существует ли кошелек в сети Base Chain (даже если баланс 0)"""
    try:
        balance = w3.eth.get_balance(wallet_address)  # Получаем баланс кошелька
        return True  # Возвращаем True, даже если баланс 0
    except Exception as e:
        print(f"Ошибка проверки кошелька: {e}")
        return False

def check_by_role(roles: List[UserRole]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, current_user: UserSchema = Depends(get_current_user), **kwargs):
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")

            if roles and current_user.role not in roles:
                raise HTTPException(status_code=403, detail="Permission denied")

            return func(*args, current_user=current_user, **kwargs)

        return wrapper

    return decorator

# Регистрация пользователя
def register_user(email: str, username: str, name: str, password: str, role: Optional[str] = None):
    conn, cursor = get_db()

    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        raise ValueError("User with this email already exists")

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        raise ValueError("Username is already taken")

    # Проверяем, если зарегистрированный пользователь - супер-админ, назначаем ему роль ADMIN
    if username == os.getenv("SUPER_ADMIN_USERNAME") and password == os.getenv("SUPER_ADMIN_PASSWORD"):
        role = UserRole.ADMIN
    else:
        role = role or UserRole.USER  # Если роль не передана, по умолчанию USER
    password_hash = get_hashed_password(password)

    cursor.execute("""
        INSERT INTO users (email, username, name, password_hash, role) 
        VALUES (?, ?, ?, ?, ?)
    """, (email, username, name, password_hash, role))

    conn.commit()
    conn.close()

    return {"message": f"User {username} registered successfully"}

def wallet_register(wallet_address: str, signature: str, message: str):
    """Регистрация пользователя через кошелек MetaMask (Base Chain)"""
    # Проверяем подпись
    message_encoded = encode_defunct(text=message)
    recovered_address = w3.eth.account.recover_message(message_encoded, signature=signature)

    if recovered_address.lower() != wallet_address.lower():
        raise HTTPException(status_code=400, detail="Signature verification failed")

    # Проверяем, существует ли кошелек в сети Base
    if not is_wallet_on_base_chain(wallet_address):
        raise HTTPException(status_code=400, detail="Wallet is not on Base Chain")

    conn, cursor = get_db()

    cursor.execute("SELECT * FROM users WHERE wallet_address = ?", (wallet_address,))
    existing_user = cursor.fetchone()

    if existing_user:
        return {"message": "User already exists", "wallet": wallet_address}

    cursor.execute("""
        INSERT INTO users (wallet_address) 
        VALUES (?)
    """, (wallet_address,))

    conn.commit()
    conn.close()

    return {"message": "Registration successful", "wallet": wallet_address}


# Аутентификация пользователя
def authenticate_user(username: str, password: str):
    conn, cursor = get_db()
    cursor.execute("SELECT password_hash, role FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if not user or user[0] != get_hashed_password(password):
        raise ValueError("Invalid credentials")

    access_token_expires = timedelta(minutes=int(Config.ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = jwt.encode(
        {"sub": username, "role": user[1], "exp": datetime.utcnow() + access_token_expires},
        Config.SECRET_KEY, algorithm=Config.ALGORITHM
    )

    return Token(access_token=access_token, token_type="bearer")

def authenticate_wallet_user(wallet_address: str, signature: str, message: str):
    """Авторизация пользователя через MetaMask"""
    # Проверяем подпись
    message_encoded = encode_defunct(text=message)
    recovered_address = w3.eth.account.recover_message(message_encoded, signature=signature)

    if recovered_address.lower() != wallet_address.lower():
        raise HTTPException(status_code=400, detail="Signature verification failed")

    conn, cursor = get_db()
    cursor.execute("SELECT role FROM users WHERE wallet_address = ?", (wallet_address,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Генерируем токен
    access_token_expires = timedelta(minutes=int(Config.ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = jwt.encode(
        {"sub": wallet_address, "role": user[0], "exp": datetime.utcnow() + access_token_expires},
        Config.SECRET_KEY, algorithm=Config.ALGORITHM
    )

    return {"message": "Login successful", "wallet": wallet_address, "token": access_token}
# Получение информации о пользователе
def get_user_info(user: dict):
    return user

# Создание агента
def create_agent(agent: AgentRequest, current_user: UserSchema):
    conn, cursor = get_db()
    if current_user.role == UserRole.USER:
        cursor.execute("SELECT COUNT(*) FROM agents WHERE created_by = ?", (current_user.username,))
        user_agents_count = cursor.fetchone()[0]

        if user_agents_count >= AGENT_LIMIT:
            raise ValueError("You have reached the agent creation limit.")

    agent_id = str(uuid.uuid4())
    apikey = hashlib.sha256(agent_id.encode()).hexdigest()
    pkl_path = f"agents/{agent_id}.pkl"

    os.makedirs(os.path.dirname(pkl_path), exist_ok=True)
    with open(pkl_path, "wb") as f:
        pickle.dump(agent.dict(), f)

    cursor.execute("""
        INSERT INTO agents (id, agent_name, main_purpose, work_description, writing_style,
                            sample_content, common_phrases, model_selection, apikey, pkl_path, create_time, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (agent_id, agent.agent_name, agent.main_purpose, agent.work_description,
          agent.writing_style, agent.sample_content, agent.common_phrases,
          agent.model_selection, apikey, pkl_path, datetime.now().isoformat(), current_user.username))

    conn.commit()
    conn.close()

    return {"id": agent_id, "apikey": apikey, "pkl_path": pkl_path}

# Получение списка агентов
def get_agents():
    conn, cursor = get_db()
    cursor.execute("SELECT * FROM agents")
    rows = cursor.fetchall()
    conn.close()

    return [dict(zip(
        ["id", "agent_name", "main_purpose", "work_description", "writing_style",
         "sample_content", "common_phrases", "model_selection", "apikey", "pkl_path", "create_time", "created_by"],
        row)) for row in rows]

# Получение ответа от агента
def get_agent_response(agent_id: str, apikey: str, user_input: str):
    conn, cursor = get_db()
    cursor.execute("SELECT * FROM agents WHERE id = ? AND apikey = ?", (agent_id, apikey))
    agent_data = cursor.fetchone()
    conn.close()

    if not agent_data:
        raise ValueError("Agent not found or API Key is invalid")

    with open(agent_data[9], "rb") as f:
        agent = pickle.load(f)

    return {"response": f"Agent {agent['agent_name']} response to {user_input}"}
