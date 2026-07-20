/**
 * VNBOT Web — Integrations panel.
 *
 * MCP server connections + integration status.
 * Per docs/09 (MCP y Skills).
 */

import { TopBar } from '@/components/shell/TopBar';
import { MascotStateView } from '@vnbot/pixelart';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';

interface Integration {
  name: string;
  type: string;
  status: 'disconnected' | 'healthy' | 'planned';
  description: string;
  icon: string;
}

const INTEGRATIONS: Integration[] = [
  { name: 'Z.AI (glm-4.6)', type: 'LLM', status: 'healthy', description: 'Proveedor LLM principal. Sin API key requerida. 30 RPM.', icon: '✦' },
  { name: 'Ollama (local)', type: 'LLM', status: 'disconnected', description: 'LLM local 100% offline. Fallback cuando Z.AI no disponible. 120 RPM.', icon: '◉' },
  { name: 'Graphify', type: 'MCP', status: 'planned', description: 'Knowledge graph local. Indexa metadata de memorias (no plaintext). 71.5x menos tokens.', icon: '⌬' },
  { name: 'Calendar (Google)', type: 'Calendar', status: 'planned', description: 'Sincronización bidireccional con Google Calendar. Scope: calendar.read, calendar.write.', icon: '📅' },
  { name: 'Telegram', type: 'Messaging', status: 'planned', description: 'Bot de Telegram para captura rápida y notificaciones. Official Bot API únicamente.', icon: '✈' },
  { name: 'Gmail (drafts)', type: 'Email', status: 'planned', description: 'Lectura limitada + borradores. NO auto-send en MVP. Scope: email.read, email.draft.', icon: '✉' },
  { name: 'WhatsApp Business', type: 'Messaging', status: 'planned', description: 'WhatsApp Business API oficial. Fase 0.8+. No Baileys/self-bots.', icon: '💬' },
  { name: 'Filesystem', type: 'MCP', status: 'planned', description: 'Acceso a archivos locales. Allowlist de paths. Requiere confirmación fuerte.', icon: '📁' },
  { name: 'Web Fetch', type: 'MCP', status: 'planned', description: 'Búsqueda y scraping web vía Firecrawl. SSRF protection activada.', icon: '🌐' },
];

const STATUS_CONFIG = {
  healthy: { color: 'text-vnbot-green', border: 'border-vnbot-green/40', bg: 'bg-vnbot-green/5', label: 'Conectado' },
  disconnected: { color: 'text-vnbot-text-muted', border: 'border-vnbot-line-soft', bg: 'bg-vnbot-panel-0', label: 'Desconectado' },
  planned: { color: 'text-vnbot-amber', border: 'border-vnbot-amber/30', bg: 'bg-vnbot-amber/5', label: 'Planificado' },
};

export function IntegrationsPanel() {
  return (
    <div className="flex flex-col h-screen">
      <TopBar title="Integraciones" />
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {/* MCP status */}
          <div className="border border-vnbot-cyan/30 bg-vnbot-panel-0 p-4">
            <div className="flex items-center gap-3 mb-2">
              <ErrorBoundary fallback={<div className="w-10 h-10 bg-vnbot-bg-1" />}>
                <MascotStateView agent="sentinel" state="idle" size={40} interactive={false} />
              </ErrorBoundary>
              <div>
                <div className="font-display text-sm text-vnbot-cyan uppercase">MCP Gateway</div>
                <div className="font-body text-xs text-vnbot-text-muted">
                  Model Context Protocol — protocolo, no autorización (ADR-0004)
                </div>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2 mt-3">
              <div className="text-center p-2 border border-vnbot-line-soft bg-vnbot-bg-1">
                <div className="font-display text-lg text-vnbot-green">1</div>
                <div className="font-mono text-[10px] text-vnbot-text-muted uppercase">Activos</div>
              </div>
              <div className="text-center p-2 border border-vnbot-line-soft bg-vnbot-bg-1">
                <div className="font-display text-lg text-vnbot-amber">8</div>
                <div className="font-mono text-[10px] text-vnbot-text-muted uppercase">Planificados</div>
              </div>
              <div className="text-center p-2 border border-vnbot-line-soft bg-vnbot-bg-1">
                <div className="font-display text-lg text-vnbot-text-muted">0</div>
                <div className="font-mono text-[10px] text-vnbot-text-muted uppercase">Revocados</div>
              </div>
            </div>
          </div>

          {/* Integrations list */}
          <div className="space-y-2">
            {INTEGRATIONS.map((int) => {
              const cfg = STATUS_CONFIG[int.status];
              return (
                <div key={int.name} className={`flex items-center gap-3 p-3 border ${cfg.border} ${cfg.bg}`}>
                  {/* Icon */}
                  <div className="flex-shrink-0 w-10 h-10 flex items-center justify-center border border-vnbot-line-soft bg-vnbot-bg-1">
                    <span className="text-lg">{int.icon}</span>
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-body text-sm text-vnbot-text">{int.name}</span>
                      <span className="font-mono text-[10px] px-1.5 py-0.5 border border-vnbot-line-soft text-vnbot-text-muted uppercase">
                        {int.type}
                      </span>
                    </div>
                    <p className="font-body text-xs text-vnbot-text-muted mt-0.5">{int.description}</p>
                  </div>

                  {/* Status */}
                  <div className="flex-shrink-0">
                    <span className={`font-mono text-[10px] uppercase ${cfg.color} flex items-center gap-1`}>
                      {int.status === 'healthy' && <span className="w-2 h-2 bg-vnbot-green inline-block" />}
                      {int.status === 'planned' && <span className="w-2 h-2 bg-vnbot-amber inline-block" />}
                      {int.status === 'disconnected' && <span className="w-2 h-2 bg-vnbot-text-muted inline-block" />}
                      {cfg.label}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Security info */}
          <div className="border border-vnbot-red/20 bg-vnbot-red/5 p-4">
            <div className="font-mono text-[10px] text-vnbot-red uppercase mb-2">⚠ Seguridad MCP</div>
            <ul className="space-y-1 font-body text-xs text-vnbot-text-muted">
              <li>• Las tools descubiertas vía MCP nunca se auto-habilitan (DISCOVERED → REVIEW_REQUIRED → ENABLED)</li>
              <li>• <code className="text-vnbot-amber">email.send</code>, <code className="text-vnbot-amber">filesystem.write</code> requieren confirmación fuerte</li>
              <li>• Un agente no hereda los permisos del usuario — solo recibe los explícitamente asignados</li>
              <li>• Scopes: <code className="text-vnbot-cyan">graph.read</code>, <code className="text-vnbot-cyan">memory.write</code>, <code className="text-vnbot-cyan">calendar.read</code>, etc.</li>
              <li>• Deny by default. No explicit policy → deny or wait for confirmation</li>
              <li>• No APIs no oficiales (Baileys, self-bots). Solo APIs oficiales.</li>
            </ul>
          </div>

          {/* Hermes info */}
          <div className="border border-vnbot-violet/30 bg-vnbot-panel-0 p-4">
            <div className="font-mono text-[10px] text-vnbot-violet uppercase mb-2">Hermes Agent (ADR-0009)</div>
            <p className="font-body text-xs text-vnbot-text-muted">
              En la Fase 0.7, VNBOT adoptará el formato <span className="text-vnbot-violet">agentskills.io</span> y el catálogo MCP de Hermes,
              permitiendo instalar skills comunitarias con <code className="text-vnbot-cyan">vnbot mcp install &lt;name&gt;</code>.
              El learning loop de Hermes (background review fork, skill creation, memory curation) se porteará selectivamente.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
