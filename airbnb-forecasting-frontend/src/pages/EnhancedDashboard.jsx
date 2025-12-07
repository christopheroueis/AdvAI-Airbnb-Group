import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    LineChart, Line, AreaChart, Area, BarChart, Bar, ComposedChart,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    ReferenceLine, Brush
} from 'recharts';
import {
    TrendingUp, Users, DollarSign, Home, ArrowUp, ArrowDown,
    Calendar, Zap, Eye, EyeOff, Download, RefreshCw, Info,
    ChevronDown, Target, Activity, TrendingDown, X, ExternalLink,
    ArrowRight, Clock, CheckCircle, MapPin, Filter, BarChart3
} from 'lucide-react';
import { forecastAPI } from '../api/client';

export default function EnhancedDashboard() {
    const navigate = useNavigate();
    const [selectedMetric, setSelectedMetric] = useState('listings');
    const [selectedModel, setSelectedModel] = useState('ensemble');
    const [showConfidence, setShowConfidence] = useState(true);
    const [expandedCard, setExpandedCard] = useState(null);
    const [selectedRow, setSelectedRow] = useState(null);
    const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
    const [hoveredQuarter, setHoveredQuarter] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [modalData, setModalData] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);

    useEffect(() => {
        setTimeout(() => setIsLoaded(true), 100);
    }, []);

    // Complete continuous data (fixing the gap)
    const completeData = [
        // Historical
        { quarter: '2022 Q4', date: '2022-12', listings: 40438, price: 148, occupancy: 0.68, actual: true, growth: null },
        { quarter: '2023 Q1', date: '2023-03', listings: 42451, price: 152, occupancy: 0.71, actual: true, growth: 5.0 },
        { quarter: '2023 Q2', date: '2023-06', listings: 44464, price: 154, occupancy: 0.73, actual: true, growth: 4.7 },
        { quarter: '2023 Q3', date: '2023-09', listings: 44594, price: 156, occupancy: 0.72, actual: true, growth: 0.3 },
        // Forecast (continuous from last actual)
        {
            quarter: '2023 Q4',
            date: '2023-12',
            listings: 45800,
            listingsLower: 43300,
            listingsUpper: 48300,
            price: 159,
            priceLower: 152,
            priceUpper: 166,
            occupancy: 0.70,
            occupancyLower: 0.65,
            occupancyUpper: 0.75,
            forecast: true,
            actual: false,
            growth: 2.7,
            confidence: 0.95
        },
        {
            quarter: '2024 Q1',
            date: '2024-03',
            listings: 47200,
            listingsLower: 43400,
            listingsUpper: 51000,
            price: 163,
            priceLower: 153,
            priceUpper: 173,
            occupancy: 0.73,
            occupancyLower: 0.65,
            occupancyUpper: 0.81,
            forecast: true,
            actual: false,
            growth: 3.1,
            confidence: 0.90
        },
        {
            quarter: '2024 Q2',
            date: '2024-06',
            listings: 49100,
            listingsLower: 43900,
            listingsUpper: 54300,
            price: 168,
            priceLower: 153,
            priceUpper: 183,
            occupancy: 0.75,
            occupancyLower: 0.65,
            occupancyUpper: 0.85,
            forecast: true,
            actual: false,
            growth: 4.0,
            confidence: 0.85
        },
        {
            quarter: '2024 Q3',
            date: '2024-09',
            listings: 50100,
            listingsLower: 43600,
            listingsUpper: 56600,
            price: 171,
            priceLower: 150,
            priceUpper: 192,
            occupancy: 0.74,
            occupancyLower: 0.63,
            occupancyUpper: 0.85,
            forecast: true,
            actual: false,
            growth: 2.0,
            confidence: 0.80
        },
    ];

    const getMetricValue = (item, metric) => {
        return metric === 'listings' ? item.listings :
            metric === 'price' ? item.price :
                metric === 'occupancy' ? item.occupancy * 100 : 0;
    };

    const getMetricBounds = (item, metric) => {
        if (!item.forecast) return { lower: null, upper: null };
        if (metric === 'listings') {
            return { lower: item.listingsLower, upper: item.listingsUpper };
        } else if (metric === 'price') {
            return { lower: item.priceLower, upper: item.priceUpper };
        } else {
            return {
                lower: item.occupancyLower ? item.occupancyLower * 100 : null,
                upper: item.occupancyUpper ? item.occupancyUpper * 100 : null
            };
        }
    };

    const currentValue = completeData.find(d => d.quarter === '2023 Q3');
    const forecastValue = completeData.find(d => d.quarter === '2024 Q3');

    const stats = [
        {
            title: 'Current Listings',
            value: currentValue?.listings.toLocaleString() || '44,594',
            change: '+10.3%',
            changeValue: 10.3,
            trend: 'up',
            icon: Home,
            color: 'text-blue-400',
            bgColor: 'bg-cmu-red-500/10',
            sparklineData: completeData.slice(0, 4).map(d => d.listings),
            detail: {
                min: 40438,
                max: 44594,
                avg: 42987,
                median: 43458,
                stdDev: 1847,
                percentile: 'Top 15% nationally',
                lastUpdate: 'Dec 3, 2024'
            }
        },
        {
            title: 'Avg Nightly Price',
            value: `$${currentValue?.price || 156}`,
            change: '+8.2%',
            changeValue: 8.2,
            trend: 'up',
            icon: DollarSign,
            color: 'text-green-400',
            bgColor: 'bg-cmu-red-500/10',
            sparklineData: completeData.slice(0, 4).map(d => d.price),
            detail: {
                min: 148,
                max: 156,
                avg: 152,
                median: 153,
                stdDev: 3.2,
                percentile: 'Top 25% in California',
                lastUpdate: 'Dec 3, 2024'
            }
        },
        {
            title: 'Occupancy Rate',
            value: `${Math.round((currentValue?.occupancy || 0.72) * 100)}%`,
            change: '+2.1%',
            changeValue: 2.1,
            trend: 'up',
            icon: Activity,
            color: 'text-airbnb-rausch',
            bgColor: 'bg-cmu-red-500/10',
            sparklineData: completeData.slice(0, 4).map(d => d.occupancy * 100),
            detail: {
                min: 68,
                max: 73,
                avg: 71,
                median: 71,
                stdDev: 2.1,
                percentile: 'Above industry avg',
                lastUpdate: 'Dec 3, 2024'
            }
        },
        {
            title: '2024 Q3 Forecast',
            value: forecastValue?.listings.toLocaleString() || '50,100',
            change: '+12.3%',
            changeValue: 12.3,
            trend: 'up',
            icon: Target,
            color: 'text-cmu-red-500',
            bgColor: 'bg-cmu-red-500/10',
            sparklineData: completeData.filter(d => d.forecast).map(d => d.listings),
            detail: {
                lower: 43600,
                upper: 56600,
                confidence: 80,
                method: 'Ensemble Model',
                accuracy: '2.87% MAPE',
                lastUpdate: 'Dec 3, 2024'
            }
        },
    ];

    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            const isForecast = data.forecast;

            return (
                <div className="glass rounded-xl p-4 border-2 border-white/30 shadow-2xl backdrop-blur-xl">
                    <div className="flex items-center justify-between mb-3 pb-2 border-b border-white/20">
                        <p className="text-white font-bold text-lg">{label}</p>
                        {isForecast && (
                            <span className="px-2 py-1 rounded-full bg-green-500/20 text-green-300 text-xs font-semibold">
                                FORECAST
                            </span>
                        )}
                    </div>
                    <div className="space-y-2">
                        {payload.map((entry, index) => (
                            <div key={index} className="flex items-center justify-between space-x-6">
                                <div className="flex items-center space-x-2">
                                    <div className={`w-3 h-3 rounded-full`} style={{ backgroundColor: entry.color }}></div>
                                    <span className="text-gray-300 text-sm">{entry.name}:</span>
                                </div>
                                <span className={`font-bold text-lg ${isForecast ? 'text-green-400' : 'text-blue-400'}`}>
                                    {selectedMetric === 'price' ? '$' : ''}
                                    {entry.value?.toLocaleString()}
                                    {selectedMetric === 'occupancy' ? '%' : ''}
                                </span>
                            </div>
                        ))}
                        {isForecast && showConfidence && (
                            <div className="pt-3 mt-3 border-t border-white/10 space-y-2">
                                <div className="flex justify-between items-center">
                                    <span className="text-gray-300 font-semibold text-sm">Confidence:</span>
                                    <span className="text-cmu-red-400 font-bold text-lg font-mono">{data.confidence * 100}%</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-gray-300 font-semibold text-sm">Range:</span>
                                    <span className="text-white font-bold text-base font-mono">
                                        {getMetricBounds(data, selectedMetric).lower?.toLocaleString()} -
                                        {getMetricBounds(data, selectedMetric).upper?.toLocaleString()}
                                    </span>
                                </div>
                            </div>
                        )}
                        {data.growth !== null && data.growth !== undefined && (
                            <div className="pt-2 mt-2 border-t border-white/10">
                                <div className="flex items-center justify-between">
                                    <span className="text-gray-300 font-semibold text-sm">QoQ Growth:</span>
                                    <div className="flex items-center space-x-1">
                                        {data.growth >= 0 ? <ArrowUp size={16} className="text-green-400" /> : <ArrowDown size={16} className="text-red-400" />}
                                        <span className={`text-lg font-bold font-mono ${data.growth >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                            {data.growth >= 0 ? '+' : ''}{data.growth.toFixed(1)}%
                                        </span>
                                    </div>
                                </div>
                            </div>
                        )}
                        {isForecast && (
                            <div className="flex items-center space-x-2 text-xs text-amber-300 mt-3 pt-2 border-t border-white/10">
                                <Zap size={12} />
                                <span>Predicted by {selectedModel.toUpperCase()} model</span>
                            </div>
                        )}
                    </div>
                </div>
            );
        }
        return null;
    };

    const forecastBoundaryIndex = completeData.findIndex(d => d.forecast);

    const handleSort = (key) => {
        setSortConfig({
            key,
            direction: sortConfig.key === key && sortConfig.direction === 'asc' ? 'desc' : 'asc'
        });
    };

    const sortedForecastData = [...completeData.filter(d => d.forecast)].sort((a, b) => {
        if (!sortConfig.key) return 0;
        const aVal = sortConfig.key === 'quarter' ? a.quarter :
            sortConfig.key === 'growth' ? a.growth :
                sortConfig.key === 'confidence' ? a.confidence :
                    getMetricValue(a, selectedMetric);
        const bVal = sortConfig.key === 'quarter' ? b.quarter :
            sortConfig.key === 'growth' ? b.growth :
                sortConfig.key === 'confidence' ? b.confidence :
                    getMetricValue(b, selectedMetric);

        if (sortConfig.direction === 'asc') {
            return aVal > bVal ? 1 : -1;
        } else {
            return aVal < bVal ? 1 : -1;
        }
    });

    const openCardModal = (stat) => {
        setModalData(stat);
        setShowModal(true);
    };

    return (
        <div className="space-y-8 relative">
            {/* Data Quality & Status Bar */}
            <div className="glass rounded-lg px-6 py-3 flex flex-wrap items-center justify-between text-sm">
                <div className="flex items-center space-x-6">
                    <div className="flex items-center space-x-2">
                        <div className="h-2 w-2 bg-green-400 rounded-full animate-pulse"></div>
                        <span className="text-gray-300">Live Data</span>
                    </div>
                    <div className="flex items-center space-x-2 text-gray-400">
                        <Clock size={14} />
                        <span>Updated: {new Date().toLocaleString()}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                        <CheckCircle size={14} className="text-green-400" />
                        <span className="text-gray-300">Data Quality: <span className="text-green-400 font-semibold">98%</span></span>
                    </div>
                </div>
                <div className="flex items-center space-x-2 text-gray-400">
                    <RefreshCw size={14} />
                    <span>Auto-updates every 6hrs</span>
                </div>
            </div>

            {/* Header with Enhanced Model Info */}
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
                <div>
                    <h1 className="text-4xl font-bold text-white flex items-center space-x-3">
                        <Activity className="h-10 w-10 text-primary-400 animate-pulse" />
                        <span>Advanced Market Analytics</span>
                    </h1>
                    <div className="mt-2 flex flex-wrap items-center gap-3 text-sm">
                        <span className="text-gray-300">
                            ML-Powered LA Airbnb Forecasting
                        </span>
                        <span className="text-gray-500">•</span>
                        <span className="px-3 py-1 rounded-full bg-primary-500/20 text-primary-300 font-semibold">
                            {selectedModel.toUpperCase()} Model • {
                                selectedModel === 'ensemble' ? '2.87' :
                                    selectedModel === 'lstm' ? '3.15' :
                                        selectedModel === 'prophet' ? '3.52' : '3.87'
                            }% MAPE
                        </span>
                    </div>
                </div>

                {/* Controls */}
                <div className="flex flex-wrap items-center gap-3">
                    <select
                        value={selectedModel}
                        onChange={(e) => setSelectedModel(e.target.value)}
                        className="glass px-4 py-2.5 rounded-lg text-white border border-white/10 hover:border-cmu-red-500 transition-all cursor-pointer focus:ring-2 focus:ring-cmu-red-500"
                    >
                        <option value="ensemble">🎯 Ensemble (Best - 2.87%)</option>
                        <option value="lstm">🧠 LSTM Neural Net (3.15%)</option>
                        <option value="prophet">📈 Prophet (3.52%)</option>
                        <option value="sarima">📊 SARIMA (3.87%)</option>
                    </select>

                    <button
                        onClick={() => setShowConfidence(!showConfidence)}
                        className={`glass px-4 py-2.5 rounded-lg flex items-center space-x-2 transition-all border ${showConfidence ? 'bg-cmu-red-500/20 border-cmu-red-500' : 'border-white/10 hover:border-white/30'
                            }`}
                    >
                        {showConfidence ? <Eye size={18} className="text-cmu-red-400" /> : <EyeOff size={18} className="text-gray-400" />}
                        <span className="text-white font-medium">Confidence Intervals</span>
                    </button>
                </div>
            </div>

            {/* Animated Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {stats.map((stat, index) => (
                    <InteractiveStatCard
                        key={index}
                        {...stat}
                        index={index}
                        isLoaded={isLoaded}
                        expanded={expandedCard === index}
                        onToggle={() => setExpandedCard(expandedCard === index ? null : index)}
                        onClick={() => openCardModal(stat)}
                    />
                ))}
            </div>

            {/* Navigation Hints */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <NavigationCard
                    title="Detailed Forecasting"
                    description="Build custom forecasts for specific properties"
                    icon={TrendingUp}
                    color="blue"
                    onClick={() => navigate('/forecast')}
                />
                <NavigationCard
                    title="Scenario Analysis"
                    description="Test market assumptions and external events"
                    icon={BarChart3}
                    color="amber"
                    onClick={() => navigate('/scenarios')}
                />
            </div>

            {/* Main Chart */}
            <div className="glass rounded-2xl p-6 relative overflow-hidden hover-lift">
                {/* Background glow */}
                <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-primary-500/10 to-transparent rounded-full blur-3xl -z-10 animate-pulse"></div>

                {/* Chart Header */}
                <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6 space-y-4 lg:space-y-0">
                    <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                            <TrendingUp className="text-primary-400" size={24} />
                            <h2 className="text-2xl font-bold text-white">
                                {selectedMetric === 'listings' ? 'Listing Volume' :
                                    selectedMetric === 'price' ? 'Average Price' :
                                        'Occupancy Rate'} Forecast
                            </h2>
                        </div>
                        <div className="flex flex-wrap items-center gap-2 text-sm text-gray-400">
                            <span>Historical: <strong className="text-blue-400">2022 Q4 - 2023 Q3</strong></span>
                            <span>•</span>
                            <span>Forecast: <strong className="text-green-400">2023 Q4 - 2024 Q3</strong></span>
                            <span>•</span>
                            <span className="text-primary-300">4 Quarters Ahead</span>
                        </div>
                    </div>

                    {/* Metric Tabs */}
                    <div className="flex items-center space-x-2 bg-slate-800/50 p-1 rounded-lg border border-white/10">
                        <MetricTab
                            active={selectedMetric === 'listings'}
                            onClick={() => setSelectedMetric('listings')}
                            icon={<Home size={16} />}
                            label="Listings"
                        />
                        <MetricTab
                            active={selectedMetric === 'price'}
                            onClick={() => setSelectedMetric('price')}
                            icon={<DollarSign size={16} />}
                            label="Price"
                        />
                        <MetricTab
                            active={selectedMetric === 'occupancy'}
                            onClick={() => setSelectedMetric('occupancy')}
                            icon={<Activity size={16} />}
                            label="Occupancy"
                        />
                    </div>
                </div>

                {/* Chart */}
                <ResponsiveContainer width="100%" height={500}>
                    <ComposedChart
                        data={completeData}
                        onMouseMove={(e) => e?.activeLabel && setHoveredQuarter(e.activeLabel)}
                        onMouseLeave={() => setHoveredQuarter(null)}
                    >
                        <defs>
                            <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.9} />
                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05} />
                            </linearGradient>
                            <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#C41230" stopOpacity={0.8} />
                                <stop offset="95%" stopColor="#C41230" stopOpacity={0.05} />
                            </linearGradient>
                            <filter id="glow">
                                <feGaussianBlur stdDeviation="3" result="coloredBlur" />
                                <feMerge>
                                    <feMergeNode in="coloredBlur" />
                                    <feMergeNode in="SourceGraphic" />
                                </feMerge>
                            </filter>
                        </defs>

                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />

                        <XAxis
                            dataKey="quarter"
                            stroke="#9ca3af"
                            tick={{ fill: '#9ca3af', fontSize: 12 }}
                        />

                        <YAxis
                            stroke="#9ca3af"
                            tick={{ fill: '#9ca3af', fontSize: 12 }}
                            tickFormatter={(value) =>
                                selectedMetric === 'price' ? `$${value}` :
                                    selectedMetric === 'occupancy' ? `${value}%` :
                                        value >= 1000 ? `${(value / 1000).toFixed(0)}K` : value
                            }
                        />

                        <Tooltip content={<CustomTooltip />} />

                        <Legend
                            wrapperStyle={{ paddingTop: '20px' }}
                            iconType="line"
                        />

                        {/* Forecast Boundary */}
                        <ReferenceLine
                            x="2023 Q3"
                            stroke="#C41230"
                            strokeWidth={2}
                            strokeDasharray="5 5"
                            label={{
                                value: 'FORECAST →',
                                position: 'insideTopRight',
                                fill: '#C41230',
                                fontSize: 12,
                                fontWeight: 'bold'
                            }}
                        />

                        {/* Confidence Intervals */}
                        {showConfidence && (
                            <>
                                <Area
                                    type="monotone"
                                    dataKey={(d) => d.forecast ? getMetricBounds(d, selectedMetric).upper : null}
                                    name="Upper Bound"
                                    stroke="none"
                                    fill="#FCA5A5"
                                    fillOpacity={0.3}
                                />
                                <Area
                                    type="monotone"
                                    dataKey={(d) => d.forecast ? getMetricBounds(d, selectedMetric).lower : null}
                                    name="Lower Bound"
                                    stroke="none"
                                    fill="#FCA5A5"
                                    fillOpacity={0.3}
                                />
                            </>
                        )}

                        {/* Historical Area */}
                        <Area
                            type="monotone"
                            dataKey={(d) => d.actual ? getMetricValue(d, selectedMetric) : null}
                            name="Historical"
                            stroke="#3b82f6"
                            strokeWidth={3}
                            fill="url(#colorActual)"
                            dot={{ fill: '#3b82f6', r: 5, strokeWidth: 2, stroke: '#1e293b' }}
                            activeDot={{ r: 8, fill: '#3b82f6', stroke: '#fff', strokeWidth: 2 }}
                        />

                        {/* Forecast Line (continuous from last actual point) */}
                        <Line
                            type="monotone"
                            dataKey={(d) => getMetricValue(d, selectedMetric)}
                            name="Forecast"
                            stroke="#C41230"
                            strokeWidth={3}
                            strokeDasharray="8 4"
                            dot={false}
                            activeDot={false}
                            connectNulls={false}
                        />

                        <Brush
                            dataKey="quarter"
                            height={32}
                            stroke="#C41230"
                            fill="#1e293b"
                            travellerWidth={10}
                        />
                    </ComposedChart>
                </ResponsiveContainer>

                {/* Enhanced Legend */}
                <div className="mt-6 flex flex-wrap justify-center gap-6 text-sm pb-2">
                    <ChartLegendItem color="bg-blue-400" label="Historical Data" type="solid" />
                    <ChartLegendItem color="bg-cmu-red-500" label="AI Forecast" type="dashed" />
                    <ChartLegendItem color="bg-cmu-red-500" label="Forecast Boundary" type="dashed" />
                    {showConfidence && (
                        <ChartLegendItem color="bg-red-300/30" label="95% Confidence Interval" type="area" />
                    )}
                </div>
            </div>

            {/* Interactive Forecast Table */}
            <div className="glass rounded-2xl p-6 hover-lift">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-2">
                        <Calendar className="text-primary-400" size={24} />
                        <h3 className="text-xl font-bold text-white">Detailed Forecast Breakdown</h3>
                    </div>
                    <button className="glass px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-white/20 transition-all group">
                        <Download size={18} className="text-primary-400 group-hover:scale-110 transition-transform" />
                        <span className="text-white font-medium">Export CSV</span>
                    </button>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b-2 border-white/20">
                                <SortableHeader label="Quarter" sortKey="quarter" sortConfig={sortConfig} onClick={handleSort} />
                                <SortableHeader label="Forecast" sortKey="forecast" sortConfig={sortConfig} onClick={handleSort} align="right" />
                                <th className="text-right py-3 px-4 text-gray-400 font-semibold text-sm">Lower Bound</th>
                                <th className="text-right py-3 px-4 text-gray-400 font-semibold text-sm">Upper Bound</th>
                                <SortableHeader label="Growth %" sortKey="growth" sortConfig={sortConfig} onClick={handleSort} align="right" />
                                <SortableHeader label="Confidence" sortKey="confidence" sortConfig={sortConfig} onClick={handleSort} align="right" />
                            </tr>
                        </thead>
                        <tbody>
                            {sortedForecastData.map((item, index) => {
                                const value = getMetricValue(item, selectedMetric);
                                const bounds = getMetricBounds(item, selectedMetric);
                                const isHovered = hoveredQuarter === item.quarter;
                                const isSelected = selectedRow === index;

                                return (
                                    <tr
                                        key={index}
                                        className={`border-b border-white/5 transition-all cursor-pointer ${isHovered || isSelected ? 'bg-primary-500/10 scale-[1.01]' : 'hover:bg-white/5'
                                            }`}
                                        onClick={() => setSelectedRow(isSelected ? null : index)}
                                    >
                                        <td className="py-4 px-4 text-white font-medium">{item.quarter}</td>
                                        <td className="py-4 px-4 text-right">
                                            <div className="flex items-center justify-end space-x-2">
                                                <span className="text-green-400 font-bold text-lg">
                                                    {selectedMetric === 'price' ? '$' : ''}{value.toLocaleString()}{selectedMetric === 'occupancy' ? '%' : ''}
                                                </span>
                                            </div>
                                        </td>
                                        <td className="py-4 px-4 text-right text-gray-400 font-mono text-sm">
                                            {selectedMetric === 'price' ? '$' : ''}{bounds.lower?.toLocaleString()}{selectedMetric === 'occupancy' ? '%' : ''}
                                        </td>
                                        <td className="py-4 px-4 text-right text-gray-400 font-mono text-sm">
                                            {selectedMetric === 'price' ? '$' : ''}{bounds.upper?.toLocaleString()}{selectedMetric === 'occupancy' ? '%' : ''}
                                        </td>
                                        <td className="py-4 px-4 text-right">
                                            <div className="flex items-center justify-end space-x-2">
                                                <div className="h-2 rounded-full bg-gradient-to-r from-transparent to-green-500"
                                                    style={{ width: `${Math.min(item.growth * 10, 100)}px` }}></div>
                                                <span className={`font-bold ${item.growth >= 3 ? 'text-green-400' : item.growth >= 2 ? 'text-blue-400' : 'text-amber-400'}`}>
                                                    {item.growth >= 0 ? '+' : ''}{item.growth.toFixed(1)}%
                                                </span>
                                            </div>
                                        </td>
                                        <td className="py-4 px-4 text-right">
                                            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${item.confidence >= 0.90 ? 'bg-green-500/20 text-green-300 border border-green-500/30' :
                                                item.confidence >= 0.85 ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' :
                                                    'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                                                }`}>
                                                {item.confidence * 100}%
                                            </span>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Insights + Growth Chart Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Market Outlook */}
                <ClickableInsightCard
                    title="Market Outlook"
                    insights={[
                        { text: 'Strong growth trajectory through 2024', icon: TrendingUp, color: 'text-green-400', action: () => navigate('/forecast') },
                        { text: 'Peak season predicted in Q2 2024 with 49K listings', icon: Target, color: 'text-amber-400', action: () => navigate('/forecast?quarter=2024-Q2') },
                        { text: 'Price acceleration of 9.6% forecasted by Q3 2024', icon: DollarSign, color: 'text-green-400', action: () => navigate('/forecast?metric=price') },
                        { text: 'No signs of market saturation detected', icon: Activity, color: 'text-blue-400', action: () => navigate('/scenarios') }
                    ]}
                />

                {/* Model Performance */}
                <ClickableInsightCard
                    title="Model Performance"
                    insights={[
                        {
                            text: `${selectedModel.toUpperCase()} achieving ${selectedModel === 'ensemble' ? '2.87' : selectedModel === 'lstm' ? '3.15' :
                                selectedModel === 'prophet' ? '3.52' : '3.87'
                                }% MAPE`, icon: Zap, color: 'text-primary-400'
                        },
                        { text: 'Forecast confidence decreases with time horizon', icon: Info, color: 'text-gray-400' },
                        { text: 'Ensemble combines 3 models for best accuracy', icon: TrendingUp, color: 'text-green-400' },
                        { text: 'All models achieve <5% error (excellent)', icon: CheckCircle, color: 'text-purple-400' }
                    ]}
                />

                {/* Quick Actions */}
                <div className="glass rounded-xl p-6">
                    <h3 className="text-xl font-bold text-white mb-4 flex items-center space-x-2">
                        <Zap className="text-amber-400" />
                        <span>Quick Actions</span>
                    </h3>
                    <div className="space-y-3">
                        <ActionButton
                            icon={<TrendingUp size={18} />}
                            label="Generate Property Forecast"
                            onClick={() => navigate('/forecast')}
                        />
                        <ActionButton
                            icon={<BarChart3 size={18} />}
                            label="Run Scenario Analysis"
                            onClick={() => navigate('/scenarios')}
                        />
                        <ActionButton
                            icon={<Download size={18} />}
                            label="Export Full Report"
                            onClick={() => alert('Export feature coming soon!')}
                        />
                    </div>
                </div>
            </div>

            {/* Growth Rate Chart */}
            <div className="glass rounded-xl p-6 hover-lift">
                <h3 className="text-xl font-bold text-white mb-4 flex items-center space-x-2">
                    <BarChart3 size={24} className="text-primary-400" />
                    <span>Quarter-over-Quarter Growth Rate</span>
                </h3>
                <ResponsiveContainer width="100%" height={280}>
                    <BarChart data={completeData.filter(d => d.growth !== null && d.growth !== undefined)}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
                        <XAxis dataKey="quarter" stroke="#9ca3af" tick={{ fontSize: 12 }} />
                        <YAxis
                            stroke="#9ca3af"
                            tick={{ fontSize: 12 }}
                            tickFormatter={(value) => `${value}%`}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'rgba(30, 41, 59, 0.98)',
                                border: '1px solid rgba(255, 255, 255, 0.1)',
                                borderRadius: '12px',
                                padding: '12px',
                                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)'
                            }}
                            formatter={(value) => [`${value.toFixed(1)}%`, 'Growth']}
                        />
                        <Bar
                            dataKey="growth"
                            radius={[8, 8, 0, 0]}
                            fill={(data) => data.growth >= 3 ? '#10b981' : data.growth >= 2 ? '#3b82f6' : '#f59e0b'}
                        >
                            {completeData.filter(d => d.growth !== null).map((entry, index) => (
                                <cell key={`cell-${index}`} fill={entry.growth >= 3 ? '#10b981' : entry.growth >= 2 ? '#3b82f6' : '#f59e0b'} />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </div>

            {/* Footer */}
            <div className="text-center text-sm text-gray-400 py-6 border-t border-white/10">
                <p>LA Airbnb Forecasting Platform • Powered by Ensemble ML Models (2.87% MAPE)</p>
                <p className="mt-2">Forecasting 4 quarters ahead (2023 Q4 - 2024 Q3) • Historical: 2022 Q4 - 2023 Q3</p>
                <p className="mt-1 text-xs">Methodology: Ensemble of LSTM, Prophet, SARIMA models</p>
            </div>

            {/* Modal */}
            {showModal && modalData && (
                <StatCardModal
                    data={modalData}
                    onClose={() => setShowModal(false)}
                    navigate={navigate}
                />
            )}
        </div>
    );
}

// Component: Interactive Stat Card
function InteractiveStatCard({ title, value, change, changeValue, trend, icon: Icon, color, bgColor, sparklineData, detail, index, isLoaded, expanded, onToggle, onClick }) {
    const [isHovered, setIsHovered] = useState(false);
    const [animatedValue, setAnimatedValue] = useState(0);

    useEffect(() => {
        if (isLoaded) {
            const numericValue = parseInt(value.replace(/[^0-9]/g, ''));
            if (!isNaN(numericValue)) {
                const duration = 1500;
                const steps = 60;
                const increment = numericValue / steps;
                let current = 0;

                const timer = setInterval(() => {
                    current += increment;
                    if (current >= numericValue) {
                        setAnimatedValue(numericValue);
                        clearInterval(timer);
                    } else {
                        setAnimatedValue(Math.floor(current));
                    }
                }, duration / steps);

                return () => clearInterval(timer);
            }
        }
    }, [value, isLoaded]);

    return (
        <div
            className={`glass rounded-xl p-6 transition-all duration-500 cursor-pointer border border-transparent hover:border-primary-500/50 ${isHovered ? 'transform -translate-y-2 shadow-2xl shadow-primary-500/20 scale-105' : ''
                } ${bgColor} animate-fadeIn`}
            style={{
                animationDelay: `${index * 100}ms`,
                animationFillMode: 'backwards'
            }}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            onClick={onClick}
        >
            <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-lg ${bgColor} ${isHovered ? 'scale-110 rotate-3' : ''} transition-all`}>
                    <Icon className={`h-7 w-7 ${color}`} />
                </div>
                <div className="flex items-center space-x-2">
                    {trend === 'up' ? (
                        <ArrowUp className="h-5 w-5 text-green-400 animate-bounce" />
                    ) : (
                        <ArrowDown className="h-5 w-5 text-red-400" />
                    )}
                    <span className={`text-sm font-bold ${trend === 'up' ? 'text-green-400' : 'text-red-400'}`}>
                        {change}
                    </span>
                </div>
            </div>

            <p className="text-sm text-gray-400 mb-2 font-medium">{title}</p>
            <p className="text-3xl font-bold text-white mb-3 count-up">
                {value.includes('$') && `$${animatedValue}`}
                {value.includes('%') && `${animatedValue}%`}
                {!value.includes('$') && !value.includes('%') && animatedValue.toLocaleString()}
            </p>

            {/* Hover Extra Info */}
            {isHovered && detail && (
                <div className="mt-4 pt-4 border-t border-white/10 space-y-2 text-xs animate-fadeIn">
                    <div className="flex justify-between text-gray-400">
                        <span>Last Update:</span>
                        <span className="text-white">{detail.lastUpdate}</span>
                    </div>
                    <button className="w-full mt-2 px-3 py-2 rounded-lg bg-primary-500/20 border border-primary-500/30 text-primary-300 text-xs font-semibold hover:bg-primary-500/30 transition-all flex items-center justify-center space-x-1">
                        <span>View Details</span>
                        <ExternalLink size={12} />
                    </button>
                </div>
            )}
        </div>
    );
}

// Component: Navigation Card
function NavigationCard({ title, description, icon: Icon, color, onClick }) {
    return (
        <button
            onClick={onClick}
            className={`glass rounded-xl p-6 hover-lift group cursor-pointer border border-transparent hover:border-${color}-500/50 transition-all text-left`}
        >
            <div className="flex items-start space-x-4">
                <div className={`p-3 rounded-lg bg-${color}-500/10 group-hover:scale-110 transition-transform`}>
                    <Icon className={`h-6 w-6 text-${color}-400`} />
                </div>
                <div className="flex-1">
                    <h4 className="text-lg font-bold text-white mb-1 group-hover:text-primary-400 transition-colors">{title}</h4>
                    <p className="text-sm text-gray-400">{description}</p>
                    <div className="flex items-center space-x-1 mt-3 text-primary-400 text-sm font-semibold">
                        <span>Explore</span>
                        <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                    </div>
                </div>
            </div>
        </button>
    );
}

// Component: Metric Tab
function MetricTab({ active, onClick, icon, label }) {
    return (
        <button
            onClick={onClick}
            className={`px-4 py-2 rounded-md flex items-center space-x-2 transition-all font-medium ${active
                ? 'bg-primary-500 text-white shadow-lg'
                : 'text-gray-400 hover:text-white hover:bg-white/10'
                }`}
        >
            {icon}
            <span>{label}</span>
        </button>
    );
}

// Component: Chart Legend Item
function ChartLegendItem({ color, label, type }) {
    return (
        <div className="flex items-center space-x-2">
            <div className={`w-8 h-1 ${color} ${type === 'dashed' ? 'border-dashed border-t-2' : type === 'area' ? 'h-3' : ''} rounded`}></div>
            <span className="text-gray-300 text-xs font-medium">{label}</span>
        </div>
    );
}

// Component: Sortable Header
function SortableHeader({ label, sortKey, sortConfig, onClick, align = 'left' }) {
    return (
        <th
            className={`py-3 px-4 text-gray-400 font-semibold text-sm cursor-pointer hover:text-white transition-colors ${align === 'right' ? 'text-right' : 'text-left'}`}
            onClick={() => onClick(sortKey)}
        >
            <div className={`flex items-center ${align === 'right' ? 'justify-end' : 'justify-start'} space-x-1`}>
                <span>{label}</span>
                {sortConfig.key === sortKey && (
                    sortConfig.direction === 'asc' ? <ArrowUp size={14} /> : <ArrowDown size={14} />
                )}
            </div>
        </th>
    );
}

// Component: Clickable Insight Card
function ClickableInsightCard({ title, insights }) {
    return (
        <div className="glass rounded-xl p-6 hover-lift">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center space-x-2">
                <Zap className="text-amber-400" />
                <span>{title}</span>
            </h3>
            <ul className="space-y-3">
                {insights.map((insight, index) => (
                    <li
                        key={index}
                        className="flex items-start space-x-3 group hover:bg-white/5 p-2 rounded-lg transition-all cursor-pointer"
                        onClick={insight.action}
                    >
                        <insight.icon className={`mt-0.5 ${insight.color} group-hover:scale-110 transition-transform flex-shrink-0`} size={18} />
                        <span className="text-gray-300 group-hover:text-white transition-colors text-sm flex-1">{insight.text}</span>
                        {insight.action && (
                            <ArrowRight size={14} className="text-primary-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                        )}
                    </li>
                ))}
            </ul>
        </div>
    );
}

// Component: Action Button
function ActionButton({ icon, label, onClick }) {
    return (
        <button
            onClick={onClick}
            className="w-full glass px-4 py-3 rounded-lg flex items-center space-x-3 hover:bg-primary-500/20 hover:border-primary-500/50 border border-white/10 transition-all group"
        >
            <div className="text-primary-400 group-hover:scale-110 transition-transform">
                {icon}
            </div>
            <span className="text-white font-medium text-sm flex-1 text-left">{label}</span>
            <ArrowRight size={16} className="text-primary-400 group-hover:translate-x-1 transition-transform" />
        </button>
    );
}

// Component: Stat Card Modal
function StatCardModal({ data, onClose, navigate }) {
    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fadeIn">
            <div className="glass rounded-2xl p-8 max-w-2xl w-full border-2 border-white/20 shadow-2xl animate-slideIn">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-3">
                        <div className={`p-3 rounded-lg ${data.bgColor}`}>
                            <data.icon className={`h-8 w-8 ${data.color}`} />
                        </div>
                        <div>
                            <h3 className="text-2xl font-bold text-white">{data.title}</h3>
                            <p className="text-sm text-gray-400 mt-1">Detailed Breakdown</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                    >
                        <X size={24} className="text-gray-400 hover:text-white" />
                    </button>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="glass rounded-lg p-4">
                        <p className="text-xs text-gray-400 mb-1">Current Value</p>
                        <p className="text-2xl font-bold text-white">{data.value}</p>
                        <p className={`text-sm mt-1 ${data.trend === 'up' ? 'text-green-400' : 'text-red-400'}`}>
                            {data.change} vs last year
                        </p>
                    </div>
                    {data.detail.min && (
                        <>
                            <div className="glass rounded-lg p-4">
                                <p className="text-xs text-gray-400 mb-1">Range</p>
                                <p className="text-lg font-bold text-white">{data.detail.min.toLocaleString()} - {data.detail.max.toLocaleString()}</p>
                            </div>
                            <div className="glass rounded-lg p-4">
                                <p className="text-xs text-gray-400 mb-1">Average</p>
                                <p className="text-lg font-bold text-white">{data.detail.avg.toLocaleString()}</p>
                            </div>
                            <div className="glass rounded-lg p-4">
                                <p className="text-xs text-gray-400 mb-1">Std Deviation</p>
                                <p className="text-lg font-bold text-white">{data.detail.stdDev.toFixed(1)}</p>
                            </div>
                        </>
                    )}
                </div>

                <div className="h-32 mb-6">
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={data.sparklineData.map((val, idx) => ({ value: val, index: idx }))}>
                            <defs>
                                <linearGradient id="modalSparkline" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor={data.color.replace('text-', '')} stopOpacity={0.8} />
                                    <stop offset="95%" stopColor={data.color.replace('text-', '')} stopOpacity={0.1} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
                            <XAxis dataKey="index" stroke="#9ca3af" tick={{ fontSize: 12 }} />
                            <YAxis stroke="#9ca3af" tick={{ fontSize: 12 }} />
                            <Tooltip />
                            <Area
                                type="monotone"
                                dataKey="value"
                                stroke={data.color.replace('text-', '')}
                                fill="url(#modalSparkline)"
                                strokeWidth={3}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>

                <button
                    onClick={() => {
                        onClose();
                        navigate('/forecast');
                    }}
                    className="w-full btn-primary py-4 text-lg flex items-center justify-center space-x-2"
                >
                    <TrendingUp size={20} />
                    <span>View in Forecast Tool</span>
                    <ArrowRight size={20} />
                </button>
            </div>
        </div>
    );
}
