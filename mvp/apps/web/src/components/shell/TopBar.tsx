/**
 * VNBOT Web — TopBar.
 *
 * Top bar with: sidebar toggle (mobile), search, mascot state indicator, settings,
 * PWA install button.
 */

import { useUIStore } from '@/lib/store/ui';
import { apiClient } from '@/lib/api/client';

interface TopBarProps {
  title: string;
}

export function TopBar({ title }: TopBarProps) {
  const { toggleSidebar, mascotState, pwaInstallEvent, pwaInstalled, setPwaInstallEvent, setPwaInstalled } = useUIStore();
  const isDemo = apiClient.isDemoMode();

  const handleInstallClick = async () => {
    if (!pwaInstallEvent) return;
    await pwaInstallEvent.prompt();
    const choice = await pwaInstallEvent.userChoice;
    if (choice.outcome === 'accepted') {
      setPwaInstalled(true);
    }
    setPwaInstallEvent(null);
  };

  return (
    <header className="sticky top-0 z-20 bg-vnbot-bg-0/95 backdrop-blur-sm border-b border-vnbot-line-soft">
      <div className="flex items-center justify-between px-4 py-3 gap-4">
        {/* Mobile menu button */}
        <button
          type="button"
          onClick={toggleSidebar}
          className="md:hidden w-10 h-10 flex items-center justify-center text-vnbot-cyan hover:bg-vnbot-panel-0"
          aria-label="Toggle navigation"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path d="M3 5h14v2H3V5zm0 4h14v2H3V9zm0 4h14v2H3v-2z" />
          </svg>
        </button>

        {/* Page title */}
        <h1 className="font-display text-base text-vnbot-text uppercase tracking-wider">
          {title}
        </h1>

        {/* Right side — mascot state + actions */}
        <div className="flex items-center gap-3 ml-auto">
          {/* PWA install button (only shown when prompt is available and not installed) */}
          {pwaInstallEvent && !pwaInstalled && (
            <button
              type="button"
              onClick={handleInstallClick}
              className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 bg-vnbot-cyan text-vnbot-bg-0 font-mono text-[10px] uppercase tracking-wider hover:bg-vnbot-cyan/90"
              aria-label="Instalar VNBOT como app"
              title="Instalar VNBOT como aplicación"
            >
              ⬇ INSTALAR
            </button>
          )}

          {/* Demo mode badge */}
          {isDemo && (
            <div
              className="hidden sm:flex items-center gap-1.5 px-2 py-1 border border-vnbot-amber/50 bg-vnbot-amber/10 text-vnbot-amber"
              title="Demo mode — using mock data, no backend connection"
            >
              <span className="font-mono text-[10px] uppercase tracking-wider">
                DEMO
              </span>
            </div>
          )}

          {/* Mascot state badge */}
          <div
            className="hidden md:flex items-center gap-2 px-3 py-1.5 border border-vnbot-line-soft bg-vnbot-panel-0"
            role="status"
          >
            <span
              className="w-2 h-2 bg-vnbot-cyan animate-visor-pulse"
              aria-hidden="true"
            />
            <span className="font-mono text-[10px] text-vnbot-text-muted uppercase">
              {mascotState.replace(/_/g, ' ')}
            </span>
          </div>

          {/* Trigger scheduler button (dev only — not in demo) */}
          {!isDemo && (
            <button
              type="button"
              onClick={() => {
                fetch(`${import.meta.env.VITE_API_BASE_URL?.replace('/api/v1', '') ?? 'http://localhost:8000'}/scheduler/trigger`, {
                  method: 'POST',
                }).catch(() => {});
              }}
              className="hidden md:flex items-center px-3 py-1.5 border border-vnbot-amber/40 text-vnbot-amber font-mono text-[10px] uppercase hover:bg-vnbot-amber/10"
              aria-label="Trigger scheduler (dev)"
            >
              ⚡ TRIGGER
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
