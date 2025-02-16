"""Run `pip install yfinance` to install dependencies."""

from cigs.agent import Agent
from cigs.model.openai import OpenAIChat
from cigs.tools.yfinance import YFinanceTools

finance_agent = Agent(
    name="Finance Agent",
    model=OpenAIChat(id="gpt-4o"),
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True, company_news=True)],
    instructions=["Use tables to display data"],
    show_tool_calls=True,
    markdown=True,
)

finance_agent.print_response("Share analyst recommendations for NVDA", stream=True)
