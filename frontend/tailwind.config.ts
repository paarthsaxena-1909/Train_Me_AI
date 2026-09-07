import type { Config } from 'tailwindcss'

export default {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#102a43',
        mist: '#f0f4f8',
        coral: '#f97068',
      },
    },
  },
  plugins: [],
} satisfies Config
