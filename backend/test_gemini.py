import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print(f"Testing Gemini API with key: {api_key[:5]}...")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

try:
    response = model.generate_content("Hello, are you working?")
    print("Success:", response.text)
except Exception as e:
    print("Error:", str(e))
