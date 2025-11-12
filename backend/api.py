from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
from datetime import datetime

from .model import StockPredictor
from .config import config

app = FastAPI(
    title="Stock Market Prediction API",
    description="API for predicting Netflix stock prices using LSTM",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global predictor instance
predictor = None
training_status = {
    'is_training': False,
    'progress': 0,
    'message': '',
    'error': None
}


class TrainRequest(BaseModel):
    epochs: Optional[int] = None
    batch_size: Optional[int] = None


class PredictRequest(BaseModel):
    days: int = 30


class SymbolRequest(BaseModel):
    symbol: str = "NFLX"


@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    global predictor
    try:
        # Validate configuration
        config.validate()
        print("Configuration validated successfully")

        # Initialize predictor
        predictor = StockPredictor(symbol='NFLX')

        # Try to load existing model
        if predictor.load_model():
            print("Existing model loaded successfully")
            # Load the data
            try:
                predictor.fetch_data()
                predictor.preprocess_data()
            except Exception as e:
                print(f"Warning: Could not load data: {e}")
        else:
            print("No existing model found. Training required.")

    except Exception as e:
        print(f"Startup error: {e}")
        print("Application started with limited functionality. Please configure TIINGO_API_KEY.")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Stock Market Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "data": "/api/data",
            "train": "/api/train",
            "predict": "/api/predict",
            "historical": "/api/historical",
            "status": "/api/status"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model_exists = predictor is not None and predictor.model is not None
    data_exists = predictor is not None and predictor.df is not None

    return {
        "status": "healthy",
        "model_loaded": model_exists,
        "data_loaded": data_exists,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/data")
async def get_data_summary():
    """Get summary of the stock data"""
    if predictor is None:
        raise HTTPException(status_code=500, detail="Predictor not initialized")

    if predictor.df is None:
        raise HTTPException(status_code=404, detail="No data available. Please train the model first.")

    summary = predictor.get_data_summary()
    return summary


@app.post("/api/data/fetch")
async def fetch_data(request: SymbolRequest):
    """Fetch fresh data from Tiingo API"""
    global predictor

    try:
        if predictor is None or predictor.symbol != request.symbol:
            predictor = StockPredictor(symbol=request.symbol)

        df = predictor.fetch_data()
        predictor.preprocess_data()

        return {
            "message": f"Data fetched successfully for {request.symbol}",
            "records": len(df),
            "summary": predictor.get_data_summary()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


@app.post("/api/train")
async def train_model(request: TrainRequest, background_tasks: BackgroundTasks):
    """Train the model"""
    global training_status, predictor

    if training_status['is_training']:
        raise HTTPException(status_code=400, detail="Training already in progress")

    if predictor is None:
        raise HTTPException(status_code=500, detail="Predictor not initialized")

    if predictor.df is None:
        try:
            predictor.fetch_data()
            predictor.preprocess_data()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")

    def train_background():
        global training_status
        try:
            training_status['is_training'] = True
            training_status['message'] = 'Training started...'
            training_status['error'] = None

            result = predictor.train(epochs=request.epochs, batch_size=request.batch_size)

            training_status['is_training'] = False
            training_status['progress'] = 100
            training_status['message'] = 'Training completed successfully'
            training_status['result'] = result
        except Exception as e:
            training_status['is_training'] = False
            training_status['error'] = str(e)
            training_status['message'] = f'Training failed: {str(e)}'

    background_tasks.add_task(train_background)

    return {
        "message": "Training started in background",
        "epochs": request.epochs or config.EPOCHS,
        "batch_size": request.batch_size or config.BATCH_SIZE
    }


@app.get("/api/train/status")
async def get_training_status():
    """Get training status"""
    return training_status


@app.post("/api/predict")
async def predict_future(request: PredictRequest):
    """Predict future stock prices"""
    if predictor is None:
        raise HTTPException(status_code=500, detail="Predictor not initialized")

    if predictor.model is None:
        raise HTTPException(status_code=400, detail="Model not trained. Please train the model first.")

    try:
        predictions = predictor.predict_future(days=request.days)

        # Generate dates for predictions
        if predictor.df is not None and 'date' in predictor.df.columns:
            last_date = pd.to_datetime(predictor.df['date'].iloc[-1])
            prediction_dates = [(last_date + pd.Timedelta(days=i+1)).strftime('%Y-%m-%d')
                               for i in range(request.days)]
        else:
            prediction_dates = [f"Day +{i+1}" for i in range(request.days)]

        return {
            "predictions": predictions,
            "dates": prediction_dates,
            "days": request.days
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.get("/api/historical")
async def get_historical_predictions():
    """Get historical predictions vs actual values"""
    if predictor is None:
        raise HTTPException(status_code=500, detail="Predictor not initialized")

    if predictor.model is None:
        raise HTTPException(status_code=400, detail="Model not trained. Please train the model first.")

    try:
        results = predictor.get_historical_predictions()

        # Get dates if available
        dates = []
        if predictor.df is not None and 'date' in predictor.df.columns:
            dates = predictor.df['date'].tolist()

        return {
            "actual": results['actual'],
            "train_predictions": results['train_predictions'],
            "test_predictions": results['test_predictions'],
            "dates": dates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting historical predictions: {str(e)}")


@app.get("/api/status")
async def get_status():
    """Get overall system status"""
    return {
        "predictor_initialized": predictor is not None,
        "model_loaded": predictor is not None and predictor.model is not None,
        "data_loaded": predictor is not None and predictor.df is not None,
        "symbol": predictor.symbol if predictor else None,
        "latest_price": predictor.get_latest_price() if predictor and predictor.df is not None else None,
        "training_status": training_status,
        "config": {
            "time_step": config.TIME_STEP,
            "epochs": config.EPOCHS,
            "batch_size": config.BATCH_SIZE
        }
    }


@app.delete("/api/model")
async def delete_model():
    """Delete the saved model"""
    if predictor is None:
        raise HTTPException(status_code=500, detail="Predictor not initialized")

    try:
        if os.path.exists(predictor.model_path):
            os.remove(predictor.model_path)
        if os.path.exists(predictor.scaler_path):
            os.remove(predictor.scaler_path)

        predictor.model = None
        predictor.scaler = MinMaxScaler(feature_range=(0, 1))

        return {"message": "Model deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting model: {str(e)}")


# Import pandas for date handling
import pandas as pd

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
