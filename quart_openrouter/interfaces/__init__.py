"""Interfaces for dependency injection and system architecture.

This module defines the core interfaces that make up the system's architecture:

1. IConversationService: Manages conversation state and persistence
   - Handles session management
   - Stores conversation history
   - Manages user interactions

2. IScenarioManager: Handles interaction scenarios
   - Determines appropriate responses based on mode/scenario
   - Works with IGifManager for media responses

3. IGifManager: Manages GIF responses
   - Provides scenario-specific GIFs
   - Handles random GIF selection

4. IAIClient: Manages AI interactions (New)
   - Generates AI responses with personality support
   - Provides both full and streaming responses
   - Used by ConversationManager for AI generation
   - Decouples AI interaction from conversation management

Interface Relationships:
- ConversationManager uses IAIClient for AI response generation
- IScenarioManager works with IGifManager for media responses
- IAIClient supports TwitterPersonality for customized interactions
- All interfaces support async operations for better performance
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, AsyncGenerator
from uuid import UUID
from ..personality import TwitterPersonality


class IConversationService(ABC):
    """Interface for conversation service operations."""

    @abstractmethod
    async def store_message(
        self,
        user_id: str,
        user_query: str,
        ai_response: Optional[str],
    ) -> None:
        """Store a message in the database."""
        pass

    @abstractmethod
    async def get_previous_conversation(
        self, window_size: int, get_direct_messages: bool, user_id: str, room_id: str
    ) -> List[Dict]:
        """Get previous conversation."""
        pass


class IScenarioManager(ABC):
    """Interface for scenario management."""

    @abstractmethod
    async def get_response(
        self, mode: str, scenario: str, mentions: Optional[List[Tuple[str, str]]] = None
    ) -> Tuple[str, Optional[str]]:
        """Get a response for a given scenario and mode."""
        pass


class IGifManager(ABC):
    """Interface for GIF management."""

    @abstractmethod
    def get_gif_for_scenario(
        self, scenario: str, probability: Optional[float] = None
    ) -> Optional[str]:
        """Get a GIF URL for a given scenario."""
        pass

    @abstractmethod
    def get_random_gif(self, gifs: Optional[List[str]] = None) -> Optional[str]:
        """Get a random GIF URL."""
        pass

    @abstractmethod
    def get_gif_meaning(self, gif_url: str) -> Optional[str]:
        """Get the meaning of a GIF URL."""
        pass


class IAIClient(ABC):
    """Interface for AI client operations."""

    @abstractmethod
    async def generate_response(
        self,
        query: str,
        mode: str,
        guards_mention: Optional[List[Tuple[str, str]]] = None,
        personality: Optional[TwitterPersonality] = None,
        messages: Optional[List[dict]] = None,
    ) -> str:
        """Generate AI response with optional personality/scenario."""
        pass

    @abstractmethod
    async def generate_direct_response(
        self,
        query: str,
        mode: str,
        guards_mention: Optional[List[Tuple[str, str]]] = None,
        personality: Optional[TwitterPersonality] = None,
        messages: Optional[List[dict]] = None,
        context: Optional[List[dict]] = None,
    ) -> str:
        """Generate direct AI response with optional personality/scenario."""
        pass

    @abstractmethod
    async def generate_stream(
        self,
        query: str,
        mode: str,
        personality: Optional[TwitterPersonality] = None,
        scenario: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream AI response with optional personality/scenario."""
        pass
