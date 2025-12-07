/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // CMU x Airbnb Brand Colors
                'cmu-red': {
                    50: '#fef2f2',
                    100: '#fee2e2',
                    200: '#fecaca',
                    300: '#fca5a5',
                    400: '#f87171',
                    500: '#C41230', // CMU Tartan Red (Primary Brand)
                    600: '#b30f28',
                    700: '#9c0c22',
                    800: '#7f0a1c',
                    900: '#660816',
                },
                'airbnb-rausch': '#FF5A5F', // Airbnb accent
                'cmu-gold': '#B4975A', // Premium features
                primary: {
                    50: '#fef2f2',
                    100: '#fee2e2',
                    200: '#fecaca',
                    300: '#fca5a5',
                    400: '#E31B48',
                    500: '#C41230', // CMU Red as primary
                    600: '#b30f28',
                    700: '#9c0c22',
                    800: '#7f0a1c',
                    900: '#660816',
                },
                navy: {
                    50: '#f8fafc',
                    100: '#f1f5f9',
                    200: '#e2e8f0',
                    300: '#cbd5e1',
                    400: '#94a3b8',
                    500: '#64748b',
                    600: '#475569',
                    700: '#334155',
                    800: '#1e293b',
                    900: '#1B2838', // Deep Navy (Main BG)
                }
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
        },
    },
    plugins: [],
}
