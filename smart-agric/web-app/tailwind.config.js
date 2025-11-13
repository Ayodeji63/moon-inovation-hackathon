/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './pages/**/*.{js,ts,jsx,tsx,mdx}',
        './components/**/*.{js,ts,jsx,tsx,mdx}',
        './app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                primary: '#49ec13',
                'background-light': '#f6f8f6',
                'background-dark': '#152210',
            },
            fontFamily: {
                display: ['Plus Jakarta Sans', 'Noto Sans', 'sans-serif'],
            },
            borderRadius: {
                DEFAULT: '1rem',
                lg: '2rem',
                xl: '3rem',
                full: '9999px',
            },
        },
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/container-queries')
    ],
}