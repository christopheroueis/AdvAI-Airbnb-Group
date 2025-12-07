import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { TrendingUp, Home, BarChart3, Settings } from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import Dashboard from './pages/Dashboard';
import EnhancedDashboard from './pages/EnhancedDashboard';
import ForecastWizard from './pages/ForecastWizard';
import ScenarioSimulator from './pages/ScenarioSimulator';
import SplashScreen from './components/SplashScreen';
import './index.css';

// Animated Routes wrapper component
function AnimatedRoutes() {
    const location = useLocation();

    return (
        <AnimatePresence mode="wait">
            <Routes location={location} key={location.pathname}>
                <Route path="/" element={
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        transition={{ duration: 0.4, ease: "easeInOut" }}
                    >
                        <EnhancedDashboard />
                    </motion.div>
                } />
                <Route path="/basic" element={
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        transition={{ duration: 0.4, ease: "easeInOut" }}
                    >
                        <Dashboard />
                    </motion.div>
                } />
                <Route path="/forecast" element={
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        transition={{ duration: 0.4, ease: "easeInOut" }}
                    >
                        <ForecastWizard />
                    </motion.div>
                } />
                <Route path="/scenarios" element={
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        transition={{ duration: 0.4, ease: "easeInOut" }}
                    >
                        <ScenarioSimulator />
                    </motion.div>
                } />
            </Routes>
        </AnimatePresence>
    );
}


function App() {
    const [showSplash, setShowSplash] = useState(true); // Always show splash screen on reload

    // Splash screen now dismisses only when user clicks Begin or Skip button
    // No auto-dismiss timer needed

    const handleSplashComplete = () => {
        setShowSplash(false);
        // We don't save to sessionStorage anymore so it shows every time
    };

    return (
        <>
            <Router>
                {!showSplash && (
                    <div className="min-h-screen" style={{ background: 'linear-gradient(135deg, #1B2838 0%, #0f1923 100%)' }}>
                        {/* CMU x Airbnb Header */}
                        <nav className="glass border-b-2 border-cmu-red-500 sticky top-0 z-50">
                            <div className="max-w-7xl mx-auto px-6 lg:px-8">
                                <div className="flex justify-between items-center h-24">
                                    {/* Logo Container */}
                                    <div className="flex items-center mr-8">
                                        <Link to="/" className="flex items-center space-x-6">
                                            {/* Animated Logo with Red Pulsing Glow */}
                                            <div className="relative">
                                                {/* Animated background glow */}
                                                <div className="absolute inset-0 blur-2xl opacity-40 bg-gradient-to-r from-red-600 to-pink-600 animate-pulse" />

                                                <motion.img
                                                    src="/finallogo-cmu-x-airbnb.png"
                                                    alt="CMU X Airbnb Partnership"
                                                    className="relative h-12 sm:h-14 md:h-16 w-auto object-contain cursor-pointer"
                                                    style={{
                                                        imageRendering: '-webkit-optimize-contrast',
                                                        WebkitFontSmoothing: 'antialiased',
                                                        display: 'block'
                                                    }}
                                                    whileHover={{ scale: 1.05 }}
                                                    animate={{
                                                        filter: [
                                                            "drop-shadow(0 0 10px rgba(196, 18, 48, 0.5))",
                                                            "drop-shadow(0 0 20px rgba(196, 18, 48, 0.8))",
                                                            "drop-shadow(0 0 10px rgba(196, 18, 48, 0.5))"
                                                        ]
                                                    }}
                                                    transition={{
                                                        filter: {
                                                            duration: 2,
                                                            repeat: Infinity,
                                                            ease: "easeInOut"
                                                        },
                                                        scale: {
                                                            duration: 0.3
                                                        }
                                                    }}
                                                />
                                            </div>
                                        </Link>
                                    </div>

                                    {/* Navigation & Status */}
                                    <div className="flex items-center space-x-4">
                                        {/* Navigation Links */}
                                        <div className="hidden md:flex space-x-2">
                                            <NavLink to="/" icon={<Home size={18} />}>
                                                Dashboard
                                            </NavLink>
                                            <NavLink to="/forecast" icon={<TrendingUp size={18} />}>
                                                Forecasting
                                            </NavLink>
                                            <NavLink to="/scenarios" icon={<BarChart3 size={18} />}>
                                                Scenarios
                                            </NavLink>
                                        </div>

                                        {/* Status Indicator */}
                                        <div className="glass px-3 py-2 rounded-lg border border-cmu-red-500/20">
                                            <div className="flex items-center space-x-2">
                                                <div className="h-2 w-2 bg-green-400 rounded-full animate-pulse-cmu"></div>
                                                <span className="text-xs text-gray-300">API Connected</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </nav>

                        {/* Main Content */}
                        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                            <AnimatedRoutes />
                        </main>

                        {/* CMU x Airbnb Footer */}
                        <footer className="mt-16 border-t border-cmu-red-500/20 py-8">
                            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                                <div className="flex flex-col items-center space-y-4">
                                    <img
                                        src="/logo-cmu-x-airbnb.png"
                                        alt="CMU x Airbnb"
                                        className="h-8 w-auto opacity-60 hover:opacity-100 transition-opacity"
                                    />
                                    <p className="text-center text-gray-400 text-sm">
                                        LA Airbnb Forecasting Platform • Powered by Ensemble ML Models (2.87% MAPE)
                                    </p>
                                    <p className="text-center text-gray-500 text-xs">
                                        Carnegie Mellon University × Airbnb Research Partnership
                                    </p>
                                </div>
                            </div>
                        </footer>
                    </div>
                )}
            </Router>

            <AnimatePresence>
                {showSplash && <SplashScreen onComplete={handleSplashComplete} />}
            </AnimatePresence>
        </>
    );
}

// NavLink Component
function NavLink({ to, icon, children }) {
    const location = useLocation();
    const isActive = location.pathname === to;

    return (
        <Link
            to={to}
            className={`relative flex items-center space-x-2 px-4 py-2 rounded-t-lg transition-all duration-300 ${isActive
                ? 'text-white border-b-2 border-cmu-red-500'
                : 'text-gray-300 hover:text-white border-b-2 border-transparent hover:border-cmu-red-500/30'
                }`}
        >
            {icon}
            <span className="font-medium">{children}</span>
        </Link>
    );
}

export default App;
