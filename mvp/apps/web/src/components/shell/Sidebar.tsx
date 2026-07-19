/**
 * VNBOT Web — Sidebar navigation.
 *
 * Main navigation with 10 items per docs/06 §7.1:
 * HOY · CHAT · MEMORIA · GRAFO · LISTAS · AGENTES · SKILLS · INTEGRACIONES · ACTIVIDAD · AJUSTES
 */

import { NavLink } from 'react-router-dom';
import { MascotStateView } from '@vnbot/pixelart';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';
import { useUIStore } from '@/lib/store/ui';

const NAV_ITEMS = [
  { to: '/today', label: 'HOY', icon: '◐', agent: 'beacon' as const },
  { to: '/chat', label: 'CHAT', icon: '✦', agent: 'chat_assistant' as const },
  { to: '/memory', label: 'MEMORIA', icon: '◈', agent: 'archivist' as const },
  { to: '/graph', label: 'GRAFO', icon: '⌬', agent: 'archivist' as const },
  { to: '/lists', label: 'LISTAS', icon: '☰', agent: 'beacon' as const },
  { to: '/agents', label: 'AGENTES', icon: '⚑', agent: 'guardian' as const },
  { to: '/skills', label: 'SKILLS', icon: '⚙', agent: 'forge' as const },
  { to: '/integrations', label: 'INTEGRACIONES', icon: '⇄', agent: 'sentinel' as const },
  { to: '/activity', label: 'ACTIVIDAD', icon: '⏱', agent: 'sentinel' as const },
  { to: '/settings', label: 'AJUSTES', icon: '✦', agent: 'guardian' as const },
];

export function Sidebar() {
  const { activeAgent, mascotState, sidebarOpen, setSidebarOpen } = useUIStore();

  return (
    <>
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-vnbot-void/80 z-30 md:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      <aside
        className={`
          fixed md:sticky top-0 left-0 z-40
          w-64 h-screen
          bg-vnbot-bg-1 border-r border-vnbot-line-soft
          flex flex-col
          transition-transform duration-200
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}
        aria-label="Main navigation"
      >
        {/* Logo + Mascot */}
        <div className="p-4 border-b border-vnbot-line-soft flex items-center gap-3">
          <ErrorBoundary fallback={<div className="w-12 h-12 bg-vnbot-panel-0 border border-vnbot-line-soft" />}>
            <MascotStateView
              agent={activeAgent}
              state={mascotState}
              size={48}
              interactive={false}
            />
          </ErrorBoundary>
          <div>
            <div className="font-pixel text-xs text-vnbot-cyan">VNBOT</div>
            <div className="font-mono text-[10px] text-vnbot-text-muted">v0.1.0</div>
          </div>
        </div>

        {/* Nav items */}
        <nav className="flex-1 overflow-y-auto py-2">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) => `
                flex items-center gap-3 px-4 py-3
                font-mono text-xs uppercase tracking-wider
                transition-colors
                ${isActive
                  ? 'bg-vnbot-panel-0 text-vnbot-cyan border-l-2 border-vnbot-cyan'
                  : 'text-vnbot-text-muted hover:bg-vnbot-panel-0/50 hover:text-vnbot-text'
                }
              `}
            >
              <span className="text-base" aria-hidden="true">
                {item.icon}
              </span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Footer — connection status */}
        <div className="p-4 border-t border-vnbot-line-soft text-[10px] font-mono text-vnbot-text-muted">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-vnbot-green inline-block" aria-hidden="true" />
            <span>Connected</span>
          </div>
          <div className="mt-1">LLM: glm-4.6</div>
          <div className="mt-1">TZ: America/Caracas</div>
        </div>
      </aside>
    </>
  );
}
