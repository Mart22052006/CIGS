from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from .models import Base, Message
import os
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, database_uri: str):
        self.engine = create_async_engine(database_uri, echo=True)
        self.SessionLocal = sessionmaker(
            bind=self.engine, expire_on_commit=False, class_=AsyncSession
        )

    async def init_db(self):
        async with self.engine.begin() as conn:
            if os.environ.get("ENV", "dev") == "dev":
                await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    # Add a new message to the database
    async def add_message(
        self,
        user_id: str,
        user_query: str,
        ai_response: str,
        is_direct_message: bool = False,
        room_id: str = "privateroom",
    ) -> Message:
        logger.info(f"Adding message - User: {user_id}, Room: {room_id}, Direct Message: {is_direct_message}")
        async with self.SessionLocal() as session:
            new_message = Message(
                user_id=user_id,
                user_query=user_query,
                ai_response=ai_response,
                is_direct_message=is_direct_message,
                datetime=datetime.now(timezone.utc),
                room_id=room_id,
            )
            session.add(new_message)
            await session.commit()
            await session.refresh(new_message)
            return new_message

    # Add a new message which is a direct message to the database
    async def add_direct_message(
        self,
        user_id: str,
        user_query: str,
        ai_response: str,
        room_id: str = "privateroom",
    ) -> Message:
        return await self.add_message(
            user_id=user_id,
            user_query=user_query,
            ai_response=ai_response,
            is_direct_message=True,
            room_id=room_id,
        )

    # Add a new message to the database which is in chat room
    async def add_chat_message(
        self,
        user_id: str,
        user_query: str,
        ai_response: str,
        room_id: str = "lounge",
    ) -> Message:
        return await self.add_message(
            user_id=user_id,
            user_query=user_query,
            ai_response=ai_response,
            is_direct_message=False,
            room_id=room_id,
        )

    # Get the last direct messages per user as messages
    async def get_last_direct_messages(
        self, 
        user_id: str, 
        count: int = 5,
        room_id: str = "privateroom",
    ) -> list:
        """Get the last direct messages for a specific user"""
        logger.info(f"Fetching direct messages - User: {user_id}, Room: {room_id}, Count: {count}")
        async with self.SessionLocal() as session:
            result = await session.execute(
                select(Message)
                .where(Message.user_id == user_id)
                .where(Message.is_direct_message == True)
                .where(Message.room_id == room_id)
                .order_by(Message.datetime.desc())
                .limit(count)
            )

            temp = result.scalars().all()
            messages = [
                message
                for compound_message in temp
                for message in compound_message.to_messages()
            ]
            return messages

    # Get the last chat room messages (all users) as messages
    async def get_last_chat_room_messages(
        self,
        count: int = 5,
        room_id: str = "lounge",
    ) -> list:
        """Get the last chat room messages"""
        logger.info(f"Fetching chat room messages - Room: {room_id}, Count: {count}")
        async with self.SessionLocal() as session:
            result = await session.execute(
                select(Message)
                .where(Message.is_direct_message == False)
                .where(Message.room_id == room_id)
                .order_by(Message.datetime.desc())
                .limit(count)
            )

            temp = result.scalars().all()
            messages = [
                message
                for compound_message in temp
                for message in compound_message.to_messages()
            ]
            return messages

    # Close the database connection
    async def close(self):
        await self.engine.dispose()
