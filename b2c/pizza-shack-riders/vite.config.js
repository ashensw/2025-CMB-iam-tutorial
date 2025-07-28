import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: process.env.PORT ? parseInt(process.env.PORT) : 5174, // Different port from main pizza-shack app to avoid conflicts
    open: true,
    host: true // Allow external connections
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  },
  define: {
    // Ensure process.env is not accessed directly in client code
    'process.env': {}
  }
})