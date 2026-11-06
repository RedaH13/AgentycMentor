import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

def list_all_models():
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    print("All Available Gemini Models:")
    print("-" * 70)
    
    try:
        # Loop through and print every model without checking for specific methods
        for model in client.models.list():
            print(f"Model Name: {model.name}")
            print(f"Display Name: {model.display_name}")
            print("-" * 70)
    except Exception as e:
        print(f"API Error: {e}")

if __name__ == "__main__":
    list_all_models()