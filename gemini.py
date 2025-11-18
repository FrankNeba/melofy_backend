import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()  # Load .env variables

api_key = os.getenv("GENAI_API_KEY")
if not api_key:
    raise ValueError("Please set GENAI_API_KEY in your environment variables")

genai.configure(api_key=api_key)

def list_gemini_models():
    try:
        models = genai.list_models()
        print("Available Gemini Models:\n")
        for model in models:
            # Print all attributes safely
            attrs = vars(model) if hasattr(model, '__dict__') else model.__slots__ if hasattr(model, '__slots__') else {}
            print(f"Model: {getattr(model, 'name', 'N/A')}, Attributes: {attrs}\n")
    except Exception as e:
        print("Error fetching models:", e)

if __name__ == "__main__":
    list_gemini_models()
