import sys
sys.path.append("../")
from flask import Flask, request, render_template_string
from cigs.agent import Agent
from cigs.model.openai import OpenAIChat
from cigs.tools.duckduckgo import DuckDuckGo
from quart_openrouter.personality import Agent1Personality
from quart_openrouter.ai_client import AIClient
from quart_openrouter.ai_client import OpenRouterClient
import os
import asyncio
app = Flask(__name__)
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Four-Step Form</title>
    <script>
        function showStep(step) {
            document.getElementById('step1').style.display = 'none';
            document.getElementById('step2').style.display = 'none';
            document.getElementById('step3').style.display = 'none';
            document.getElementById('step4').style.display = 'none';
            document.getElementById(step).style.display = 'block';
        }
    </script>
</head>
<body>
    <h1>Four-Step Form</h1>
    <form action="/submit" method="post">
        <div id="step1">
            <h2>Step 1</h2>
            <label for="twitter_handle">Twitter Handle:</label><br>
            <input type="text" id="twitter_handle" name="twitter_handle"><br><br>

            <label for="agent_name">Agent Name:</label><br>
            <input type="text" id="agent_name" name="agent_name"><br><br>

            <button type="button" onclick="showStep('step2')">Next</button>
        </div>

        <div id="step2" style="display:none;">
            <h2>Step 2</h2>
            <label for="main_purpose">Main Purpose:</label><br>
            <textarea id="main_purpose" name="main_purpose" rows="4" cols="50"></textarea><br><br>

            <label for="work_description">Work Description:</label><br>
            <textarea id="work_description" name="work_description" rows="4" cols="50"></textarea><br><br>

            <button type="button" onclick="showStep('step1')">Previous</button>
            <button type="button" onclick="showStep('step3')">Next</button>
        </div>

        <div id="step3" style="display:none;">
            <h2>Step 3</h2>
            <label for="writing_style">Writing Style:</label><br>
            <textarea id="writing_style" name="writing_style" rows="4" cols="50"></textarea><br><br>

            <label for="sample_content">Sample Content:</label><br>
            <textarea id="sample_content" name="sample_content" rows="4" cols="50"></textarea><br><br>

            <label for="common_phrases">Common Phrases or Slang:</label><br>
            <textarea id="common_phrases" name="common_phrases" rows="4" cols="50"></textarea><br><br>

            <button type="button" onclick="showStep('step2')">Previous</button>
            <button type="button" onclick="showStep('step4')">Next</button>
        </div>

        <div id="step4" style="display:none;">
            <h2>Step 4</h2>
            <label for="model_selection">Model Selection:</label><br>
            <table border="1">
                <tr>
                    <th>Model</th>
                    <th>Parameters</th>
                    <th>Select</th>
                </tr>
                <tr>
                    <td>GPT-3.5</td>
                    <td>Parameters for GPT-3.5</td>
                    <td><input type="radio" name="model_selection" value="gpt-3.5"></td>
                </tr>
                <tr>
                    <td>GPT-4</td>
                    <td>Parameters for GPT-4</td>
                    <td><input type="radio" name="model_selection" value="gpt-4"></td>
                </tr>
                <tr>
                    <td>DALL-E 2</td>
                    <td>Parameters for DALL-E 2</td>
                    <td><input type="radio" name="model_selection" value="dall-e-2"></td>
                </tr>
                <tr>
                    <td>DALL-E 3</td>
                    <td>Parameters for DALL-E 3</td>
                    <td><input type="radio" name="model_selection" value="dall-e-3"></td>
                </tr>
            </table><br><br>

            <button type="button" onclick="showStep('step3')">Previous</button>
            <input type="submit" value="Submit">
        </div>
    </form>
</body>
</html>
"""

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
@app.route('/')
def form():
    return render_template_string(html_template)

@app.route('/submit', methods=['POST'])
def submit():
    twitter_handle = request.form['twitter_handle']
    agent_name = request.form['agent_name']
    main_purpose = request.form['main_purpose']
    work_description = request.form['work_description']
    writing_style = request.form['writing_style']
    sample_content = request.form['sample_content']
    common_phrases = request.form['common_phrases']
    model_selection = request.form['model_selection']
    
    # 处理接收到的数据
    print(f"Twitter Handle: {twitter_handle}")
    print(f"Agent Name: {agent_name}")
    print(f"Main Purpose: {main_purpose}")
    print(f"Work Description: {work_description}")
    print(f"Writing Style: {writing_style}")
    print(f"Sample Content: {sample_content}")
    print(f"Common Phrases: {common_phrases}")
    print(f"Model Selection: {model_selection}")
    asyncio.run(main(agent_name,main_purpose,work_description,writing_style,sample_content,common_phrases,model_selection))
    # web_agent.print_response(main_purpose, stream=True)
    return "Form submitted successfully!"


    # Iterate over scenarios and get responses
async def main(agent_name,main_purpose,work_description,writing_style,sample_content,common_phrases,model_selection):
    
    for scenario in scenarios:
        question = scenario["question"]
        mode = scenario["mode"]
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


if __name__ == "__main__":
    app.run(debug=True, port=1245)