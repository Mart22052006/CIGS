from typing import Dict, List, Optional, Any
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion


class OpenRouterClient:
    """Client for interacting with the OpenRouter API using OpenAI's client."""

    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url.rstrip("/"),
            default_headers={
                "HTTP-Referer": "https://github.com/your-username/quart-openrouter",  # Update this
                "X-Title": "Quart-OpenRouter",  # You can customize this
            },
        )

    async def generate_response_stream(
        self,
        messages: List[Dict[str, str]],
        model: str = "gryphe/mythomax-l2-13b",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> ChatCompletion:
        """
        Create a chat completion using the OpenRouter API.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model identifier to use
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters to pass to the API

        Returns:
            ChatCompletion object from OpenAI client
        """
        async for chunk in await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        ):
            yield chunk.choices[0].delta.content

    async def generate_full_response(
        self,
        messages: List[Dict[str, str]],
        model: str = "gryphe/mythomax-l2-13b",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate a full response from the OpenRouter API.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model identifier to use
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters to pass to the API

        Returns:
            The full response text
        """
        response = await self.client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        )

        if not response:
            return ""

        return response.choices[0].message.content

    async def get_models(self) -> Dict:
        """Get available models from OpenRouter."""
        return await self.client.models.list()
