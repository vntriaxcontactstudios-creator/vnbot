/**
 * VNBOT Web — Skills panel (Hermes ADR-0009 Fase 0.7).
 *
 * Lists all skills (Hermes-learned + user-authored), lets the user:
 *  - Create new skills (markdown body)
 *  - Activate draft skills (promote draft → active)
 *  - View skill detail (body_markdown, triggers, history)
 *  - Delete (soft-archive) skills
 *  - Materialize USER.md + MEMORY.md from DB
 *
 * Per ADR-0009 §3.2: skills are markdown bodies + trigger metadata. Hermes
 * creates drafts (confidence=0.3); user must activate.
 */

import { useState, useEffect, useCallback } from 'react';
import { TopBar } from '@/components/shell/TopBar';
import { apiClient } from '@/lib/api/client';
import type {
  SkillSummary,
  SkillDetail,
  SkillHistoryResponse,
  MaterializeResponse,
} from '@/lib/api/client';

const STATUS_COLORS: Record<string, string> = {
  draft: 'text-vnbot-amber border-vnbot-amber',
  active: 'text-vnbot-green border-vnbot-green',
  deprecated: 'text-vnbot-text-muted border-vnbot-line-soft',
  archived: 'text-vnbot-text-muted border-vnbot-line-soft line-through',
};

const ORIGIN_LABEL: Record<string, string> = {
  hermes: '⚡ Hermes',
  user: '✎ User',
  imported: '⇄ Imported',
};

export function SkillsPanel() {
  const [skills, setSkills] = useState<SkillSummary[]>([]);
  const [selected, setSelected] = useState<SkillDetail | null>(null);
  const [history, setHistory] = useState<SkillHistoryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'draft' | 'active' | 'hermes' | 'user'>('all');
  const [showCreate, setShowCreate] = useState(false);
  const [materializeResult, setMaterializeResult] = useState<MaterializeResponse | null>(null);

  // New skill form state
  const [newName, setNewName] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [newBody, setNewBody] = useState('# New Skill\n\n## Description\n\n## Steps\n1. \n2. \n3. \n');

  const loadSkills = useCallback(async () => {
    setIsLoading(true);
    try {
      const resp = await apiClient.listSkills(
        filter === 'draft' || filter === 'active' ? { status: filter } : undefined,
      );
      let items = resp.items;
      if (filter === 'hermes' || filter === 'user') {
        items = items.filter((s) => s.origin === filter);
      }
      setSkills(items);
    } catch {
      /* silent */
    } finally {
      setIsLoading(false);
    }
  }, [filter]);

  const loadSkill = useCallback(async (id: string) => {
    try {
      const detail = await apiClient.getSkill(id);
      setSelected(detail);
      const hist = await apiClient.getSkillHistory(id);
      setHistory(hist);
    } catch {
      /* silent */
    }
  }, []);

  useEffect(() => {
    void loadSkills();
  }, [loadSkills]);

  const handleCreate = useCallback(async () => {
    if (!newName.trim() || !newBody.trim()) return;
    try {
      const created = await apiClient.createSkill({
        name: newName.trim(),
        description: newDescription.trim(),
        body_markdown: newBody,
        status: 'draft',
      });
      setNewName('');
      setNewDescription('');
      setNewBody('# New Skill\n\n## Description\n\n## Steps\n1. \n2. \n3. \n');
      setShowCreate(false);
      void loadSkills();
      void loadSkill(created.id);
    } catch (e) {
      alert(`Error al crear skill: ${(e as Error).message}`);
    }
  }, [newName, newDescription, newBody, loadSkills, loadSkill]);

  const handleActivate = useCallback(
    async (id: string) => {
      try {
        await apiClient.activateSkill(id);
        void loadSkill(id);
        void loadSkills();
      } catch (e) {
        alert(`Error al activar: ${(e as Error).message}`);
      }
    },
    [loadSkill, loadSkills],
  );

  const handleDelete = useCallback(
    async (id: string) => {
      if (!confirm('¿Archivar esta skill? (status=archived)')) return;
      try {
        await apiClient.deleteSkill(id);
        setSelected(null);
        void loadSkills();
      } catch (e) {
        alert(`Error al archivar: ${(e as Error).message}`);
      }
    },
    [loadSkills],
  );

  const handleMaterialize = useCallback(async () => {
    try {
      const result = await apiClient.materializePersistence();
      setMaterializeResult(result);
      setTimeout(() => setMaterializeResult(null), 5000);
    } catch (e) {
      alert(`Error al materializar: ${(e as Error).message}`);
    }
  }, []);

  return (
    <div className="flex flex-col h-screen">
      <TopBar title="SKILLS" />
      <div className="flex flex-1 min-h-0">
        {/* Sidebar: skills list */}
        <div className="w-80 border-r border-vnbot-line-soft flex flex-col bg-vnbot-bg-1">
          <div className="p-3 border-b border-vnbot-line-soft flex gap-2 flex-wrap">
            {(['all', 'active', 'draft', 'hermes', 'user'] as const).map((f) => (
              <button
                key={f}
                type="button"
                onClick={() => setFilter(f)}
                className={`px-2 py-1 font-mono text-[10px] uppercase border ${
                  filter === f
                    ? 'bg-vnbot-cyan text-vnbot-bg-0 border-vnbot-cyan'
                    : 'border-vnbot-line-soft text-vnbot-text-muted hover:text-vnbot-text'
                }`}
              >
                {f}
              </button>
            ))}
          </div>
          <div className="p-3 border-b border-vnbot-line-soft flex gap-2">
            <button
              type="button"
              onClick={() => setShowCreate(!showCreate)}
              className="flex-1 px-3 py-2 bg-vnbot-cyan text-vnbot-bg-0 font-mono text-xs uppercase"
            >
              + Nueva skill
            </button>
            <button
              type="button"
              onClick={handleMaterialize}
              className="px-3 py-2 border border-vnbot-line-soft text-vnbot-text-muted hover:text-vnbot-text font-mono text-xs"
              title="Regenerar USER.md + MEMORY.md desde la DB"
            >
              ↻ Materializar
            </button>
          </div>
          {showCreate && (
            <div className="p-3 border-b border-vnbot-line-soft space-y-2">
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="Nombre (slug-style, ej: morning-routine)"
                className="w-full bg-vnbot-panel-0 border border-vnbot-line-soft px-2 py-1 text-vnbot-text text-xs focus:border-vnbot-cyan focus:outline-none"
                autoFocus
              />
              <input
                type="text"
                value={newDescription}
                onChange={(e) => setNewDescription(e.target.value)}
                placeholder="Descripción corta (opcional)"
                className="w-full bg-vnbot-panel-0 border border-vnbot-line-soft px-2 py-1 text-vnbot-text text-xs focus:border-vnbot-cyan focus:outline-none"
              />
              <textarea
                value={newBody}
                onChange={(e) => setNewBody(e.target.value)}
                placeholder="Cuerpo markdown..."
                rows={6}
                className="w-full bg-vnbot-panel-0 border border-vnbot-line-soft px-2 py-1 text-vnbot-text text-xs font-mono focus:border-vnbot-cyan focus:outline-none"
              />
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={handleCreate}
                  className="flex-1 px-2 py-1 bg-vnbot-green text-vnbot-bg-0 font-mono text-xs uppercase"
                >
                  ✓ Crear
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreate(false)}
                  className="px-2 py-1 border border-vnbot-line-soft text-vnbot-text-muted font-mono text-xs"
                >
                  ✕
                </button>
              </div>
            </div>
          )}
          {materializeResult && (
            <div className="p-3 border-b border-vnbot-line-soft bg-vnbot-green/10 text-vnbot-green font-mono text-[10px]">
              ↻ Materializado: USER.md {materializeResult.user_md_bytes}B · MEMORY.md {materializeResult.memory_md_bytes}B
            </div>
          )}
          {isLoading ? (
            <div className="p-4 text-center font-mono text-xs text-vnbot-text-muted animate-pulse">
              Cargando...
            </div>
          ) : skills.length === 0 ? (
            <div className="p-4 text-center font-body text-sm text-vnbot-text-muted">
              Sin skills aún.
              <br />
              <span className="text-[10px]">Hermes creará skills cuando detecte patrones repetidos.</span>
            </div>
          ) : (
            skills.map((skill) => (
              <button
                key={skill.id}
                type="button"
                onClick={() => loadSkill(skill.id)}
                className={`w-full text-left p-3 border-b border-vnbot-line-soft hover:bg-vnbot-panel-0 ${
                  selected?.id === skill.id ? 'bg-vnbot-panel-0 border-l-2 border-l-vnbot-cyan' : ''
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className={`font-mono text-[9px] px-1 border ${STATUS_COLORS[skill.status] || ''}`}>
                    {skill.status}
                  </span>
                  <span className="font-mono text-[9px] text-vnbot-text-muted">
                    {ORIGIN_LABEL[skill.origin] || skill.origin}
                  </span>
                  <span className="font-mono text-[9px] text-vnbot-text-muted ml-auto">
                    v{skill.version}
                  </span>
                </div>
                <div className="font-body text-sm text-vnbot-text truncate">{skill.name}</div>
                <div className="font-mono text-[10px] text-vnbot-text-muted mt-0.5 truncate">
                  {skill.description || '(sin descripción)'}
                </div>
                <div className="flex items-center gap-3 mt-1 font-mono text-[10px] text-vnbot-text-muted">
                  <span title="Confidence">conf={skill.confidence.toFixed(2)}</span>
                  <span title="Use count">uses={skill.use_count}</span>
                </div>
              </button>
            ))
          )}
        </div>

        {/* Detail panel */}
        <div className="flex-1 overflow-y-auto p-6">
          {selected ? (
            <div className="max-w-3xl mx-auto space-y-4">
              {/* Header */}
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="font-display text-2xl text-vnbot-text">{selected.name}</h2>
                  <p className="font-body text-sm text-vnbot-text-muted mt-1">{selected.description}</p>
                  <div className="flex items-center gap-3 mt-2 font-mono text-[10px] text-vnbot-text-muted">
                    <span className={`px-1 border ${STATUS_COLORS[selected.status]}`}>
                      {selected.status}
                    </span>
                    <span>{ORIGIN_LABEL[selected.origin] || selected.origin}</span>
                    <span>v{selected.version}</span>
                    <span>conf={selected.confidence.toFixed(2)}</span>
                    <span>uses={selected.use_count}</span>
                  </div>
                </div>
                <div className="flex gap-2">
                  {selected.status === 'draft' && (
                    <button
                      type="button"
                      onClick={() => handleActivate(selected.id)}
                      className="px-3 py-1.5 bg-vnbot-green text-vnbot-bg-0 font-mono text-xs uppercase"
                    >
                      ✓ Activar
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={() => handleDelete(selected.id)}
                    className="px-3 py-1.5 border border-vnbot-red text-vnbot-red hover:bg-vnbot-red hover:text-vnbot-bg-0 font-mono text-xs uppercase"
                  >
                    ✕ Archivar
                  </button>
                </div>
              </div>

              {/* Body markdown */}
              <div className="border border-vnbot-line-soft bg-vnbot-panel-0 p-4">
                <div className="font-mono text-[10px] uppercase text-vnbot-text-muted mb-2">
                  Cuerpo (markdown)
                </div>
                <pre className="font-mono text-xs text-vnbot-text whitespace-pre-wrap break-words">
                  {selected.body_markdown}
                </pre>
              </div>

              {/* Triggers */}
              <div className="border border-vnbot-line-soft bg-vnbot-panel-0 p-4">
                <div className="font-mono text-[10px] uppercase text-vnbot-text-muted mb-2">
                  Triggers
                </div>
                {Object.keys(selected.triggers_json).length > 0 ? (
                  <pre className="font-mono text-xs text-vnbot-text whitespace-pre-wrap">
                    {JSON.stringify(selected.triggers_json, null, 2)}
                  </pre>
                ) : (
                  <div className="font-mono text-xs text-vnbot-text-muted">
                    (sin triggers definidos)
                  </div>
                )}
              </div>

              {/* History */}
              {history && history.items.length > 0 && (
                <div className="border border-vnbot-line-soft bg-vnbot-panel-0 p-4">
                  <div className="font-mono text-[10px] uppercase text-vnbot-text-muted mb-2">
                    Historial ({history.total} entradas)
                  </div>
                  <div className="space-y-1">
                    {history.items.map((entry) => (
                      <div
                        key={entry.id}
                        className={`flex items-start gap-2 p-2 border-l-2 ${
                          entry.success ? 'border-vnbot-green' : 'border-vnbot-red'
                        }`}
                      >
                        <div className="flex-1">
                          <div className="font-mono text-[10px] text-vnbot-text-muted">
                            {new Date(entry.created_at).toLocaleString()} · {entry.action}
                          </div>
                          <div className="font-body text-xs text-vnbot-text">{entry.outcome_summary}</div>
                          {entry.trigger_reason && (
                            <div className="font-mono text-[10px] text-vnbot-text-muted mt-0.5">
                              → {entry.trigger_reason}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Metadata */}
              <div className="grid grid-cols-2 gap-2 font-mono text-[10px] text-vnbot-text-muted">
                <div>Created: {new Date(selected.created_at).toLocaleString()}</div>
                <div>Updated: {new Date(selected.updated_at).toLocaleString()}</div>
                {selected.last_used_at && (
                  <div>Last used: {new Date(selected.last_used_at).toLocaleString()}</div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center max-w-md">
                <div className="font-display text-2xl text-vnbot-text mb-2">Skills de VNBOT</div>
                <p className="font-body text-sm text-vnbot-text-muted mb-4">
                  Las skills son patrones aprendidos por Hermes o creados por ti. Hermes detecta
                  triggers (≥5 tool calls, error recovery, user correction) y genera drafts.
                  Tú decides cuáles activar.
                </p>
                <p className="font-mono text-[10px] text-vnbot-text-muted">
                  Selecciona una skill de la izquierda para ver detalles.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
