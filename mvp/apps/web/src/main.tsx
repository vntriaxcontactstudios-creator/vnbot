/**
 * VNBOT Web — Entry point.
 *
 * Mounts <App/> + registers Service Worker (for PWA in 0.2).
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './styles/global.css';

const root = document.getElementById('root');
if (!root) {
  throw new Error('Root element not found');
}

createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>,
);

// ─── Register Service Worker (PWA — ADR-0008 local-first) ───
// Only register in production builds (dev server doesn't serve /sw.js cleanly)
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/sw.js', { scope: '/' })
      .then((reg) => {
        // Check for updates every hour
        setInterval(() => reg.update().catch(() => {}), 60 * 60 * 1000);
      })
      .catch((err) => {
        // SW registration is best-effort — never block the app
        console.warn('[VNBOT] SW registration failed:', err);
      });

    // Allow page to trigger skipWaiting on new SW
    let refreshing = false;
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      if (refreshing) return;
      refreshing = true;
      window.location.reload();
    });
  });
}

