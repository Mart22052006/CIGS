import json
import time
from pathlib import Path
from typing import Union, Optional, List

from cigs.storage.agent.base import AgentStorage
from cigs.agent import AgentSession
from cigs.utils.log import logger


class JsonFileAgentStorage(AgentStorage):
    def __init__(self, dir_path: Union[str, Path]):
        self.dir_path = Path(dir_path)
        self.dir_path.mkdir(parents=True, exist_ok=True)

    def serialize(self, data: dict) -> str:
        return json.dumps(data, ensure_ascii=False, indent=4)

    def deserialize(self, data: str) -> dict:
        return json.loads(data)

    def create(self) -> None:
        """Create the storage if it doesn't exist."""
        if not self.dir_path.exists():
            self.dir_path.mkdir(parents=True, exist_ok=True)

    def read(self, session_id: str, user_id: Optional[str] = None) -> Optional[AgentSession]:
        """Read an AgentSession from storage."""
        try:
            with open(self.dir_path / f"{session_id}.json", "r", encoding="utf-8") as f:
                data = self.deserialize(f.read())
                if user_id and data["user_id"] != user_id:
                    return None
                return AgentSession.model_validate(data)
        except FileNotFoundError:
            return None

    def get_all_session_ids(self, user_id: Optional[str] = None, agent_id: Optional[str] = None) -> List[str]:
        """Get all session IDs, optionally filtered by user_id and/or agent_id."""
        session_ids = []
        for file in self.dir_path.glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                data = self.deserialize(f.read())
                if (not user_id or data["user_id"] == user_id) and (not agent_id or data["agent_id"] == agent_id):
                    session_ids.append(data["session_id"])
        return session_ids

    def get_all_sessions(self, user_id: Optional[str] = None, agent_id: Optional[str] = None) -> List[AgentSession]:
        """Get all sessions, optionally filtered by user_id and/or agent_id."""
        sessions = []
        for file in self.dir_path.glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                data = self.deserialize(f.read())
                if (not user_id or data["user_id"] == user_id) and (not agent_id or data["agent_id"] == agent_id):
                    sessions.append(AgentSession.model_validate(data))
        return sessions

    def upsert(self, session: AgentSession) -> Optional[AgentSession]:
        """Insert or update an AgentSession in storage."""
        try:
            data = session.model_dump()
            data["updated_at"] = int(time.time())
            if "created_at" not in data:
                data["created_at"] = data["updated_at"]

            with open(self.dir_path / f"{session.session_id}.json", "w", encoding="utf-8") as f:
                f.write(self.serialize(data))
            return session
        except Exception as e:
            logger.error(f"Error upserting session: {e}")
            return None

    def delete_session(self, session_id: Optional[str] = None):
        """Delete a session from storage."""
        if session_id is None:
            return
        try:
            (self.dir_path / f"{session_id}.json").unlink(missing_ok=True)
        except Exception as e:
            logger.error(f"Error deleting session: {e}")

    def drop(self) -> None:
        """Drop all sessions from storage."""
        for file in self.dir_path.glob("*.json"):
            file.unlink()

    def upgrade_schema(self) -> None:
        """Upgrade the schema of the storage."""
        pass

    def fetch_user_from_db(self, user_id: str) -> Optional[dict]:
        """Получение пользователя по user_id из JSON-хранилища."""
        for file in self.dir_path.glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                data = self.deserialize(f.read())
                if data["user_id"] == user_id:
                    return {
                        "id_user": data["user_id"],
                        "email": data.get("user_data", {}).get("email", ""),
                        "role": data.get("user_data", {}).get("role", "user"),
                        "username": data.get("user_data", {}).get("username", ""),
                    }
        return None
