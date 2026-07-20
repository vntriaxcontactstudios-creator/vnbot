/**
 * VNBOT Web — Reminders panel.
 *
 * Full reminders management: list, complete, snooze, cancel.
 */

import { useState, useEffect, useCallback } from 'react';
import { TopBar } from '@/components/shell/TopBar';
import { apiClient } from '@/lib/api/client';
import type { ReminderItem } from '@/lib/api/client';

export function RemindersPanel() {
  const [reminders, setReminders] = useState<ReminderItem[]>([]);
  const [counts, setCounts] = useState({ total: 0, upcoming: 0, overdue: 0, completed: 0 });
  const [filter, setFilter] = useState<'all' | 'active' | 'overdue' | 'completed'>('all');
  const [isLoading, setIsLoading] = useState(true);

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      const resp = await apiClient.listReminders();
      setReminders(resp.items);
      setCounts({ total: resp.total, upcoming: resp.upcoming, overdue: resp.overdue, completed: resp.completed });
    } catch { /* silent */ }
    finally { setIsLoading(false); }
  }, []);

  useEffect(() => { void load(); }, [load]);

  const handleComplete = useCallback(async (id: string) => {
    try { await apiClient.completeReminder(id); void load(); } catch { /* silent */ }
  }, [load]);

  const handleSnooze = useCallback(async (id: string) => {
    try { await apiClient.snoozeReminder(id, 1); void load(); } catch { /* silent */ }
  }, [load]);

  const handleCancel = useCallback(async (id: string) => {
    if (!confirm('¿Cancelar este recordatorio?')) return;
    try { await apiClient.cancelReminder(id); void load(); } catch { /* silent */ }
  }, [load]);

  const now = new Date();
  const filtered = reminders.filter((r) => {
    if (filter === 'active') return r.status === 'active';
    if (filter === 'overdue') return r.status === 'active' && r.next_due_at && new Date(r.next_due_at) < now;
    if (filter === 'completed') return r.status === 'completed';
    return true;
  });

  return (
    <div className="flex flex-col h-screen">
      <TopBar title="Recordatorios" />

      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {/* Summary cards */}
          <div className="grid grid-cols-4 gap-2">
            <div className={`border p-3 cursor-pointer ${filter === 'all' ? 'border-vnbot-cyan bg-vnbot-cyan/5' : 'border-vnbot-line-soft bg-vnbot-panel-0'}`} onClick={() => setFilter('all')}>
              <div className="font-mono text-[10px] text-vnbot-text-muted uppercase">Total</div>
              <div className="font-display text-xl text-vnbot-text">{counts.total}</div>
            </div>
            <div className={`border p-3 cursor-pointer ${filter === 'active' ? 'border-vnbot-amber bg-vnbot-amber/5' : 'border-vnbot-line-soft bg-vnbot-panel-0'}`} onClick={() => setFilter('active')}>
              <div className="font-mono text-[10px] text-vnbot-amber uppercase">Próximos</div>
              <div className="font-display text-xl text-vnbot-amber">{counts.upcoming}</div>
            </div>
            <div className={`border p-3 cursor-pointer ${filter === 'overdue' ? 'border-vnbot-red bg-vnbot-red/5' : 'border-vnbot-line-soft bg-vnbot-panel-0'}`} onClick={() => setFilter('overdue')}>
              <div className="font-mono text-[10px] text-vnbot-red uppercase">Vencidos</div>
              <div className="font-display text-xl text-vnbot-red">{counts.overdue}</div>
            </div>
            <div className={`border p-3 cursor-pointer ${filter === 'completed' ? 'border-vnbot-green bg-vnbot-green/5' : 'border-vnbot-line-soft bg-vnbot-panel-0'}`} onClick={() => setFilter('completed')}>
              <div className="font-mono text-[10px] text-vnbot-green uppercase">Hechos</div>
              <div className="font-display text-xl text-vnbot-green">{counts.completed}</div>
            </div>
          </div>

          {/* Reminders list */}
          {isLoading ? (
            <div className="text-center py-8 font-mono text-xs text-vnbot-text-muted animate-pulse">Cargando...</div>
          ) : filtered.length === 0 ? (
            <div className="text-center py-12">
              <div className="font-body text-sm text-vnbot-text-muted">Sin recordatorios en esta categoría</div>
            </div>
          ) : (
            <div className="space-y-2">
              {filtered.map((r) => {
                const isOverdue = r.status === 'active' && r.next_due_at && new Date(r.next_due_at) < now;
                const isCompleted = r.status === 'completed';
                const isRecurring = r.recurrence_frequency !== 'none';

                return (
                  <div key={r.id} className={`flex items-center gap-3 p-3 border bg-vnbot-panel-0 ${isOverdue ? 'border-vnbot-red/40' : isCompleted ? 'border-vnbot-green/30 opacity-60' : 'border-vnbot-line-soft'}`}>
                    {/* Status icon */}
                    <div className="flex-shrink-0">
                      {isCompleted ? (
                        <span className="text-vnbot-green text-lg">✓</span>
                      ) : isOverdue ? (
                        <span className="text-vnbot-red text-lg">⚠</span>
                      ) : (
                        <span className="text-vnbot-amber text-lg">⏱</span>
                      )}
                    </div>

                    {/* Title + meta */}
                    <div className="flex-1 min-w-0">
                      <div className={`font-body text-sm ${isCompleted ? 'line-through text-vnbot-text-muted' : 'text-vnbot-text'}`}>
                        {r.title}
                      </div>
                      <div className="flex items-center gap-2 mt-0.5">
                        {r.next_due_at && (
                          <span className={`font-mono text-[10px] ${isOverdue ? 'text-vnbot-red' : 'text-vnbot-text-muted'}`}>
                            {new Date(r.next_due_at).toLocaleString('es-VE', { weekday: 'short', day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}
                          </span>
                        )}
                        {isRecurring && (
                          <span className="font-mono text-[10px] text-vnbot-violet uppercase">↻ {r.recurrence_frequency}</span>
                        )}
                        {r.priority !== 'normal' && (
                          <span className="font-mono text-[10px] text-vnbot-amber uppercase">{r.priority}</span>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    {!isCompleted && (
                      <div className="flex gap-1 flex-shrink-0">
                        <button type="button" onClick={() => handleComplete(r.id)} title="Completar" className="w-8 h-8 flex items-center justify-center border border-vnbot-green/40 text-vnbot-green hover:bg-vnbot-green/10">✓</button>
                        <button type="button" onClick={() => handleSnooze(r.id)} title="Posponer 1h" className="w-8 h-8 flex items-center justify-center border border-vnbot-amber/40 text-vnbot-amber hover:bg-vnbot-amber/10">⏰</button>
                        <button type="button" onClick={() => handleCancel(r.id)} title="Cancelar" className="w-8 h-8 flex items-center justify-center border border-vnbot-red/40 text-vnbot-red hover:bg-vnbot-red/10">✕</button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
