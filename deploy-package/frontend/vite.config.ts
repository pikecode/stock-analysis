import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    host: '127.0.0.1',
    port: 8005,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8006',
        changeOrigin: true,
      },
    },
  },
})
