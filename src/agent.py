import os
import requests

API_KEY = os.getenv("OPENROUTER_API_KEY")

def ask_openrouter(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "google/gemma-2b-it",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    print("DEBUG OPENROUTER RESPONSE:", result)

    if "choices" not in result:
        return f"OpenRouter error: {result}"

    return result["choices"][0]["message"]["content"]

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        break

    answer = ask_openrouter(user_input)
    print("Agent:", answer)

