#!/bin/bash

# Quick start script for Stock Prediction Application

set -e

echo "=================================="
echo "Stock Prediction Application"
echo "=================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your TIINGO_API_KEY"
    echo "   Get your API key from: https://www.tiingo.com/"
    echo ""
    read -p "Press enter to open .env file with nano (or Ctrl+C to exit)..."
    nano .env
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"
echo ""

# Ask user preference
echo "Choose deployment method:"
echo "1) Docker Compose (recommended)"
echo "2) Local development (Python + Node)"
echo ""
read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "1" ]; then
    echo ""
    echo "Starting with Docker Compose..."
    echo ""
    docker-compose up --build -d

    echo ""
    echo "✓ Application started!"
    echo ""
    echo "Access the application:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - Backend API: http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo ""
    echo "View logs:"
    echo "  docker-compose logs -f"
    echo ""
    echo "Stop application:"
    echo "  docker-compose down"
    echo ""

elif [ "$choice" = "2" ]; then
    echo ""
    echo "Starting local development..."
    echo ""

    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is not installed"
        exit 1
    fi

    # Check Node
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js is not installed"
        exit 1
    fi

    echo "Installing Python dependencies..."
    pip3 install -r requirements.txt

    echo ""
    echo "Installing Node dependencies..."
    cd frontend && npm install && cd ..

    echo ""
    echo "✓ Dependencies installed!"
    echo ""
    echo "To start the application:"
    echo ""
    echo "Terminal 1 - Backend:"
    echo "  python3 main.py"
    echo ""
    echo "Terminal 2 - Frontend:"
    echo "  cd frontend && npm start"
    echo ""

else
    echo "Invalid choice"
    exit 1
fi
