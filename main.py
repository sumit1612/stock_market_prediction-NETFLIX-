"""
Main entry point for the Stock Market Prediction API
"""
import uvicorn
from backend.config import config

if __name__ == "__main__":
    print(f"Starting Stock Market Prediction API on {config.API_HOST}:{config.API_PORT}")
    uvicorn.run(
        "backend.api:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )
