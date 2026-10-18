import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/voice': 'http://127.0.0.1:8000',
      '/bhav': 'http://127.0.0.1:8000',
      '/logbook': 'http://127.0.0.1:8000',
      '/glut': 'http://127.0.0.1:8000',
      '/tractor': 'http://127.0.0.1:8000',
      '/power': 'http://127.0.0.1:8000',
      '/water': 'http://127.0.0.1:8000',
      '/radar': 'http://127.0.0.1:8000',
      '/doctor': 'http://127.0.0.1:8000',
      '/bazaar': 'http://127.0.0.1:8000',
      '/suraksha': 'http://127.0.0.1:8000',
      '/shock': 'http://127.0.0.1:8000',
      '/sim': 'http://127.0.0.1:8000',
    }
  }
});