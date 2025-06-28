import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
  plugins: [svelte()],
  server: {
    host: true,
    port: 3000,
    proxy: {
      '/api/': {
        target: 'http://fb-backend:8000',
        changeOrigin: true,
        secure: false,
      }
    },
    
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
})
