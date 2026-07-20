/* VNBOT Service Worker — offline-first for shell + static assets.
 *
 * Strategy:
 *  - Precache the app shell on install
 *  - Cache-first for static assets (JS, CSS, fonts, images)
 *  - Network-first for API calls (always try fresh, fallback to cache)
 *  - Stale-while-revalidate for same-origin GETs
 *
 * Per ADR-0008: single-user local-first. The SW enables PWA install
 * and basic offline shell, but the app needs the API for real data.
 */

const CACHE_VERSION = "vnbot-v1";
const APP_SHELL = [
  "/",
  "/index.html",
  "/manifest.json",
  "/favicon.svg",
];

// ───────────────────────────────────────────────────────────────────────────
// Install: precache app shell
// ───────────────────────────────────────────────────────────────────────────
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => {
      return cache.addAll(APP_SHELL).catch((err) => {
        // Don't fail install if a single resource fails
        console.warn("[VNBOT SW] Precache partial failure:", err);
      });
    })
  );
  self.skipWaiting();
});

// ───────────────────────────────────────────────────────────────────────────
// Activate: clear old caches
// ───────────────────────────────────────────────────────────────────────────
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys
          .filter((key) => key.startsWith("vnbot-") && key !== CACHE_VERSION)
          .map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

// ───────────────────────────────────────────────────────────────────────────
// Fetch: route by request type
// ───────────────────────────────────────────────────────────────────────────
self.addEventListener("fetch", (event) => {
  const { request } = event;

  // Only handle GET
  if (request.method !== "GET") return;

  const url = new URL(request.url);

  // Skip cross-origin requests (e.g., Google Fonts CDN)
  if (url.origin !== self.location.origin) return;

  // ─── API calls: network-first ───
  if (url.pathname.startsWith("/api/")) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Cache successful GET responses for offline fallback
          if (response.ok && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_VERSION).then((cache) => {
              cache.put(request, clone).catch(() => {
                // Some responses (e.g., opaque) can't be cached; ignore
              });
            });
          }
          return response;
        })
        .catch(() => {
          // Network failed — try cache
          return caches.match(request).then((cached) => {
            return (
              cached ||
              new Response(
                JSON.stringify({
                  error: "offline",
                  message: "VNBOT está offline. Conéctate a internet para sincronizar.",
                }),
                {
                  status: 503,
                  headers: { "Content-Type": "application/json" },
                }
              )
            );
          });
        })
    );
    return;
  }

  // ─── Navigation requests: serve index.html (SPA) ───
  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const clone = response.clone();
          caches.open(CACHE_VERSION).then((cache) => cache.put("/index.html", clone));
          return response;
        })
        .catch(() => caches.match("/index.html"))
    );
    return;
  }

  // ─── Static assets: stale-while-revalidate ───
  event.respondWith(
    caches.match(request).then((cached) => {
      const fetchPromise = fetch(request)
        .then((response) => {
          if (response.ok && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_VERSION).then((cache) => cache.put(request, clone));
          }
          return response;
        })
        .catch(() => cached);
      return cached || fetchPromise;
    })
  );
});

// ───────────────────────────────────────────────────────────────────────────
// Message: allow page to trigger skipWaiting
// ───────────────────────────────────────────────────────────────────────────
self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
});
