/**
 * VNBOT Web — Message list.
 *
 * Renders the conversation history with role-based styling.
 * Messages have role: 'user' | 'assistant' | 'system' | 'tool'.
 */

import { useEffect, useRef } from 'react';
import { MascotStateView } from '@vnbot/pixelart';
import type { AgentId, MascotState } from '@vnbot/pixelart';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  timestamp: string;
  agent?: AgentId;
  mascotState?: MascotState;
}

interface MessageListProps {
  messages: Message[];
}

export function MessageList({ messages }: MessageListProps) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center max-w-md">
          <div className="flex justify-center mb-6">
            <ErrorBoundary fallback={<div className="w-32 h-32 bg-vnbot-panel-0 border border-vnbot-line-soft" />}>
              <MascotStateView agent="guardian" state="idle" size={128} interactive />
            </ErrorBoundary>
          </div>
          <h2 className="font-display text-xl text-vnbot-text mb-2">
            Bienvenido a VNBOT
          </h2>
          <p className="font-body text-sm text-vnbot-text-muted mb-6">
            Tu memoria personal open source. Captura ideas, crea recordatorios
            y gestiona tu conocimiento — todo bajo tu control.
          </p>
          <div className="font-mono text-[10px] text-vnbot-cyan uppercase tracking-wider space-y-1">
            <div>→ Recuérdame mañana a las 9 revisar VNBOT</div>
            <div>→ Guarda que el wifi de la oficina es vnbot123</div>
            <div>→ Tengo que enviar el reporte el viernes</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4">
      <div className="max-w-4xl mx-auto space-y-4">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        <div ref={endRef} />
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] bg-vnbot-panel-1 border border-vnbot-line-soft px-4 py-2">
          <div className="font-body text-sm text-vnbot-text whitespace-pre-wrap">
            {message.content}
          </div>
          <div className="mt-1 font-mono text-[10px] text-vnbot-text-muted text-right">
            {new Date(message.timestamp).toLocaleTimeString('es-VE', { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
      </div>
    );
  }

  // Assistant / system / tool messages
  return (
    <div className="flex justify-start gap-3">
      <div className="flex-shrink-0">
        <ErrorBoundary fallback={<div className="w-12 h-12 bg-vnbot-panel-0 border border-vnbot-line-soft" />}>
          <MascotStateView
            agent={message.agent ?? 'guardian'}
            state={message.mascotState ?? 'idle'}
            size={48}
            interactive={false}
          />
        </ErrorBoundary>
      </div>
      <div className="max-w-[80%] bg-vnbot-panel-0 border border-vnbot-line-soft px-4 py-2">
        <div className="font-mono text-[10px] text-vnbot-cyan uppercase tracking-wider mb-1">
          {message.role === 'assistant' ? (message.agent ?? 'vnbot') : message.role}
        </div>
        <div className="font-body text-sm text-vnbot-text whitespace-pre-wrap">
          {message.content}
        </div>
        <div className="mt-1 font-mono text-[10px] text-vnbot-text-muted">
          {new Date(message.timestamp).toLocaleTimeString('es-VE', { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
}
