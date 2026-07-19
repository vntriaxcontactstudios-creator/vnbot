/**
 * VNBOT Web — App root.
 *
 * Sets up routing + global state providers.
 * Per docs/06 §3, routes are:
 *   /today (default) · /chat · /memory · /graph · /lists
 *   /agents · /skills · /integrations · /activity · /settings
 */

import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Sidebar } from '@/components/shell/Sidebar';
import { TodayPanel } from '@/routes/today/TodayPanel';
import { MemoryPanel } from '@/routes/memory/MemoryPanel';
import { ActivityPanel } from '@/routes/activity/ActivityPanel';
import { useUIStore } from '@/lib/store/ui';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 60_000,
    },
  },
});

// For GitHub Pages, BrowserRouter needs a basename matching the repo subpath.
// When VITE_DEMO_MODE=true, base is '/vnbot/' so basename is '/vnbot'.
const ROUTER_BASENAME = import.meta.env.VITE_DEMO_MODE === 'true' ? '/vnbot' : '/';

function App() {
  const { setOnline } = useUIStore();

  useEffect(() => {
    const update = () => setOnline(navigator.onLine);
    update();
    window.addEventListener('online', update);
    window.addEventListener('offline', update);
    return () => {
      window.removeEventListener('online', update);
      window.removeEventListener('offline', update);
    };
  }, [setOnline]);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter basename={ROUTER_BASENAME}>
        <div className="flex min-h-screen bg-vnbot-bg-0">
          <Sidebar />
          <main className="flex-1 min-w-0 flex flex-col">
            <Routes>
              <Route path="/" element={<Navigate to="/today" replace />} />
              <Route path="/today" element={<TodayPanel />} />
              <Route path="/chat" element={<TodayPanel />} />
              <Route path="/memory" element={<MemoryPanel />} />
              <Route path="/activity" element={<ActivityPanel />} />
              <Route
                path="*"
                element={
                  <div className="flex-1 flex items-center justify-center p-8 text-center">
                    <div>
                      <h2 className="font-display text-xl text-vnbot-text mb-2">
                        Route not implemented yet
                      </h2>
                      <p className="font-body text-sm text-vnbot-text-muted">
                        This route is part of Phase 0.5+. For now use /today.
                      </p>
                    </div>
                  </div>
                }
              />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
