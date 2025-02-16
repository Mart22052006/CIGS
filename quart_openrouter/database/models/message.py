from sqlalchemy import Column, Text, DateTime, Boolean
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
from .base import Base
import uuid


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Text, nullable=False)
    user_query = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    datetime = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    is_direct_message = Column(Boolean, default=False)
    room_id = Column(Text, default="privateroom")

    def to_messages(self):
        user_content = self.user_query
        if not self.is_direct_message:
            user_content = (
                "<user_id>\n"
                f"{self.user_id}\n"
                "</user_id>\n"
                "<message>\n"
                f"{self.user_query}\n"
                "</message>\n"
            )

        return {
            "role": "user",
            "content": user_content,
        }, {
            "role": "assistant",
            "content": self.ai_response,
        }
