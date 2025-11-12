import numpy as np
import pandas as pd
import pandas_datareader as pdr
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, LSTM
from sklearn.metrics import mean_squared_error
import math
import os
import pickle
from datetime import datetime, timedelta
from .config import config

class StockPredictor:
    """Stock price prediction model using LSTM"""

    def __init__(self, symbol='NFLX', time_step=None):
        self.symbol = symbol
        self.time_step = time_step or config.TIME_STEP
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.df = None
        self.scaled_data = None
        self.train_data = None
        self.test_data = None
        self.model_path = os.path.join(config.MODEL_DIR, f'{symbol}_model.h5')
        self.scaler_path = os.path.join(config.MODEL_DIR, f'{symbol}_scaler.pkl')

        # Create directories if they don't exist
        os.makedirs(config.DATA_DIR, exist_ok=True)
        os.makedirs(config.MODEL_DIR, exist_ok=True)

    def fetch_data(self, start_date=None, end_date=None):
        """Fetch stock data from Tiingo API"""
        try:
            print(f"Fetching data for {self.symbol}...")
            df = pdr.get_data_tiingo(self.symbol, api_key=config.TIINGO_API_KEY)

            # Save raw data
            csv_path = os.path.join(config.DATA_DIR, f'{self.symbol}.csv')
            df.to_csv(csv_path)

            self.df = pd.read_csv(csv_path)
            print(f"Data fetched successfully. Shape: {self.df.shape}")
            return self.df
        except Exception as e:
            print(f"Error fetching data: {e}")
            # Try to load from existing file
            csv_path = os.path.join(config.DATA_DIR, f'{self.symbol}.csv')
            if os.path.exists(csv_path):
                print("Loading data from cached file...")
                self.df = pd.read_csv(csv_path)
                return self.df
            raise

    def preprocess_data(self):
        """Preprocess the stock data"""
        if self.df is None:
            raise ValueError("No data available. Call fetch_data() first.")

        # Extract close prices
        df1 = self.df.reset_index()['close'].values.reshape(-1, 1)

        # Scale the data
        self.scaled_data = self.scaler.fit_transform(df1)

        # Split into training and test sets
        training_size = int(len(self.scaled_data) * config.TRAINING_SIZE_RATIO)
        self.train_data = self.scaled_data[0:training_size]
        self.test_data = self.scaled_data[training_size:]

        print(f"Training size: {len(self.train_data)}, Test size: {len(self.test_data)}")

        return self.train_data, self.test_data

    def create_dataset(self, dataset, time_step=None):
        """Convert an array of values into a dataset matrix"""
        if time_step is None:
            time_step = self.time_step

        dataX, dataY = [], []
        for i in range(len(dataset) - time_step - 1):
            a = dataset[i:(i + time_step), 0]
            dataX.append(a)
            dataY.append(dataset[i + time_step, 0])
        return np.array(dataX), np.array(dataY)

    def build_model(self):
        """Build the LSTM model"""
        model = Sequential()
        model.add(LSTM(config.LSTM_UNITS, return_sequences=True, input_shape=(self.time_step, 1)))
        model.add(LSTM(config.LSTM_UNITS, return_sequences=True))
        model.add(LSTM(config.LSTM_UNITS))
        model.add(Dense(1))
        model.compile(loss='mean_squared_error', optimizer='adam')

        self.model = model
        return model

    def train(self, epochs=None, batch_size=None):
        """Train the model"""
        if self.train_data is None:
            raise ValueError("No training data. Call preprocess_data() first.")

        epochs = epochs or config.EPOCHS
        batch_size = batch_size or config.BATCH_SIZE

        # Prepare training and test datasets
        X_train, y_train = self.create_dataset(self.train_data)
        X_test, y_test = self.create_dataset(self.test_data)

        # Reshape for LSTM
        X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
        X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

        # Build model if not exists
        if self.model is None:
            self.build_model()

        # Train the model
        print(f"Training model for {epochs} epochs...")
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=batch_size,
            verbose=1
        )

        # Calculate metrics
        train_predict = self.model.predict(X_train)
        test_predict = self.model.predict(X_test)

        train_rmse = math.sqrt(mean_squared_error(y_train, train_predict))
        test_rmse = math.sqrt(mean_squared_error(y_test, test_predict))

        print(f"Training RMSE: {train_rmse}")
        print(f"Test RMSE: {test_rmse}")

        # Save model and scaler
        self.save_model()

        return {
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'history': history.history
        }

    def predict_future(self, days=30):
        """Predict future stock prices"""
        if self.model is None:
            if os.path.exists(self.model_path):
                self.load_model()
            else:
                raise ValueError("No model available. Train the model first.")

        if self.test_data is None or len(self.test_data) == 0:
            raise ValueError("No test data available.")

        # Get the last 100 days from test data
        last_sequence = self.test_data[-self.time_step:].copy()
        temp_input = last_sequence.flatten().tolist()

        lst_output = []
        n_steps = self.time_step

        for i in range(days):
            if len(temp_input) > n_steps:
                x_input = np.array(temp_input[-n_steps:])
                x_input = x_input.reshape(1, n_steps, 1)
                yhat = self.model.predict(x_input, verbose=0)
                temp_input.append(yhat[0][0])
                lst_output.append(yhat[0][0])
            else:
                x_input = np.array(temp_input).reshape(1, n_steps, 1)
                yhat = self.model.predict(x_input, verbose=0)
                temp_input.append(yhat[0][0])
                lst_output.append(yhat[0][0])

        # Inverse transform predictions
        predictions = self.scaler.inverse_transform(np.array(lst_output).reshape(-1, 1))

        return predictions.flatten().tolist()

    def get_historical_predictions(self):
        """Get predictions for historical data"""
        if self.model is None:
            if os.path.exists(self.model_path):
                self.load_model()
            else:
                raise ValueError("No model available. Train the model first.")

        # Prepare datasets
        X_train, y_train = self.create_dataset(self.train_data)
        X_test, y_test = self.create_dataset(self.test_data)

        X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
        X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

        # Make predictions
        train_predict = self.model.predict(X_train)
        test_predict = self.model.predict(X_test)

        # Inverse transform
        train_predict = self.scaler.inverse_transform(train_predict)
        test_predict = self.scaler.inverse_transform(test_predict)

        # Create plot arrays
        look_back = self.time_step
        trainPredictPlot = np.empty((len(self.scaled_data), 1))
        trainPredictPlot[:, :] = np.nan
        trainPredictPlot[look_back:len(train_predict) + look_back, :] = train_predict

        testPredictPlot = np.empty((len(self.scaled_data), 1))
        testPredictPlot[:, :] = np.nan
        testPredictPlot[len(train_predict) + (look_back * 2) + 1:len(self.scaled_data) - 1, :] = test_predict

        # Get actual values
        actual = self.scaler.inverse_transform(self.scaled_data)

        return {
            'actual': actual.flatten().tolist(),
            'train_predictions': trainPredictPlot.flatten().tolist(),
            'test_predictions': testPredictPlot.flatten().tolist()
        }

    def save_model(self):
        """Save model and scaler"""
        self.model.save(self.model_path)
        with open(self.scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        print(f"Model saved to {self.model_path}")

    def load_model(self):
        """Load model and scaler"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = load_model(self.model_path)
            with open(self.scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            print(f"Model loaded from {self.model_path}")
            return True
        return False

    def get_latest_price(self):
        """Get the latest stock price"""
        if self.df is not None and len(self.df) > 0:
            return float(self.df['close'].iloc[-1])
        return None

    def get_data_summary(self):
        """Get summary of the data"""
        if self.df is None:
            return None

        return {
            'symbol': self.symbol,
            'total_records': len(self.df),
            'date_range': {
                'start': str(self.df['date'].iloc[0]) if 'date' in self.df.columns else None,
                'end': str(self.df['date'].iloc[-1]) if 'date' in self.df.columns else None
            },
            'latest_price': self.get_latest_price(),
            'price_stats': {
                'min': float(self.df['close'].min()),
                'max': float(self.df['close'].max()),
                'mean': float(self.df['close'].mean()),
                'std': float(self.df['close'].std())
            }
        }
