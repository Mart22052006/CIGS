from typing import List, Optional, Dict, Any
from uuid import UUID
import logging

from quart_openrouter.database import Database
from quart_openrouter.interfaces import IConversationService

logger: logging.Logger = logging.getLogger(__name__)


class ConversationService(IConversationService):
    """Service layer for handling conversation-related database operations."""

    def __init__(self, database: Database):
        """Initialize the conversation service with database instances.

        Args:
            database (Database): Database instance for persistent storage
        """
        self.database = database

    async def store_message(
        self,
        user_id: str,
        user_query: str,
        ai_response: str = "",
        is_direct_message: bool = False,
        room_id: str = "privateroom",
    ) -> None:
        """Store a message in database.

        Args:
            user_query (str): The user's message
            ai_response (str, optional): The AI's response. Defaults to "".
            gif_url (str, optional): URL of associated GIF. Defaults to "".
            is_direct_message (bool, optional): Whether the message is a direct message. Defaults to False.
            room_id (str, optional): Room ID for group chat. Defaults to "privateroom".
        """
        try:
            await self.database.add_message(
                user_id=user_id,
                user_query=user_query,
                ai_response=ai_response,
                is_direct_message=is_direct_message,
                room_id=room_id,
            )
        except Exception as e:
            logger.error("Error storing message: %s", e)
            raise

    async def get_previous_conversation(
        self,
        window_size: int = 2,
        get_direct_messages: bool = False,
        user_id: str = "",
        room_id: str = "privateroom",
    ) -> List[Dict[str, Any]]:
        """Get previous conversation messages within window size.

        Args:
            window_size (int): Number of messages to retrieve
            is_direct_message (bool): Whether the message is a direct message
            user_id (str): User ID to filter messages
            room_id (str): Room ID to filter messages

        Returns:
            List[Dict[str, Any]]: List of message dictionaries
        """

        try:

            if get_direct_messages and user_id:
                messages = await self.database.get_last_direct_messages(
                    user_id=user_id, count=window_size, room_id=room_id
                )
                return messages

            messages = await self.database.get_last_chat_room_messages(
                count=window_size, room_id=room_id
            )
            return messages
        except Exception as e:
            logger.error("Error retrieving previous conversation: %s", e)
            return []
