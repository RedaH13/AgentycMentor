import os
import google.generativeai as genai
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not set in environment variables")

# Configurer le client
genai.configure(api_key=api_key)

# Lister les modèles disponibles
models = genai.list_models()

for model in models:
    print(f"- {model.name} | Actions: {model.supported_generation_methods}")
