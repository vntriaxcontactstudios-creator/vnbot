/**
 * VNBOT Web — Memory panel.
 *
 * Lists all memories + FTS5 search + inspector drawer.
 * Per docs/06 §3 (/memory route).
 */

import { useState, useEffect, useCallback } from 'react';
import { MascotStateView } from '@vnbot/pixelart';
import { TopBar } from '@/components/shell/TopBar';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';
import { apiClient } from '@/lib/api/client';
import type { MemoryNode, MemorySearchResult } from '@/lib/api/client';

export function MemoryPanel() {
  const [memories, setMemories] = useState<MemoryNode[]>([]);
  const [searchResults, setSearchResults] = useState<MemorySearchResult[] | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMemory, setSelectedMemory] = useState<MemoryNode | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);

  const loadMemories = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await apiClient.listMemories({ limit: 100 });
      setMemories(resp.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load memories');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadMemories();
  }, [loadMemories]);

  const handleSearch = useCallback(async () => {
    const q = searchQuery.trim();
    if (!q) {
      setSearchResults(null);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const resp = await apiClient.searchMemories(q);
      setSearchResults(resp.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery]);

  const handleDelete = useCallback(async (id: string) => {
    if (!confirm('¿Eliminar esta memoria? (soft delete)')) return;
    try {
      await apiClient.deleteMemory(id);
      setMemories((prev) => prev.filter((m) => m.id !== id));
      setSelectedMemory(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed');
    }
  }, []);

  const handleCreate = useCallback(async (data: { label: string; content: string; type: string; sensitivity: string }) => {
    try {
      const newMem = await apiClient.createMemory(data);
      setMemories((prev) => [newMem, ...prev]);
      setShowCreateForm(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Create failed');
    }
  }, []);

  const displayList = searchResults ?? [];

  return (
    <div className="flex flex-col h-screen">
      <TopBar title="Memoria" />

      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="p-4 border-b border-vnbot-line-soft bg-vnbot-bg-1">
            <div className="max-w-4xl mx-auto flex gap-2">
              <input
                type="search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') void handleSearch();
                }}
                placeholder="Buscar memorias... (Enter para buscar)"
                className="flex-1 bg-vnbot-panel-0 border border-vnbot-line-soft px-4 py-2 text-vnbot-text font-body text-sm placeholder:text-vnbot-text-muted focus:border-vnbot-cyan focus:outline-none"
                aria-label="Search memories"
              />
              <button
                type="button"
                onClick={() => void handleSearch()}
                className="px-4 py-2 bg-vnbot-violet text-vnbot-bg-0 font-mono text-xs uppercase hover:bg-vnbot-violet/80"
              >
                Buscar
              </button>
              {searchResults && (
                <button
                  type="button"
                  onClick={() => {
                    setSearchResults(null);
                    setSearchQuery('');
                  }}
                  className="px-4 py-2 border border-vnbot-line-soft text-vnbot-text-muted font-mono text-xs uppercase hover:bg-vnbot-panel-0"
                >
                  ✕ Clear
                </button>
              )}
              <button
                type="button"
                onClick={() => setShowCreateForm(true)}
                className="px-4 py-2 bg-vnbot-cyan text-vnbot-bg-0 font-mono text-xs uppercase hover:bg-vnbot-cyan/80"
              >
                + Nueva
              </button>
            </div>
          </div>

          {showCreateForm && (
            <CreateMemoryForm
              onSubmit={handleCreate}
              onCancel={() => setShowCreateForm(false)}
            />
          )}

          <div className="flex-1 overflow-y-auto p-4">
            <div className="max-w-4xl mx-auto">
              {isLoading && (
                <div className="text-center py-8">
                  <div className="font-mono text-xs text-vnbot-text-muted uppercase animate-pulse">
                    Cargando...
                  </div>
                </div>
              )}

              {error && (
                <div className="p-4 border border-vnbot-red/40 bg-vnbot-red/5 text-vnbot-red font-mono text-xs">
                  ⚠ {error}
                </div>
              )}

              {!isLoading && !error && searchResults === null && memories.length === 0 && (
                <EmptyState />
              )}

              {!isLoading && !error && searchResults !== null && displayList.length === 0 && (
                <div className="text-center py-12">
                  <div className="font-display text-lg text-vnbot-text-muted mb-2">
                    Sin resultados
                  </div>
                  <div className="font-body text-sm text-vnbot-text-muted">
                    No se encontraron memorias para "{searchQuery}"
                  </div>
                </div>
              )}

              {!isLoading && !error && searchResults !== null && displayList.length > 0 && (
                <div className="space-y-2">
                  <div className="font-mono text-[10px] text-vnbot-text-muted uppercase mb-2">
                    {displayList.length} resultado(s) para "{searchQuery}"
                  </div>
                  {displayList.map((result) => (
                    <SearchResultCard
                      key={result.id}
                      result={result}
                      onSelect={async () => {
                        try {
                          const m = await apiClient.getMemory(result.id);
                          setSelectedMemory(m);
                        } catch (err) {
                          setError(err instanceof Error ? err.message : 'Failed to load memory');
                        }
                      }}
                    />
                  ))}
                </div>
              )}

              {!isLoading && !error && searchResults === null && memories.length > 0 && (
                <div className="space-y-2">
                  <div className="font-mono text-[10px] text-vnbot-text-muted uppercase mb-2">
                    {memories.length} memoria(s)
                  </div>
                  {memories.map((memory) => (
                    <MemoryCard
                      key={memory.id}
                      memory={memory}
                      onSelect={() => setSelectedMemory(memory)}
                      isSelected={selectedMemory?.id === memory.id}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {selectedMemory && (
          <MemoryInspector
            memory={selectedMemory}
            onClose={() => setSelectedMemory(null)}
            onDelete={() => void handleDelete(selectedMemory.id)}
          />
        )}
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="text-center py-12">
      <div className="flex justify-center mb-4">
        <ErrorBoundary fallback={<div className="w-24 h-24 bg-vnbot-panel-0 border border-vnbot-line-soft" />}>
          <MascotStateView agent="archivist" state="idle" size={96} interactive />
        </ErrorBoundary>
      </div>
      <h2 className="font-display text-lg text-vnbot-text mb-2">
        Sin memorias todavía
      </h2>
      <p className="font-body text-sm text-vnbot-text-muted mb-4">
        Crea tu primera memoria desde el chat con: "Guarda que..."
      </p>
    </div>
  );
}

function MemoryCard({
  memory,
  onSelect,
  isSelected,
}: {
  memory: MemoryNode;
  onSelect: () => void;
  isSelected: boolean;
}) {
  const sensitivityColor =
    memory.sensitivity === 'SENSITIVE' || memory.sensitivity === 'sensitive'
      ? 'border-vnbot-amber/40 text-vnbot-amber'
      : memory.sensitivity === 'SECRET' || memory.sensitivity === 'secret'
        ? 'border-vnbot-red/40 text-vnbot-red'
        : 'border-vnbot-line-soft text-vnbot-text-muted';

  return (
    <button
      type="button"
      onClick={onSelect}
      className={`
        w-full text-left p-4 border bg-vnbot-panel-0 hover:bg-vnbot-panel-1 transition-colors
        ${isSelected ? 'border-vnbot-cyan' : 'border-vnbot-line-soft'}
      `}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-mono text-[10px] text-vnbot-cyan uppercase">
              {memory.type}
            </span>
            <span className={`font-mono text-[10px] uppercase px-1.5 py-0.5 border ${sensitivityColor}`}>
              {memory.sensitivity}
            </span>
          </div>
          <div className="font-display text-sm text-vnbot-text truncate">
            {memory.label}
          </div>
          {memory.content && (
            <div className="font-body text-xs text-vnbot-text-muted mt-1 line-clamp-2">
              {memory.content}
            </div>
          )}
        </div>
        <div className="font-mono text-[10px] text-vnbot-text-muted flex-shrink-0">
          {new Date(memory.created_at).toLocaleDateString('es-VE', { day: '2-digit', month: 'short' })}
        </div>
      </div>
    </button>
  );
}

function SearchResultCard({
  result,
  onSelect,
}: {
  result: MemorySearchResult;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className="w-full text-left p-4 border border-vnbot-violet/30 bg-vnbot-panel-0 hover:bg-vnbot-panel-1 transition-colors"
    >
      <div className="flex items-center gap-2 mb-1">
        <span className="font-mono text-[10px] text-vnbot-violet uppercase">
          {result.type}
        </span>
        <span className="font-mono text-[10px] text-vnbot-text-muted">
          rank: {result.rank.toFixed(4)}
        </span>
      </div>
      <div className="font-display text-sm text-vnbot-text mb-1">
        {result.label}
      </div>
      <div
        className="font-body text-xs text-vnbot-text-muted"
        dangerouslySetInnerHTML={{ __html: result.content_snippet }}
      />
    </button>
  );
}

function MemoryInspector({
  memory,
  onClose,
  onDelete,
}: {
  memory: MemoryNode;
  onClose: () => void;
  onDelete: () => void;
}) {
  return (
    <aside className="w-full max-w-md border-l border-vnbot-line-soft bg-vnbot-bg-1 overflow-y-auto">
      <div className="p-4 border-b border-vnbot-line-soft flex items-center justify-between">
        <h3 className="font-display text-sm text-vnbot-cyan uppercase tracking-wider">
          Inspector
        </h3>
        <button
          type="button"
          onClick={onClose}
          className="text-vnbot-text-muted hover:text-vnbot-text"
          aria-label="Close inspector"
        >
          ✕
        </button>
      </div>

      <div className="p-4 space-y-4">
        <div>
          <div className="font-mono text-[10px] text-vnbot-text-muted uppercase mb-1">Label</div>
          <div className="font-display text-base text-vnbot-text">{memory.label}</div>
        </div>

        <div>
          <div className="font-mono text-[10px] text-vnbot-text-muted uppercase mb-1">Content</div>
          <div className="font-body text-sm text-vnbot-text whitespace-pre-wrap bg-vnbot-panel-0 p-3 border border-vnbot-line-soft">
            {memory.content || '(empty)'}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <div className="font-mono text-[10px] text-vnbot-text-muted uppercase mb-1">Type</div>
            <div className="font-body text-sm text-vnbot-text">{memory.type}</div>
          </div>
          <div>
            <div className="font-mono text-[10px] text-vnbot-text-muted uppercase mb-1">Sensitivity</div>
            <div className="font-body text-sm text-vnbot-text">{memory.sensitivity}</div>
          </div>
          <div>
            <div className="font-mono text-[10px] text-vnbot-text-muted uppercase mb-1">Provenance</div>
            <div className="font-body text-sm text-vnbot-text">{memory.provenance}</div>
          </div>
          <div>
            <div className="font-mono text-[10px] text-vnbot-text-muted uppercase mb-1">Authority</div>
            <div className="font-body text-sm text-vnbot-text">{memory.authority}</div>
          </div>
        </div>

        <div>
          <div className="font-mono text-[10px] text-vnbot-text-muted uppercase mb-1">ID</div>
          <div className="font-mono text-xs text-vnbot-text-muted break-all">{memory.id}</div>
        </div>

        <div>
          <div className="font-mono text-[10px] text-vnbot-text-muted uppercase mb-1">Created</div>
          <div className="font-body text-xs text-vnbot-text">
            {new Date(memory.created_at).toLocaleString('es-VE')}
          </div>
        </div>

        <div>
          <div className="font-mono text-[10px] text-vnbot-text-muted uppercase mb-1">Updated</div>
          <div className="font-body text-xs text-vnbot-text">
            {new Date(memory.updated_at).toLocaleString('es-VE')}
          </div>
        </div>

        <button
          type="button"
          onClick={onDelete}
          className="w-full py-2 border border-vnbot-red/40 text-vnbot-red font-mono text-xs uppercase hover:bg-vnbot-red/10"
        >
          ✕ Eliminar (soft delete)
        </button>
      </div>
    </aside>
  );
}

function CreateMemoryForm({
  onSubmit,
  onCancel,
}: {
  onSubmit: (data: { label: string; content: string; type: string; sensitivity: string }) => void;
  onCancel: () => void;
}) {
  const [label, setLabel] = useState('');
  const [content, setContent] = useState('');
  const [type, setType] = useState('note');
  const [sensitivity, setSensitivity] = useState('personal');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!label.trim()) return;
    setIsSubmitting(true);
    await onSubmit({ label: label.trim(), content: content.trim(), type, sensitivity });
    setIsSubmitting(false);
  };

  return (
    <div className="p-4 border-b border-vnbot-line-soft bg-vnbot-panel-0">
      <form onSubmit={handleSubmit} className="max-w-4xl mx-auto space-y-3">
        <div className="font-display text-sm text-vnbot-cyan uppercase tracking-wider mb-2">
          ◆ Nueva memoria
        </div>

        <div>
          <label htmlFor="mem-label" className="font-mono text-[10px] text-vnbot-text-muted uppercase tracking-wider">
            Título
          </label>
          <input
            id="mem-label"
            type="text"
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            placeholder="Ej: Wifi de la oficina"
            autoFocus
            className="w-full mt-1 bg-vnbot-bg-1 border border-vnbot-line-soft px-3 py-2 text-vnbot-text font-body text-sm placeholder:text-vnbot-text-muted focus:border-vnbot-cyan focus:outline-none"
          />
        </div>

        <div>
          <label htmlFor="mem-content" className="font-mono text-[10px] text-vnbot-text-muted uppercase tracking-wider">
            Contenido
          </label>
          <textarea
            id="mem-content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Ej: La contraseña es vnbot123, cambia cada mes"
            rows={3}
            className="w-full mt-1 bg-vnbot-bg-1 border border-vnbot-line-soft px-3 py-2 text-vnbot-text font-body text-sm placeholder:text-vnbot-text-muted focus:border-vnbot-cyan focus:outline-none resize-none"
          />
        </div>

        <div className="flex gap-4">
          <div className="flex-1">
            <label htmlFor="mem-type" className="font-mono text-[10px] text-vnbot-text-muted uppercase tracking-wider">
              Tipo
            </label>
            <select
              id="mem-type"
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="w-full mt-1 bg-vnbot-bg-1 border border-vnbot-line-soft px-3 py-2 text-vnbot-text font-body text-sm focus:border-vnbot-cyan focus:outline-none"
            >
              <option value="note">Nota</option>
              <option value="event">Evento</option>
              <option value="preference">Preferencia</option>
              <option value="task">Tarea</option>
              <option value="contact">Contacto</option>
            </select>
          </div>

          <div className="flex-1">
            <label htmlFor="mem-sensitivity" className="font-mono text-[10px] text-vnbot-text-muted uppercase tracking-wider">
              Sensibilidad
            </label>
            <select
              id="mem-sensitivity"
              value={sensitivity}
              onChange={(e) => setSensitivity(e.target.value)}
              className="w-full mt-1 bg-vnbot-bg-1 border border-vnbot-line-soft px-3 py-2 text-vnbot-text font-body text-sm focus:border-vnbot-cyan focus:outline-none"
            >
              <option value="public">Público</option>
              <option value="personal">Personal</option>
              <option value="sensitive">Sensible</option>
              <option value="secret">Secreto</option>
            </select>
          </div>
        </div>

        <div className="flex gap-2 pt-2">
          <button
            type="submit"
            disabled={!label.trim() || isSubmitting}
            className="px-4 py-2 bg-vnbot-cyan text-vnbot-bg-0 font-mono text-xs uppercase hover:bg-vnbot-cyan/80 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'GUARDANDO...' : '✓ GUARDAR'}
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 border border-vnbot-line-soft text-vnbot-text-muted font-mono text-xs uppercase hover:bg-vnbot-panel-1"
          >
            ✕ Cancelar
          </button>
        </div>
      </form>
    </div>
  );
}
