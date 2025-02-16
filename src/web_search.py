"""Run `pip install openai duckduckgo-search phidata` to install dependencies."""
import sys
sys.path.append("../")
from cigs.agent import Agent
from cigs.model.openai import OpenAIChat
from cigs.tools.duckduckgo import DuckDuckGo
from quart_openrouter.personality import Agent1Personality
from quart_openrouter.ai_client import AIClient
from quart_openrouter.ai_client import OpenRouterClient
import os
import asyncio
OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY", "")

agent_name = 'BiBs'
twitter_handle = 'Bib'
main_purpose =' The Main purpose of this bot is to talk about FOGO and new stuff on mushrooms for good '
work_description = 'The description of this bot is to act as the roboadvisor promoting FOGO and the mushrooms for sale to Guatemala Malaysia and China and America. The fun of the fun, the king of kids'
writing_style='The style is Naughty and Funny and in Singlish'
sample_content='''
        Wah, you all heard of FOGO or not?
        This bot here is all about promoting FOGO and some really shiok new mushrooms that will make you go wah, trust me. If you into mushrooms, or you just want to try something new, this is the place to be lah. We got the freshest, most exciting mushrooms, all packed with health benefits, and the best part is, they’re not just for show. They can do real good for your body, so you’ll be feeling shiok while you enjoy.
        What is FOGO?
        FOGO is one of those things that sounds simple but got a lot of meaning behind it. It’s all about food, sustainability, and giving people access to good things without harming the planet. So, FOGO got this mission to bring you some of the best, organic, high-quality mushrooms, and it’s all about making sure the environment stays happy too. It’s a win-win, lah. You eat good, you support the planet, and you feel good inside. Best part, this bot is the one that will tell you everything you need to know about FOGO and the new mushrooms we selling.
'''
common_phrases='''Bojio, Go wah, lah, shiok'''
personality = Agent1Personality(agent_name, ["crypto", "trading"])
AIClient = AIClient(OpenRouterClient(OPEN_ROUTER_API_KEY))
scenarios = [
        {"question": "What is Fogo?", "mode": "neutral"},
        {"question": "What is magic mushrooms? ", "mode": "neutral"},
        {"question": "What is your name? ", "mode": "neutral"},
        {"question": "Fuck jesse pollak", "mode": "neutral"},
        # {"question": "Fuck base", "mode": "neutral"},
        # {"question": "fuck this base project", "mode": "neutral"},
        # {"question": "Base is a scam chain", "mode": "neutral"},
        # {"question": "solana is better than base", "mode": "neutral"},
        # {"question": "Fuck jesse pollak", "mode": "neutral"},
        # {"question": "Fuck base", "mode": "neutral"},
        # {"question": "fuck this base project", "mode": "neutral"},
        # {"question": "Base is a scam chain", "mode": "neutral"},
        # {"question": "solana is better than base", "mode": "neutral"},
        # {"question": "Fuck jesse pollak", "mode": "neutral"},
        # {"question": "Fuck base", "mode": "neutral"},
        # {"question": "Who is Jesse?", "mode": "neutral"},
        # {"question": "Who is Jesse?", "mode": "neutral"},
        # {"question": "Who is Jesse?", "mode": "neutral"},
        # {"question": "Who is Jesse?", "mode": "neutral"},
        # {"question": "Who is Jesse?", "mode": "neutral"},
        # {"question": "Is Jesse Pollak such a big fraud?", "mode": "neutral"},
        # {"question": "Nah Jesse is a lil scammer", "mode": "neutral"},
        # {"question": "Bruh, Solana is better than this BASE bs", "mode": "neutral"},
        # {"question": "Ayo based, are you really a bot?", "mode": "neutral"},
    ]

    # Iterate over scenarios and get responses

async def main():
    for scenario in scenarios:
        question = scenario["question"]
        mode = scenario["mode"]
        # new_messages =await AIClient.generate_prompt(
        #             question,
        #             mode,
        #             personality,
        #         )
        # print(new_messages[0].keys())
        web_agent = Agent(
            name=agent_name,
            model=OpenAIChat(id="gpt-4o"),
            # tools=[DuckDuckGo()],
            description=main_purpose,
            introduction=work_description,
            system_prompt=f'Your name is {agent_name},here is the rules and informations you can use:'+'Writing Style:'+writing_style+'Sample Content:'+sample_content+'Common Phrases: '+common_phrases,
            # show_tool_calls=True,new_messages[0].get('content')+
            add_history_to_messages=True,
            num_history_responses=5,
            use_memory=True,
            markdown=True,
        )
        web_agent.print_response(question, stream=True)

asyncio.run(main())


