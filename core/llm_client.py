import google.generativeai as genai
from openai import OpenAI
from core.config import Config
import os
from typing import List, Dict

class LLMClient:
    def __init__(self, provider="openrouter", model_name=None):
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
            self.model_name = self.model_name or 'gemini-2.5-flash'
            self.genai_model = genai.GenerativeModel(self.model_name)
            
        elif self.provider == "openrouter":
            if not Config.OPENROUTER_API_KEY:
                print("⚠️ Warning: OPENROUTER_API_KEY missing")
                return
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=Config.OPENROUTER_API_KEY,
            )
            self.model_name = self.model_name or 'google/gemini-2.5-flash'
            
        elif self.provider == "nvidia":
            if not Config.NVIDIA_API_KEY:
                print("⚠️ Warning: NVIDIA_API_KEY missing")
                return
            self.client = OpenAI(
                base_url=Config.NVIDIA_BASE_URL,
                api_key=Config.NVIDIA_API_KEY,
            )
            self.model_name = self.model_name or 'z-ai/glm4.7'

    def generate_content(self, prompt: str, use_search: bool = False) -> str:
        """Generate text from the selected LLM."""
        try:
            if self.provider == "gemini":
                if not self.genai_model: raise Exception("Gemini not configured")
                
                # Google Search Grounding Support
                tools = []
                if use_search:
                    # Try the most robust format for Gemini 2.0/2.5 grounding
                    tools = [{"google_search": {}}]
                    
                # Re-init model if tools changed
                # Ensure we use a 2.5 model for grounding
                grounding_model = self.model_name
                if use_search and "2.5" not in grounding_model:
                    grounding_model = "gemini-2.5-flash"
                
                model = genai.GenerativeModel(grounding_model, tools=tools)
                response = model.generate_content(prompt)
                return response.text
                
            elif self.provider in ["openrouter", "nvidia"]:
                if not self.client: raise Exception(f"{self.provider} not configured")
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1500 # Limit to save credits
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
                    fallback_model = genai.GenerativeModel('gemini-2.5-flash')
                    response = fallback_model.generate_content(prompt)
                    return f"{response.text}\n\n[MENSAGEM DO SISTEMA: O provedor '{self.provider}' falhou. Resposta gerada via Backup (Gemini).]"
                except Exception as fallback_error:
                    return f"❌ Error (Primary & Backup): {error_msg} | Fallback: {str(fallback_error)}"
            
            return f"❌ Error: {error_msg}"

    def generate_with_image(self, prompt: str, image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
        """Generate content based on text prompt and image."""
        try:
            if self.provider == "gemini":
                # Use a vision-capable model
                vision_model_name = 'gemini-2.5-flash'
                model = genai.GenerativeModel(vision_model_name)
                
                response = model.generate_content([
                    prompt,
                    {"mime_type": mime_type, "data": image_bytes}
                ])
                return response.text
            elif self.provider in ["openrouter", "nvidia"]:
                if not self.client: raise Exception(f"{self.provider} not configured")
                
                import base64
                base64_image = base64.b64encode(image_bytes).decode('utf-8')
                
                # OpenRouter/OpenAI Vision Format
                try:
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
                                    }
                                ],
                            }
                        ],
                        max_tokens=800 # Reduced to save credits
                    )
                    return response.choices[0].message.content
                except Exception as api_err:
                    # Specific check for model mismatch
                    if "vision" not in self.model_name.lower():
                        print(f"⚠️ Warning: Model {self.model_name} might not support vision. Retrying with a known vision model...")
                        # Optional: auto-fallback to a vision model if needed
                    raise api_err
            else:
                return f"Vision support not implemented for {self.provider}."
        except Exception as e:
            return f"❌ Vision Error: {str(e)}"

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
                if not Config.GOOGLE_API_KEY: return ["gemini-2.0-flash"]
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
            if self.provider == "gemini": return ["gemini-2.5-flash", "gemini-1.5-flash"]
            if self.provider == "openrouter": return ["openai/gpt-3.5-turbo", "google/gemini-pro"]
            if self.provider == "nvidia": return ["google/gemma-2-27b-it"]
            
        return []

# Singleton instance
llm_client = LLMClient(provider="openrouter")
