import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OCRSPACE_API_KEY = os.getenv("OCRSPACE_API_KEY")

settings = Settings()
