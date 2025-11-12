# Netflix Stock Market Prediction System

A full-stack machine learning application for predicting Netflix (NFLX) stock prices using LSTM neural networks. The system features a RESTful API backend built with FastAPI and an interactive React dashboard for visualization and model management.

## Features

- **Stock Price Prediction**: Uses LSTM neural networks to predict future stock prices
- **Interactive Dashboard**: Modern React-based UI for data visualization and model management
- **RESTful API**: FastAPI backend with comprehensive endpoints for training and prediction
- **Real-time Data**: Fetches latest stock data from Tiingo API
- **Historical Analysis**: Visualizes model performance on historical data
- **AWS Deployment**: Complete infrastructure-as-code for AWS deployment
- **Docker Support**: Containerized application for easy deployment

## Architecture

```
├── backend/              # FastAPI backend
│   ├── api.py           # API endpoints
│   ├── model.py         # LSTM model implementation
│   └── config.py        # Configuration management
├── frontend/            # React dashboard
│   ├── src/
│   │   ├── App.js      # Main application component
│   │   └── App.css     # Styling
│   └── public/
├── aws/                 # AWS deployment files
│   ├── cloudformation-template.yaml
│   ├── ecs-task-definition.json
│   └── deploy.sh
├── data/               # Stock data storage
├── models/             # Trained model storage
└── docker-compose.yml  # Docker orchestration
```

## Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **TensorFlow/Keras**: Deep learning framework for LSTM
- **Pandas**: Data manipulation and analysis
- **Scikit-learn**: Data preprocessing and metrics
- **pandas-datareader**: Stock data fetching

### Frontend
- **React**: UI library
- **Chart.js**: Data visualization
- **Axios**: HTTP client
- **Lucide React**: Icon library

### Infrastructure
- **Docker**: Containerization
- **AWS ECS**: Container orchestration
- **AWS CloudFormation**: Infrastructure as code
- **Nginx**: Web server for frontend

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker and Docker Compose (for containerized deployment)
- AWS Account (for cloud deployment)
- Tiingo API Key ([Get one here](https://www.tiingo.com/))

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd stock_market_prediction-NETFLIX-
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env and add your Tiingo API key
```

### 3. Local Development

#### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Run the backend
python main.py
```

The API will be available at `http://localhost:8000`

#### Frontend

```bash
cd frontend
npm install
npm start
```

The dashboard will be available at `http://localhost:3000`

### 4. Using Docker Compose

```bash
# Create .env file with your API key
echo "TIINGO_API_KEY=your_api_key_here" > .env

# Build and run
docker-compose up --build
```

Access the application:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

## API Endpoints

### Health & Status
- `GET /health` - Health check
- `GET /api/status` - System status

### Data Management
- `GET /api/data` - Get data summary
- `POST /api/data/fetch` - Fetch latest stock data

### Model Training
- `POST /api/train` - Train the model
- `GET /api/train/status` - Get training status

### Predictions
- `POST /api/predict` - Predict future prices
- `GET /api/historical` - Get historical predictions

### Model Management
- `DELETE /api/model` - Delete saved model

## Usage Guide

### 1. Fetch Data

Click "Fetch Latest Data" to download the latest Netflix stock data from Tiingo API.

### 2. Train Model

Click "Train Model" to train the LSTM model on the fetched data. Training may take several minutes depending on your hardware.

### 3. View Historical Performance

Click "Load Historical" to see how the model performs on historical data, showing both training and test predictions.

### 4. Make Predictions

Enter the number of days (1-365) and click "Predict" to generate future stock price predictions.

## AWS Deployment

### Option 1: CloudFormation Stack

Deploy the complete infrastructure:

```bash
# Deploy infrastructure
aws cloudformation create-stack \
  --stack-name stock-prediction \
  --template-body file://aws/cloudformation-template.yaml \
  --parameters ParameterKey=TiingoAPIKey,ParameterValue=YOUR_API_KEY \
  --capabilities CAPABILITY_IAM

# Wait for stack creation
aws cloudformation wait stack-create-complete --stack-name stock-prediction
```

### Option 2: Manual ECS Deployment

1. **Create ECR Repositories**

```bash
aws ecr create-repository --repository-name stock-prediction
aws ecr create-repository --repository-name stock-prediction-frontend
```

2. **Build and Push Docker Images**

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
docker build -t stock-prediction .
docker tag stock-prediction:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/stock-prediction:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/stock-prediction:latest

# Build and push frontend
docker build -f frontend/Dockerfile.frontend -t stock-prediction-frontend frontend/
docker tag stock-prediction-frontend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/stock-prediction-frontend:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/stock-prediction-frontend:latest
```

3. **Deploy using the script**

```bash
chmod +x aws/deploy.sh
./aws/deploy.sh
```

### Option 3: AWS Elastic Beanstalk

```bash
# Initialize EB
eb init -p docker stock-prediction --region us-east-1

# Create environment
eb create production-env

# Deploy
eb deploy
```

## Configuration

Configuration is managed through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `TIINGO_API_KEY` | Tiingo API key (required) | - |
| `TIME_STEP` | LSTM lookback window | 100 |
| `TRAINING_SIZE_RATIO` | Train/test split ratio | 0.65 |
| `LSTM_UNITS` | Number of LSTM units | 50 |
| `EPOCHS` | Training epochs | 100 |
| `BATCH_SIZE` | Training batch size | 64 |
| `API_HOST` | API host address | 0.0.0.0 |
| `API_PORT` | API port | 8000 |

## Model Architecture

The LSTM model consists of:
- 3 LSTM layers with 50 units each
- First two layers return sequences
- Final dense layer for prediction
- Mean Squared Error loss function
- Adam optimizer

## Project Structure Details

```
stock_market_prediction-NETFLIX-/
├── backend/
│   ├── __init__.py
│   ├── api.py              # FastAPI application
│   ├── model.py            # LSTM model class
│   └── config.py           # Configuration
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   ├── App.css         # Styles
│   │   ├── index.js        # Entry point
│   │   └── index.css       # Global styles
│   ├── package.json
│   ├── Dockerfile.frontend
│   └── nginx.conf
├── aws/
│   ├── cloudformation-template.yaml
│   ├── ecs-task-definition.json
│   └── deploy.sh
├── data/                   # Created at runtime
├── models/                 # Created at runtime
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Troubleshooting

### Backend Issues

**Problem**: "TIINGO_API_KEY is required"
**Solution**: Make sure you've set the API key in your `.env` file

**Problem**: Training takes too long
**Solution**: Reduce `EPOCHS` or `BATCH_SIZE` in configuration

**Problem**: Out of memory during training
**Solution**: Reduce `BATCH_SIZE` or use a machine with more RAM

### Frontend Issues

**Problem**: Cannot connect to backend
**Solution**: Check that backend is running on port 8000 and CORS is enabled

**Problem**: Charts not displaying
**Solution**: Ensure data is loaded and predictions are available

### Docker Issues

**Problem**: Container fails to start
**Solution**: Check logs with `docker-compose logs` and verify environment variables

## Performance Metrics

The model typically achieves:
- Training RMSE: ~280
- Test RMSE: ~470

Note: Stock market prediction is inherently uncertain. These metrics represent model fit to historical data and do not guarantee future performance.

## Security Considerations

- Never commit `.env` file with real API keys
- Use AWS Secrets Manager for production deployments
- Enable HTTPS in production
- Restrict CORS origins in production
- Use IAM roles with minimal required permissions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Stock data provided by [Tiingo](https://www.tiingo.com/)
- Built with FastAPI, React, and TensorFlow
- Inspired by financial machine learning research

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the API documentation at `/docs`

## Roadmap

- [ ] Support for multiple stock symbols
- [ ] Real-time prediction updates
- [ ] Model performance metrics dashboard
- [ ] Automated retraining schedule
- [ ] Advanced technical indicators
- [ ] Portfolio prediction support
- [ ] Mobile-responsive improvements
- [ ] Export predictions to CSV
- [ ] Email notifications for predictions
- [ ] Multi-model ensemble predictions

## Version History

- **1.0.0** (2024): Initial release
  - LSTM model for Netflix stock prediction
  - React dashboard
  - AWS deployment support
  - Docker containerization
