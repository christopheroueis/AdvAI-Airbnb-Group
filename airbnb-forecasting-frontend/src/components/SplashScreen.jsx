import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

const SplashScreen = ({ onComplete }) => {
    const [showContent, setShowContent] = useState(false);

    useEffect(() => {
        // Delay content appearance for dramatic effect
        setTimeout(() => setShowContent(true), 300);
    }, []);

    return (
        <div className="fixed inset-0 bg-gradient-to-br from-[#0a0e1a] via-[#1a1f35] to-[#0a0e1a] flex flex-col items-center justify-center overflow-hidden">

            {/* Video Background */}
            <div className="absolute inset-0 z-0">
                <video
                    autoPlay
                    loop
                    muted
                    playsInline
                    className="absolute inset-0 w-full h-full object-cover"
                    style={{
                        filter: 'brightness(0.6)',
                        opacity: 0.5
                    }}
                >
                    <source src="/LAvideo.mp4" type="video/mp4" />
                </video>
                {/* Dark overlay for better contrast */}
                <div className="absolute inset-0 bg-black/40" />
            </div>

            {/* Floating Particles */}
            <FloatingParticles />

            {/* Animated Grid Background */}
            <div className="absolute inset-0 opacity-10 z-1">
                <div className="absolute inset-0" style={{
                    backgroundImage: 'linear-gradient(rgba(196, 18, 48, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(196, 18, 48, 0.1) 1px, transparent 1px)',
                    backgroundSize: '50px 50px'
                }} />
            </div>

            {/* Skip Button */}
            <button
                onClick={onComplete}
                className="absolute top-8 right-8 text-gray-500 hover:text-white text-sm transition-colors duration-300 z-10"
            >
                Skip intro →
            </button>

            {showContent && (
                <motion.div
                    className="relative z-10 flex flex-col items-center"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.8 }}
                >

                    {/* Logo with Enhanced Glow */}
                    <motion.div
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ duration: 1, ease: "easeOut" }}
                        className="relative mb-12"
                    >
                        {/* Animated background glow */}
                        <div className="absolute inset-0 blur-3xl opacity-30 bg-gradient-to-r from-red-600 to-pink-600 animate-pulse" />

                        {/* Logo */}
                        <img
                            src="/finallogo-cmu-x-airbnb.png"
                            alt="CMU X Airbnb Partnership"
                            className="relative z-10 w-[500px] sm:w-[600px] h-auto object-contain"
                            style={{
                                filter: 'drop-shadow(0 20px 60px rgba(196, 18, 48, 0.4))'
                            }}
                        />
                    </motion.div>

                    {/* Animated Tagline - Word by Word Fade */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 1, duration: 0.8 }}
                        className="mb-8"
                    >
                        <AnimatedTagline text="Predicting the Future of LA's Home-Sharing Market" />
                    </motion.div>

                    {/* Stats Ticker */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 1.5, duration: 0.6 }}
                        className="flex gap-8 sm:gap-12 mb-12 text-center flex-wrap justify-center px-4"
                    >
                        <StatCard value="2.87%" label="Model MAPE" color="red" delay={1.7} />
                        <div className="w-px bg-gray-700 hidden sm:block" />
                        <StatCard value="44.6K" label="Active Listings" color="cyan" delay={1.9} />
                        <div className="w-px bg-gray-700 hidden sm:block" />
                        <StatCard value="+12.3%" label="Annual Growth" color="green" delay={2.1} />
                    </motion.div>

                    {/* Enhanced CTA Button */}
                    <motion.button
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 2.3, duration: 0.6 }}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={onComplete}
                        className="group relative px-14 sm:px-16 py-5 sm:py-6 bg-gradient-to-r from-red-700 via-red-600 to-red-700 text-white text-xl sm:text-2xl font-bold rounded-full overflow-hidden shadow-2xl hover:shadow-red-600/50 transition-shadow duration-300"
                    >
                        {/* Animated gradient sweep */}
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 group-hover:opacity-20 translate-x-[-100%] group-hover:translate-x-[100%] transition-all duration-1000" />

                        <span className="relative z-10 flex items-center gap-3 sm:gap-4">
                            Click Here to Begin
                            <motion.svg
                                className="w-6 h-6 sm:w-7 sm:h-7"
                                animate={{ x: [0, 5, 0] }}
                                transition={{ repeat: Infinity, duration: 1.5, ease: "easeInOut" }}
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                            </motion.svg>
                        </span>
                    </motion.button>

                    {/* Partnership Badges */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 2.8 }}
                        className="flex flex-wrap gap-4 sm:gap-6 mt-10 sm:mt-12 items-center justify-center text-gray-500 text-xs sm:text-sm px-4"
                    >
                        <span className="flex items-center gap-2">
                            <CheckCircleIcon className="w-4 h-4 text-green-500" />
                            CMU Verified
                        </span>
                        <span className="flex items-center gap-2">
                            <ShieldIcon className="w-4 h-4 text-blue-500" />
                            Airbnb Official Data
                        </span>
                        <span className="flex items-center gap-2">
                            <ZapIcon className="w-4 h-4 text-yellow-500" />
                            Real-Time Updates
                        </span>
                    </motion.div>

                    {/* Footer */}
                    <motion.p
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 3.2 }}
                        className="absolute bottom-8 text-gray-600 text-xs sm:text-sm text-center px-4"
                    >
                        Powered by Ensemble ML Models
                    </motion.p>
                </motion.div>
            )}
        </div>
    );
};

// Animated Tagline Component - Word by Word Fade
const AnimatedTagline = ({ text }) => {
    const words = text.split(" ");

    return (
        <h2 className="text-2xl sm:text-3xl font-light text-white/90 tracking-wide flex flex-wrap justify-center gap-2 text-center px-4">
            {words.map((word, i) => (
                <motion.span
                    key={i}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1, duration: 0.5 }}
                >
                    {word}
                </motion.span>
            ))}
        </h2>
    );
};

// Stats Card Component
const StatCard = ({ value, label, color, delay }) => {
    const colorMap = {
        red: 'text-red-500',
        cyan: 'text-cyan-400',
        green: 'text-green-400'
    };

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay, duration: 0.5 }}
            className="min-w-[100px]"
        >
            <div className={`text-3xl sm:text-4xl font-bold ${colorMap[color]}`}>{value}</div>
            <div className="text-xs sm:text-sm text-gray-400 mt-1">{label}</div>
        </motion.div>
    );
};

// Floating Particles Component
const FloatingParticles = () => {
    return (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
            {[...Array(20)].map((_, i) => (
                <motion.div
                    key={i}
                    className="absolute w-2 h-2 bg-red-500/20 rounded-full"
                    style={{
                        left: `${Math.random() * 100}%`,
                        top: `${Math.random() * 100}%`,
                    }}
                    animate={{
                        y: [0, -100, 0],
                        opacity: [0, 1, 0],
                    }}
                    transition={{
                        duration: 3 + Math.random() * 2,
                        repeat: Infinity,
                        delay: Math.random() * 3,
                        ease: "easeInOut"
                    }}
                />
            ))}
        </div>
    );
};

// Simple Icon Components
const CheckCircleIcon = ({ className }) => (
    <svg className={className} fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
    </svg>
);

const ShieldIcon = ({ className }) => (
    <svg className={className} fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
    </svg>
);

const ZapIcon = ({ className }) => (
    <svg className={className} fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
    </svg>
);

export default SplashScreen;
