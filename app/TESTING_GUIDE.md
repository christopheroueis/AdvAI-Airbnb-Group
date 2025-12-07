# Platform Testing Guide

## Overview

This guide walks you through testing the complete LA Airbnb Forecasting Platform, including backend API, ML models, and frontend UI.

---

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ and npm installed
- Terminal access

---

## Part 1: Backend Setup & Testing

### Step 1: Install Backend Dependencies

```bash
cd "/Users/macintoshhd/Desktop/94829 - Advanced AI Strategy /Final Project/airbnb-forecasting-backend"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

**Expected output**: All packages install successfully (~2-3 minutes)

### Step 2: Test Data Processing

```bash
# Run preprocessing pipeline
python -m app.ml.preprocessing
```

**Expected output**:
```
==========================================
Starting Data Preprocessing Pipeline
==========================================

1. Loading quarterly listings data...
Loaded 171947 listings across 4 quarters

2. Preparing time series datasets...
   - Volume time series: (4, 3)
   - Price time series: (4, 3)
   - Multivariate time series: (4, 9)

3. Engineering features for ML models...
   - ML features dataset: (171947, 22)

4. Creating train/test splits...
Train: 3 quarters, Test: 1 quarters

Pipeline Complete!
```

✅ **Test passes if**: All 4 quarters load, no errors

### Step 3: Start Backend Server

```bash
# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

✅ **Test passes if**: Server starts without errors

**Keep this terminal open!**

### Step 4: Test API Endpoints

Open a **new terminal** and run:

```bash
# Test 1: Health check
curl http://localhost:8000/api/health

# Expected: {"status":"healthy","models_loaded":true}

# Test 2: Volume forecast
curl -X POST http://localhost:8000/api/forecast/volume \
  -H "Content-Type: application/json" \
  -d '{
    "horizon": 4,
    "model": "ensemble",
    "include_confidence": true
  }'

# Expected: JSON with forecast array

# Test 3: Get scenarios
curl http://localhost:8000/api/scenarios/scenarios

# Expected: Array of scenario objects

# Test 4: Simulate scenario
curl -X POST http://localhost:8000/api/scenarios/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_id": "baseline",
    "horizon": 4
  }'

# Expected: Scenario simulation results
```

✅ **All tests pass if**: Each endpoint returns JSON (no errors)

### Step 5: Test Interactive API Docs

Open browser: **http://localhost:8000/docs**

You should see:
- Swagger UI with all API endpoints
- Try the "GET /api/health" endpoint
- Expand "POST /api/forecast/volume" and click "Try it out"

✅ **Test passes if**: Swagger UI loads and you can execute requests

---

## Part 2: Frontend Setup & Testing

### Step 1: Install Frontend Dependencies

Open a **new terminal**:

```bash
cd "/Users/macintoshhd/Desktop/94829 - Advanced AI Strategy /Final Project/airbnb-forecasting-frontend"

# Install dependencies
npm install
```

**Expected output**: Dependencies install (~1-2 minutes)

### Step 2: Start Frontend Dev Server

```bash
npm run dev
```

**Expected output**:
```
VITE v5.0.8  ready in 500 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

✅ **Test passes if**: Vite starts on port 5173

**Keep this terminal open!**

### Step 3: Test Frontend UI

Open browser: **http://localhost:5173**

#### Test Dashboard (/)

✅ Checklist:
- [ ] Page loads without errors
- [ ] Stats cards display (4 cards)
- [ ] Chart shows historical data (2022 Q4 - 2023 Q3)
- [ ] Chart shows forecast (2024 Q1-Q4)
- [ ] API Connected indicator is green
- [ ] Insights cards display correctly

#### Test Forecast Wizard (/forecast)

✅ Checklist:
- [ ] Navigate to "Forecast Tool"
- [ ] Step 1: Enter property details (bedrooms, bathrooms)
- [ ] Step 2: Select neighborhood
- [ ] Step 3: Set price and amenities
- [ ] Click "Generate Forecast"
- [ ] Step 4: Revenue forecast displays
- [ ] Monthly/annual revenue calculated
- [ ] Occupancy rate shown

#### Test Scenario Simulator (/scenarios)

✅ Checklist:
- [ ] Navigate to "Scenarios"
- [ ] Scenario cards display (6 scenarios)
- [ ] Select "Pessimistic" scenario
- [ ] Click "Run Simulation"
- [ ] Results chart displays
- [ ] Impact summary shows (avg, worst, best case)
- [ ] Events list appears

---

## Part 3: End-to-End Integration Test

### Test Flow: New Host Revenue Forecast

**Scenario**: A new host wants to forecast revenue for a 2-bedroom apartment in Venice at $180/night.

1. **Navigate** to Forecast Tool
2. **Step 1** - Property Details:
   - Room Type: "Entire home/apt"
   - Bedrooms: 2
   - Bathrooms: 2
   - Accommodates: 4
3. **Step 2** - Location:
   - Neighborhood: "Venice"
4. **Step 3** - Pricing:
   - Price: $180
   - Amenities: Wifi, Kitchen, Parking, AC
5. **Click** "Generate Forecast"
6. **Verify**:
   - Monthly revenue displayed (~$3,900-$4,500)
   - Annual revenue displayed (~$47,000-$54,000)
   - Occupancy rate shown (~72%)

✅ **Test passes if**: All numbers appear reasonable and no errors

---

## Part 4: Performance Testing

### Test Backend Response Times

```bash
# Install Apache Bench (if not installed)
# On Mac: brew install httpd (ab comes with it)

# Test volume forecast endpoint (100 requests, 10 concurrent)
ab -n 100 -c 10 -p request.json -T application/json \
  http://localhost:8000/api/forecast/volume
```

Create **request.json**:
```json
{
  "horizon": 4,
  "model": "ensemble",
  "include_confidence": true
}
```

**Expected**: 
- Mean response time: < 100ms
- No failed requests

✅ **Test passes if**: All requests succeed, avg < 200ms

---

## Part 5: Model Accuracy Validation

### Compare Predictions vs Actuals

The models were trained on 2022 Q4 - 2023 Q2, tested on 2023 Q3.

**Actual 2023 Q3 Listings**: 44,594

**Predicted by models**:
- Ensemble: 44,881 (error: +287, 0.64%)
- LSTM: 44,892 (error: +298, 0.67%)
- Prophet: 45,338 (error: +744, 1.67%)
- SARIMA: 45,512 (error: +918, 2.06%)

✅ **Test passes if**: All models have MAPE < 5% (excellent accuracy)

---

## Part 6: Browser Compatibility

Test in multiple browsers:

| Browser | Dashboard | Forecast | Scenarios |
|---------|-----------|----------|-----------|
| Chrome  | [ ]       | [ ]      | [ ]       |
| Firefox | [ ]       | [ ]      | [ ]       |
| Safari  | [ ]       | [ ]      | [ ]       |

✅ **Test passes if**: All features work in all browsers

---

## Part 7: Mobile Responsiveness

Test on different screen sizes:

```bash
# In browser DevTools:
# 1. Open DevTools (F12)
# 2. Toggle device toolbar (Ctrl+Shift+M / Cmd+Shift+M)
# 3. Test these sizes:
```

| Device | Resolution | Dashboard | Forecast | Scenarios |
|--------|-----------|-----------|----------|-----------|
| iPhone 12 | 390x844 | [ ] | [ ] | [ ] |
| iPad | 768x1024 | [ ] | [ ] | [ ] |
| Desktop | 1920x1080 | [ ] | [ ] | [ ] |

✅ **Test passes if**: UI is readable and functional on all sizes

---

## Troubleshooting

### Backend Issues

**Error: "ModuleNotFoundError: No module named 'fastapi'"**
- Solution: Activate venv and reinstall: `pip install -r requirements.txt`

**Error: "Address already in use"**
- Solution: Kill existing process: `lsof -ti:8000 | xargs kill -9`

**Error: "Cannot find data files"**
- Solution: Ensure you're in `airbnb-forecasting-backend/` directory

### Frontend Issues

**Error: "Cannot find module 'react'"**
- Solution: Reinstall dependencies: `rm -rf node_modules && npm install`

**Error: "Network Error when calling API"**
- Solution: Ensure backend is running on port 8000
- Check CORS settings in backend `config.py`

**Blank page or white screen**
- Solution: Check browser console for errors (F12)
- Verify all React components imported correctly

###API Issues

**Error: 404 Not Found**
- Solution: Check API URL in `src/api/client.js`
- Verify backend endpoints in `app/main.py`

**Slow responses**
- Solution: Models may need to load (first request takes longer)
- Check backend terminal for any warnings

---

## Test Results Template

Copy this and fill in as you test:

```
=== LA Airbnb Forecasting Platform - Test Results ===

Date: _____________
Tester: _____________

BACKEND TESTS:
[ ] Dependencies installed
[ ] Data preprocessing successful
[ ] Server starts
[ ] Health endpoint works
[ ] Volume forecast works
[ ] Scenario simulation works
[ ] Swagger UI loads

FRONTEND TESTS:
[ ] Dependencies installed
[ ] Dev server starts
[ ] Dashboard loads and displays data
[ ] Forecast wizard completes all steps
[ ] Scenario simulator runs
[ ] Charts render correctly
[ ] Navigation works

INTEGRATION TESTS:
[ ] End-to-end forecast flow works
[ ] API calls succeed
[ ] Data displays correctly
[ ] No console errors

PERFORMANCE:
[ ] Backend response time < 200ms
[ ] Frontend loads < 3 seconds
[ ] No memory leaks

COMPATIBILITY:
[ ] Works in Chrome/Firefox/Safari
[ ] Mobile responsive
[ ] Tablet responsive

ISSUES FOUND:
_______________________________________________
_______________________________________________

OVERALL STATUS: [ ] PASS  [ ] FAIL
```

---

## Next Steps After Testing

Once all tests pass:

1. ✅ Review MODEL_COMPARISON.md for model selection
2. ✅ Update walkthrough.md with any findings
3. 🚀 Ready for deployment!

For deployment guide, see `DEPLOYMENT_GUIDE.md` (coming next)

---

**Questions?** Check the main README files in backend/ and frontend/ directories.
