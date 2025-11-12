# API Documentation

Complete API reference for the Stock Market Prediction System.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required. In production, implement API keys or OAuth2.

## Endpoints

### Health & Status

#### GET /health

Health check endpoint.

**Response**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "data_loaded": true,
  "timestamp": "2024-01-15T10:30:00"
}
```

#### GET /

Root endpoint with API information.

**Response**
```json
{
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
```

#### GET /api/status

Get overall system status.

**Response**
```json
{
  "predictor_initialized": true,
  "model_loaded": true,
  "data_loaded": true,
  "symbol": "NFLX",
  "latest_price": 530.31,
  "training_status": {
    "is_training": false,
    "progress": 100,
    "message": "Training completed",
    "error": null
  },
  "config": {
    "time_step": 100,
    "epochs": 100,
    "batch_size": 64
  }
}
```

### Data Management

#### GET /api/data

Get summary of loaded stock data.

**Response**
```json
{
  "symbol": "NFLX",
  "total_records": 1257,
  "date_range": {
    "start": "2016-07-20T00:00:00+00:00",
    "end": "2021-07-16T00:00:00+00:00"
  },
  "latest_price": 530.31,
  "price_stats": {
    "min": 45.23,
    "max": 575.37,
    "mean": 312.45,
    "std": 145.67
  }
}
```

**Error Responses**
- `404`: No data available

#### POST /api/data/fetch

Fetch fresh data from Tiingo API.

**Request Body**
```json
{
  "symbol": "NFLX"
}
```

**Response**
```json
{
  "message": "Data fetched successfully for NFLX",
  "records": 1257,
  "summary": {
    "symbol": "NFLX",
    "total_records": 1257,
    "latest_price": 530.31
  }
}
```

**Error Responses**
- `500`: Error fetching data (API key invalid, network error, etc.)

### Model Training

#### POST /api/train

Start model training in the background.

**Request Body**
```json
{
  "epochs": 100,
  "batch_size": 64
}
```

Both parameters are optional and will use defaults from configuration if not provided.

**Response**
```json
{
  "message": "Training started in background",
  "epochs": 100,
  "batch_size": 64
}
```

**Error Responses**
- `400`: Training already in progress
- `500`: Predictor not initialized or data not available

#### GET /api/train/status

Get current training status.

**Response** (While Training)
```json
{
  "is_training": true,
  "progress": 50,
  "message": "Training epoch 50/100",
  "error": null
}
```

**Response** (Completed)
```json
{
  "is_training": false,
  "progress": 100,
  "message": "Training completed successfully",
  "error": null,
  "result": {
    "train_rmse": 279.89,
    "test_rmse": 469.18,
    "history": {
      "loss": [...],
      "val_loss": [...]
    }
  }
}
```

**Response** (Error)
```json
{
  "is_training": false,
  "progress": 0,
  "message": "Training failed: error description",
  "error": "error description"
}
```

### Predictions

#### POST /api/predict

Predict future stock prices.

**Request Body**
```json
{
  "days": 30
}
```

**Response**
```json
{
  "predictions": [
    532.45,
    534.12,
    535.89,
    ...
  ],
  "dates": [
    "2021-07-17",
    "2021-07-18",
    "2021-07-19",
    ...
  ],
  "days": 30
}
```

**Error Responses**
- `400`: Model not trained
- `500`: Prediction error

#### GET /api/historical

Get historical predictions vs actual values.

**Response**
```json
{
  "actual": [87.91, 85.99, 85.89, ...],
  "train_predictions": [null, null, ..., 88.45, 86.12, ...],
  "test_predictions": [null, ..., 535.67, 534.89, ...],
  "dates": ["2016-07-20", "2016-07-21", ...]
}
```

The arrays contain NaN (null in JSON) for positions where predictions aren't available.

**Error Responses**
- `400`: Model not trained
- `500`: Error getting historical predictions

### Model Management

#### DELETE /api/model

Delete the saved model files.

**Response**
```json
{
  "message": "Model deleted successfully"
}
```

**Error Responses**
- `500`: Error deleting model

## Error Handling

All errors follow this format:

```json
{
  "detail": "Error message description"
}
```

HTTP Status Codes:
- `200`: Success
- `400`: Bad Request (invalid parameters, model not trained, etc.)
- `404`: Not Found (data not available)
- `500`: Internal Server Error

## Rate Limiting

Currently, no rate limiting is implemented. In production, consider implementing:
- Per-IP rate limiting
- Per-endpoint rate limiting
- Authenticated rate limits

## WebSocket Support

Not currently implemented. Future versions may include:
- Real-time training progress
- Live prediction updates
- Real-time stock data streaming

## Examples

### Using cURL

**Fetch Data**
```bash
curl -X POST http://localhost:8000/api/data/fetch \
  -H "Content-Type: application/json" \
  -d '{"symbol": "NFLX"}'
```

**Train Model**
```bash
curl -X POST http://localhost:8000/api/train \
  -H "Content-Type: application/json" \
  -d '{"epochs": 50, "batch_size": 32}'
```

**Get Predictions**
```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"days": 30}'
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Fetch data
response = requests.post(f"{BASE_URL}/api/data/fetch", json={"symbol": "NFLX"})
print(response.json())

# Train model
response = requests.post(f"{BASE_URL}/api/train", json={"epochs": 100})
print(response.json())

# Wait for training...
import time
while True:
    status = requests.get(f"{BASE_URL}/api/train/status").json()
    if not status['is_training']:
        break
    print(f"Training: {status['message']}")
    time.sleep(5)

# Make predictions
response = requests.post(f"{BASE_URL}/api/predict", json={"days": 30})
predictions = response.json()
print(f"Predictions: {predictions['predictions'][:5]}...")
```

### Using JavaScript/Axios

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

async function main() {
  // Fetch data
  const fetchResponse = await axios.post(`${BASE_URL}/api/data/fetch`, {
    symbol: 'NFLX'
  });
  console.log('Data fetched:', fetchResponse.data);

  // Train model
  const trainResponse = await axios.post(`${BASE_URL}/api/train`, {
    epochs: 100,
    batch_size: 64
  });
  console.log('Training started:', trainResponse.data);

  // Poll training status
  let isTraining = true;
  while (isTraining) {
    const statusResponse = await axios.get(`${BASE_URL}/api/train/status`);
    isTraining = statusResponse.data.is_training;
    console.log('Status:', statusResponse.data.message);
    await new Promise(resolve => setTimeout(resolve, 5000));
  }

  // Make predictions
  const predictResponse = await axios.post(`${BASE_URL}/api/predict`, {
    days: 30
  });
  console.log('Predictions:', predictResponse.data.predictions.slice(0, 5));
}

main();
```

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- View all endpoints
- See request/response schemas
- Try out endpoints directly
- Download OpenAPI specification

## Versioning

Current version: `1.0.0`

API versioning will be implemented in future releases using URL prefixing:
- `/v1/api/...`
- `/v2/api/...`

## Future Enhancements

Planned API features:
- Authentication & authorization
- Multiple stock symbol support
- Batch predictions
- Model versioning
- Model comparison endpoints
- Export predictions (CSV, Excel)
- Webhook notifications
- GraphQL support
- WebSocket real-time updates
