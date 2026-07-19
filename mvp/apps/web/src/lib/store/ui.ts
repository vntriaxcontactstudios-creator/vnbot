/**
 * VNBOT Web — UI session store.
 *
 * Zustand store for global UI state: current route, mascot state, theme.
 * Server state (chat responses, reminders, etc.) is handled by TanStack Query.
 *
 * IMPORTANT: do NOT persist masterKey/plaintext here (ADR-0002).
 * Only persist: theme, locale, last_used_agent (preferences).
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { AgentId, MascotState } from '@vnbot/pixelart';

interface UIState {
  // Mascot state — driven by operations stream
  mascotState: MascotState;
  activeAgent: AgentId;
  setMascotState: (state: MascotState) => void;
  setActiveAgent: (agent: AgentId) => void;

  // Theme
  theme: 'dark' | 'amber' | 'violet' | 'high-contrast';
  setTheme: (theme: UIState['theme']) => void;

  // Locale + timezone
  locale: string;
  timezone: string;
  setTimezone: (tz: string) => void;

  // Sidebar (mobile)
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;

  // Inspector drawer
  inspectorOpen: boolean;
  setInspectorOpen: (open: boolean) => void;

  // Online status
  isOnline: boolean;
  setOnline: (online: boolean) => void;

  // LLM degraded mode (when LLM unavailable, falling back to heuristics)
  llmDegraded: boolean;
  setLlmDegraded: (degraded: boolean) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      // Mascot
      mascotState: 'idle',
      activeAgent: 'guardian',
      setMascotState: (mascotState) => set({ mascotState }),
      setActiveAgent: (activeAgent) => set({ activeAgent }),

      // Theme
      theme: 'dark',
      setTheme: (theme) => set({ theme }),

      // Locale + timezone
      locale: 'es',
      timezone: 'America/Caracas',
      setTimezone: (timezone) => set({ timezone }),

      // Sidebar
      sidebarOpen: false,
      toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
      setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),

      // Inspector
      inspectorOpen: false,
      setInspectorOpen: (inspectorOpen) => set({ inspectorOpen }),

      // Online
      isOnline: true,
      setOnline: (isOnline) => set({ isOnline }),

      // LLM degraded
      llmDegraded: false,
      setLlmDegraded: (llmDegraded) => set({ llmDegraded }),
    }),
    {
      name: 'vnbot-ui-store',
      // Only persist preferences — never persist runtime state
      partialize: (state) => ({
        theme: state.theme,
        locale: state.locale,
        timezone: state.timezone,
        activeAgent: state.activeAgent,
      }),
    },
  ),
);
