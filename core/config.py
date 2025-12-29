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
