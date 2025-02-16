import random
import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Any
import traceback
import os
from dotenv import load_dotenv

from quart import Quart, jsonify, send_file
from quart_cors import cors
from quart_schema import QuartSchema, validate_request

from quart_openrouter.ai_client import AIClient
from quart_openrouter.database import Database
from quart_openrouter.openrouter_client import OpenRouterClient
from .conversation_manager import ConversationManager
from .conversation_service import ConversationService
from quart_openrouter.scenarios.scenario_manager import ScenarioManager
from quart_openrouter.gifs.gif_manager import GifManager
from quart_openrouter.data.agent1_data import RANDOM_TEXTS, RANDOM_GIFS
from quart_openrouter.personality import Agent1Personality
from quart_openrouter.memory import MemoryRetriever

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Define tweet modes
tweet_modes = ["friendly", "hostile", "neutral"]

# Get environment variables
DB_URL = os.getenv("DB_URL", "")
OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")

GIF_URL = os.getenv("GIF_URL", "http://localhost:5000") + "/conversation/gifs/based/"
for i, gif in enumerate(RANDOM_GIFS):
    RANDOM_GIFS[i] = GIF_URL + gif

app = Quart(__name__, static_folder="static")
app = cors(app, allow_origin="*")
quart_schema = QuartSchema(app)


proactive_random = list(RANDOM_TEXTS)
random.choice(list(RANDOM_TEXTS))
proactive_index = 0

personality = Agent1Personality("BASED", ["crypto", "trading"])

# Get memory
database = Database(DB_URL)
memory_retriever = MemoryRetriever(db_url=os.getenv("SYNC_DB_URL", ""))


@dataclass
class Query:
    query: str
    user_id: str
    room_id: str = "privateroom"  # Default to "privateroom"


@app.before_serving
async def setup():
    """Initialize application components and services."""
    # Initialize OpenRouter client
    app.openrouter_client = OpenRouterClient(api_key=OPEN_ROUTER_API_KEY)
    app.ai_client = AIClient(openrouter_client=app.openrouter_client)
    app.messages = defaultdict(list)

    try:
        # Initialize database
        await database.init_db()

        # Initialize memory retriever
        await memory_retriever.init_db()

        # Initialize services with dependency injection
        conversation_service = ConversationService(database=database)

        # Initialize managers
        scenario_manager = ScenarioManager()
        gif_manager = GifManager()

        # Initialize ConversationManager with injected dependencies
        app.conversation_manager = ConversationManager(
            conversation_service=conversation_service,
            scenario_manager=scenario_manager,
            gif_manager=gif_manager,
            ai_client=app.ai_client,
        )
    except Exception as e:
        logger.error(f"Error during application setup: {e}")
        exit(1)


@app.get("/conversation/gifs/based/<gif_name>")
async def serve_gif(gif_name: str):
    """Serve the requested GIF."""
    # One level up from the current directory
    GIF_DIRECTORY = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "static", "gifs", "based"
    )
    gif_path = os.path.join(GIF_DIRECTORY, gif_name)
    if os.path.exists(gif_path):
        return await send_file(gif_path, mimetype="image/gif")
    return jsonify({"status": "error", "message": "GIF not found."}), 404


@app.post("/conversation/new-mention")
@validate_request(Query)
async def new_mention(data: Query):
    """Handle new mentions in the conversation.

    Returns:
        Dict[str, Any]: JSON response indicating the status of the operation.
    """
    try:
        output = await app.conversation_manager.generate_response(
            user_query=data.query, mode="neutral", personality=personality, messages=[]
        )
        return (
            jsonify({"status": "ok", "message": output, "endpoint": "new-mention"}),
            200,
        )

    except Exception:
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500


@app.post("/conversation/new-chat-message")
@validate_request(Query)
async def new_chat_message(data: Query, probability: float = 0.3):
    try:

        # If room_id is privateroom (default), change it to lounge
        room_id = "lounge" if data.room_id == "privateroom" else data.room_id

        if random.random() < probability:
            messages = await app.conversation_manager.get_memory(
                get_direct_messages=False,
                room_id=room_id,
            )

            memories = await memory_retriever.fetch_memories(data.query)

            output = await app.conversation_manager.generate_direct_response(
                user_query=data.query,
                mode="chatbot",
                personality=personality,
                messages=messages,
                memories=memories,
            )

        else:
            # Empty string for no response
            output = ""

        await app.conversation_manager.add_to_memory(
            room_id=room_id,  # Use modified room_id
            user_id=data.user_id,
            user_query=data.query,
            ai_response=output,
            is_direct_message=False,
        )
        return (
            jsonify(
                {
                    "status": "ok",
                    "message": output if output else "",
                    "endpoint": "new-chat-message",
                }
            ),
            200,
        )

    except Exception:
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500


# For direct messages
@app.post("/conversation/new-direct-message")
@validate_request(Query)
async def new_direct_message(data: Query):
    try:
        # For direct messages, always use privateroom
        room_id = "privateroom"

        messages = await app.conversation_manager.get_memory(
            get_direct_messages=True, room_id=room_id, user_id=data.user_id
        )

        memories = await memory_retriever.fetch_memories(data.query)

        output = await app.conversation_manager.generate_direct_response(
            user_query=data.query,
            mode="chatbot",
            personality=personality,
            messages=messages,
            memories=memories,
        )

        await app.conversation_manager.add_to_memory(
            room_id=room_id,
            user_id=data.user_id,
            user_query=data.query,
            ai_response=output,
            is_direct_message=True,
        )
        return (
            jsonify(
                {
                    "status": "ok",
                    "message": output if output else "",
                    "endpoint": "new-direct-message",
                }
            ),
            200,
        )

    except Exception:
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500


@app.get("/conversation/random-message")
async def get_random_message() -> Dict[str, Any]:
    """Get a random message from the conversation history.

    Returns:
        Dict[str, Any]: JSON response containing a random message
    """
    try:
        output = random.choice(list(RANDOM_TEXTS) + list(RANDOM_GIFS))
        return jsonify(
            {
                "status": "ok",
                "endpoint": "random-message",
                "message": output,
                "endpoint": "random-message",
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
