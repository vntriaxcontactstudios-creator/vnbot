/**
 * VNBOT Web — Action proposal component.
 *
 * Shows the parsed proposal from /chat endpoint before user confirms.
 * Supports reminder proposals + memory proposals.
 * Editable: user can modify title + due_at before confirming.
 */

import { useState } from 'react';
import { apiClient } from '@/lib/api/client';
import type { ChatResponse, ConfirmResponse } from '@/lib/api/client';
import { useUIStore } from '@/lib/store/ui';

interface ActionProposalProps {
  proposal: ChatResponse;
  onConfirmed: (response: ConfirmResponse) => void;
  onDismiss: () => void;
}

export function ActionProposal({ proposal, onConfirmed, onDismiss }: ActionProposalProps) {
  const { setMascotState } = useUIStore();
  const [isConfirming, setIsConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Editable fields
  const [editedTitle, setEditedTitle] = useState(
    proposal.proposal_reminder?.title ?? '',
  );
  const [editedDueAt, setEditedDueAt] = useState(
    proposal.proposal_reminder?.due_at ?? '',
  );

  const handleConfirm = async () => {
    setIsConfirming(true);
    setError(null);
    setMascotState('processing');

    try {
      const edits: Record<string, unknown> = {};
      if (proposal.proposal_reminder) {
        if (editedTitle !== proposal.proposal_reminder.title) {
          edits.title = editedTitle;
        }
        if (editedDueAt !== proposal.proposal_reminder.due_at) {
          edits.due_at = editedDueAt;
        }
      }

      const response = await apiClient.confirmOperation(
        proposal.operation_id,
        Object.keys(edits).length > 0 ? edits : undefined,
      );
      setMascotState(response.status === 'succeeded' ? 'success' : 'error');
      onConfirmed(response);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
      setMascotState('error');
    } finally {
      setIsConfirming(false);
    }
  };

  const handleDismiss = () => {
    setMascotState('idle');
    onDismiss();
  };

  if (!proposal.parsed) {
    // Parse failure — show suggestion
    return (
      <div className="border border-vnbot-red/40 bg-vnbot-red/5 p-4">
        <div className="flex items-start gap-3">
          <span className="text-vnbot-red text-xl" aria-hidden="true">⚠</span>
          <div className="flex-1">
            <div className="font-display text-sm text-vnbot-red uppercase mb-1">
              No pude interpretar eso
            </div>
            <div className="font-body text-sm text-vnbot-text mb-2">
              {proposal.error}
            </div>
            {proposal.suggestion && (
              <div className="font-body text-xs text-vnbot-text-muted italic">
                {proposal.suggestion}
              </div>
            )}
          </div>
          <button
            type="button"
            onClick={handleDismiss}
            className="text-vnbot-text-muted hover:text-vnbot-text"
            aria-label="Dismiss"
          >
            ✕
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="border border-vnbot-amber/40 bg-vnbot-amber/5 p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="font-display text-sm text-vnbot-amber uppercase tracking-wider">
          ◆ Propuesta · {proposal.intent.replace(/_/g, ' ')}
        </div>
        <button
          type="button"
          onClick={handleDismiss}
          className="text-vnbot-text-muted hover:text-vnbot-text text-sm"
          aria-label="Cancel proposal"
        >
          ✕ Cancelar
        </button>
      </div>

      {/* Reminder proposal */}
      {proposal.proposal_reminder && (
        <div className="space-y-3">
          <div>
            <label
              htmlFor="proposal-title"
              className="font-mono text-[10px] text-vnbot-text-muted uppercase tracking-wider"
            >
              Título
            </label>
            <input
              id="proposal-title"
              type="text"
              value={editedTitle}
              onChange={(e) => setEditedTitle(e.target.value)}
              className="w-full mt-1 bg-vnbot-bg-1 border border-vnbot-line-soft px-3 py-2 text-vnbot-text font-body text-sm focus:border-vnbot-cyan focus:outline-none"
            />
          </div>
          <div>
            <label
              htmlFor="proposal-due-at"
              className="font-mono text-[10px] text-vnbot-text-muted uppercase tracking-wider"
            >
              Fecha y hora
            </label>
            <input
              id="proposal-due-at"
              type="datetime-local"
              value={toDateTimeLocal(editedDueAt)}
              onChange={(e) => setEditedDueAt(fromDateTimeLocal(e.target.value, proposal.proposal_reminder!.timezone))}
              className="w-full mt-1 bg-vnbot-bg-1 border border-vnbot-line-soft px-3 py-2 text-vnbot-text font-body text-sm focus:border-vnbot-cyan focus:outline-none"
            />
            <div className="mt-1 font-mono text-[10px] text-vnbot-text-muted">
              TZ: {proposal.proposal_reminder.timezone} · Recurrencia: {proposal.proposal_reminder.recurrence_frequency}
            </div>
          </div>
        </div>
      )}

      {/* Memory proposal */}
      {proposal.proposal_memory && (
        <div className="space-y-2">
          <div className="font-body text-sm text-vnbot-text">
            {proposal.proposal_memory.content}
          </div>
          {proposal.proposal_memory.tags.length > 0 && (
            <div className="flex gap-2 flex-wrap">
              {proposal.proposal_memory.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-2 py-1 bg-vnbot-violet/20 border border-vnbot-violet/40 text-vnbot-violet font-mono text-[10px] uppercase"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Confidence + notes */}
      <div className="mt-3 pt-3 border-t border-vnbot-line-soft/50">
        <div className="flex items-center gap-3 text-[10px] font-mono text-vnbot-text-muted">
          <span>Confianza: {(proposal.confidence * 100).toFixed(0)}%</span>
          {proposal.notes.map((note, i) => (
            <span key={i}>· {note}</span>
          ))}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mt-3 p-2 bg-vnbot-red/10 border border-vnbot-red/40 text-vnbot-red font-mono text-xs">
          {error}
        </div>
      )}

      {/* Confirm button */}
      <button
        type="button"
        onClick={() => void handleConfirm()}
        disabled={isConfirming}
        className="mt-4 w-full py-3 bg-vnbot-cyan text-vnbot-bg-0 font-mono text-xs uppercase tracking-wider hover:bg-vnbot-cyan/80 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isConfirming ? 'CONFIRMANDO...' : '✓ CONFIRMAR'}
      </button>
    </div>
  );
}

// Helpers for datetime-local input format
function toDateTimeLocal(iso: string): string {
  if (!iso) return '';
  try {
    const d = new Date(iso);
    const pad = (n: number) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  } catch {
    return '';
  }
}

function fromDateTimeLocal(value: string, timezone: string): string {
  if (!value) return '';
  void timezone; // reserved for tz-aware conversion in 0.2+
  try {
    // The input gives us a local datetime. We treat it as being in the proposal's timezone.
    // For simplicity in 0.1, we return ISO with the timezone offset of the proposal.
    const d = new Date(value);
    return d.toISOString();
  } catch {
    return value;
  }
}
