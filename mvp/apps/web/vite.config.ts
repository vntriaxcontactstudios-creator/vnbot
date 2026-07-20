/// <reference types="vitest/config" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { fileURLToPath, URL } from 'node:url';

// https://vitejs.dev/config/
export default defineConfig({
  // Base path: '/' for root domains (Netlify, self-hosted), '/vnbot/' for GitHub Pages subpath.
  // VITE_BASE_PATH takes priority; falls back to demo-mode heuristic.
  // - Set VITE_BASE_PATH='/' explicitly for Netlify root domain
  // - Set VITE_BASE_PATH='/vnbot/' for GitHub Pages (repo subpath)
  base: process.env.VITE_BASE_PATH ?? (process.env.VITE_DEMO_MODE === 'true' ? '/' : '/'),
  plugins: [react()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      '@vnbot/ui': fileURLToPath(new URL('../../packages/ui/src', import.meta.url)),
      '@vnbot/pixelart': fileURLToPath(new URL('../../packages/pixelart/src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    target: 'es2022',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'state': ['zustand', '@tanstack/react-query'],
          'pixelart': ['@vnbot/pixelart', 'atropos', 'animejs'],
        },
      },
    },
  },
});
