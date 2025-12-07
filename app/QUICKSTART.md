# 🚀 Quick Start Guide

## Start the Platform (Easy Way)

Run this single command from the project root:

```bash
cd "/Users/macintoshhd/Desktop/94829 - Advanced AI Strategy /Final Project"
./start.sh
```

This will start both backend and frontend automatically!

## Start Manually (Step by Step)

### Terminal 1: Backend

```bash
cd "/Users/macintoshhd/Desktop/94829 - Advanced AI Strategy /Final Project/airbnb-forecasting-backend"

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Frontend

```bash
cd "/Users/macintoshhd/Desktop/94829 - Advanced AI Strategy /Final Project/airbnb-forecasting-frontend"

# Install dependencies (first time only)
npm install

# Start frontend dev server
npm run dev
```

## Access the Platform

Once both servers are running:

- **🌐 Web Application**: http://localhost:5173
- **📡 Backend API**: http://localhost:8000
- **📚 API Docs (Swagger)**: http://localhost:8000/docs

## Features to Test

1. **Dashboard** - View market overview and forecasts
2. **Forecast Wizard** - Generate revenue predictions
3. **Scenario Simulator** - Explore "what-if" scenarios

## Stop the Servers

Press **Ctrl+C** in each terminal to stop the servers.

---

**Need help?** See TESTING_GUIDE.md for detailed testing procedures.
