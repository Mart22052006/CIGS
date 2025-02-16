from cigs.assistant import Assistant
from cigs.tools.website import WebsiteTools

assistant = Assistant(tools=[WebsiteTools()], show_tool_calls=True)
assistant.print_response("Search web page: 'https://docs.phidata.com/introduction'", markdown=True)
