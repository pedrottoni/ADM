import google.generativeai as genai
from openai import OpenAI
from core.config import Config
import os
from typing import List, Dict

class LLMClient:
    def __init__(self, provider="gemini", model_name=None):
        self.provider = provider
        self.model_name = model_name
        self.client = None
        self.genai_model = None
        self.setup_provider()

    def update_settings(self, provider, model_name):
        """Update instance settings dynamically."""
        self.provider = provider
        self.model_name = model_name
        self.setup_provider()

    def setup_provider(self):
        """Initialize the selected provider."""
        if self.provider == "gemini":
            if not Config.GOOGLE_API_KEY:
                print("⚠️ Warning: GOOGLE_API_KEY missing")
                return
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            self.model_name = self.model_name or 'gemini-pro'
            self.genai_model = genai.GenerativeModel(self.model_name)
            
        elif self.provider == "openrouter":
            if not Config.OPENROUTER_API_KEY:
                print("⚠️ Warning: OPENROUTER_API_KEY missing")
                return
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=Config.OPENROUTER_API_KEY,
            )
            self.model_name = self.model_name or 'openai/gpt-3.5-turbo'
            
        elif self.provider == "nvidia":
            if not Config.NVIDIA_API_KEY:
                print("⚠️ Warning: NVIDIA_API_KEY missing")
                return
            self.client = OpenAI(
                base_url=Config.NVIDIA_BASE_URL,
                api_key=Config.NVIDIA_API_KEY,
            )
            self.model_name = self.model_name or 'google/gemma-2-27b-it'

    def generate_content(self, prompt: str) -> str:
        """Generate text from the selected LLM."""
        try:
            if self.provider == "gemini":
                if not self.genai_model: raise Exception("Gemini not configured")
                response = self.genai_model.generate_content(prompt)
                return response.text
                
            elif self.provider in ["openrouter", "nvidia"]:
                if not self.client: raise Exception(f"{self.provider} not configured")
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
                
            return "Provider not implemented."
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error with {self.provider}: {error_msg}")
            
            # Smart Fallback Strategy
            if self.provider != "gemini" and Config.GOOGLE_API_KEY:
                print("⚠️ Attempting fallback to Gemini...")
                try:
                    # Create a temporary Gemini model for fallback
                    fallback_model = genai.GenerativeModel('gemini-pro')
                    response = fallback_model.generate_content(prompt)
                    return f"{response.text}\n\n[MENSAGEM DO SISTEMA: O provedor '{self.provider}' falhou. Resposta gerada via Backup (Gemini).]"
                except Exception as fallback_error:
                    return f"❌ Error (Primary & Backup): {error_msg} | Fallback: {str(fallback_error)}"
            
            return f"❌ Error: {error_msg}"

    def check_connection(self) -> bool:
        """Simple 'Hello' test."""
        try:
            res = self.generate_content("Say 'OK' in 1 word.")
            return "OK" in res or len(res) < 20 # Flexible check
        except:
            return False

    def get_available_models(self) -> List[str]:
        """Return list of models, fetching dynamically from provider if possible."""
        try:
            if self.provider == "gemini":
                # Dynamic fetch from Google
                if not Config.GOOGLE_API_KEY: return ["gemini-pro"]
                models = genai.list_models()
                return [m.name.replace("models/", "") for m in models if 'generateContent' in m.supported_generation_methods]
                
            elif self.provider in ["openrouter", "nvidia"]:
                # Dynamic fetch from OpenAI-compatible endpoints
                if not self.client: return []
                models = self.client.models.list()
                return sorted([m.id for m in models.data])
                
        except Exception as e:
            print(f"⚠️ Error fetching models for {self.provider}: {e}")
            # Fallback lists if API fails
            if self.provider == "gemini": return ["gemini-pro", "gemini-1.5-flash"]
            if self.provider == "openrouter": return ["openai/gpt-3.5-turbo", "google/gemini-pro"]
            if self.provider == "nvidia": return ["google/gemma-2-27b-it"]
            
        return []

# Singleton instance
llm_client = LLMClient(provider="gemini")
