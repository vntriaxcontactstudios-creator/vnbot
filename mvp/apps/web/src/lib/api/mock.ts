/**
 * VNBOT Web — Mock data for GitHub Pages demo.
 *
 * When VITE_DEMO_MODE=true, the app uses this mock data instead of calling
 * the backend. This allows the demo to run on GitHub Pages without a server.
 *
 * Per docs/04 §5 (Phase 1 — GitHub Pages demo):
 * - No API keys, no real emails, no user data on server
 * - Label simulated parts
 * - Must load without backend
 */

import type { ChatResponse, ConfirmResponse, MemoryNode, MemoryListResponse, MemorySearchResponse } from './client';

const NOW = new Date();
const TOMORROW = new Date(NOW.getTime() + 24 * 60 * 60 * 1000);
const NEXT_WEEK = new Date(NOW.getTime() + 7 * 24 * 60 * 60 * 1000);

export const MOCK_MEMORIES: MemoryNode[] = [
  {
    id: 'mock-mem-1',
    workspace_id: 'default',
    type: 'note',
    label: 'Wifi de la oficina',
    content: 'El wifi de la oficina es vnbot123. Cambia cada mes.',
    tags: [],
    sensitivity: 'PERSONAL',
    status: 'active',
    provenance: 'explicit_user_input',
    authority: 'user_confirmed',
    confidence: 1.0,
    valid_from: null,
    valid_until: null,
    created_at: new Date(NOW.getTime() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(NOW.getTime() - 3 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'mock-mem-2',
    workspace_id: 'default',
    type: 'event',
    label: 'Cumpleaños Daniel',
    content: 'El cumpleaños de Daniel es el 15 de agosto. Le gustan los libros de ciencia ficción.',
    tags: [],
    sensitivity: 'PERSONAL',
    status: 'active',
    provenance: 'explicit_user_input',
    authority: 'user_confirmed',
    confidence: 1.0,
    valid_from: null,
    valid_until: null,
    created_at: new Date(NOW.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(NOW.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'mock-mem-3',
    workspace_id: 'default',
    type: 'preference',
    label: 'Preferencia café',
    content: 'Prefiero el café sin azúcar, con un poco de leche de almendras.',
    tags: [],
    sensitivity: 'PERSONAL',
    status: 'active',
    provenance: 'explicit_user_input',
    authority: 'user_confirmed',
    confidence: 1.0,
    valid_from: null,
    valid_until: null,
    created_at: new Date(NOW.getTime() - 14 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(NOW.getTime() - 14 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'mock-mem-4',
    workspace_id: 'default',
    type: 'note',
    label: 'Password del router',
    content: 'La contraseña del router de casa es vnbot2024. No compartirla.',
    tags: [],
    sensitivity: 'SENSITIVE',
    status: 'active',
    provenance: 'explicit_user_input',
    authority: 'user_confirmed',
    confidence: 1.0,
    valid_from: null,
    valid_until: null,
    created_at: new Date(NOW.getTime() - 21 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(NOW.getTime() - 21 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'mock-mem-5',
    workspace_id: 'default',
    type: 'task',
    label: 'Proyecto VNBOT',
    content: 'El proyecto VNBOT usa React 19 + Vite + FastAPI + SQLite. Stack: Tailwind 4, Atropos.js, anime.js.',
    tags: [],
    sensitivity: 'PERSONAL',
    status: 'active',
    provenance: 'explicit_user_input',
    authority: 'user_confirmed',
    confidence: 1.0,
    valid_from: null,
    valid_until: null,
    created_at: new Date(NOW.getTime() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(NOW.getTime() - 1 * 24 * 60 * 60 * 1000).toISOString(),
  },
];

export const MOCK_REMINDERS = [
  {
    id: 'mock-rem-1',
    title: 'Revisar VNBOT',
    due_at: TOMORROW.toISOString(),
    timezone: 'America/Caracas',
    recurrence_frequency: 'none',
    status: 'active',
    priority: 'normal',
  },
  {
    id: 'mock-rem-2',
    title: 'Llamar al banco',
    due_at: NEXT_WEEK.toISOString(),
    timezone: 'America/Caracas',
    recurrence_frequency: 'none',
    status: 'active',
    priority: 'high',
  },
];

export const MOCK_OPERATIONS = [
  {
    id: 'mock-op-1',
    type: 'create_reminder',
    status: 'succeeded',
    risk_level: 'low',
    agent_id: 'heuristic',
    input_ref: 'a1b2c3d4e5f6...',
    created_at: new Date(NOW.getTime() - 2 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'mock-op-2',
    type: 'create_memory',
    status: 'succeeded',
    risk_level: 'low',
    agent_id: 'heuristic',
    input_ref: 'f6e5d4c3b2a1...',
    created_at: new Date(NOW.getTime() - 5 * 60 * 60 * 1000).toISOString(),
  },
];

// ─── Mock API responses ───

export function mockChat(text: string): ChatResponse {
  // Simple heuristic simulation for demo
  const lowerText = text.toLowerCase();

  if (lowerText.includes('recuérdame') || lowerText.includes('recuerdame') || lowerText.includes('avísame')) {
    const title = text.replace(/^(.*?)(recuérdame|recuerdame|avísame|avisa)\s*(que|de)?/i, '').trim() || 'Recordatorio';
    return {
      operation_id: `mock-op-${Date.now()}`,
      intent: 'create_reminder',
      parsed: true,
      confidence: 0.9,
      proposal_reminder: {
        title: title.charAt(0).toUpperCase() + title.slice(1),
        due_at: TOMORROW.toISOString(),
        timezone: 'America/Caracas',
        recurrence_frequency: 'none',
        recurrence_interval: 1,
        priority: 'normal',
        channel: 'mock',
        confidence: 0.9,
      },
      proposal_memory: null,
      requires_confirmation: true,
      expires_at: new Date(NOW.getTime() + 5 * 60 * 1000).toISOString(),
      notes: ['Demo mode — heuristic parse (mock)'],
      error: null,
      suggestion: null,
    };
  }

  if (lowerText.includes('guarda') || lowerText.includes('anota') || lowerText.includes('memoriza')) {
    const content = text.replace(/^(.*?)(guarda que|anota|memoriza|apunta que)\s*/i, '').trim() || 'Memoria';
    return {
      operation_id: `mock-op-${Date.now()}`,
      intent: 'create_memory',
      parsed: true,
      confidence: 0.85,
      proposal_reminder: null,
      proposal_memory: {
        content: content.charAt(0).toUpperCase() + content.slice(1),
        memory_type: 'note',
        tags: [],
        confidence: 0.85,
      },
      requires_confirmation: true,
      expires_at: new Date(NOW.getTime() + 5 * 60 * 1000).toISOString(),
      notes: ['Demo mode — heuristic parse (mock)'],
      error: null,
      suggestion: null,
    };
  }

  // Unknown
  return {
    operation_id: `mock-op-${Date.now()}`,
    intent: 'unknown',
    parsed: false,
    confidence: 0.0,
    proposal_reminder: null,
    proposal_memory: null,
    requires_confirmation: false,
    expires_at: new Date(NOW.getTime() + 5 * 60 * 1000).toISOString(),
    notes: [],
    error: 'No se detectó una intención reconocida',
    suggestion: 'Demo mode — escribe "Recuérdame..." o "Guarda que..." para ver el flujo.',
  };
}

export function mockConfirm(): ConfirmResponse {
  return {
    operation_id: `mock-op-${Date.now()}`,
    status: 'succeeded',
    entity_id: `mock-entity-${Date.now()}`,
    entity_type: 'reminder',
    next_due_at: TOMORROW.toISOString(),
    error: null,
  };
}

export function mockListMemories(): MemoryListResponse {
  return {
    items: MOCK_MEMORIES,
    total: MOCK_MEMORIES.length,
    limit: 100,
    offset: 0,
  };
}

export function mockSearchMemories(query: string): MemorySearchResponse {
  const lowerQuery = query.toLowerCase();
  const results = MOCK_MEMORIES.filter(
    (m) =>
      m.label.toLowerCase().includes(lowerQuery) ||
      m.content.toLowerCase().includes(lowerQuery),
  ).map((m) => ({
    id: m.id,
    label: m.label,
    content_snippet: m.content.replace(
      new RegExp(`(${query})`, 'gi'),
      '<mark>$1</mark>',
    ),
    type: m.type,
    sensitivity: m.sensitivity,
    rank: -0.5,
    created_at: m.created_at,
  }));

  return {
    items: results,
    total: results.length,
    query,
    limit: 20,
    offset: 0,
  };
}

export const IS_DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true' || import.meta.env.DEV === false;
