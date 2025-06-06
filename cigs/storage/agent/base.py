from abc import ABC, abstractmethod
from typing import Optional, List

from cigs.agent.session import AgentSession
from cigs.api.schemas.user import UserSchema, UserRole

class AgentStorage(ABC):
    @abstractmethod
    def create(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def read(self, session_id: str, user_id: Optional[str] = None) -> Optional[AgentSession]:
        raise NotImplementedError

    @abstractmethod
    def get_all_session_ids(self, user_id: Optional[str] = None, agent_id: Optional[str] = None) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def get_all_sessions(self, user_id: Optional[str] = None, agent_id: Optional[str] = None) -> List[AgentSession]:
        raise NotImplementedError

    @abstractmethod
    def upsert(self, session: AgentSession) -> Optional[AgentSession]:
        raise NotImplementedError

    @abstractmethod
    def delete_session(self, session_id: Optional[str] = None):
        raise NotImplementedError

    @abstractmethod
    def drop(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def upgrade_schema(self) -> None:
        raise NotImplementedError
    @abstractmethod
    async def fetch_user_from_db(user_id: str) -> Optional[UserSchema]:
        raise NotImplementedError

