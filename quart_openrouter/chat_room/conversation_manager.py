from datetime import datetime
import logging
import random
import traceback
from typing import Dict, List, Optional, Tuple, Any
from dotenv import load_dotenv

from quart_openrouter.personality import TwitterPersonality
from quart_openrouter.data.prompts.random_messages import RANDOM_MESSAGES
from quart_openrouter.guards import Guards, FRIENDLY_AGENT_LIST
from quart_openrouter.interfaces import (
    IConversationService,
    IScenarioManager,
    IGifManager,
    IAIClient,
)

logger: logging.Logger = logging.getLogger(__name__)
load_dotenv()


class ConversationManager:
    def __init__(
        self,
        conversation_service: IConversationService,
        scenario_manager: IScenarioManager,
        gif_manager: IGifManager,
        ai_client: IAIClient,
        window_size: int = 2,
    ):
        """
        Handles storing user messages, retrieving conversation history, and generating responses.
        """
        self.window_size = window_size
        self.ai_client: IAIClient = ai_client
        self.conversation_service = conversation_service
        self.scenario_manager = scenario_manager
        self.gif_manager = gif_manager
        self.guards = Guards(FRIENDLY_AGENT_LIST)

    def sanitize_response(self, character_name: str, response: str) -> str:
        """
        Removes the character's name prompt and extra quotes from a response.
        """
        return response.replace(character_name + ":", "").replace('"', "")

    async def add_to_memory(
        self,
        room_id: str,
        user_id: str,
        user_query: str,
        ai_response: Optional[str] = "",
        is_direct_message: bool = False,
    ) -> None:
        """
        Stores both the user query and optional AI response in the conversation service.
        """
        if not ai_response:
            ai_response = ""

        # Check if ai_response ends up with .gif, if so, store it as gif_url
        if ai_response and ai_response.endswith(".gif"):
            ai_response = self.gif_manager.get_gif_meaning(ai_response)

        try:
            await self.conversation_service.store_message(
                room_id=room_id,
                user_id=user_id,
                user_query=user_query,
                ai_response=ai_response,
                is_direct_message=is_direct_message,
            )
        except Exception:
            traceback.print_exc()

    async def get_memory(
        self,
        k: int = 2,
        get_direct_messages: bool = False,
        room_id: str = "",
        user_id: str = "",
    ) -> List[Dict[str, Any]]:
        """
        Retrieves the last k messages pairs from the conversation service (async).
        """
        try:
            return await self.conversation_service.get_previous_conversation(
                window_size=k,
                get_direct_messages=get_direct_messages,
                user_id=user_id,
                room_id=room_id,
            )
        except Exception:
            traceback.print_exc()
            return []

    async def generate_response(
        self,
        personality: TwitterPersonality,
        user_query: str,
        mode: str,
        messages: List[Dict[str, Any]],
    ) -> str:
        """
        Chooses between returning a random GIF URL, random text, or generating an AI response.
        """
        gif_url = ""
        ai_response = ""

        outcome: str = random_gif_message_or_ai_response()
        if outcome == "USE_GIF":
            gif_url = self.gif_manager.get_random_gif()
        elif outcome == "USE_RANDOM":
            ai_response = random.choice(RANDOM_MESSAGES)
        else:
            try:
                mentions: List[Tuple[str, str]] = self.guards.get_guards_mention(
                    user_query
                )
                # Use AIClient for response generation
                ai_response = await self.ai_client.generate_response(
                    query=user_query,
                    guards_mention=mentions,
                    mode=mode,
                    personality=personality,
                    messages=messages,
                )
            except Exception:
                traceback.print_exc()
                ai_response = random.choice(RANDOM_MESSAGES)

        # Return whichever is populated: AI text, or GIF URL, or fall back to random text
        if ai_response:
            return ai_response
        if gif_url:
            return gif_url
        return random.choice(RANDOM_MESSAGES)

    async def generate_direct_response(
        self,
        personality: TwitterPersonality,
        user_query: str,
        mode: str,
        messages: List[Dict[str, Any]],
        memories: List[dict],
    ) -> str:
        """
        Chooses an AI response (which may include a GIF).
        """

        try:
            mentions: List[Tuple[str, str]] = self.guards.get_guards_mention(user_query)
            ai_response = await self.ai_client.generate_direct_response(
                query=user_query,
                guards_mention=mentions,
                mode=mode,
                personality=personality,
                messages=messages,
                context=memories,
            )
        except Exception:
            traceback.print_exc()
            ai_response = random.choice(RANDOM_MESSAGES)

        return ai_response


def random_gif_message_or_ai_response() -> str:
    """
    Weighted choice: 'USE_GIF' (2x), 'USE_RANDOM' (1x), 'USE_AI' (4x).
    This influences the probability of each outcome.
    """
    return random.choice(
        ["USE_GIF", "USE_GIF", "USE_RANDOM", "USE_AI", "USE_AI", "USE_AI", "USE_AI"]
    )
