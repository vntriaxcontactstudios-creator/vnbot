/**
 * VNBOT Web — Entry point.
 *
 * Mounts <App/> + registers Service Worker (for PWA in 0.2).
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './styles/global.css';
import { useUIStore } from './lib/store/ui';

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

// ─── PWA install prompt handler (Fase 0.8) ───
// Capture beforeinstallprompt so we can show a custom install button in the UI.
// Per PWA spec: the browser fires this event when it deems the app installable.
// We MUST call event.prompt() from a user gesture (click handler).
window.addEventListener('beforeinstallprompt', (e) => {
  // Prevent the mini-infobar from appearing on mobile
  e.preventDefault();
  // Stash the event so the UI can trigger it later via a button click.
  // Cast through unknown because BeforeInstallPromptEvent is non-standard.
  useUIStore.getState().setPwaInstallEvent(e as unknown as NonNullable<ReturnType<typeof useUIStore.getState>['pwaInstallEvent']>);
  console.info('[VNBOT] PWA install prompt captured — show install button');
});

window.addEventListener('appinstalled', () => {
  useUIStore.getState().setPwaInstallEvent(null);
  useUIStore.getState().setPwaInstalled(true);
  console.info('[VNBOT] PWA installed — hiding install button');
});

// Detect if already running as PWA (display-mode: standalone)
if (window.matchMedia('(display-mode: standalone)').matches) {
  useUIStore.getState().setPwaInstalled(true);
}



