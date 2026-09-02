import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    watch: {
      ignored: ['**/__pycache__/**', '**/dataset/**', '**/static/**', '**/.git/**', '**/*.csv']
    }
  }
})
