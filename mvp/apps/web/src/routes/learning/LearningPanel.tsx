/**
 * VNBOT Web — Learning panel (Hermes ADR-0009 Fase 0.7).
 *
 * Shows what Hermes has learned:
 *  - Summary stats (counts by action, success rate, tokens used)
 *  - Recent LearningLog entries (audit trail)
 *  - Manual triggers: curate memories, run background review
 *  - USER.md + MEMORY.md viewer (Fase 0.8 context)
 *  - Cost tracking per LLM provider (ADR-0012)
 *
 * Per ADR-0011: every Hermes action writes a LearningLog entry for audit.
 * This panel makes that audit visible to the user.
 */

import { useState, useEffect, useCallback } from 'react';
import { TopBar } from '@/components/shell/TopBar';
import { apiClient } from '@/lib/api/client';
import type {
  LearningSummary,
  LearningLogEntry,
  CurationResponse,
  ManualReviewResponse,
  ContextResponse,
  CostTrackingResponse,
} from '@/lib/api/client';

const ACTION_LABELS: Record<string, string> = {
  background_review: '🔍 Background Review',
  memory_curation: '🧹 Memory Curation',
  skill_created: '⚙ Skill Created',
  skill_patched: '✎ Skill Patched',
  memory_saved: '💾 Memory Saved',
  user_info_updated: '👤 User Info Updated',
};

const PROVIDER_LABELS: Record<string, string> = {
  zai: 'Z.AI (glm-4.6)',
  openai: 'OpenAI',
  anthropic: 'Anthropic',
  gemini: 'Google Gemini',
  ollama: 'Ollama (local)',
  unknown: 'Unknown / legacy',
};

export function LearningPanel() {
  const [summary, setSummary] = useState<LearningSummary | null>(null);
  const [entries, setEntries] = useState<LearningLogEntry[]>([]);
  const [context, setContext] = useState<ContextResponse | null>(null);
  const [costs, setCosts] = useState<CostTrackingResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState<string>('');
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [reviewInput, setReviewInput] = useState('');
  const [reviewResponse, setReviewResponse] = useState('');
  const [reviewResult, setReviewResult] = useState<ManualReviewResponse | null>(null);
  const [curationResult, setCurationResult] = useState<CurationResponse | null>(null);
  const [activeTab, setActiveTab] = useState<'log' | 'context' | 'costs'>('log');

  const loadAll = useCallback(async () => {
    setIsLoading(true);
    try {
      const [sum, list, ctx, costData] = await Promise.all([
        apiClient.getLearningSummary(),
        apiClient.listLearning(actionFilter ? { action: actionFilter, limit: 50 } : { limit: 50 }),
        apiClient.getContext(),
        apiClient.getCostTracking(30),
      ]);
      setSummary(sum);
      setEntries(list.items);
      setContext(ctx);
      setCosts(costData);
    } catch {
      /* silent */
    } finally {
      setIsLoading(false);
    }
  }, [actionFilter]);

  useEffect(() => {
    void loadAll();
  }, [loadAll]);

  const handleCurate = useCallback(async () => {
    try {
      const result = await apiClient.triggerCuration();
      setCurationResult(result);
      setTimeout(() => setCurationResult(null), 8000);
      void loadAll();
    } catch (e) {
      alert(`Error: ${(e as Error).message}`);
    }
  }, [loadAll]);

  const handleReview = useCallback(async () => {
    if (!reviewInput.trim() || !reviewResponse.trim()) return;
    try {
      const result = await apiClient.triggerReview({
        user_input: reviewInput,
        assistant_response: reviewResponse,
        intent: 'create_memory',
        used_llm: true,
      });
      setReviewResult(result);
      void loadAll();
    } catch (e) {
      alert(`Error: ${(e as Error).message}`);
    }
  }, [reviewInput, reviewResponse, loadAll]);

  const handleMaterialize = useCallback(async () => {
    try {
      await apiClient.materializeContext();
      void loadAll();
    } catch (e) {
      alert(`Error: ${(e as Error).message}`);
    }
  }, [loadAll]);

  return (
    <div className="flex flex-col h-screen">
      <TopBar title="APRENDIZAJE" />
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {/* Header */}
          <div className="border border-vnbot-line-soft bg-vnbot-bg-1 p-4">
            <div className="font-display text-lg text-vnbot-text mb-2">
              Hermes Learning Loop
            </div>
            <p className="font-body text-sm text-vnbot-text-muted">
              VNBOT aprende en background después de cada confirmación. Aquí puedes ver qué ha
              aprendido, los tokens consumidos y el audit trail completo.
            </p>
          </div>

          {/* Summary stats */}
          {summary && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="border border-vnbot-line-soft bg-vnbot-panel-0 p-3">
                <div className="font-mono text-[10px] uppercase text-vnbot-text-muted">Total</div>
                <div className="font-display text-2xl text-vnbot-text">{summary.total_entries}</div>
                <div className="font-mono text-[10px] text-vnbot-text-muted">
                  {summary.last_24h_count} en 24h · {summary.last_7d_count} en 7d
                </div>
              </div>
              <div className="border border-vnbot-line-soft bg-vnbot-panel-0 p-3">
                <div className="font-mono text-[10px] uppercase text-vnbot-text-muted">Éxito</div>
                <div className="font-display text-2xl text-vnbot-green">
                  {(summary.success_rate * 100).toFixed(0)}%
                </div>
                <div className="font-mono text-[10px] text-vnbot-text-muted">
                  {summary.successful} ok · {summary.failed} fallidos
                </div>
              </div>
              <div className="border border-vnbot-line-soft bg-vnbot-panel-0 p-3">
                <div className="font-mono text-[10px] uppercase text-vnbot-text-muted">Tokens</div>
                <div className="font-display text-2xl text-vnbot-cyan">
                  {summary.total_tokens_used.toLocaleString()}
                </div>
                <div className="font-mono text-[10px] text-vnbot-text-muted">LLM totales</div>
              </div>
              <div className="border border-vnbot-line-soft bg-vnbot-panel-0 p-3">
                <div className="font-mono text-[10px] uppercase text-vnbot-text-muted">Actions</div>
                <div className="font-display text-2xl text-vnbot-text">
                  {Object.keys(summary.by_action).length}
                </div>
                <div className="font-mono text-[10px] text-vnbot-text-muted">tipos distintos</div>
              </div>
            </div>
          )}

          {/* Action breakdown */}
          {summary && Object.keys(summary.by_action).length > 0 && (
            <div className="border border-vnbot-line-soft bg-vnbot-panel-0 p-4">
              <div className="font-mono text-[10px] uppercase text-vnbot-text-muted mb-2">
                Desglose por acción
              </div>
              <div className="space-y-1">
                {Object.entries(summary.by_action).map(([action, count]) => (
                  <div key={action} className="flex items-center gap-2">
                    <span className="font-mono text-xs text-vnbot-text w-48">
                      {ACTION_LABELS[action] || action}
                    </span>
                    <div className="flex-1 h-2 bg-vnbot-bg-0 border border-vnbot-line-soft">
                      <div
                        className="h-full bg-vnbot-cyan"
                        style={{
                          width: `${summary.total_entries > 0 ? (count / summary.total_entries) * 100 : 0}%`,
                        }}
                      />
                    </div>
                    <span className="font-mono text-xs text-vnbot-text-muted w-8 text-right">
                      {count}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Manual triggers */}
          <div className="border border-vnbot-line-soft bg-vnbot-panel-0 p-4 space-y-3">
            <div className="font-mono text-[10px] uppercase text-vnbot-text-muted">
              Triggers manuales
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={handleCurate}
                className="px-3 py-1.5 bg-vnbot-cyan text-vnbot-bg-0 font-mono text-xs uppercase"
              >
                🧹 Curar memoria
              </button>
              <button
                type="button"
                onClick={() => setShowReviewForm(!showReviewForm)}
                className="px-3 py-1.5 border border-vnbot-cyan text-vnbot-cyan hover:bg-vnbot-cyan hover:text-vnbot-bg-0 font-mono text-xs uppercase"
              >
                🔍 Review manual
              </button>
              <button
                type="button"
                onClick={handleMaterialize}
                className="px-3 py-1.5 border border-vnbot-line-soft text-vnbot-text-muted hover:text-vnbot-text font-mono text-xs uppercase"
              >
                ↻ Materializar USER.md + MEMORY.md
              </button>
            </div>
            {curationResult && (
              <div className="border border-vnbot-green bg-vnbot-green/10 p-2 font-mono text-[10px] text-vnbot-green">
                ✓ Curación: {curationResult.demoted_low_confidence} low-conf demoted ·{' '}
                {curationResult.compressed_old_entries} old archived ·{' '}
                {curationResult.kept_active} kept active ·{' '}
                {curationResult.bytes_estimate}B
              </div>
            )}
            {showReviewForm && (
              <div className="border border-vnbot-line-soft p-3 space-y-2">
                <textarea
                  value={reviewInput}
                  onChange={(e) => setReviewInput(e.target.value)}
                  placeholder="Input del usuario (texto a analizar)"
                  rows={2}
                  className="w-full bg-vnbot-bg-0 border border-vnbot-line-soft px-2 py-1 text-vnbot-text text-xs focus:border-vnbot-cyan focus:outline-none"
                />
                <textarea
                  value={reviewResponse}
                  onChange={(e) => setReviewResponse(e.target.value)}
                  placeholder="Respuesta del asistente"
                  rows={2}
                  className="w-full bg-vnbot-bg-0 border border-vnbot-line-soft px-2 py-1 text-vnbot-text text-xs focus:border-vnbot-cyan focus:outline-none"
                />
                <button
                  type="button"
                  onClick={handleReview}
                  className="px-3 py-1.5 bg-vnbot-green text-vnbot-bg-0 font-mono text-xs uppercase"
                >
                  → Ejecutar review
                </button>
                {reviewResult && (
                  <div className="border border-vnbot-cyan bg-vnbot-cyan/10 p-2 font-mono text-[10px] text-vnbot-cyan">
                    {reviewResult.error ? (
                      <span>✗ Error: {reviewResult.error}</span>
                    ) : reviewResult.nothing_to_learn ? (
                      <span>○ Nada que aprender</span>
                    ) : (
                      <div>
                        ✓ {reviewResult.memories_to_save.length} memorias detectadas ·{' '}
                        {reviewResult.llm_tokens_used} tokens
                        <pre className="mt-1 text-vnbot-text whitespace-pre-wrap">
                          {JSON.stringify(reviewResult.memories_to_save, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Tabs: Log / Context */}
          <div className="flex gap-2 border-b border-vnbot-line-soft">
            <button
              type="button"
              onClick={() => setActiveTab('log')}
              className={`px-4 py-2 font-mono text-xs uppercase border-b-2 ${
                activeTab === 'log'
                  ? 'border-vnbot-cyan text-vnbot-text'
                  : 'border-transparent text-vnbot-text-muted hover:text-vnbot-text'
              }`}
            >
              Audit Log ({entries.length})
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('context')}
              className={`px-4 py-2 font-mono text-xs uppercase border-b-2 ${
                activeTab === 'context'
                  ? 'border-vnbot-cyan text-vnbot-text'
                  : 'border-transparent text-vnbot-text-muted hover:text-vnbot-text'
              }`}
            >
              Contexto (USER.md + MEMORY.md)
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('costs')}
              className={`px-4 py-2 font-mono text-xs uppercase border-b-2 ${
                activeTab === 'costs'
                  ? 'border-vnbot-cyan text-vnbot-text'
                  : 'border-transparent text-vnbot-text-muted hover:text-vnbot-text'
              }`}
            >
              Costos ({costs?.total_calls ?? 0})
            </button>
          </div>

          {activeTab === 'log' && (
            <>
              {/* Filters */}
              <div className="flex gap-2 flex-wrap">
                <button
                  type="button"
                  onClick={() => setActionFilter('')}
                  className={`px-2 py-1 font-mono text-[10px] uppercase border ${
                    actionFilter === ''
                      ? 'bg-vnbot-cyan text-vnbot-bg-0 border-vnbot-cyan'
                      : 'border-vnbot-line-soft text-vnbot-text-muted'
                  }`}
                >
                  todos
                </button>
                {Object.keys(ACTION_LABELS).map((action) => (
                  <button
                    key={action}
                    type="button"
                    onClick={() => setActionFilter(action)}
                    className={`px-2 py-1 font-mono text-[10px] uppercase border ${
                      actionFilter === action
                        ? 'bg-vnbot-cyan text-vnbot-bg-0 border-vnbot-cyan'
                        : 'border-vnbot-line-soft text-vnbot-text-muted'
                    }`}
                  >
                    {action}
                  </button>
                ))}
              </div>

              {/* Log entries */}
              {isLoading ? (
                <div className="text-center py-8 font-mono text-xs text-vnbot-text-muted animate-pulse">
                  Cargando...
                </div>
              ) : entries.length === 0 ? (
                <div className="text-center py-8 font-body text-sm text-vnbot-text-muted">
                  Sin entradas en el log.
                  <br />
                  <span className="text-[10px]">
                    Converse con VNBOT y confirma operaciones — Hermes aprenderá en background.
                  </span>
                </div>
              ) : (
                <div className="space-y-2">
                  {entries.map((entry) => (
                    <div
                      key={entry.id}
                      className={`border-l-2 p-3 bg-vnbot-panel-0 ${
                        entry.success ? 'border-vnbot-green' : 'border-vnbot-red'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-mono text-[10px] text-vnbot-text">
                          {ACTION_LABELS[entry.action] || entry.action}
                        </span>
                        <span className="font-mono text-[10px] text-vnbot-text-muted">
                          {entry.origin}
                        </span>
                        {entry.llm_model && (
                          <span className="font-mono text-[10px] text-vnbot-cyan">
                            {entry.llm_model} · {entry.llm_tokens_used} tok
                          </span>
                        )}
                        <span className="ml-auto font-mono text-[10px] text-vnbot-text-muted">
                          {new Date(entry.created_at).toLocaleString()}
                        </span>
                      </div>
                      <div className="font-body text-xs text-vnbot-text mb-1">
                        {entry.outcome_summary}
                      </div>
                      {entry.trigger_reason && (
                        <div className="font-mono text-[10px] text-vnbot-text-muted">
                          → {entry.trigger_reason}
                        </div>
                      )}
                      {entry.error_message && (
                        <div className="font-mono text-[10px] text-vnbot-red mt-1">
                          ✗ {entry.error_message}
                        </div>
                      )}
                      {entry.memory_ids.length > 0 && (
                        <div className="font-mono text-[10px] text-vnbot-text-muted mt-1">
                          memories: {entry.memory_ids.length}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </>
          )}

          {activeTab === 'context' && context && (
            <div className="space-y-4">
              <div className="border border-vnbot-line-soft bg-vnbot-panel-0 p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="font-mono text-[10px] uppercase text-vnbot-text-muted">
                    USER.md ({context.user_md_bytes}B)
                  </div>
                  <button
                    type="button"
                    onClick={handleMaterialize}
                    className="px-2 py-1 border border-vnbot-line-soft text-vnbot-text-muted hover:text-vnbot-text font-mono text-[10px]"
                  >
                    ↻ Regenerar
                  </button>
                </div>
                <pre className="font-mono text-xs text-vnbot-text whitespace-pre-wrap break-words">
                  {context.user_md}
                </pre>
              </div>
              <div className="border border-vnbot-line-soft bg-vnbot-panel-0 p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="font-mono text-[10px] uppercase text-vnbot-text-muted">
                    MEMORY.md ({context.memory_md_bytes}B / {context.memory_cap_bytes}B cap)
                  </div>
                  <div className="font-mono text-[10px] text-vnbot-text-muted">
                    {((context.memory_md_bytes / context.memory_cap_bytes) * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="h-1 bg-vnbot-bg-0 border border-vnbot-line-soft mb-3">
                  <div
                    className="h-full bg-vnbot-cyan"
                    style={{
                      width: `${Math.min(100, (context.memory_md_bytes / context.memory_cap_bytes) * 100)}%`,
                    }}
                  />
                </div>
                <pre className="font-mono text-xs text-vnbot-text whitespace-pre-wrap break-words">
                  {context.memory_md}
                </pre>
              </div>
            </div>
          )}

          {activeTab === 'costs' && costs && (
            <div className="space-y-4">
              {/* Summary */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                <div className="border border-vnbot-line-soft bg-vnbot-panel-0 p-3">
                  <div className="font-mono text-[10px] uppercase text-vnbot-text-muted">
                    Llamadas totales (30 días)
                  </div>
                  <div className="font-display text-2xl text-vnbot-text">
                    {costs.total_calls}
                  </div>
                </div>
                <div className="border border-vnbot-line-soft bg-vnbot-panel-0 p-3">
                  <div className="font-mono text-[10px] uppercase text-vnbot-text-muted">
                    Tokens totales
                  </div>
                  <div className="font-display text-2xl text-vnbot-cyan">
                    {costs.total_tokens.toLocaleString()}
                  </div>
                </div>
                <div className="border border-vnbot-line-soft bg-vnbot-panel-0 p-3">
                  <div className="font-mono text-[10px] uppercase text-vnbot-text-muted">
                    Costo estimado (USD)
                  </div>
                  <div className="font-display text-2xl text-vnbot-green">
                    ${costs.estimated_cost_usd.toFixed(4)}
                  </div>
                </div>
              </div>

              {/* Per-provider breakdown */}
              <div className="border border-vnbot-line-soft bg-vnbot-panel-0 p-4">
                <div className="font-mono text-[10px] uppercase text-vnbot-text-muted mb-3">
                  Uso por provider
                </div>
                {costs.providers.length === 0 ? (
                  <div className="text-center py-4 font-body text-sm text-vnbot-text-muted">
                    Sin datos de uso en los últimos 30 días.
                  </div>
                ) : (
                  <div className="space-y-2">
                    {costs.providers.map((p) => (
                      <div key={p.provider} className="flex items-center gap-3 p-2 bg-vnbot-bg-0 border border-vnbot-line-soft">
                        <div className="w-32">
                          <div className="font-body text-sm text-vnbot-text">
                            {PROVIDER_LABELS[p.provider] || p.provider}
                          </div>
                          <div className="font-mono text-[9px] text-vnbot-text-muted">
                            {p.last_used
                              ? `último: ${new Date(p.last_used).toLocaleDateString()}`
                              : 'sin uso'}
                          </div>
                        </div>
                        <div className="flex-1 grid grid-cols-4 gap-2 font-mono text-[10px]">
                          <div>
                            <div className="text-vnbot-text-muted">calls</div>
                            <div className="text-vnbot-text">
                              {p.total_calls} ({p.successful_calls}✓/{p.failed_calls}✗)
                            </div>
                          </div>
                          <div>
                            <div className="text-vnbot-text-muted">tokens</div>
                            <div className="text-vnbot-cyan">{p.total_tokens.toLocaleString()}</div>
                          </div>
                          <div>
                            <div className="text-vnbot-text-muted">avg/call</div>
                            <div className="text-vnbot-text">{p.avg_tokens_per_call}</div>
                          </div>
                          <div>
                            <div className="text-vnbot-text-muted">share</div>
                            <div className="text-vnbot-text">
                              {costs.total_tokens > 0
                                ? `${((p.total_tokens / costs.total_tokens) * 100).toFixed(0)}%`
                                : '0%'}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Token share bar chart */}
              {costs.providers.length > 0 && (
                <div className="border border-vnbot-line-soft bg-vnbot-panel-0 p-4">
                  <div className="font-mono text-[10px] uppercase text-vnbot-text-muted mb-3">
                    Distribución de tokens
                  </div>
                  <div className="flex h-6 border border-vnbot-line-soft">
                    {costs.providers.map((p, i) => {
                      const colors = ['bg-vnbot-cyan', 'bg-vnbot-green', 'bg-vnbot-amber', 'bg-vnbot-red', 'bg-vnbot-text-muted'];
                      const color = colors[i % colors.length];
                      const width = costs.total_tokens > 0 ? (p.total_tokens / costs.total_tokens) * 100 : 0;
                      return width > 0 ? (
                        <div
                          key={p.provider}
                          className={`${color} flex items-center justify-center font-mono text-[9px] text-vnbot-bg-0`}
                          style={{ width: `${width}%` }}
                          title={`${PROVIDER_LABELS[p.provider] || p.provider}: ${p.total_tokens} tokens (${width.toFixed(1)}%)`}
                        >
                          {width > 8 ? `${width.toFixed(0)}%` : ''}
                        </div>
                      ) : null;
                    })}
                  </div>
                  <div className="flex flex-wrap gap-3 mt-2">
                    {costs.providers.map((p, i) => {
                      const colors = ['bg-vnbot-cyan', 'bg-vnbot-green', 'bg-vnbot-amber', 'bg-vnbot-red', 'bg-vnbot-text-muted'];
                      return (
                        <div key={p.provider} className="flex items-center gap-1 font-mono text-[10px] text-vnbot-text-muted">
                          <span className={`w-2 h-2 ${colors[i % colors.length]}`} />
                          {PROVIDER_LABELS[p.provider] || p.provider}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              <div className="p-3 border border-vnbot-line-soft bg-vnbot-bg-1 font-mono text-[10px] text-vnbot-text-muted">
                ℹ Los precios son estimaciones basadas en tarifas públicas (julio 2026).
                Z.AI y Ollama son gratuitos. Para costos reales consulta tu dashboard del provider.
                <br />
                Período: {new Date(costs.period_start).toLocaleDateString()} → {new Date(costs.period_end).toLocaleDateString()}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
