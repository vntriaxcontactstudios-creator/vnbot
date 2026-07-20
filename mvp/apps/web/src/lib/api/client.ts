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
// Briefing types
// ──────────────────────────────────────────────────────────────────────────────

export interface BriefingResponse {
  date: string;
  greeting: string;
  pending_reminders: number;
  overdue_reminders: number;
  upcoming_reminders: { id: string; title: string; due_at: string | null }[];
  recent_memories: { id: string; label: string; type: string }[];
  summary: string;
  generated_at: string;
}

// ──────────────────────────────────────────────────────────────────────────────
// Skills types (Hermes ADR-0009 Fase 0.7)
// ──────────────────────────────────────────────────────────────────────────────

export interface SkillSummary {
  id: string;
  name: string;
  description: string;
  status: 'draft' | 'active' | 'deprecated' | 'archived';
  origin: 'hermes' | 'user' | 'imported';
  version: number;
  confidence: number;
  use_count: number;
  last_used_at: string | null;
  created_at: string;
}

export interface SkillDetail extends SkillSummary {
  body_markdown: string;
  triggers_json: Record<string, unknown>;
  updated_at: string;
}

export interface SkillListResponse {
  items: SkillSummary[];
  total: number;
}

export interface CreateSkillRequest {
  name: string;
  description?: string;
  body_markdown: string;
  triggers_json?: Record<string, unknown>;
  status?: 'draft' | 'active' | 'deprecated' | 'archived';
  tags?: string[];
}

export interface PatchSkillRequest {
  name?: string;
  description?: string;
  body_markdown?: string;
  triggers_json?: Record<string, unknown>;
  status?: 'draft' | 'active' | 'deprecated' | 'archived';
  confidence?: number;
}

export interface SkillHistoryEntry {
  id: string;
  action: string;
  trigger_reason: string | null;
  outcome_summary: string;
  success: boolean;
  created_at: string;
}

export interface SkillHistoryResponse {
  items: SkillHistoryEntry[];
  total: number;
}

// ──────────────────────────────────────────────────────────────────────────────
// Learning types (Hermes ADR-0009 Fase 0.7)
// ──────────────────────────────────────────────────────────────────────────────

export interface LearningLogEntry {
  id: string;
  action: string;
  origin: string;
  trigger_reason: string | null;
  review_json: Record<string, unknown>;
  outcome_summary: string;
  memory_ids: string[];
  skill_id: string | null;
  llm_model: string | null;
  llm_tokens_used: number;
  success: boolean;
  error_message: string | null;
  created_at: string;
}

export interface LearningListResponse {
  items: LearningLogEntry[];
  total: number;
}

export interface LearningSummary {
  total_entries: number;
  successful: number;
  failed: number;
  success_rate: number;
  by_action: Record<string, number>;
  by_origin: Record<string, number>;
  total_tokens_used: number;
  last_24h_count: number;
  last_7d_count: number;
}

export interface ManualReviewRequest {
  user_input: string;
  assistant_response: string;
  intent?: string;
  used_llm?: boolean;
}

export interface ManualReviewResponse {
  memories_to_save: Array<Record<string, unknown>>;
  nothing_to_learn: boolean;
  error: string | null;
  llm_tokens_used: number;
}

export interface CurationResponse {
  started_at: string;
  total_memories_before: number;
  total_memories_after: number;
  demoted_low_confidence: number;
  compressed_old_entries: number;
  kept_active: number;
  bytes_estimate: number;
}

// ──────────────────────────────────────────────────────────────────────────────
// Context types (Fase 0.8)
// ──────────────────────────────────────────────────────────────────────────────

export interface ContextResponse {
  user_md: string;
  memory_md: string;
  user_md_bytes: number;
  memory_md_bytes: number;
  memory_cap_bytes: number;
}

export interface MaterializeResponse {
  user_md: string;
  memory_md: string;
  user_md_bytes: number;
  memory_md_bytes: number;
}

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

  // ─── Briefing ───

  async getBriefing(): Promise<BriefingResponse> {
    if (this.demoMode) {
      return {
        date: new Date().toISOString().split('T')[0],
        greeting: 'Buenos días',
        pending_reminders: 2,
        overdue_reminders: 0,
        upcoming_reminders: [
          { id: 'mock-1', title: 'Revisar VNBOT', due_at: new Date(Date.now() + 86400000).toISOString() },
          { id: 'mock-2', title: 'Llamar al banco', due_at: new Date(Date.now() + 7 * 86400000).toISOString() },
        ],
        recent_memories: [
          { id: 'mock-m1', label: 'Wifi oficina', type: 'note' },
          { id: 'mock-m2', label: 'Proyecto VNBOT', type: 'task' },
        ],
        summary: 'Tienes 2 recordatorios pendientes. Tu próximo recordatorio es "Revisar VNBOT". Ayer guardaste 2 memorias.',
        generated_at: new Date().toISOString(),
      };
    }
    return this.request<BriefingResponse>('/briefing');
  }

  // ─── Skills (Hermes ADR-0009 Fase 0.7) ───

  async listSkills(params?: { status?: string; origin?: string }): Promise<SkillListResponse> {
    if (this.demoMode) {
      return {
        items: [
          {
            id: 'mock-skill-1',
            name: 'morning-routine',
            description: 'Rutina matutina: calendario + tareas + focus mode',
            status: 'active',
            origin: 'user',
            version: 1,
            confidence: 0.7,
            use_count: 12,
            last_used_at: new Date(Date.now() - 3600000).toISOString(),
            created_at: new Date(Date.now() - 86400000 * 7).toISOString(),
          },
          {
            id: 'mock-skill-2',
            name: 'weekly-review',
            description: 'Revisión semanal: progreso + ajustar prioridades',
            status: 'draft',
            origin: 'hermes',
            version: 1,
            confidence: 0.3,
            use_count: 0,
            last_used_at: null,
            created_at: new Date(Date.now() - 86400000 * 2).toISOString(),
          },
        ],
        total: 2,
      };
    }
    const qs = new URLSearchParams();
    if (params?.status) qs.set('status', params.status);
    if (params?.origin) qs.set('origin', params.origin);
    const q = qs.toString();
    return this.request<SkillListResponse>(`/skills${q ? `?${q}` : ''}`);
  }

  async getSkill(id: string): Promise<SkillDetail> {
    if (this.demoMode) {
      return {
        id,
        name: 'morning-routine',
        description: 'Rutina matutina: calendario + tareas + focus mode',
        body_markdown: '# Morning Routine\n\n## Pasos\n1. Check calendar\n2. List today tasks\n3. Set focus mode',
        triggers_json: {},
        status: 'active',
        origin: 'user',
        version: 1,
        confidence: 0.7,
        use_count: 12,
        last_used_at: new Date(Date.now() - 3600000).toISOString(),
        created_at: new Date(Date.now() - 86400000 * 7).toISOString(),
        updated_at: new Date(Date.now() - 3600000).toISOString(),
      };
    }
    return this.request<SkillDetail>(`/skills/${id}`);
  }

  async createSkill(data: CreateSkillRequest): Promise<SkillDetail> {
    if (this.demoMode) {
      throw new Error('Skills creation no disponible en modo demo');
    }
    return this.request<SkillDetail>('/skills', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async patchSkill(id: string, data: PatchSkillRequest): Promise<SkillDetail> {
    if (this.demoMode) {
      throw new Error('Skills patch no disponible en modo demo');
    }
    return this.request<SkillDetail>(`/skills/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteSkill(id: string): Promise<void> {
    if (this.demoMode) return;
    await this.request<void>(`/skills/${id}`, { method: 'DELETE' });
  }

  async activateSkill(id: string): Promise<SkillDetail> {
    if (this.demoMode) {
      throw new Error('Skill activation no disponible en modo demo');
    }
    return this.request<SkillDetail>(`/skills/${id}/activate`, { method: 'POST' });
  }

  async recordSkillUse(id: string): Promise<SkillDetail> {
    if (this.demoMode) return this.getSkill(id);
    return this.request<SkillDetail>(`/skills/${id}/use`, { method: 'POST' });
  }

  async materializePersistence(): Promise<MaterializeResponse> {
    if (this.demoMode) {
      return {
        user_md: '# Perfil del Usuario\n\n- Nombre: Local User\n- Zona horaria: America/Caracas',
        memory_md: '# Memoria de Trabajo\n\n- (sin memorias)',
        user_md_bytes: 80,
        memory_md_bytes: 40,
      };
    }
    return this.request<MaterializeResponse>('/skills/materialize', { method: 'POST' });
  }

  async getSkillHistory(id: string): Promise<SkillHistoryResponse> {
    if (this.demoMode) {
      return {
        items: [
          {
            id: 'mock-log-1',
            action: 'skill_created',
            trigger_reason: 'manual creation via API',
            outcome_summary: 'user created skill',
            success: true,
            created_at: new Date(Date.now() - 86400000 * 7).toISOString(),
          },
        ],
        total: 1,
      };
    }
    return this.request<SkillHistoryResponse>(`/skills/${id}/history`);
  }

  // ─── Learning (Hermes ADR-0009 Fase 0.7) ───

  async listLearning(params?: {
    action?: string;
    origin?: string;
    success?: boolean;
    limit?: number;
  }): Promise<LearningListResponse> {
    if (this.demoMode) {
      return {
        items: [
          {
            id: 'mock-learn-1',
            action: 'background_review',
            origin: 'hermes',
            trigger_reason: 'post-response (intent=create_memory, used_llm=true)',
            review_json: { memories_to_save: [{ content: 'Prefiere café sobre té' }] },
            outcome_summary: 'saved 1 memories',
            memory_ids: ['mock-mem-1'],
            skill_id: null,
            llm_model: 'glm-4.6',
            llm_tokens_used: 412,
            success: true,
            error_message: null,
            created_at: new Date(Date.now() - 3600000).toISOString(),
          },
        ],
        total: 1,
      };
    }
    const qs = new URLSearchParams();
    if (params?.action) qs.set('action', params.action);
    if (params?.origin) qs.set('origin', params.origin);
    if (params?.success !== undefined) qs.set('success', String(params.success));
    if (params?.limit) qs.set('limit', String(params.limit));
    const q = qs.toString();
    return this.request<LearningListResponse>(`/learning${q ? `?${q}` : ''}`);
  }

  async getLearningSummary(): Promise<LearningSummary> {
    if (this.demoMode) {
      return {
        total_entries: 24,
        successful: 22,
        failed: 2,
        success_rate: 0.917,
        by_action: { background_review: 18, skill_created: 4, memory_curation: 2 },
        by_origin: { hermes: 20, user: 4 },
        total_tokens_used: 8420,
        last_24h_count: 6,
        last_7d_count: 18,
      };
    }
    return this.request<LearningSummary>('/learning/summary');
  }

  async triggerCuration(): Promise<CurationResponse> {
    if (this.demoMode) {
      return {
        started_at: new Date().toISOString(),
        total_memories_before: 8,
        total_memories_after: 5,
        demoted_low_confidence: 2,
        compressed_old_entries: 1,
        kept_active: 5,
        bytes_estimate: 1000,
      };
    }
    return this.request<CurationResponse>('/learning/curate', { method: 'POST' });
  }

  async triggerReview(data: ManualReviewRequest): Promise<ManualReviewResponse> {
    if (this.demoMode) {
      return {
        memories_to_save: [{ content: 'Demo memory', type: 'note', confidence: 0.7 }],
        nothing_to_learn: false,
        error: null,
        llm_tokens_used: 0,
      };
    }
    return this.request<ManualReviewResponse>('/learning/review', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ─── Context (Fase 0.8) ───

  async getContext(): Promise<ContextResponse> {
    if (this.demoMode) {
      return {
        user_md: '# Perfil del Usuario\n\n## Información Básica\n- Nombre: Local User\n- Zona horaria: America/Caracas\n- Idioma: es\n\n## Preferencias Conocidas\n- Prefiere café sobre té\n- Trabaja en proyecto VNBOT',
        memory_md: '# Memoria de Trabajo\n\n- **Wifi oficina** (conf=0.95): clave 1234\n- **Cumpleaños** (conf=0.90): 15 marzo\n- **Proyecto VNBOT** (conf=0.85): monorepo Next.js + FastAPI',
        user_md_bytes: 220,
        memory_md_bytes: 180,
        memory_cap_bytes: 3500,
      };
    }
    return this.request<ContextResponse>('/context');
  }

  async materializeContext(): Promise<MaterializeResponse> {
    if (this.demoMode) {
      return {
        user_md: '# Perfil del Usuario (materializado)\n\n- Nombre: Local User',
        memory_md: '# Memoria (materializada)\n\n- (sin memorias)',
        user_md_bytes: 60,
        memory_md_bytes: 40,
      };
    }
    return this.request<MaterializeResponse>('/context/materialize', { method: 'POST' });
  }
}

export const apiClient = new ApiClient();
