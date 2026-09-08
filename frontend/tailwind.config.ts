import type { Config } from 'tailwindcss'

export default {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#6658DC',
        dark: '#111025',
        background: '#F5F7FA',
        surface: '#FFFFFF',
        'light-purple': '#E6E2FF',
        'pink-accent': '#F5D7F0',
        'blue-accent': '#DDF2F7',
        orange: '#FF6B2C',
        'main-text': '#141326',
        'muted-text': '#8C8B98',
        border: '#E8E8EE',
        'outer-preview': '#B8BEC6',
      },
    },
  },
  plugins: [],
} satisfies Config
