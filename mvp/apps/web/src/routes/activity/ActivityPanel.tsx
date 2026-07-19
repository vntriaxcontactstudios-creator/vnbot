/**
 * VNBOT Web — Activity panel.
 *
 * Shows operation history + summary stats.
 * Per docs/06 §3 (/activity route).
 */

import { useState, useEffect, useCallback } from 'react';
import { TopBar } from '@/components/shell/TopBar';
import { apiClient } from '@/lib/api/client';

interface Operation {
  id: string;
  type: string;
  status: string;
  risk_level: string;
  agent_id: string | null;
  input_ref: string | null;
  requires_confirmation: boolean;
  confirmed_at: string | null;
  created_at: string;
  updated_at: string;
}

interface OperationListResponse {
  items: Operation[];
  total: number;
  limit: number;
  offset: number;
}

interface ActivitySummary {
  total_operations: number;
  status_counts: Record<string, number>;
  type_counts: Record<string, number>;
  recent_operations: Operation[];
  generated_at: string;
}

export function ActivityPanel() {
  const [operations, setOperations] = useState<Operation[]>([]);
  const [summary, setSummary] = useState<ActivitySummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('');

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [opsResp, sumResp] = await Promise.all([
        apiClient.request<OperationListResponse>(
          `/operations?limit=100${statusFilter ? `&status=${statusFilter}` : ''}`,
        ),
        apiClient.request<ActivitySummary>('/activity/summary'),
      ]);
      setOperations(opsResp.items);
      setSummary(sumResp);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load activity');
    } finally {
      setIsLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  return (
    <div className="flex flex-col h-screen">
      <TopBar title="Actividad" />

      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-5xl mx-auto space-y-6">
          {summary && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <SummaryCard label="Total operaciones" value={summary.total_operations} color="cyan" />
              <SummaryCard label="Exitosas" value={summary.status_counts['succeeded'] ?? 0} color="green" />
              <SummaryCard label="Fallidas" value={summary.status_counts['failed'] ?? 0} color="red" />
              <SummaryCard
                label="Pendientes"
                value={(summary.status_counts['proposed'] ?? 0) +
                  (summary.status_counts['needs_clarification'] ?? 0)}
                color="amber"
              />
            </div>
          )}

          {summary && Object.keys(summary.status_counts).length > 0 && (
            <div className="border border-vnbot-line-soft bg-vnbot-panel-0 p-4">
              <h3 className="font-display text-sm text-vnbot-cyan uppercase tracking-wider mb-3">
                Desglose por estado
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {Object.entries(summary.status_counts).map(([status, count]) => (
                  <div key={status} className="flex items-center justify-between p-2 bg-vnbot-bg-1 border border-vnbot-line-soft">
                    <span className="font-mono text-xs text-vnbot-text-muted uppercase">
                      {status.replace(/_/g, ' ')}
                    </span>
                    <span className="font-mono text-sm text-vnbot-text">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {summary && Object.keys(summary.type_counts).length > 0 && (
            <div className="border border-vnbot-line-soft bg-vnbot-panel-0 p-4">
              <h3 className="font-display text-sm text-vnbot-violet uppercase tracking-wider mb-3">
                Desglose por tipo
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {Object.entries(summary.type_counts).map(([type, count]) => (
                  <div key={type} className="flex items-center justify-between p-2 bg-vnbot-bg-1 border border-vnbot-line-soft">
                    <span className="font-mono text-xs text-vnbot-text-muted uppercase">
                      {type.replace(/_/g, ' ')}
                    </span>
                    <span className="font-mono text-sm text-vnbot-text">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="border border-vnbot-line-soft bg-vnbot-panel-0">
            <div className="p-4 border-b border-vnbot-line-soft flex items-center justify-between">
              <h3 className="font-display text-sm text-vnbot-amber uppercase tracking-wider">
                Historial de operaciones
              </h3>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="bg-vnbot-bg-1 border border-vnbot-line-soft px-3 py-1 text-vnbot-text font-mono text-xs focus:border-vnbot-cyan focus:outline-none"
                aria-label="Filter by status"
              >
                <option value="">Todos los estados</option>
                <option value="succeeded">Exitosas</option>
                <option value="failed">Fallidas</option>
                <option value="proposed">Pendientes</option>
                <option value="needs_clarification">Requieren clarificación</option>
                <option value="expired">Expiradas</option>
              </select>
            </div>

            {isLoading && (
              <div className="p-8 text-center">
                <div className="font-mono text-xs text-vnbot-text-muted uppercase animate-pulse">
                  Cargando...
                </div>
              </div>
            )}

            {error && (
              <div className="p-4 m-4 border border-vnbot-red/40 bg-vnbot-red/5 text-vnbot-red font-mono text-xs">
                ⚠ {error}
              </div>
            )}

            {!isLoading && !error && operations.length === 0 && (
              <div className="p-8 text-center">
                <div className="font-body text-sm text-vnbot-text-muted">
                  No hay operaciones registradas
                </div>
              </div>
            )}

            {!isLoading && !error && operations.length > 0 && (
              <div className="divide-y divide-vnbot-line-soft">
                {operations.map((op) => (
                  <OperationRow key={op.id} op={op} />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function SummaryCard({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: 'cyan' | 'green' | 'red' | 'amber';
}) {
  const colorClasses = {
    cyan: 'border-vnbot-cyan/40 text-vnbot-cyan',
    green: 'border-vnbot-green/40 text-vnbot-green',
    red: 'border-vnbot-red/40 text-vnbot-red',
    amber: 'border-vnbot-amber/40 text-vnbot-amber',
  };
  return (
    <div className={`border ${colorClasses[color]} bg-vnbot-panel-0 p-4`}>
      <div className="font-mono text-[10px] uppercase tracking-wider opacity-80">
        {label}
      </div>
      <div className={`font-display text-2xl mt-1 ${colorClasses[color].split(' ')[1]}`}>
        {value}
      </div>
    </div>
  );
}

function OperationRow({ op }: { op: Operation }) {
  const statusColor =
    op.status === 'succeeded'
      ? 'text-vnbot-green border-vnbot-green/40'
      : op.status === 'failed'
        ? 'text-vnbot-red border-vnbot-red/40'
        : op.status === 'proposed' || op.status === 'needs_clarification'
          ? 'text-vnbot-amber border-vnbot-amber/40'
          : 'text-vnbot-text-muted border-vnbot-line-soft';

  return (
    <div className="p-4 hover:bg-vnbot-panel-1 transition-colors">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className="font-mono text-[10px] text-vnbot-cyan uppercase">
              {op.type.replace(/_/g, ' ')}
            </span>
            <span className={`font-mono text-[10px] uppercase px-1.5 py-0.5 border ${statusColor}`}>
              {op.status}
            </span>
            <span className="font-mono text-[10px] text-vnbot-text-muted">
              risk: {op.risk_level}
            </span>
            {op.agent_id && (
              <span className="font-mono text-[10px] text-vnbot-violet">
                agent: {op.agent_id}
              </span>
            )}
          </div>
          <div className="font-mono text-xs text-vnbot-text-muted break-all">
            id: {op.id}
          </div>
          {op.input_ref && (
            <div className="font-mono text-[10px] text-vnbot-text-muted mt-1 break-all">
              input_hash: {op.input_ref.slice(0, 32)}...
            </div>
          )}
        </div>
        <div className="font-mono text-[10px] text-vnbot-text-muted flex-shrink-0 text-right">
          <div>{new Date(op.created_at).toLocaleDateString('es-VE', { day: '2-digit', month: 'short' })}</div>
          <div>{new Date(op.created_at).toLocaleTimeString('es-VE', { hour: '2-digit', minute: '2-digit' })}</div>
        </div>
      </div>
    </div>
  );
}
