#!/bin/bash

# Quick Test Script for LA Airbnb Forecasting Platform
# Run this to quickly verify backend is working

echo "=================================="
echo "Backend Quick Test"
echo "=================================="

# Test 1: Health Check
echo -e "\n✓ Test 1: Health Check"
curl -s http://localhost:8000/api/health | python3 -m json.tool

# Test 2: Volume Forecast
echo -e "\n✓ Test 2: Volume Forecast (Ensemble Model)"
curl -s -X POST http://localhost:8000/api/forecast/volume \
  -H "Content-Type: application/json" \
  -d '{"horizon": 4, "model": "ensemble", "include_confidence": true}' | \
  python3 -m json.tool | head -30

# Test 3: Get Scenarios
echo -e "\n✓ Test 3: Available Scenarios"
curl -s http://localhost:8000/api/scenarios/scenarios | \
  python3 -m json.tool | head -20

# Test 4: Simulate Baseline Scenario
echo -e "\n✓ Test 4: Baseline Scenario Simulation"
curl -s -X POST http://localhost:8000/api/scenarios/simulate \
  -H "Content-Type: application/json" \
  -d '{"scenario_id": "baseline", "horizon": 4}' | \
  python3 -m json.tool | head -30

echo -e "\n=================================="
echo "All tests completed!"
echo "=================================="
