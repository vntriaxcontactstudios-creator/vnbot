/**
 * VNBOT Web — Chat input component.
 *
 * Captures user text input and submits to /chat endpoint.
 * Shows typing indicator + handles Enter to submit (Shift+Enter for newline).
 */

import { useState, useCallback, type KeyboardEvent } from 'react';
import { apiClient } from '@/lib/api/client';
import type { ChatResponse } from '@/lib/api/client';

interface ChatInputProps {
  onSubmitted: (response: ChatResponse, inputText: string) => void;
  onError: (error: string) => void;
  disabled?: boolean;
  timezone?: string;
}

export function ChatInput({
  onSubmitted,
  onError,
  disabled = false,
  timezone = 'America/Caracas',
}: ChatInputProps) {
  const [text, setText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const submit = useCallback(async () => {
    const trimmed = text.trim();
    if (!trimmed || isSubmitting || disabled) return;

    setIsSubmitting(true);
    try {
      const response = await apiClient.chat(trimmed, timezone);
      onSubmitted(response, trimmed);
      setText('');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      onError(message);
    } finally {
      setIsSubmitting(false);
    }
  }, [text, isSubmitting, disabled, timezone, onSubmitted, onError]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      void submit();
    }
  };

  return (
    <div className="border-t border-vnbot-line-soft bg-vnbot-bg-1 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-end gap-2 bg-vnbot-panel-0 border border-vnbot-line-soft focus-within:border-vnbot-cyan transition-colors">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled || isSubmitting}
            placeholder="Escribe: 'Recuérdame mañana a las 9 revisar VNBOT' o 'Guarda que el wifi es...'"
            rows={2}
            className="flex-1 bg-transparent px-4 py-3 text-vnbot-text font-body text-sm placeholder:text-vnbot-text-muted focus:outline-none resize-none disabled:opacity-50"
            aria-label="Chat input"
          />
          <button
            type="button"
            onClick={() => void submit()}
            disabled={!text.trim() || isSubmitting || disabled}
            className="m-2 px-4 py-2 bg-vnbot-cyan text-vnbot-bg-0 font-mono text-xs uppercase tracking-wider hover:bg-vnbot-cyan/80 disabled:opacity-30 disabled:cursor-not-allowed"
            aria-label="Send message"
          >
            {isSubmitting ? '...' : 'ENVIAR'}
          </button>
        </div>
        <div className="mt-2 text-[10px] font-mono text-vnbot-text-muted">
          Enter para enviar · Shift+Enter para nueva línea · Heurístico (sin LLM)
        </div>
      </div>
    </div>
  );
}
