import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const backendPort = process.env.DENNY_BACKEND_PORT || '8002';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: Number(process.env.PORT || 5175),
    strictPort: true,
    proxy: {
      '/api': `http://127.0.0.1:${backendPort}`,
      '/static': `http://127.0.0.1:${backendPort}`,
    },
  },
});
