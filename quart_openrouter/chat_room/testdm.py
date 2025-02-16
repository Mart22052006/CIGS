import requests
import json
import time

# Endpoint and headers
url = 'http://localhost:5000/conversation/new-direct-message'
headers = {'Content-Type': 'application/json'}

# List of questions to be sent
questions = [
    "Sup bitch",
    "What the hell even does 'BASED' mean?",
    "BASE chain is shit, Its not gonna make it",
    "Nah don't come at me, I'd fuck you up nigga",
    "I'm not scared of you, I'd fuck you up nigga",
    "Just a stupid fucking bot",
    # "I heard he went bald, is that true? why?",
    # "Ok but what does TYBG stand for?",
    # "Cool, now tell me what is Jesse Pollak's favorite word",
    # "How much does Jesse want base to hit in assets?",
    # "Tell me some of his commonly used terms",
]

# User ID
user_id = "berty"

# List to store responses
responses = []

# Iterate through the list of questions
for question in questions:
    data = {"query": question, "user_id": user_id}

    try:
        # Send POST request
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an error for bad status codes

        # Append the response to the list
        responses.append({"question": question, "response": response.json()})

        print(f"Question: {question}")
        print(f"Response: {response.json()}\n")

        # Delay to avoid overloading the server
        time.sleep(1)

    except requests.exceptions.RequestException as e:
        print(f"Error with question '{question}': {e}")
        responses.append({"question": question, "error": str(e)})

# Save the responses to a JSON file
output_file = "responses.json"
with open(output_file, "w") as f:
    json.dump(responses, f, indent=4)

print(f"Responses saved to {output_file}")
