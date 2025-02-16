from cigs.assistant import Assistant
from cigs.tools.serpapi_tools import SerpApiTools

assistant = Assistant(
    tools=[SerpApiTools()],
    show_tool_calls=True,
    debug_mode=True,
)

assistant.print_response("Whats happening in the USA?", markdown=True)
