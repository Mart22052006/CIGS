from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class UserSchema(BaseModel):
    """Schema for user data returned by the API."""
    id_user: str
    email: Optional[str] = None
    role: str = "user"
    username: Optional[str] = None
    name: Optional[str] = None
    email_verified: Optional[bool] = False
    is_active: Optional[bool] = True
    is_machine: Optional[bool] = False
    user_data: Optional[Dict[str, Any]] = None


class EmailPasswordAuthSchema(BaseModel):
    email: str
    password: str
    auth_source: str = "cli"

class Token(BaseModel):
    access_token: str
    token_type: str
