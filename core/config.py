import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
    NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
    
    # App Settings
    APP_NAME = "Shopee Growth Quest"
    VERSION = "0.1.0"
    
    @staticmethod
    def validate_keys():
        """Check if essential keys are present."""
        if not Config.GOOGLE_API_KEY:
            print("⚠️ Warning: GOOGLE_API_KEY not found in .env")
            return False
        return True

    @classmethod
    def set_api_key(cls, provider: str, new_key: str):
        import os
        from dotenv import set_key
        
        env_map = {
            "gemini": "GOOGLE_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
            "nvidia": "NVIDIA_API_KEY"
        }
        
        env_var_name = env_map.get(provider)
        if env_var_name:
            # Update memory
            setattr(cls, env_var_name, new_key)
            # Find and update .env
            env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
            set_key(env_path, env_var_name, new_key)
            return True
        return False
