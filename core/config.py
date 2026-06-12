import os
from dotenv import load_dotenv, set_key

load_dotenv()

_ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")

class Config:
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
    NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")

    # Persisted LLM settings
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter")
    LLM_MODEL = os.getenv("LLM_MODEL", None)
    LLM_ENABLED = os.getenv("LLM_ENABLED", "false")

    # App Settings
    APP_NAME = "Shopee Growth Quest"
    VERSION = "0.1.0"

    @staticmethod
    def validate_keys():
        if not Config.GOOGLE_API_KEY:
            print("⚠️ Warning: GOOGLE_API_KEY not found in .env")
            return False
        return True

    @classmethod
    def set_api_key(cls, provider: str, new_key: str):
        env_map = {
            "gemini": "GOOGLE_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
            "nvidia": "NVIDIA_API_KEY"
        }
        env_var_name = env_map.get(provider)
        if env_var_name:
            setattr(cls, env_var_name, new_key)
            set_key(_ENV_PATH, env_var_name, new_key)
            return True
        return False

    @classmethod
    def set_llm_settings(cls, provider: str, model: str = None):
        cls.LLM_PROVIDER = provider
        set_key(_ENV_PATH, "LLM_PROVIDER", provider)
        if model is not None:
            cls.LLM_MODEL = model
            set_key(_ENV_PATH, "LLM_MODEL", model)

    @classmethod
    def set_llm_enabled(cls, enabled: bool):
        value = "true" if enabled else "false"
        cls.LLM_ENABLED = value
        set_key(_ENV_PATH, "LLM_ENABLED", value)
