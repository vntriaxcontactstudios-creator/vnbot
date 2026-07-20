/**
 * VNBOT Web — API client.
 *
 * Typed fetch client for the VNBOT backend.
 */

interface ApiConfig {
  baseUrl: string;
}

const DEFAULT_CONFIG: ApiConfig = {
  baseUrl: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1',
};

// ──────────────────────────────────────────────────────────────────────────────
// Types (mirror services/api/app/schemas/chat.py)
// ──────────────────────────────────────────────────────────────────────────────

export interface ProposalReminder {
  title: string;
  due_at: string;
  timezone: string;
  recurrence_frequency: string;
  recurrence_interval: number;
  priority: string;
  channel: string;
  confidence: number;
}

export interface ProposalMemory {
  content: string;
  memory_type: string;
  tags: string[];
  confidence: number;
}

export interface ChatResponse {
  operation_id: string;
  intent: string;
  parsed: boolean;
  confidence: number;
  proposal_reminder: ProposalReminder | null;
  proposal_memory: ProposalMemory | null;
  requires_confirmation: boolean;
  expires_at: string | null;
  notes: string[];
  error: string | null;
  suggestion: string | null;
}

export interface ConfirmResponse {
  operation_id: string;
  status: string;
  entity_id: string | null;
  entity_type: string | null;
  next_due_at: string | null;
  error: string | null;
}

export interface HealthResponse {
  status: 'ok' | 'degraded' | 'down';
  version: string;
  timestamp: string;
  checks: Record<string, string>;
}

// ──────────────────────────────────────────────────────────────────────────────
// Memory types (mirror services/api/app/schemas/memories.py)
// ──────────────────────────────────────────────────────────────────────────────

export interface MemoryNode {
  id: string;
  workspace_id: string;
  type: string;
  label: string;
  content: string;
  tags: string[];
  sensitivity: string;
  status: string;
  provenance: string;
  authority: string;
  confidence: number;
  valid_from: string | null;
  valid_until: string | null;
  created_at: string;
  updated_at: string;
}

export interface MemoryListResponse {
  items: MemoryNode[];
  total: number;
  limit: number;
  offset: number;
}

export interface MemorySearchResult {
  id: string;
  label: string;
  content_snippet: string;
  type: string;
  sensitivity: string;
  rank: number;
  created_at: string;
}

export interface MemorySearchResponse {
  items: MemorySearchResult[];
  total: number;
  query: string;
  limit: number;
  offset: number;
}

// ──────────────────────────────────────────────────────────────────────────────
// Reminder types
// ──────────────────────────────────────────────────────────────────────────────

export interface ReminderItem {
  id: string;
  title: string;
  timezone: string;
  recurrence_frequency: string;
  recurrence_interval: number;
  priority: string;
  channel: string;
  status: string;
  next_due_at: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  cancelled_at: string | null;
}

export interface ReminderListResponse {
  items: ReminderItem[];
  total: number;
  upcoming: number;
  overdue: number;
  completed: number;
}

// ──────────────────────────────────────────────────────────────────────────────
// Graph types
// ──────────────────────────────────────────────────────────────────────────────

export interface GraphNode {
  id: string;
  type: string;
  label: string;
  sensitivity: string;
  status: string;
  created_at: string;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relation: string;
  confidence: number;
  created_at: string;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  total_nodes: number;
  total_edges: number;
}

export const RELATION_TYPES = [
  'KNOWS', 'WORKS_ON', 'RELATED_TO', 'DEPENDS_ON',
  'REMINDER_FOR', 'HAPPENS_AT', 'PREFERS', 'SUPERSEDES',
  'CONTRADICTS', 'DERIVED_FROM', 'ASSIGNED_TO', 'MENTIONED_IN',
  'LOCATED_AT',
] as const;

// ──────────────────────────────────────────────────────────────────────────────
// Client
// ──────────────────────────────────────────────────────────────────────────────

class ApiClient {
  private config: ApiConfig;
  private demoMode: boolean;

  constructor(config: Partial<ApiConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    // Demo mode: when VITE_DEMO_MODE=true OR when running on GitHub Pages (no backend)
    this.demoMode = import.meta.env.VITE_DEMO_MODE === 'true';
  }

  isDemoMode(): boolean {
    return this.demoMode;
  }

  async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.config.baseUrl}${path}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'X-Workspace-Id': 'default',
      ...(options.headers as Record<string, string>),
    };

    const response = await fetch(url, { ...options, headers });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(errorBody.detail ?? `API error ${response.status}`);
    }

    return response.json() as Promise<T>;
  }

  async chat(text: string, timezone = 'America/Caracas'): Promise<ChatResponse> {
    if (this.demoMode) {
      // Dynamic import to avoid loading mock data in production builds
      const { mockChat } = await import('./mock');
      // Simulate network delay
      await new Promise((r) => setTimeout(r, 400));
      return mockChat(text);
    }
    return this.request<ChatResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify({ text, timezone }),
    });
  }

  async confirmOperation(
    operationId: string,
    edits?: Record<string, unknown>,
  ): Promise<ConfirmResponse> {
    if (this.demoMode) {
      const { mockConfirm } = await import('./mock');
      await new Promise((r) => setTimeout(r, 500));
      return mockConfirm();
    }
    return this.request<ConfirmResponse>(`/chat/operations/${operationId}/confirm`, {
      method: 'POST',
      body: JSON.stringify({ edits }),
    });
  }

  async getHealth(): Promise<HealthResponse> {
    const url = this.config.baseUrl.replace('/api/v1', '') + '/healthz';
    const response = await fetch(url);
    return response.json();
  }

  async getDependencies(): Promise<HealthResponse> {
    const url = this.config.baseUrl.replace('/api/v1', '') + '/dependencies';
    const response = await fetch(url);
    return response.json();
  }

  async triggerScheduler(): Promise<{
    triggered: boolean;
    generated_occurrences: number;
    delivered_notifications: number;
    timestamp: string;
  }> {
    const url = this.config.baseUrl.replace('/api/v1', '') + '/scheduler/trigger';
    const response = await fetch(url, { method: 'POST' });
    return response.json();
  }

  // ─── Memories ───

  async listMemories(params?: {
    limit?: number;
    offset?: number;
    type?: string;
  }): Promise<MemoryListResponse> {
    if (this.demoMode) {
      const { mockListMemories } = await import('./mock');
      await new Promise((r) => setTimeout(r, 300));
      return mockListMemories();
    }
    const searchParams = new URLSearchParams();
    if (params?.limit) searchParams.set('limit', String(params.limit));
    if (params?.offset) searchParams.set('offset', String(params.offset));
    if (params?.type) searchParams.set('type', params.type);
    const qs = searchParams.toString();
    return this.request<MemoryListResponse>(`/memories${qs ? '?' + qs : ''}`);
  }

  async getMemory(id: string): Promise<MemoryNode> {
    return this.request<MemoryNode>(`/memories/${id}`);
  }

  async createMemory(data: {
    label: string;
    content: string;
    type?: string;
    sensitivity?: string;
  }): Promise<MemoryNode> {
    return this.request<MemoryNode>('/memories', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateMemory(
    id: string,
    data: { label?: string; content?: string; sensitivity?: string },
  ): Promise<MemoryNode> {
    return this.request<MemoryNode>(`/memories/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteMemory(id: string): Promise<void> {
    if (this.demoMode) {
      await new Promise((r) => setTimeout(r, 200));
      return;
    }
    await this.request<void>(`/memories/${id}`, { method: 'DELETE' });
  }

  async searchMemories(query: string, limit = 20): Promise<MemorySearchResponse> {
    if (this.demoMode) {
      const { mockSearchMemories } = await import('./mock');
      await new Promise((r) => setTimeout(r, 300));
      return mockSearchMemories(query);
    }
    return this.request<MemorySearchResponse>('/memories/search', {
      method: 'POST',
      body: JSON.stringify({ query, limit }),
    });
  }

  // ─── Reminders ───

  async listReminders(): Promise<ReminderListResponse> {
    if (this.demoMode) {
      const { MOCK_REMINDERS } = await import('./mock');
      await new Promise((r) => setTimeout(r, 300));
      return {
        items: MOCK_REMINDERS.map((r) => ({
          id: r.id,
          title: r.title,
          timezone: r.timezone,
          recurrence_frequency: r.recurrence_frequency,
          recurrence_interval: 1,
          priority: r.priority,
          channel: 'mock',
          status: r.status,
          next_due_at: r.due_at,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          completed_at: null,
          cancelled_at: null,
        })),
        total: MOCK_REMINDERS.length,
        upcoming: MOCK_REMINDERS.length,
        overdue: 0,
        completed: 0,
      };
    }
    return this.request<ReminderListResponse>('/reminders');
  }

  async completeReminder(id: string): Promise<ReminderItem> {
    return this.request<ReminderItem>(`/reminders/${id}/complete`, { method: 'POST' });
  }

  async snoozeReminder(id: string, hours: number): Promise<ReminderItem> {
    return this.request<ReminderItem>(`/reminders/${id}/snooze`, {
      method: 'POST',
      body: JSON.stringify({ hours }),
    });
  }

  async cancelReminder(id: string): Promise<ReminderItem> {
    return this.request<ReminderItem>(`/reminders/${id}/cancel`, { method: 'POST' });
  }

  // ─── Graph ───

  async getGraph(limit = 50): Promise<GraphResponse> {
    if (this.demoMode) {
      return {
        nodes: [
          { id: 'mock-node-1', type: 'note', label: 'Wifi oficina', sensitivity: 'PERSONAL', status: 'active', created_at: new Date().toISOString() },
          { id: 'mock-node-2', type: 'event', label: 'Cumpleaños Daniel', sensitivity: 'PERSONAL', status: 'active', created_at: new Date().toISOString() },
          { id: 'mock-node-3', type: 'preference', label: 'Preferencia café', sensitivity: 'PERSONAL', status: 'active', created_at: new Date().toISOString() },
          { id: 'mock-node-4', type: 'note', label: 'Proyecto VNBOT', sensitivity: 'PERSONAL', status: 'active', created_at: new Date().toISOString() },
        ],
        edges: [
          { id: 'mock-edge-1', source: 'mock-node-2', target: 'mock-node-1', relation: 'RELATED_TO', confidence: 0.8, created_at: new Date().toISOString() },
          { id: 'mock-edge-2', source: 'mock-node-4', target: 'mock-node-3', relation: 'RELATED_TO', confidence: 0.6, created_at: new Date().toISOString() },
          { id: 'mock-edge-3', source: 'mock-node-2', target: 'mock-node-3', relation: 'PREFERS', confidence: 0.5, created_at: new Date().toISOString() },
        ],
        total_nodes: 4,
        total_edges: 3,
      };
    }
    return this.request<GraphResponse>(`/graph?limit=${limit}`);
  }

  async createEdge(source: string, target: string, relation: string, confidence = 1.0): Promise<{ id: string; source: string; target: string; relation: string; confidence: number; created_at: string }> {
    return this.request('/graph/edges', {
      method: 'POST',
      body: JSON.stringify({ source_node_id: source, target_node_id: target, relation_type: relation, confidence }),
    });
  }

  async deleteEdge(id: string): Promise<void> {
    await this.request<void>(`/graph/edges/${id}`, { method: 'DELETE' });
  }
}

export const apiClient = new ApiClient();
