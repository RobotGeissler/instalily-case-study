import requests
import os

api_key = os.getenv("DEEPSEEK_API_KEY")
headers = {"Authorization": f"Bearer {api_key}"}
r = requests.post(
    "https://api.deepseek.com/v1/chat/completions",
    headers=headers,
    json={
        "model": "deepseek-chat", 
        "messages": [{"role": "user", "content": "Hello"}]
    },
)
print(r.status_code)
print(r.text)
