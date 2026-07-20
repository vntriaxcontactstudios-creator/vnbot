/**
 * VNBOT Web — Lists panel.
 *
 * Simple todo lists with items.
 * Per docs/06 §3 (/lists route).
 */

import { useState, useEffect, useCallback } from 'react';
import { TopBar } from '@/components/shell/TopBar';
import { apiClient } from '@/lib/api/client';

interface ListSummary {
  id: string;
  name: string;
  status: string;
  item_count: number;
  pending_count: number;
  completed_count: number;
  created_at: string;
}

interface ListItem {
  id: string;
  title: string;
  position: number;
  status: string;
  priority: string;
  due_at: string | null;
  created_at: string;
}

interface ListDetail {
  id: string;
  name: string;
  description: string | null;
  status: string;
  created_at: string;
  items: ListItem[];
}

export function ListsPanel() {
  const [lists, setLists] = useState<ListSummary[]>([]);
  const [selectedList, setSelectedList] = useState<ListDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newListName, setNewListName] = useState('');
  const [newItemText, setNewItemText] = useState('');

  const loadLists = useCallback(async () => {
    setIsLoading(true);
    try {
      const resp = await apiClient.request<{ items: ListSummary[]; total: number }>('/lists');
      setLists(resp.items);
    } catch { /* silent */ }
    finally { setIsLoading(false); }
  }, []);

  const loadList = useCallback(async (id: string) => {
    try {
      const detail = await apiClient.request<ListDetail>(`/lists/${id}`);
      setSelectedList(detail);
    } catch { /* silent */ }
  }, []);

  useEffect(() => { void loadLists(); }, [loadLists]);

  const handleCreateList = useCallback(async () => {
    if (!newListName.trim()) return;
    try {
      await apiClient.request('/lists', { method: 'POST', body: JSON.stringify({ name: newListName.trim() }) });
      setNewListName('');
      setShowCreate(false);
      void loadLists();
    } catch { /* silent */ }
  }, [newListName, loadLists]);

  const handleAddItem = useCallback(async () => {
    if (!selectedList || !newItemText.trim()) return;
    try {
      await apiClient.request(`/lists/${selectedList.id}/items`, {
        method: 'POST',
        body: JSON.stringify({ title: newItemText.trim() }),
      });
      setNewItemText('');
      void loadList(selectedList.id);
      void loadLists();
    } catch { /* silent */ }
  }, [selectedList, newItemText, loadList, loadLists]);

  const handleCompleteItem = useCallback(async (itemId: string) => {
    if (!selectedList) return;
    try {
      await apiClient.request(`/lists/${selectedList.id}/items/${itemId}/complete`, { method: 'POST' });
      void loadList(selectedList.id);
      void loadLists();
    } catch { /* silent */ }
  }, [selectedList, loadList, loadLists]);

  const handleDeleteItem = useCallback(async (itemId: string) => {
    if (!selectedList) return;
    try {
      await apiClient.request(`/lists/${selectedList.id}/items/${itemId}`, { method: 'DELETE' });
      void loadList(selectedList.id);
      void loadLists();
    } catch { /* silent */ }
  }, [selectedList, loadList, loadLists]);

  return (
    <div className="flex flex-col h-screen">
      <TopBar title="Listas" />
      <div className="flex-1 flex overflow-hidden">
        {/* Lists sidebar */}
        <div className="w-64 border-r border-vnbot-line-soft bg-vnbot-bg-1 overflow-y-auto">
          <div className="p-3 border-b border-vnbot-line-soft">
            <button
              type="button"
              onClick={() => setShowCreate(!showCreate)}
              className="w-full px-3 py-2 bg-vnbot-cyan text-vnbot-bg-0 font-mono text-xs uppercase hover:bg-vnbot-cyan/80"
            >
              + Nueva lista
            </button>
          </div>
          {showCreate && (
            <div className="p-3 border-b border-vnbot-line-soft flex gap-2">
              <input
                type="text"
                value={newListName}
                onChange={(e) => setNewListName(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAddItem()}
                placeholder="Nombre de lista..."
                className="flex-1 bg-vnbot-panel-0 border border-vnbot-line-soft px-2 py-1 text-vnbot-text text-xs focus:border-vnbot-cyan focus:outline-none"
                autoFocus
              />
              <button type="button" onClick={handleCreateList} className="px-2 py-1 bg-vnbot-green text-vnbot-bg-0 font-mono text-xs">✓</button>
            </div>
          )}
          {isLoading ? (
            <div className="p-4 text-center font-mono text-xs text-vnbot-text-muted animate-pulse">Cargando...</div>
          ) : lists.length === 0 ? (
            <div className="p-4 text-center font-body text-sm text-vnbot-text-muted">Sin listas</div>
          ) : (
            lists.map((lst) => (
              <button
                key={lst.id}
                type="button"
                onClick={() => loadList(lst.id)}
                className={`w-full text-left p-3 border-b border-vnbot-line-soft hover:bg-vnbot-panel-0 ${selectedList?.id === lst.id ? 'bg-vnbot-panel-0 border-l-2 border-l-vnbot-cyan' : ''}`}
              >
                <div className="font-body text-sm text-vnbot-text truncate">{lst.name}</div>
                <div className="font-mono text-[10px] text-vnbot-text-muted mt-0.5">
                  {lst.pending_count} pendientes · {lst.completed_count} hechos
                </div>
              </button>
            ))
          )}
        </div>

        {/* Items */}
        <div className="flex-1 overflow-y-auto p-4">
          {selectedList ? (
            <div className="max-w-2xl mx-auto">
              <h2 className="font-display text-lg text-vnbot-text mb-4">{selectedList.name}</h2>

              {/* Add item */}
              <div className="flex gap-2 mb-4">
                <input
                  type="text"
                  value={newItemText}
                  onChange={(e) => setNewItemText(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddItem()}
                  placeholder="Añadir item..."
                  className="flex-1 bg-vnbot-panel-0 border border-vnbot-line-soft px-3 py-2 text-vnbot-text text-sm placeholder:text-vnbot-text-muted focus:border-vnbot-cyan focus:outline-none"
                />
                <button type="button" onClick={handleAddItem} className="px-4 py-2 bg-vnbot-cyan text-vnbot-bg-0 font-mono text-xs uppercase">+</button>
              </div>

              {/* Items */}
              <div className="space-y-1">
                {selectedList.items.map((item) => (
                  <div key={item.id} className={`flex items-center gap-3 p-3 border border-vnbot-line-soft bg-vnbot-panel-0 ${item.status === 'completed' ? 'opacity-50' : ''}`}>
                    <button
                      type="button"
                      onClick={() => handleCompleteItem(item.id)}
                      className={`w-6 h-6 border-2 flex items-center justify-center ${item.status === 'completed' ? 'border-vnbot-green bg-vnbot-green text-vnbot-bg-0' : 'border-vnbot-line-soft'}`}
                    >
                      {item.status === 'completed' ? '✓' : ''}
                    </button>
                    <span className={`flex-1 font-body text-sm ${item.status === 'completed' ? 'line-through text-vnbot-text-muted' : 'text-vnbot-text'}`}>
                      {item.title}
                    </span>
                    {item.priority !== 'normal' && (
                      <span className="font-mono text-[10px] text-vnbot-amber uppercase">{item.priority}</span>
                    )}
                    <button type="button" onClick={() => handleDeleteItem(item.id)} className="text-vnbot-text-muted hover:text-vnbot-red font-mono text-xs">✕</button>
                  </div>
                ))}
                {selectedList.items.length === 0 && (
                  <div className="text-center py-8 font-body text-sm text-vnbot-text-muted">Lista vacía. Añade items arriba.</div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="font-display text-lg text-vnbot-text-muted mb-2">Selecciona una lista</div>
                <div className="font-body text-sm text-vnbot-text-muted">O crea una nueva con el botón +</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
