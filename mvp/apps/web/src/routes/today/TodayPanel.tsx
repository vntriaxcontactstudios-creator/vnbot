/**
 * VNBOT Web — Today panel.
 *
 * Operational center: mascot + chat + reminders summary.
 */

import { useState, useCallback, useEffect } from 'react';
import { MascotStateView } from '@vnbot/pixelart';
import { TopBar } from '@/components/shell/TopBar';
import { ChatInput } from '@/components/chat/ChatInput';
import { MessageList, type Message } from '@/components/chat/MessageList';
import { ActionProposal } from '@/components/chat/ActionProposal';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';
import { useUIStore } from '@/lib/store/ui';
import { apiClient } from '@/lib/api/client';
import type { ChatResponse, ConfirmResponse, ReminderItem } from '@/lib/api/client';

export function TodayPanel() {
  const { mascotState, setMascotState, timezone } = useUIStore();
  const [messages, setMessages] = useState<Message[]>([]);
  const [pendingProposal, setPendingProposal] = useState<ChatResponse | null>(null);
  const [reminders, setReminders] = useState<ReminderItem[]>([]);
  const [reminderCounts, setReminderCounts] = useState({ upcoming: 0, overdue: 0, completed: 0 });

  const loadReminders = useCallback(async () => {
    try {
      const resp = await apiClient.listReminders();
      setReminders(resp.items.slice(0, 5));
      setReminderCounts({ upcoming: resp.upcoming, overdue: resp.overdue, completed: resp.completed });
    } catch {
      // silent fail — reminders are supplementary
    }
  }, []);

  useEffect(() => {
    void loadReminders();
  }, [loadReminders]);

  const handleChatSubmitted = useCallback(
    (response: ChatResponse, inputText: string) => {
      const userMsg: Message = {
        id: crypto.randomUUID(),
        role: 'user',
        content: inputText,
        timestamp: new Date().toISOString(),
      };
      setMascotState(response.parsed ? 'waiting_confirmation' : 'warning');
      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.parsed
          ? `Detecté intención: ${response.intent.replace(/_/g, ' ')}. Confirma la propuesta abajo.`
          : response.error ?? 'No pude interpretar eso.',
        timestamp: new Date().toISOString(),
        agent: 'chat_assistant',
        mascotState: response.parsed ? 'waiting_confirmation' : 'warning',
      };
      setMessages((prev) => [...prev, userMsg, assistantMsg]);
      if (response.requires_confirmation || !response.parsed) {
        setPendingProposal(response);
      }
    },
    [setMascotState],
  );

  const handleConfirmed = useCallback(
    (response: ConfirmResponse) => {
      const msg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content:
          response.status === 'succeeded'
            ? response.entity_type === 'reminder'
              ? `✓ Recordatorio creado para ${response.next_due_at ? new Date(response.next_due_at).toLocaleString('es-VE') : 'próximamente'}`
              : `✓ ${response.entity_type ?? 'Operación'} creada`
            : `✗ Error: ${response.error ?? 'desconocido'}`,
        timestamp: new Date().toISOString(),
        agent: response.entity_type === 'reminder' ? 'beacon' : 'archivist',
        mascotState: response.status === 'succeeded' ? 'success' : 'error',
      };
      setMessages((prev) => [...prev, msg]);
      setPendingProposal(null);
      setMascotState('idle');
      // Reload reminders if a reminder was created
      if (response.entity_type === 'reminder') {
        void loadReminders();
      }
    },
    [setMascotState, loadReminders],
  );

  const handleDismiss = useCallback(() => {
    setPendingProposal(null);
    setMascotState('idle');
  }, [setMascotState]);

  const handleError = useCallback(
    (error: string) => {
      const msg: Message = {
        id: crypto.randomUUID(),
        role: 'system',
        content: `Error: ${error}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, msg]);
      setMascotState('error');
    },
    [setMascotState],
  );

  const handleCompleteReminder = useCallback(async (id: string) => {
    try {
      await apiClient.completeReminder(id);
      setReminders((prev) => prev.filter((r) => r.id !== id));
      setReminderCounts((prev) => ({ ...prev, completed: prev.completed + 1, upcoming: Math.max(0, prev.upcoming - 1) }));
    } catch {
      // silent
    }
  }, []);

  return (
    <div className="flex flex-col h-screen">
      <TopBar title="Hoy" />

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Mascot + Reminder summary */}
        <div className="flex justify-center py-3">
          <ErrorBoundary fallback={<div className="w-24 h-24 bg-vnbot-panel-0 border border-vnbot-line-soft" />}>
            <MascotStateView agent="guardian" state={mascotState} size={96} interactive />
          </ErrorBoundary>
        </div>

        {/* Reminders bar */}
        {reminders.length > 0 && (
          <div className="px-4 pb-2">
            <div className="max-w-4xl mx-auto flex gap-2 flex-wrap">
              {reminderCounts.overdue > 0 && (
                <span className="px-2 py-1 border border-vnbot-red/40 bg-vnbot-red/5 text-vnbot-red font-mono text-[10px] uppercase">
                  ⚠ {reminderCounts.overdue} vencido(s)
                </span>
              )}
              {reminderCounts.upcoming > 0 && (
                <span className="px-2 py-1 border border-vnbot-amber/40 bg-vnbot-amber/5 text-vnbot-amber font-mono text-[10px] uppercase">
                  ⏱ {reminderCounts.upcoming} próximo(s)
                </span>
              )}
              {reminderCounts.completed > 0 && (
                <span className="px-2 py-1 border border-vnbot-green/40 bg-vnbot-green/5 text-vnbot-green font-mono text-[10px] uppercase">
                  ✓ {reminderCounts.completed} completado(s)
                </span>
              )}
            </div>
            <div className="max-w-4xl mx-auto mt-2 space-y-1">
              {reminders.slice(0, 3).map((r) => (
                <div key={r.id} className="flex items-center justify-between p-2 border border-vnbot-line-soft bg-vnbot-panel-0">
                  <div className="flex-1 min-w-0">
                    <span className="font-body text-sm text-vnbot-text truncate">{r.title}</span>
                    {r.next_due_at && (
                      <span className="font-mono text-[10px] text-vnbot-text-muted ml-2">
                        {new Date(r.next_due_at).toLocaleString('es-VE', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}
                      </span>
                    )}
                  </div>
                  <button
                    type="button"
                    onClick={() => void handleCompleteReminder(r.id)}
                    className="px-2 py-1 border border-vnbot-green/40 text-vnbot-green font-mono text-[10px] uppercase hover:bg-vnbot-green/10"
                  >
                    ✓
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        <MessageList messages={messages} />

        {pendingProposal && (
          <div className="border-t border-vnbot-line-soft p-4 bg-vnbot-bg-0">
            <div className="max-w-4xl mx-auto">
              <ActionProposal proposal={pendingProposal} onConfirmed={handleConfirmed} onDismiss={handleDismiss} />
            </div>
          </div>
        )}

        <ChatInput
          onSubmitted={handleChatSubmitted}
          onError={handleError}
          timezone={timezone}
          disabled={pendingProposal?.requires_confirmation}
        />
      </div>
    </div>
  );
}
