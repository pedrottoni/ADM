import google.generativeai as genai
from core.config import Config
import os

class LLMClient:
    def __init__(self, provider="gemini"):
        self.provider = provider
        self.setup_provider()

    def setup_provider(self):
        """Initialize the selected provider."""
        if self.provider == "gemini":
            if not Config.GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY is missing.")
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
        
    def generate_content(self, prompt: str) -> str:
        """Generate text from the selected LLM."""
        try:
            if self.provider == "gemini":
                response = self.model.generate_content(prompt)
                return response.text
            # Future: Add OpenRouter/Nvidia implementation here
            else:
                return "Provider not implemented yet."
        except Exception as e:
            return f"Error connecting to AI: {str(e)}"

# Singleton instance for easy import
llm_client = LLMClient(provider="gemini")
