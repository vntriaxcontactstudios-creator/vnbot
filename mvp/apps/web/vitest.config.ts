/**
 * VNBOT Web — Vitest configuration (separate from vite.config.ts).
 *
 * Test config lives here to avoid TypeScript overload conflicts with Vite's
 * UserConfig type.
 */

import { defineConfig } from 'vitest/config';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test-setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/**/*.{ts,tsx}'],
      exclude: ['src/**/*.d.ts', 'src/test-setup.ts'],
      thresholds: {
        lines: 60,
        functions: 60,
        branches: 60,
        statements: 60,
      },
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      '@vnbot/ui': fileURLToPath(new URL('../../packages/ui/src', import.meta.url)),
      '@vnbot/pixelart': fileURLToPath(new URL('../../packages/pixelart/src', import.meta.url)),
    },
  },
});
