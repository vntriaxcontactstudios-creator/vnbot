/**
 * VNBOT Web — Learning panel (Hermes ADR-0009 Fase 0.7).
 *
 * Shows what Hermes has learned:
 *  - Summary stats (counts by action, success rate, tokens used)
 *  - Recent LearningLog entries (audit trail)
 *  - Manual triggers: curate memories, run background review
 *  - USER.md + MEMORY.md viewer (Fase 0.8 context)
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
} from '@/lib/api/client';

const ACTION_LABELS: Record<string, string> = {
  background_review: '🔍 Background Review',
  memory_curation: '🧹 Memory Curation',
  skill_created: '⚙ Skill Created',
  skill_patched: '✎ Skill Patched',
  memory_saved: '💾 Memory Saved',
  user_info_updated: '👤 User Info Updated',
};

export function LearningPanel() {
  const [summary, setSummary] = useState<LearningSummary | null>(null);
  const [entries, setEntries] = useState<LearningLogEntry[]>([]);
  const [context, setContext] = useState<ContextResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState<string>('');
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [reviewInput, setReviewInput] = useState('');
  const [reviewResponse, setReviewResponse] = useState('');
  const [reviewResult, setReviewResult] = useState<ManualReviewResponse | null>(null);
  const [curationResult, setCurationResult] = useState<CurationResponse | null>(null);
  const [activeTab, setActiveTab] = useState<'log' | 'context'>('log');

  const loadAll = useCallback(async () => {
    setIsLoading(true);
    try {
      const [sum, list, ctx] = await Promise.all([
        apiClient.getLearningSummary(),
        apiClient.listLearning(actionFilter ? { action: actionFilter, limit: 50 } : { limit: 50 }),
        apiClient.getContext(),
      ]);
      setSummary(sum);
      setEntries(list.items);
      setContext(ctx);
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
        </div>
      </div>
    </div>
  );
}
