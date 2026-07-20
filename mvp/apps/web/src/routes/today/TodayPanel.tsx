/**
 * VNBOT Web — Today panel.
 *
 * Operational center: briefing + mascot + chat + reminders.
 */

import { useState, useCallback, useEffect } from 'react';
import { MascotStateView } from '@vnbot/pixelart';
import { TopBar } from '@/components/shell/TopBar';
import { ChatInput } from '@/components/chat/ChatInput';
import { MessageList, type Message } from '@/components/chat/MessageList';
import { ActionProposal } from '@/components/chat/ActionProposal';
import { FileUpload } from '@/components/chat/FileUpload';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';
import { useUIStore } from '@/lib/store/ui';
import { apiClient } from '@/lib/api/client';
import type { ChatResponse, ConfirmResponse, ReminderItem, BriefingResponse } from '@/lib/api/client';

export function TodayPanel() {
  const { mascotState, setMascotState, timezone } = useUIStore();
  const [messages, setMessages] = useState<Message[]>([]);
  const [pendingProposal, setPendingProposal] = useState<ChatResponse | null>(null);
  const [reminders, setReminders] = useState<ReminderItem[]>([]);
  const [briefing, setBriefing] = useState<BriefingResponse | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [briefingResp, remResp] = await Promise.all([
        apiClient.getBriefing(),
        apiClient.listReminders(),
      ]);
      setBriefing(briefingResp);
      setReminders(remResp.items.slice(0, 5));
    } catch {
      // silent — supplementary data
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

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
      void loadData(); // Refresh briefing + reminders
    },
    [setMascotState, loadData],
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

  const handleFileUploaded = useCallback((label: string, _content: string) => {
    const msg: Message = {
      id: crypto.randomUUID(),
      role: 'assistant',
      content: `✓ Archivo procesado y guardado como memoria: "${label}"`,
      timestamp: new Date().toISOString(),
      agent: 'archivist',
      mascotState: 'success',
    };
    setMessages((prev) => [...prev, msg]);
    setMascotState('idle');
    void loadData();
  }, [loadData, setMascotState]);

  const handleFileError = useCallback((error: string) => {
    const msg: Message = {
      id: crypto.randomUUID(),
      role: 'system',
      content: `⚠ Error al procesar archivo: ${error}`,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, msg]);
    setMascotState('warning');
  }, [setMascotState]);

  const handleCompleteReminder = useCallback(async (id: string) => {
    try {
      await apiClient.completeReminder(id);
      setReminders((prev) => prev.filter((r) => r.id !== id));
      void loadData();
    } catch { /* silent */ }
  }, [loadData]);

  return (
    <div className="flex flex-col h-screen">
      <TopBar title="Hoy" />

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Mascot */}
        <div className="flex justify-center py-3">
          <ErrorBoundary fallback={<div className="w-24 h-24 bg-vnbot-panel-0 border border-vnbot-line-soft" />}>
            <MascotStateView agent="guardian" state={mascotState} size={96} interactive />
          </ErrorBoundary>
        </div>

        {/* Briefing card */}
        {briefing && !pendingProposal && messages.length === 0 && (
          <div className="px-4 pb-3">
            <div className="max-w-4xl mx-auto border border-vnbot-cyan/30 bg-vnbot-panel-0 p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="font-pixel text-xs text-vnbot-cyan">{briefing.greeting}</span>
                <span className="font-mono text-[10px] text-vnbot-text-muted">
                  {new Date(briefing.date).toLocaleDateString('es-VE', { weekday: 'long', day: 'numeric', month: 'long' })}
                </span>
              </div>
              <p className="font-body text-sm text-vnbot-text mb-3">{briefing.summary}</p>

              {/* Upcoming reminders */}
              {briefing.upcoming_reminders.length > 0 && (
                <div className="space-y-1">
                  <div className="font-mono text-[10px] text-vnbot-amber uppercase">Próximos recordatorios</div>
                  {briefing.upcoming_reminders.map((r) => (
                    <div key={r.id} className="flex items-center gap-2 text-xs">
                      <span className="text-vnbot-amber">⏱</span>
                      <span className="font-body text-vnbot-text">{r.title}</span>
                      {r.due_at && (
                        <span className="font-mono text-[10px] text-vnbot-text-muted">
                          {new Date(r.due_at).toLocaleString('es-VE', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Recent memories */}
              {briefing.recent_memories.length > 0 && (
                <div className="mt-2 space-y-1">
                  <div className="font-mono text-[10px] text-vnbot-violet uppercase">Memorias recientes</div>
                  <div className="flex gap-2 flex-wrap">
                    {briefing.recent_memories.map((m) => (
                      <span key={m.id} className="font-mono text-[10px] px-2 py-1 border border-vnbot-violet/30 text-vnbot-violet">
                        {m.label}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Reminders bar (when there are reminders) */}
        {reminders.length > 0 && (
          <div className="px-4 pb-2">
            <div className="max-w-4xl mx-auto space-y-1">
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

        {/* File upload */}
        {!pendingProposal && (
          <div className="px-4 pb-2">
            <div className="max-w-4xl mx-auto">
              <FileUpload onMemoryCreated={handleFileUploaded} onError={handleFileError} />
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
