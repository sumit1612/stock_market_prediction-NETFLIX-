import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { TrendingUp, Activity, Database, Play, Download, RefreshCw } from 'lucide-react';
import './App.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [status, setStatus] = useState(null);
  const [dataSummary, setDataSummary] = useState(null);
  const [predictions, setPredictions] = useState(null);
  const [historical, setHistorical] = useState(null);
  const [loading, setLoading] = useState(false);
  const [trainingStatus, setTrainingStatus] = useState(null);
  const [predictionDays, setPredictionDays] = useState(30);

  useEffect(() => {
    fetchStatus();
    fetchDataSummary();
  }, []);

  useEffect(() => {
    if (trainingStatus?.is_training) {
      const interval = setInterval(() => {
        fetchTrainingStatus();
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [trainingStatus]);

  const fetchStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/status`);
      setStatus(response.data);
    } catch (error) {
      console.error('Error fetching status:', error);
    }
  };

  const fetchDataSummary = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/data`);
      setDataSummary(response.data);
    } catch (error) {
      console.error('Error fetching data summary:', error);
    }
  };

  const fetchTrainingStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/train/status`);
      setTrainingStatus(response.data);
      if (!response.data.is_training && response.data.progress === 100) {
        fetchStatus();
      }
    } catch (error) {
      console.error('Error fetching training status:', error);
    }
  };

  const handleFetchData = async () => {
    setLoading(true);
    try {
      await axios.post(`${API_BASE_URL}/api/data/fetch`, { symbol: 'NFLX' });
      await fetchDataSummary();
      await fetchStatus();
      alert('Data fetched successfully!');
    } catch (error) {
      alert('Error fetching data: ' + error.response?.data?.detail || error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTrainModel = async () => {
    setLoading(true);
    try {
      await axios.post(`${API_BASE_URL}/api/train`, {});
      setTrainingStatus({ is_training: true, message: 'Training started...' });
      alert('Training started! This may take several minutes.');
    } catch (error) {
      alert('Error training model: ' + error.response?.data?.detail || error.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePredict = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/predict`, { days: predictionDays });
      setPredictions(response.data);
    } catch (error) {
      alert('Error making predictions: ' + error.response?.data?.detail || error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadHistorical = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/historical`);
      setHistorical(response.data);
    } catch (error) {
      alert('Error loading historical data: ' + error.response?.data?.detail || error.message);
    } finally {
      setLoading(false);
    }
  };

  const getPredictionChartData = () => {
    if (!predictions) return null;

    return {
      labels: predictions.dates,
      datasets: [
        {
          label: 'Predicted Price',
          data: predictions.predictions,
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.1,
          fill: true
        }
      ]
    };
  };

  const getHistoricalChartData = () => {
    if (!historical) return null;

    const labels = historical.dates.length > 0
      ? historical.dates.map((d, i) => i % 50 === 0 ? d.split('T')[0] : '')
      : historical.actual.map((_, i) => i);

    return {
      labels,
      datasets: [
        {
          label: 'Actual Price',
          data: historical.actual,
          borderColor: 'rgb(99, 102, 241)',
          backgroundColor: 'rgba(99, 102, 241, 0.1)',
          tension: 0.1,
          pointRadius: 0
        },
        {
          label: 'Training Predictions',
          data: historical.train_predictions,
          borderColor: 'rgb(34, 197, 94)',
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          tension: 0.1,
          pointRadius: 0
        },
        {
          label: 'Test Predictions',
          data: historical.test_predictions,
          borderColor: 'rgb(251, 146, 60)',
          backgroundColor: 'rgba(251, 146, 60, 0.1)',
          tension: 0.1,
          pointRadius: 0
        }
      ]
    };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: false
      }
    },
    scales: {
      y: {
        beginAtZero: false
      }
    }
  };

  return (
    <div className="App">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <TrendingUp size={32} />
            <h1>Netflix Stock Prediction</h1>
          </div>
          <div className="status-badge">
            <Activity size={16} />
            <span>{status?.model_loaded ? 'Model Ready' : 'No Model'}</span>
          </div>
        </div>
      </header>

      <main className="main-content">
        {/* Status Cards */}
        <div className="cards-grid">
          <div className="card">
            <div className="card-header">
              <Database size={20} />
              <h3>Data Status</h3>
            </div>
            <div className="card-content">
              {dataSummary ? (
                <>
                  <div className="stat">
                    <span className="stat-label">Symbol:</span>
                    <span className="stat-value">{dataSummary.symbol}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Records:</span>
                    <span className="stat-value">{dataSummary.total_records}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Latest Price:</span>
                    <span className="stat-value">${dataSummary.latest_price?.toFixed(2)}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Date Range:</span>
                    <span className="stat-value">
                      {dataSummary.date_range?.start?.split('T')[0]} to {dataSummary.date_range?.end?.split('T')[0]}
                    </span>
                  </div>
                </>
              ) : (
                <p>No data loaded</p>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <Activity size={20} />
              <h3>Model Status</h3>
            </div>
            <div className="card-content">
              {status ? (
                <>
                  <div className="stat">
                    <span className="stat-label">Status:</span>
                    <span className={`stat-value ${status.model_loaded ? 'success' : 'warning'}`}>
                      {status.model_loaded ? 'Trained' : 'Not Trained'}
                    </span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Epochs:</span>
                    <span className="stat-value">{status.config?.epochs}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Batch Size:</span>
                    <span className="stat-value">{status.config?.batch_size}</span>
                  </div>
                  {trainingStatus?.is_training && (
                    <div className="training-status">
                      <RefreshCw size={16} className="spin" />
                      <span>{trainingStatus.message}</span>
                    </div>
                  )}
                </>
              ) : (
                <p>Loading...</p>
              )}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="actions-section">
          <h2>Actions</h2>
          <div className="actions-grid">
            <button
              className="btn btn-primary"
              onClick={handleFetchData}
              disabled={loading}
            >
              <Download size={20} />
              Fetch Latest Data
            </button>
            <button
              className="btn btn-success"
              onClick={handleTrainModel}
              disabled={loading || !status?.data_loaded || trainingStatus?.is_training}
            >
              <Play size={20} />
              Train Model
            </button>
            <button
              className="btn btn-info"
              onClick={handleLoadHistorical}
              disabled={loading || !status?.model_loaded}
            >
              <Activity size={20} />
              Load Historical
            </button>
            <div className="predict-section">
              <input
                type="number"
                value={predictionDays}
                onChange={(e) => setPredictionDays(Number(e.target.value))}
                min="1"
                max="365"
                placeholder="Days"
                className="input"
              />
              <button
                className="btn btn-warning"
                onClick={handlePredict}
                disabled={loading || !status?.model_loaded}
              >
                <TrendingUp size={20} />
                Predict
              </button>
            </div>
          </div>
        </div>

        {/* Charts */}
        {historical && (
          <div className="chart-section">
            <h2>Historical Data & Predictions</h2>
            <div className="chart-container">
              <Line data={getHistoricalChartData()} options={chartOptions} />
            </div>
          </div>
        )}

        {predictions && (
          <div className="chart-section">
            <h2>Future Predictions ({predictions.days} days)</h2>
            <div className="chart-container">
              <Line data={getPredictionChartData()} options={chartOptions} />
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
        <p>Stock Market Prediction Dashboard - Netflix (NFLX)</p>
        <p>Powered by LSTM Neural Networks</p>
      </footer>
    </div>
  );
}

export default App;
