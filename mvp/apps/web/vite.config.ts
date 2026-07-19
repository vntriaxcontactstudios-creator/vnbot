/// <reference types="vitest/config" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { fileURLToPath, URL } from 'node:url';

// https://vitejs.dev/config/
export default defineConfig({
  // For GitHub Pages deployment, base must match the repo subpath.
  // When building for GH Pages (VITE_DEMO_MODE=true), use '/vnbot/' as base.
  // For local dev or self-hosted, use '/' (default).
  base: process.env.VITE_DEMO_MODE === 'true' ? '/vnbot/' : '/',
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
