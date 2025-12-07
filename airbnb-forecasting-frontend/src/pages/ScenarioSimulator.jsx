import { useState, useEffect } from 'react';
import { Zap, Play, AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react';
import { forecastAPI } from '../api/client';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function ScenarioSimulator() {
    const [scenarios, setScenarios] = useState([]);
    const [selectedScenario, setSelectedScenario] = useState(null);
    const [simulationResult, setSimulationResult] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadScenarios();
    }, []);

    const loadScenarios = async () => {
        try {
            const response = await forecastAPI.getScenarios();
            setScenarios(response.data);
            setSelectedScenario(response.data[1]?.id); // Default to baseline
        } catch (error) {
            console.error('Error loading scenarios:', error);
        }
    };

    const runSimulation = async () => {
        if (!selectedScenario) return;

        setLoading(true);
        try {
            const response = await forecastAPI.simulateScenario({
                scenario_id: selectedScenario,
                horizon: 4,
                base_model: 'ensemble'
            });
            setSimulationResult(response.data);
        } catch (error) {
            console.error('Error running simulation:', error);
        } finally {
            setLoading(false);
        }
    };

    const getScenarioIcon = (id) => {
        const icons = {
            optimistic: <TrendingUp className="text-green-400" />,
            pessimistic: <TrendingDown className="text-red-400" />,
            baseline: <Zap className="text-blue-400" />,
        };
        return icons[id] || <AlertTriangle className="text-amber-400" />;
    };

    const chartData = simulationResult ?
        simulationResult.periods.map((period, index) => ({
            period,
            baseline: simulationResult.base_forecast[index],
            adjusted: simulationResult.adjusted_forecast[index],
            impact: simulationResult.total_impact_pct[index]
        })) : [];

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="text-center space-y-4">
                <Zap className="h-12 w-12 text-amber-400 mx-auto" />
                <h1 className="text-4xl font-bold text-white">
                    Scenario Simulator
                </h1>
                <p className="text-xl text-gray-300">
                    Explore how external events impact the Airbnb market
                </p>
            </div>

            {/* Scenario Selection */}
            <div className="glass rounded-xl p-6">
                <h2 className="text-2xl font-bold text-white mb-6">
                    Select Scenario
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {scenarios.map((scenario) => (
                        <button
                            key={scenario.id}
                            onClick={() => setSelectedScenario(scenario.id)}
                            className={`p-6 rounded-lg border-2 transition-all text-left ${selectedScenario === scenario.id
                                    ? 'border-primary-500 bg-primary-500/20'
                                    : 'border-gray-700 bg-slate-800/50 hover:border-gray-600'
                                }`}
                        >
                            <div className="flex items-start space-x-3">
                                <div className="mt-1">{getScenarioIcon(scenario.id)}</div>
                                <div className="flex-1">
                                    <h3 className="font-bold text-white mb-1">
                                        {scenario.name}
                                    </h3>
                                    <p className="text-sm text-gray-400">
                                        {scenario.description}
                                    </p>
                                </div>
                            </div>
                        </button>
                    ))}
                </div>

                <button
                    onClick={runSimulation}
                    disabled={loading || !selectedScenario}
                    className="mt-6 px-8 py-4 rounded-lg bg-primary-500 hover:bg-primary-600 text-white font-bold text-lg transition-all disabled:opacity-50 flex items-center space-x-2 mx-auto"
                >
                    {loading ? (
                        <>
                            <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-white"></div>
                            <span>Running Simulation...</span>
                        </>
                    ) : (
                        <>
                            <Play size={24} />
                            <span>Run Simulation</span>
                        </>
                    )}
                </button>
            </div>

            {/* Results */}
            {simulationResult && (
                <div className="glass rounded-xl p-6 space-y-6">
                    <h2 className="text-2xl font-bold text-white">
                        {simulationResult.scenario_name} Results
                    </h2>

                    {/* Impact Summary */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="glass rounded-lg p-4">
                            <p className="text-sm text-gray-400">Avg Impact</p>
                            <p className={`text-3xl font-bold mt-2 ${simulationResult.summary.avg_impact_pct >= 0
                                    ? 'text-green-400'
                                    : 'text-red-400'
                                }`}>
                                {simulationResult.summary.avg_impact_pct >= 0 ? '+' : ''}
                                {simulationResult.summary.avg_impact_pct.toFixed(1)}%
                            </p>
                        </div>
                        <div className="glass rounded-lg p-4">
                            <p className="text-sm text-gray-400">Worst Case</p>
                            <p className="text-3xl font-bold text-red-400 mt-2">
                                {simulationResult.summary.max_negative_impact_pct.toFixed(1)}%
                            </p>
                        </div>
                        <div className="glass rounded-lg p-4">
                            <p className="text-sm text-gray-400">Best Case</p>
                            <p className="text-3xl font-bold text-green-400 mt-2">
                                +{simulationResult.summary.max_positive_impact_pct.toFixed(1)}%
                            </p>
                        </div>
                    </div>

                    {/* Chart */}
                    <div className="mt-8">
                        <ResponsiveContainer width="100%" height={400}>
                            <LineChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                <XAxis dataKey="period" stroke="#9ca3af" />
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
                                <Line
                                    type="monotone"
                                    dataKey="baseline"
                                    stroke="#3b82f6"
                                    strokeWidth={2}
                                    name="Baseline Forecast"
                                    strokeDasharray="5 5"
                                />
                                <Line
                                    type="monotone"
                                    dataKey="adjusted"
                                    stroke={simulationResult.summary.avg_impact_pct >= 0 ? '#10b981' : '#ef4444'}
                                    strokeWidth={3}
                                    name="Scenario Forecast"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Events Included */}
                    <div className="glass rounded-lg p-4">
                        <h3 className="font-bold text-white mb-3">Events Included</h3>
                        <div className="flex flex-wrap gap-2">
                            {simulationResult.summary.events_included.map((event, index) => (
                                <span
                                    key={index}
                                    className="px-3 py-1 rounded-full bg-primary-500/20 text-primary-300 text-sm"
                                >
                                    {event.replace('_', ' ').toUpperCase()}
                                </span>
                            ))}
                            {simulationResult.summary.events_included.length === 0 && (
                                <span className="text-gray-400 text-sm">No external events</span>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Event Legend */}
            <div className="glass rounded-xl p-6">
                <h2 className="text-xl font-bold text-white mb-4">
                    Event Types
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {[
                        { name: 'COVID-19', impact: '-60%', color: 'red' },
                        { name: 'Wildfires', impact: '-30%', color: 'orange' },
                        { name: 'Extreme Weather', impact: '-15%', color: 'yellow' },
                        { name: '2028 Olympics', impact: '+50%', color: 'green' },
                        { name: 'Economic Recession', impact: '-40%', color: 'red' },
                        { name: 'Regulatory Change', impact: '-25%', color: 'amber' },
                    ].map((event, index) => (
                        <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50">
                            <span className="text-gray-300">{event.name}</span>
                            <span className={`font-bold text-${event.color}-400`}>
                                {event.impact}
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
