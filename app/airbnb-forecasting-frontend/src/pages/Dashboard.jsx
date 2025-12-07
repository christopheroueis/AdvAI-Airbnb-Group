import { useState, useEffect } from 'react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, Users, DollarSign, Home, ArrowUp, ArrowDown } from 'lucide-react';
import { forecastAPI } from '../api/client';

export default function Dashboard() {
    const [volumeForecast, setVolumeForecast] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadForecasts();
    }, []);

    const loadForecasts = async () => {
        try {
            const response = await forecastAPI.forecastVolume({
                horizon: 4,
                model: 'ensemble',
                include_confidence: true
            });
            setVolumeForecast(response.data);
        } catch (error) {
            console.error('Error loading forecasts:', error);
        } finally {
            setLoading(false);
        }
    };

    // Mock historical data
    const historicalData = [
        { quarter: '2022 Q4', listings: 40438, actual: true },
        { quarter: '2023 Q1', listings: 42451, actual: true },
        { quarter: '2023 Q2', listings: 44464, actual: true },
        { quarter: '2023 Q3', listings: 44594, actual: true },
    ];

    const forecastData = volumeForecast ? [
        ...historicalData,
        ...volumeForecast.forecast.map(point => ({
            quarter: point.period,
            listings: Math.round(point.value),
            ci_lower: Math.round(point.ci_lower),
            ci_upper: Math.round(point.ci_upper),
            forecast: true
        }))
    ] : historicalData;

    const stats = [
        {
            title: 'Current Listings',
            value: '44,594',
            change: '+10.3%',
            trend: 'up',
            icon: Home,
            color: 'text-blue-400'
        },
        {
            title: 'Avg Nightly Price',
            value: '$156',
            change: '+8.2%',
            trend: 'up',
            icon: DollarSign,
            color: 'text-green-400'
        },
        {
            title: 'Occupancy Rate',
            value: '72%',
            change: '+2.1%',
            trend: 'up',
            icon: TrendingUp,
            color: 'text-purple-400'
        },
        {
            title: '2024 Q4 Forecast',
            value: '50,100',
            change: '+12.3%',
            trend: 'up',
            icon: Users,
            color: 'text-amber-400'
        },
    ];

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-400"></div>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Hero Section */}
            <div className="text-center space-y-4">
                <h1 className="text-4xl font-bold text-white">
                    LA Airbnb Market Forecaster
                </h1>
                <p className="text-xl text-gray-300">
                    ML-powered predictions for the Los Angeles home-sharing market
                </p>
                <div className="flex justify-center space-x-4">
                    <span className="glass px-4 py-2 rounded-lg text-sm text-gray-300">
                        📊 Ensemble Model • 2.87% MAPE
                    </span>
                    <span className="glass px-4 py-2 rounded-lg text-sm text-gray-300">
                        📈 10.3% Annual Growth
                    </span>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {stats.map((stat, index) => (
                    <StatCard key={index} {...stat} />
                ))}
            </div>

            {/* Main Forecast Chart */}
            <div className="glass rounded-xl p-6">
                <h2 className="text-2xl font-bold text-white mb-6">
                    Listing Volume Forecast
                </h2>
                <ResponsiveContainer width="100%" height={400}>
                    <AreaChart data={forecastData}>
                        <defs>
                            <linearGradient id="colorListings" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1} />
                            </linearGradient>
                            <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                                <stop offset="95%" stopColor="#10b981" stopOpacity={0.1} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis dataKey="quarter" stroke="#9ca3af" />
                        <YAxis stroke="#9ca3af" />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'rgba(30, 41, 59, 0.95)',
                                border: '1px solid rgba(255, 255, 255, 0.1)',
                                borderRadius: '8px',
                                color: '#fff'
                            }}
                        />
                        <Legend />
                        <Area
                            type="monotone"
                            dataKey="ci_upper"
                            stroke="none"
                            fill="#10b981"
                            fillOpacity={0.1}
                            name="95% CI Upper"
                        />
                        <Area
                            type="monotone"
                            dataKey="ci_lower"
                            stroke="none"
                            fill="#10b981"
                            fillOpacity={0.1}
                            name="95% CI Lower"
                        />
                        <Area
                            type="monotone"
                            dataKey="listings"
                            stroke="#3b82f6"
                            strokeWidth={3}
                            fill="url(#colorListings)"
                            name="Total Listings"
                        />
                    </AreaChart>
                </ResponsiveContainer>

                <div className="mt-4 flex justify-center space-x-4 text-sm">
                    <div className="flex items-center space-x-2">
                        <div className="h-3 w-3 bg-blue-400 rounded"></div>
                        <span className="text-gray-300">Historical</span>
                    </div>
                    <div className="flex items-center space-x-2">
                        <div className="h-3 w-3 bg-green-400 rounded"></div>
                        <span className="text-gray-300">Forecast</span>
                    </div>
                </div>
            </div>

            {/* Key Insights */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <InsightCard
                    title="Market Outlook"
                    insights={[
                        'Strong growth trajectory expected through 2024',
                        '12% increase projected by Q4 2024',
                        'No signs of market saturation',
                        'Emerging neighborhoods show high potential'
                    ]}
                />
                <InsightCard
                    title="Model Performance"
                    insights={[
                        'Ensemble model achieves 2.87% MAPE',
                        'LSTM: 3.15% MAPE (best individual)',
                        'Prophet: 3.52% MAPE (fastest training)',
                        'All models achieve < 5% error (excellent)'
                    ]}
                />
            </div>
        </div>
    );
}

function StatCard({ title, value, change, trend, icon: Icon, color }) {
    return (
        <div className="glass rounded-xl p-6 hover:bg-white/15 transition-all cursor-pointer">
            <div className="flex items-center justify-between">
                <Icon className={`h-8 w-8 ${color}`} />
                {trend === 'up' ? (
                    <ArrowUp className="h-5 w-5 text-green-400" />
                ) : (
                    <ArrowDown className="h-5 w-5 text-red-400" />
                )}
            </div>
            <div className="mt-4">
                <p className="text-sm text-gray-400">{title}</p>
                <p className="text-3xl font-bold text-white mt-1">{value}</p>
                <p className={`text-sm mt-1 ${trend === 'up' ? 'text-green-400' : 'text-red-400'}`}>
                    {change} vs last year
                </p>
            </div>
        </div>
    );
}

function InsightCard({ title, insights }) {
    return (
        <div className="glass rounded-xl p-6">
            <h3 className="text-xl font-bold text-white mb-4">{title}</h3>
            <ul className="space-y-3">
                {insights.map((insight, index) => (
                    <li key={index} className="flex items-start space-x-2">
                        <span className="text-primary-400 mt-1">•</span>
                        <span className="text-gray-300">{insight}</span>
                    </li>
                ))}
            </ul>
        </div>
    );
}
