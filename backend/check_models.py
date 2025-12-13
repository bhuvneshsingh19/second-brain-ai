import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv("../.env")
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: API Key not found in .env")
else:
    genai.configure(api_key=api_key)
    print(f"✅ Key found: {api_key[:5]}...")

    print("\n🔍 Listing available models for your key:")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name}")
    except Exception as e:
        print(f"❌ Error listing models: {e}")