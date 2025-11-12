import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for the application"""

    # API Keys
    TIINGO_API_KEY = os.getenv("TIINGO_API_KEY", "")

    # Model parameters
    TIME_STEP = int(os.getenv("TIME_STEP", "100"))
    TRAINING_SIZE_RATIO = float(os.getenv("TRAINING_SIZE_RATIO", "0.65"))
    LSTM_UNITS = int(os.getenv("LSTM_UNITS", "50"))
    EPOCHS = int(os.getenv("EPOCHS", "100"))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "64"))

    # API configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))

    # Paths
    DATA_DIR = "data"
    MODEL_DIR = "models"

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.TIINGO_API_KEY:
            raise ValueError("TIINGO_API_KEY is required. Please set it in .env file")
        return True

config = Config()
