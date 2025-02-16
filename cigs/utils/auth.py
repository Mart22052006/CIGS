
from cigs.api.schemas.user import UserSchema, UserRole
from cigs.api.user import authenticate_and_get_user
from typing import List, Optional
from fastapi.security import OAuth2PasswordBearer
from cigs.agent.session import AgentSession
from cigs.utils.log import logger
from cigs.storage.agent.sqlite import SqlAgentStorage
from jose import JWTError, jwt
from config import Config
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)

async def get_user_by_session(session_id: str) -> Optional[UserSchema]:
    """Получение пользователя по session_id"""
    try:
        session = await AgentSession.get(session_id)
        if not session or not session.user_id:
            return None

        user = await SqlAgentStorage.fetch_user_from_db(session.user_id)
        if not user:
            return None

        return UserSchema(
            id_user=user.id_user,
            email=user.email,
            role=user.role  # Теперь роль берётся из БД
        )
    except Exception:
        return None


    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def _validate_user(user: UserSchema, roles: List[UserRole] = None):
    """check if user have the needed rights"""
    if not user:
        raise HTTPException(status_code=403, detail="Access denied")

    if user.role == UserRole.ADMIN:
        return

    if roles is not None and user.role not in roles:
        raise HTTPException(status_code=403, detail="Permission denied")
