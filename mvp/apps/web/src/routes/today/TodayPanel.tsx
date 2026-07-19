/**
 * VNBOT Web — Today panel.
 *
 * Operational center of VNBOT.
 */

import { useState, useCallback } from 'react';
import { MascotStateView } from '@vnbot/pixelart';
import { TopBar } from '@/components/shell/TopBar';
import { ChatInput } from '@/components/chat/ChatInput';
import { MessageList, type Message } from '@/components/chat/MessageList';
import { ActionProposal } from '@/components/chat/ActionProposal';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';
import { useUIStore } from '@/lib/store/ui';
import type { ChatResponse, ConfirmResponse } from '@/lib/api/client';

export function TodayPanel() {
  const { mascotState, setMascotState, timezone } = useUIStore();
  const [messages, setMessages] = useState<Message[]>([]);
  const [pendingProposal, setPendingProposal] = useState<ChatResponse | null>(null);

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
        agent: 'beacon',
        mascotState: response.status === 'succeeded' ? 'success' : 'error',
      };
      setMessages((prev) => [...prev, msg]);
      setPendingProposal(null);
      setMascotState('idle');
    },
    [setMascotState],
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

  return (
    <div className="flex flex-col h-screen">
      <TopBar title="Hoy" />

      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="flex justify-center py-4">
          <ErrorBoundary fallback={<div className="w-24 h-24 bg-vnbot-panel-0 border border-vnbot-line-soft" />}>
            <MascotStateView
              agent="guardian"
              state={mascotState}
              size={96}
              interactive
            />
          </ErrorBoundary>
        </div>

        <MessageList messages={messages} />

        {pendingProposal && (
          <div className="border-t border-vnbot-line-soft p-4 bg-vnbot-bg-0">
            <div className="max-w-4xl mx-auto">
              <ActionProposal
                proposal={pendingProposal}
                onConfirmed={handleConfirmed}
                onDismiss={handleDismiss}
              />
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
