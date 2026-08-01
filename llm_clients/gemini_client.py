import os
from langchain_google_genai import ChatGoogleGenerativeAI

def get_gemini_client(temperature: float = 0.2, model: str = "gemini-1.5-flash"):
    """
    Returns a configured native Gemini client for LangGraph nodes.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
        
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        api_key=api_key
    )