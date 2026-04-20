/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // KORP AI brand — navy + cyan (จากโลโก้จริง)
        brand: {
          navy: {
            50:  '#F2F5FB',
            100: '#E2E8F4',
            200: '#C5CFE6',
            300: '#8FA0CC',
            400: '#5B72AE',
            500: '#3C7CFF',  // accent blue (จาก path สี #3C7CFF)
            600: '#1E3A6F',
            700: '#142A52',
            800: '#0F2A55',  // mid navy
            900: '#0B1830',  // deep navy (สีหลัก K)
          },
          cyan: {
            100: '#EAFBFE',
            200: '#A9F2FF',
            300: '#7BE8FF',
            400: '#26D7F6',  // primary cyan
            500: '#0EB7D8',
            600: '#0790AA',
          },
          ink: {
            50:  '#F8FAFC',
            100: '#F1F5F9',
            200: '#E2E8F0',
            300: '#CBD5E1',
            400: '#94A3B8',
            500: '#64748B',
            600: '#475569',
            700: '#334155',
            800: '#1E293B',
            900: '#0F172A',
          },
          bg: '#F7FAFF', // off-white จาก rect bg ของโลโก้
        },
      },
      fontFamily: {
        sans: ['Inter', '"IBM Plex Sans Thai Looped"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['Inter', '"IBM Plex Sans Thai Looped"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        card: '0 1px 2px rgba(11, 24, 48, 0.05), 0 12px 32px rgba(11, 24, 48, 0.08)',
        soft: '0 1px 3px rgba(11, 24, 48, 0.06)',
        glow: '0 0 0 1px rgba(38, 215, 246, 0.15), 0 8px 32px rgba(38, 215, 246, 0.18)',
      },
      borderRadius: {
        xl2: '1.25rem',
      },
      maxWidth: {
        content: '76rem',
      },
      keyframes: {
        'beam-drift': {
          '0%, 100%': { transform: 'translate3d(0,0,0) rotate(var(--r,0deg))' },
          '50%':      { transform: 'translate3d(2%, -1%, 0) rotate(var(--r,0deg))' },
        },
        'fade-up': {
          '0%':   { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        'beam-drift': 'beam-drift 14s ease-in-out infinite',
        'fade-up':    'fade-up 0.6s ease-out both',
      },
    },
  },
  plugins: [],
};
