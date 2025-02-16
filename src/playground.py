"""Run `pip install openai exa_py duckduckgo-search yfinance pypdf sqlalchemy 'fastapi[standard]' phidata youtube-transcript-api` to install dependencies."""
import sys
sys.path.append("../")
from textwrap import dedent
from datetime import datetime

from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.playground import Playground, serve_playground_app
from phi.storage.agent.sqlite import SqlAgentStorage
from phi.tools.dalle import Dalle
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.exa import ExaTools
from phi.tools.yfinance import YFinanceTools
from phi.tools.youtube_tools import YouTubeTools

agent_storage_file: str = "tmp/agents.db"

web_agent = Agent(
    name="Web Agent",
    role="Search the web for information",
    agent_id="web-agent",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGo()],
    instructions=["Break down the users request into 2-3 different searches.", "Always include sources"],
    storage=SqlAgentStorage(table_name="web_agent", db_file=agent_storage_file),
    add_history_to_messages=True,
    num_history_responses=5,
    add_datetime_to_instructions=True,
    markdown=True,
)


image_agent = Agent(
    name="Image Agent",
    role="Generate images given a prompt",
    agent_id="image-agent",
    model=OpenAIChat(id="gpt-4o"),
    tools=[Dalle(model="dall-e-3", size="1792x1024", quality="hd", style="vivid")],
    storage=SqlAgentStorage(table_name="image_agent", db_file=agent_storage_file),
    add_history_to_messages=True,
    add_datetime_to_instructions=True,
    markdown=True,
)

app = Playground(agents=[web_agent, image_agent]).get_app()

if __name__ == "__main__":
    serve_playground_app("playground:app", reload=True, port=8818)
