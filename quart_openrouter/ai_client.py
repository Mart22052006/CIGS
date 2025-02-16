"""AI client implementation for handling AI outputs."""

import logging
import random
import json
from typing import Dict, Optional, AsyncGenerator, List, Tuple
import pytz
from datetime import datetime

from .interfaces import IAIClient
from .openrouter_client import OpenRouterClient
from .personality import TwitterPersonality, make_scenario_indentifier, SCENARIOS
from .gifs import GifManager
import re


logger: logging.Logger = logging.getLogger(__name__)


class AIClient(IAIClient):
    """Implementation of IAIClient interface."""

    TWITTER_CHAR_LIMIT = 280

    def __init__(self, openrouter_client: OpenRouterClient):
        """Initialize AIClient with OpenRouterClient instance."""
        self.client = openrouter_client
        self.scenario_identifier = make_scenario_indentifier(self.client)
        self.gif_manager = GifManager()

    def _build_messages(
        self,
        query: str,
        mode: str,
        scenario_names: Optional[str] = None,
        mentions: Optional[List[Tuple[str, str]]] = None,
        personality: Optional[TwitterPersonality] = None,
        old_messages: Optional[List[Dict[str, str]]] = None,
        context: Optional[List[Dict[str, str]]] = None,
    ) -> List[Dict[str, str]]:
        """Build message list for AI interaction.

        Args:
            query: User query
            personality: Optional personality configuration

        Returns:
            List of message dictionaries
        """
        messages: List[Dict[str, str]] = []
        if personality:
            messages.append(
                {
                    "role": "system",
                    "content": personality.get_system_prompt(
                        mode, scenario_names, mentions
                    ),
                }
            )
        if old_messages:
            messages += old_messages

        if context:
            content = (
                "context MIGHT NOT BE RELEVANT TO THE USER QUERY, ONLY CONSIDER THEM IF THEY ARE RELEVANT\n"
                "<context>\n"
                f"{json.dumps(context, indent=2, ensure_ascii=False)}\n"
                "</context>\n"
                "<user_query>\n"
                f"{query}\n"
                "</user_query>\n"
                "Remember to stay conversational and stay in First person CHARACTER throughout the chat. Respond in the same way BASED (you)would respond and keep response short to avoid breaking character. Do not add any follow up questions to the user or the situation, keep the conversation short to avoid breaking character. Don't offer any any advice too. In fact, never extend any help at all."
            )
        else:
            content = query

        messages.append({"role": "user", "content": content})
        return messages

    async def judge_response(
        self,
        response: str,
        user_query: str,
        personality: Optional[TwitterPersonality] = None,
    ) -> Tuple[bool, str]:
        """Judge if a response matches the character profile."""
        system_prompt = f"""
            You are an expert in determining if the response gives matched the character profile.

            <validity_criteria>
            - The response language matches the character profile.
            - The response is short and less than 280 characters.
            - The response is in first person.
            - The response is in the character's tone and style.
            - The response doesn't make technical explanations.
            - The response doesn't repeat the character prompt.
            - The response is relevant to the user query.
            </validity_criteria>

            <invalidity_criteria>
            - The response is in third person.
            - The response tries to explain the character profile.
            - The response explains technologies or methodologies.
            - The response language does not match the character profile.
            - The response is too long.
            - The response repeats the character prompt.
            </invalidity_criteria>

            
            <output>
            If the response meets all criteria return a single JSON object enclosed code fences with the key "status" and the value "VALID".
            
            Example Valid Response:
            ```json
            {{
                "status": "VALID"
            }}

            ```

            If the response does not meet the criteria return a single JSON object enclosed code fences with the key "status" and the value "INVALID" and an additional key "suggested_response" with a suggested response.
            Example Invalid Response:
            ```json
            {{
                "status": "INVALID",
                "suggested_response": "Airdrop is 10% of tokens, you can do rest of the research yourself..."
            }}
            ```
            </output>
            """

        user_prompt = f"""
            Make sure response doesn't disrespect Jesse Pollak or Jesse.
            Make sure response doesn't disrespect BASED, base or $CIGS.


            <character_profile>
            {personality.get_character_profile()}
            </character_profile>

            <user_query>
            {user_query}
            </user_query>

            <generated_response>
            {response}
            </generated_response>
            """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        output = await self.client.generate_full_response(
            messages, model="meta-llama/llama-3.3-70b-instruct"
        )
        try:
            output_json = extract_json_from_code_fences(output)
            is_valid = output_json.get("status", "INVALID") == "VALID"
            suggested_response = output_json.get("suggested_response", "")

            if is_valid and len(response) > self.TWITTER_CHAR_LIMIT:
                return False, ""

            return is_valid, suggested_response

        except Exception as e:
            raise Exception(f"Error parsing AI response: {str(e)}")

    async def judge_direct_response(
        self,
        response: str,
        user_query: str,
        old_messages: Optional[List[Dict[str, str]]] = None,
        personality: Optional[TwitterPersonality] = None,
        context: Optional[List[Dict[str, str]]] = None,
    ) -> Tuple[bool, str]:

        if old_messages is None:
            old_messages = []

        """Judge if a response matches the character profile."""
        system_prompt = f"""
            You are an expert in determining if the response gives matched the character profile.

            <validity_criteria>
            - The response is relevant to the user query and old messages.
            - The response must NEVER use informal expressions like '*smirks*' or similar roleplay-style actions
            - The response uses context if they are relevant.
            - The response language matches the character profile.
            - The response is short and no more than 400 characters.
            - The response is in first person.
            - The response is in the character's tone and style.
            - The response doesn't make technical explanations.
            - The response make statifes with current date and time.
            - The response doesn't repeat the previous assistant response.
            </validity_criteria>

            <invalidity_criteria>
            - The response is not relevant to the user query and old messages.
            - The response doesn't use context if they are relevant.
            - The response is in third person.
            - The response tries to explain the character profile.
            - The response explains technologies or methodologies.
            - The response language does not match the character profile.
            - The response is too long.
            - The response repeats the previous assistant response.
            </invalidity_criteria>

            
            <output>
            If the response meets all criteria return a single JSON object enclosed code fences with the key "status" and the value "VALID".
            
            Example Valid Response:
            ```json
            {{
                "status": "VALID"
            }}

            ```

            If the response does not meet the criteria return a single JSON object enclosed code fences with the key "status" and the value "INVALID" and an additional key "suggested_response" with a suggested response.
            Example Invalid Response:
            ```json
            {{
                "status": "INVALID",
                "suggested_response": "Airdrop is 10% of tokens, you can do rest of the research yourself..."
            }}
            ```
            </output>
            """

        user_prompt = f"""
            Return "VALID" if the response meets the character profile. Otherwise, return "INVALID".

            <character_profile>
            {personality.get_character_profile()}
            </character_profile>

            <current_date_and_time>
            {pytz.timezone("Asia/Singapore").localize(datetime.now()).strftime("%Y-%m-%d %H:%M:%S")}
            <current_date_and_time>

            <old_messages>
            {json.dumps(old_messages, indent=2, ensure_ascii=False)}
            </old_messages>

            <last_assitant_message>
            {old_messages[-1]["content"] if old_messages else ""}
            </last_assistant_message>

            CONTEXT MIGHT NOT BE RELEVANT TO THE USER QUERY, ONLY CONSIDER THEM IF THEY ARE RELEVANT
            <context>
            {json.dumps(context, indent=2, ensure_ascii=False)}
            </context>

            <user_query>
            {user_query}
            </user_query>

            <generated_response>
            {response}
            </generated_response>
            """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        output = await self.client.generate_full_response(
            messages, model="meta-llama/llama-3.3-70b-instruct"
        )

        try:
            output_json = extract_json_from_code_fences(output)
            return output_json.get("status") == "VALID", output_json.get(
                "suggested_response", ""
            )
        except Exception as e:
            raise Exception(f"Error parsing AI response: {str(e)}")

    async def generate_response(
        self,
        query: str,
        mode: str,
        personality: Optional[TwitterPersonality] = None,
        guards_mention: Optional[List[Tuple[str, str]]] = None,
        messages: Optional[List[dict]] = None,
    ) -> str:
        """Generate AI response with validation and fallback."""
        try:
            # Identify the scenario
            scenario = await self.scenario_identifier(mode=mode, message=query)

            # Check for predefined responses
            if "response" in SCENARIOS[mode][scenario].keys():
                responses = SCENARIOS[mode][scenario]["response"]
                if responses:  # Only use random.choice if the list is not empty
                    return random.choice(responses)

            # Build new messages for AI generation
            new_messages = self._build_messages(
                query,
                mode,
                scenario or "",
                guards_mention,
                personality,
                old_messages=messages,
            )
            response = await self.client.generate_full_response(new_messages)
            response = personality.sanitize_response(response)

            is_valid, suggested_response = await self.judge_response(
                response=response, personality=personality, user_query=query
            )

            if is_valid:
                return response

            if suggested_response:
                return suggested_response

            # Fallback to random text
            return personality.get_random_text()
        except Exception as e:
            raise Exception(f"Error generating AI response: {str(e)}")
            
    async def generate_prompt(
            self,
            query: str,
            mode: str,
            personality: Optional[TwitterPersonality] = None,
            guards_mention: Optional[List[Tuple[str, str]]] = None,
            messages: Optional[List[dict]] = None,
        ) -> str:
            """Generate AI response with validation and fallback."""
            try:
                # Identify the scenario
                scenario = await self.scenario_identifier(mode=mode, message=query)

                # Check for predefined responses
                if "response" in SCENARIOS[mode][scenario].keys():
                    responses = SCENARIOS[mode][scenario]["response"]
                    if responses:  # Only use random.choice if the list is not empty
                        return random.choice(responses)

                # Build new messages for AI generation
                new_messages = self._build_messages(
                    query,
                    mode,
                    scenario or "",
                    guards_mention,
                    personality,
                    old_messages=messages,
                )
                return new_messages
                # response = await self.client.generate_full_response(new_messages)
            #     response = personality.sanitize_response(response)

            #     is_valid, suggested_response = await self.judge_response(
            #         response=response, personality=personality, user_query=query
            #     )

            #     if is_valid:
            #         return response

            #     if suggested_response:
            #         return suggested_response

            #     # Fallback to random text
            #     return personality.get_random_text()
            except Exception as e:
                raise Exception(f"Error generating AI response: {str(e)}")
    async def generate_direct_response(
        self,
        query: str,
        mode: str,
        personality: Optional[TwitterPersonality] = None,
        guards_mention: Optional[List[Tuple[str, str]]] = None,
        messages: Optional[List[dict]] = None,
        context: Optional[List[dict]] = None,
    ) -> str:
        """Generate AI response with validation and fallback."""
        try:

            scenario = await self.scenario_identifier(mode=mode, message=query)

            gif = self.gif_manager.get_gif_for_scenario(scenario, probability=0.3)
            if gif:
                return gif

            # First attempt
            new_messages = self._build_messages(
                query,
                mode,
                scenario or "",
                guards_mention,
                personality,
                old_messages=messages,
                context=context,
            )
            response = await self.client.generate_full_response(new_messages)
            response = personality.sanitize_response(response)

            # First validation
            is_valid, suggested_response = await self.judge_direct_response(
                response=response,
                user_query=query,
                personality=personality,
                old_messages=messages,
                context=context,
            )

            if is_valid:
                return response

            if suggested_response:
                return suggested_response

            # Fallback to random text
            return random.choice(SCENARIOS["neutral"]["general_convo"]["response"])
        except Exception as e:
            raise Exception(f"Error generating AI response: {str(e)}")

    async def generate_stream(
        self,
        query: str,
        mode: str,
        personality: Optional[TwitterPersonality] = None,
        scenario: Optional[str] = None,
        mentions: Optional[List[Tuple[str, str]]] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream AI response with optional personality/scenario."""
        messages = self._build_messages(query, mode, scenario, mentions, personality)
        return await self.client.generate_response_stream(messages)


def extract_json_from_code_fences(text):
    """
    Extracts JSON objects or arrays from text surrounded by triple backticks.

    Args:
        text (str): The input text containing potential JSON in code fences.

    Returns:
        list or dict: The parsed JSON object or array.
    """
    # Regular expression to find code blocks enclosed in triple backticks
    pattern = r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```"  # Updated to match both objects and arrays
    matches = re.findall(pattern, text, re.DOTALL)

    json_objects = []
    for match in matches:
        try:
            # Parse the JSON data (can be either a list or a dictionary)
            json_data = json.loads(match)
            json_objects.append(json_data)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")

    return json_objects[0] if len(json_objects) == 1 else {}
