# LA Airbnb Forecasting Platform - Frontend

Modern React application for the LA Airbnb forecasting platform.

## Features

- 📊 **Interactive Dashboard**: Real-time market stats and forecasts
- 🔮 **Forecast Wizard**: Multi-step tool for revenue prediction
- 🎯 **Scenario Simulator**: Explore "what-if" scenarios with external events
- 📈 **Beautiful Charts**: Powered by Recharts
- 🎨 **Modern UI**: Tailwind CSS with glassmorphism effects
- ⚡ **Fast**: Built with Vite

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

The app will run on `http://localhost:5173`

## Environment Variables

Create a `.env` file:

```
VITE_API_URL=http://localhost:8000/api
```

## Project Structure

```
src/
├── pages/
│   ├── Dashboard.jsx          # Main dashboard
│   ├── ForecastWizard.jsx     # Revenue forecast tool
│   └── ScenarioSimulator.jsx  # Scenario analysis
├── api/
│   └── client.js              # API client
├── App.jsx                    # Main app component
└── main.jsx                   # Entry point
```

## API Integration

The frontend connects to the FastAPI backend:
- `/api/forecast/volume` - Listing volume forecasts
- `/api/forecast/price` - Price predictions
- `/api/forecast/occupancy` - Occupancy & revenue
- `/api/scenarios/*` - Scenario simulation

## Tech Stack

- **React 18**: UI library
- **Vite**: Build tool
- **Tailwind CSS**: Styling
- **Recharts**: Data visualization
- **Axios**: HTTP client
- **React Router**: Navigation
- **Lucide React**: Icons

## Development

```bash
# Run dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Deployment

Deploy to Vercel:
```bash
vercel --prod
```

Configure environment variable `VITEAPI_URL` in Vercel dashboard to point to your backend.
