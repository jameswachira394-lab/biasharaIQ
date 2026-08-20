import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


def list_models():
    """List available Gemini models. Requires `GEMINI_API_KEY` at runtime."""
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY not configured. Set the environment variable to use this utility.")

    genai.configure(api_key=api_key)
    models = []
    for m in genai.list_models():
        if hasattr(
                m,
                'supported_generation_methods') and 'generateContent' in m.supported_generation_methods:
            models.append(m.name)
    return models


if __name__ == '__main__':
    print("Listing models:")
    try:
        for name in list_models():
            print(name)
    except Exception as e:
        print("Error:", e)
