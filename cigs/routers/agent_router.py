from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Depends, Header
from fastapi.responses import StreamingResponse, JSONResponse
from typing import List, Optional, Union

from typing import List
from cigs.services.agent_service import (
    AgentRequest,
    register_user,
    authenticate_user,
    get_user_info,
    create_agent,
    get_agents,
    get_agent_response,
    get_current_user,
    check_by_role,

)
from cigs.api.schemas.user import (
                          UserSchema,
                          UserRole,
                          Token,
                        )

router = APIRouter()


# Регистрация пользователя
@router.post("/register", summary="User registration")
def register(
    email: str = Form(...),
    username: str = Form(...),
    name: str = Form(...),
    password: str = Form(...)
):
    return register_user(email, username, name, password)

# Авторизация пользователя
@router.post("/login", response_model=Token, summary="Авторизация пользователя")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return authenticate_user(form_data.username, form_data.password)

# Доступ к информации о текущем пользователе
@router.get("/me", summary="Информация о пользователе")
def get_me(user: dict = Depends(get_current_user)):
    return get_user_info(user)

# Регистрация админа
@router.post("/admin_register", summary="Admin registration")
@check_by_role([UserRole.ADMIN])
def admin_register(
    email: str = Form(...),
    username: str = Form(...),
    name: str = Form(...),
    password: str = Form(...)
):
    return register_user(email, username, name, password, role=UserRole.ADMIN)

# Создание агента
@router.post("/api/agent")
async def create_new_agent(
    agent: AgentRequest,
    current_user: UserSchema = Depends(get_current_user)
):
    return create_agent(agent, current_user)

# Получение списка агентов (только админ)
@router.get("/agents", response_model=List[AgentRequest])
@check_by_role([UserRole.ADMIN])
async def list_agents(current_user: UserSchema = Depends(get_current_user)):
    return get_agents()

# Получение ответа от агента
@router.post("/agents/{agent_id}")
def agent_interact(agent_id: str, apikey: str = Header(...), user_input: str = Form(...)):
    return get_agent_response(agent_id, apikey, user_input)
