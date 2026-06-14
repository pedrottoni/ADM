from google import genai
from google.genai import types as genai_types
from openai import OpenAI
from core.config import Config
import os
from typing import List, Dict


class LLMClient:
    def __init__(self, provider="openrouter", model_name=None):
        self.provider = provider
        self.model_name = model_name
        self.openai_client = None       # OpenAI-compatible (OpenRouter / NVIDIA)
        self.genai_client = None        # google.genai.Client (Gemini)
        self.enabled = Config.LLM_ENABLED == "true"
        self._setup_provider()

    def update_settings(self, provider, model_name):
        """Update instance settings dynamically."""
        self.provider = provider
        self.model_name = model_name
        self._setup_provider()

    def set_enabled(self, value: bool):
        """Enable or disable LLM connection. Persists to .env."""
        self.enabled = value
        Config.set_llm_enabled(value)

    # ------------------------------------------------------------------
    # Provider setup
    # ------------------------------------------------------------------
    def _setup_provider(self):
        """Initialize the selected provider's client."""
        if self.provider == "gemini":
            if not Config.GOOGLE_API_KEY:
                print("⚠️ Warning: GOOGLE_API_KEY missing")
                return
            self.genai_client = genai.Client(api_key=Config.GOOGLE_API_KEY)
            self.model_name = self.model_name or "gemini-2.5-flash"

        elif self.provider == "openrouter":
            if not Config.OPENROUTER_API_KEY:
                print("⚠️ Warning: OPENROUTER_API_KEY missing")
                return
            self.openai_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=Config.OPENROUTER_API_KEY,
            )
            self.model_name = self.model_name or "google/gemini-2.5-flash"

        elif self.provider == "nvidia":
            if not Config.NVIDIA_API_KEY:
                print("⚠️ Warning: NVIDIA_API_KEY missing")
                return
            self.openai_client = OpenAI(
                base_url=Config.NVIDIA_BASE_URL,
                api_key=Config.NVIDIA_API_KEY,
            )
            self.model_name = self.model_name or "z-ai/glm4.7"

    # ------------------------------------------------------------------
    # Text generation
    # ------------------------------------------------------------------
    def generate_content(self, prompt: str, use_search: bool = False) -> str:
        """Generate text from the selected LLM."""
        if not self.enabled:
            return ":material/smart_toy: IA desativada. Ative a conexão no botão no topo da página."

        try:
            if self.provider == "gemini":
                return self._generate_gemini(prompt, use_search)
            elif self.provider in ("openrouter", "nvidia"):
                return self._generate_openai(prompt)
            return "Provider not implemented."

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error with {self.provider}: {error_msg}")

            # Smart fallback → Gemini (only when primary isn't already Gemini)
            if self.provider != "gemini" and Config.GOOGLE_API_KEY:
                print("⚠️ Attempting fallback to Gemini...")
                try:
                    fallback_client = genai.Client(api_key=Config.GOOGLE_API_KEY)
                    resp = fallback_client.models.generate_content(
                        model="gemini-2.5-flash", contents=prompt
                    )
                    return (
                        f"{resp.text}\n\n"
                        f"[MENSAGEM DO SISTEMA: O provedor '{self.provider}' falhou. "
                        f"Resposta gerada via Backup (Gemini).]"
                    )
                except Exception as fb_err:
                    return f":material/error: Error (Primary & Backup): {error_msg} | Fallback: {str(fb_err)}"

            return f":material/error: Error: {error_msg}"

    def _generate_gemini(self, prompt: str, use_search: bool) -> str:
        """Call Gemini via google.genai SDK."""
        if not self.genai_client:
            raise Exception("Gemini not configured")

        config_kwargs = {}
        if use_search:
            config_kwargs["tools"] = [{"google_search": {}}]

        response = self.genai_client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=genai_types.GenerateContentConfig(**config_kwargs) if config_kwargs else None,
        )
        return response.text

    def _generate_openai(self, prompt: str) -> str:
        """Call an OpenAI-compatible provider."""
        if not self.openai_client:
            raise Exception(f"{self.provider} not configured")

        response = self.openai_client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
        )
        return response.choices[0].message.content

    # ------------------------------------------------------------------
    # Vision (image-in-prompt)
    # ------------------------------------------------------------------
    def generate_with_image(
        self, prompt: str, image_bytes: bytes, mime_type: str = "image/jpeg"
    ) -> str:
        """Generate content based on text prompt and image."""
        if not self.enabled:
            return ":material/smart_toy: IA desativada. Ative a conexão no botão no topo da página."

        try:
            if self.provider == "gemini":
                if not self.genai_client:
                    raise Exception("Gemini not configured")
                part = genai_types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                response = self.genai_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[prompt, part],
                )
                return response.text

            elif self.provider in ("openrouter", "nvidia"):
                if not self.openai_client:
                    raise Exception(f"{self.provider} not configured")

                import base64
                b64 = base64.b64encode(image_bytes).decode("utf-8")

                try:
                    response = self.openai_client.chat.completions.create(
                        model=self.model_name,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:{mime_type};base64,{b64}"
                                        },
                                    },
                                ],
                            }
                        ],
                        max_tokens=800,
                    )
                    return response.choices[0].message.content
                except Exception as api_err:
                    if "vision" not in self.model_name.lower():
                        print(
                            f"⚠️ Warning: Model {self.model_name} might not support vision. "
                            f"Retrying with a known vision model..."
                        )
                    raise api_err

            return f"Vision support not implemented for {self.provider}."

        except Exception as e:
            return f":material/error: Vision Error: {str(e)}"

    # ------------------------------------------------------------------
    # Connection check
    # ------------------------------------------------------------------
    def check_connection(self) -> bool:
        """Simple 'Hello' test."""
        if not self.enabled:
            return False
        try:
            res = self.generate_content("Say 'OK' in 1 word.")
            return "OK" in res or len(res) < 20
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Model listing
    # ------------------------------------------------------------------
    def get_available_models(self) -> List[str]:
        """Return list of models, fetching dynamically from provider if possible."""
        try:
            if self.provider == "gemini":
                if not self.genai_client:
                    return ["gemini-2.5-flash"]
                models = self.genai_client.models.list()
                return sorted(
                    m.name for m in models
                    if "generateContent" in (m.supported_generation_methods or [])
                )

            elif self.provider in ("openrouter", "nvidia"):
                if not self.openai_client:
                    return []
                models = self.openai_client.models.list()
                return sorted(m.id for m in models.data)

        except Exception as e:
            print(f"⚠️ Error fetching models for {self.provider}: {e}")
            # Static fallbacks
            if self.provider == "gemini":
                return ["gemini-2.5-flash", "gemini-1.5-flash"]
            if self.provider == "openrouter":
                return ["openai/gpt-3.5-turbo", "google/gemini-pro"]
            if self.provider == "nvidia":
                return ["google/gemma-2-27b-it"]

        return []


# Singleton — restores last saved provider/model from .env
llm_client = LLMClient(provider=Config.LLM_PROVIDER, model_name=Config.LLM_MODEL)
