import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
print(f"API KEY from dotenv: {api_key[:5] if api_key else 'None'}...")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
try:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=10
    )
    print("Success:", response.choices[0].message.content)
except Exception as e:
    print("Error:", str(e))
