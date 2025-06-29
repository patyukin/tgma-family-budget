import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
  plugins: [svelte()],
  server: {
    host: true,
    port: 3000,
    proxy: {
      '/api/': {
        target: process.env.VITE_APP_API_URL,
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
