/**
 * VNBOT Web — Agents panel.
 *
 * Shows the 7 VNBOT agents with their mascots, roles, and palettes.
 * Per docs/05 §13.2 + VNBOT_SPRITESHEET_REFERENCE.
 */

import { TopBar } from '@/components/shell/TopBar';
import { MascotStateView } from '@vnbot/pixelart';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';
import { useUIStore } from '@/lib/store/ui';
import type { AgentId } from '@vnbot/pixelart';

interface AgentInfo {
  id: AgentId;
  name: string;
  role: string;
  palette: string;
  accessory: string;
  screens: string;
}

const AGENTS: AgentInfo[] = [
  { id: 'guardian', name: 'Guardian', role: 'VNBOT Core, asistente general', palette: 'cyan_graphite', accessory: 'Shield/weapon', screens: 'Landing, Login, Today (default)' },
  { id: 'chat_assistant', name: 'Chat Assistant', role: 'Captura, conversación, onboarding', palette: 'white_chat', accessory: 'Microphone/antenna', screens: 'Chat, Onboarding' },
  { id: 'archivist', name: 'Archivist', role: 'Memoria, búsqueda, grafo', palette: 'violet_archive', accessory: 'Lenses/data crystal', screens: 'Memory, Graph' },
  { id: 'beacon', name: 'Beacon', role: 'Recordatorios y tareas', palette: 'amber_graphite', accessory: 'Beacon antenna/clock', screens: 'Today, Reminders, Lists' },
  { id: 'navigator', name: 'Navigator', role: 'Calendario y agenda', palette: 'cyan_graphite', accessory: 'Compass/route', screens: 'Calendar (future)' },
  { id: 'forge', name: 'Forge', role: 'Creatividad, proyectos, drones', palette: 'magenta_forge', accessory: 'Drones/tools', screens: 'Skills, Projects (future)' },
  { id: 'sentinel', name: 'Sentinel', role: 'Seguridad, bóveda, permisos', palette: 'green_sentinel', accessory: 'Barrier/shield', screens: 'Settings, Integrations, Activity' },
];

export function AgentsPanel() {
  const { activeAgent, setActiveAgent, mascotState } = useUIStore();

  return (
    <div className="flex flex-col h-screen">
      <TopBar title="Agentes" />

      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Active agent selector */}
          <div className="border border-vnbot-cyan/30 bg-vnbot-panel-0 p-4">
            <div className="font-mono text-[10px] text-vnbot-cyan uppercase tracking-wider mb-2">
              Agente activo
            </div>
            <div className="flex items-center gap-4">
              <ErrorBoundary fallback={<div className="w-16 h-16 bg-vnbot-bg-1" />}>
                <MascotStateView agent={activeAgent} state={mascotState} size={64} interactive />
              </ErrorBoundary>
              <div>
                <div className="font-display text-lg text-vnbot-text">
                  {AGENTS.find((a) => a.id === activeAgent)?.name ?? 'Unknown'}
                </div>
                <div className="font-body text-sm text-vnbot-text-muted">
                  {AGENTS.find((a) => a.id === activeAgent)?.role}
                </div>
                <div className="font-mono text-[10px] text-vnbot-cyan mt-1">
                  Palette: {AGENTS.find((a) => a.id === activeAgent)?.palette}
                </div>
              </div>
            </div>
            <div className="mt-3 font-mono text-[10px] text-vnbot-text-muted">
              El agente activo se muestra en el sidebar y en las notificaciones. Cámbialo desde Ajustes o haciendo click en un agente abajo.
            </div>
          </div>

          {/* Agent grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {AGENTS.map((agent) => (
              <button
                key={agent.id}
                type="button"
                onClick={() => setActiveAgent(agent.id)}
                className={`text-left p-4 border transition-colors ${
                  activeAgent === agent.id
                    ? 'border-vnbot-cyan bg-vnbot-cyan/5'
                    : 'border-vnbot-line-soft bg-vnbot-panel-0 hover:bg-vnbot-panel-1'
                }`}
              >
                <div className="flex items-start gap-4">
                  {/* Mascot preview */}
                  <div className="flex-shrink-0">
                    <ErrorBoundary fallback={<div className="w-12 h-12 bg-vnbot-bg-1" />}>
                      <MascotStateView agent={agent.id} state="idle" size={48} interactive={false} />
                    </ErrorBoundary>
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-display text-sm text-vnbot-text">{agent.name}</span>
                      {activeAgent === agent.id && (
                        <span className="font-mono text-[10px] px-1.5 py-0.5 border border-vnbot-cyan text-vnbot-cyan uppercase">
                          Activo
                        </span>
                      )}
                    </div>
                    <div className="font-body text-xs text-vnbot-text-muted mb-2">{agent.role}</div>

                    <div className="space-y-0.5">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-[10px] text-vnbot-text-muted uppercase w-16">Palette</span>
                        <span className="font-mono text-[10px] text-vnbot-cyan">{agent.palette}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-[10px] text-vnbot-text-muted uppercase w-16">Accesorio</span>
                        <span className="font-mono text-[10px] text-vnbot-amber">{agent.accessory}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-[10px] text-vnbot-text-muted uppercase w-16">Pantallas</span>
                        <span className="font-mono text-[10px] text-vnbot-violet">{agent.screens}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>

          {/* Info card */}
          <div className="border border-vnbot-violet/30 bg-vnbot-panel-0 p-4">
            <div className="font-mono text-[10px] text-vnbot-violet uppercase tracking-wider mb-2">
              Sobre los agentes
            </div>
            <p className="font-body text-sm text-vnbot-text-muted">
              Los 7 agentes de VNBOT son variantes del golem informático original, diferenciados por paleta, accesorio y visor.
              Cada agente tiene un rol específico y aparece en las pantallas donde su especialidad es relevante.
              En la Fase 0.7 (Skills y agentes), cada agente tendrá skills asignadas, niveles de autonomía y presupuestos configurables.
            </p>
            <div className="mt-3 flex gap-2 flex-wrap">
              <span className="font-mono text-[10px] px-2 py-1 border border-vnbot-line-soft text-vnbot-text-muted">
                7 agentes
              </span>
              <span className="font-mono text-[10px] px-2 py-1 border border-vnbot-line-soft text-vnbot-text-muted">
                10 estados de mascota
              </span>
              <span className="font-mono text-[10px] px-2 py-1 border border-vnbot-line-soft text-vnbot-text-muted">
                7 paletas
              </span>
              <span className="font-mono text-[10px] px-2 py-1 border border-vnbot-line-soft text-vnbot-text-muted">
                Procedural pixelart (128×128 base)
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
