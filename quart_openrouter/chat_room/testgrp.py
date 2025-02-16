import requests
import json
import time

# Endpoint and headers
url = "http://localhost:5000/conversation/new-chat-message"
headers = {"Content-Type": "application/json"}

# A list of messages from 5 different people, all using the same room_id ("loungers").
messages = [
    {"query": "Hey, it's Tom checking in!", "user_id": "TOM", "room_id": "loungers"},
    {"query": "Won't you say hi to me?", "user_id": "SARAH", "room_id": "loungers"},
    {"query": "Hey, how is it going based?", "user_id": "MIKE", "room_id": "loungers"},
    {"query": "I am 70 years old", "user_id": "JILL", "room_id": "loungers"},
    {"query": "Who is 70 years old?", "user_id": "BOB", "room_id": "loungers"},
    # Continue the conversation with more back-and-forth as needed...
    {
        "query": "Sure Bob, I'm curious about your ideas.",
        "user_id": "TOM",
        "room_id": "loungers",
    },
    {
        "query": "Yes, I'd love to hear more too!",
        "user_id": "SARAH",
        "room_id": "loungers",
    },
    {
        "query": "Can you ask the other girl to shut up?",
        "user_id": "MIKE",
        "room_id": "loungers",
    },
]
# Continue the conversation with more back-and-forth as needed...
#     {"query": "Sure Bob, I'm curious about your ideas.", "user_id": "TOM", "room_id": "loungers"},
#     {"query": "Yes, I'd love to hear more too!", "user_id": "SARAH", "room_id": "loungers"},
#     {"query": "Can you ask the other girl to shut up?", "user_id": "MIKE", "room_id": "loungers"},
# ]

# List to store responses
responses = []

# Iterate through each message
for msg in messages:
    try:
        # Send POST request
        response = requests.post(url, headers=headers, json=msg)
        response.raise_for_status()  # Raise an error if a bad status code

        # Append the response to the list
        responses.append(
            {
                "question": msg["query"],
                "user_id": msg["user_id"],
                "room_id": msg["room_id"],
                "response": response.json(),
            }
        )

        print(f'User: {msg["user_id"]}, Room: {msg["room_id"]}, Query: {msg["query"]}')
        print(f"Bot Response: {response.json()}\n")

        # Delay to avoid overloading the server
        time.sleep(1)

    except requests.exceptions.RequestException as e:
        print(f"Error with message '{msg['query']}': {e}")
        responses.append(
            {
                "question": msg["query"],
                "user_id": msg["user_id"],
                "room_id": msg["room_id"],
                "error": str(e),
            }
        )

# Save the responses to a JSON file
output_file = "responses_groupchat.json"
with open(output_file, "w") as f:
    json.dump(responses, f, indent=4)

print(f"Responses saved to {output_file}")
