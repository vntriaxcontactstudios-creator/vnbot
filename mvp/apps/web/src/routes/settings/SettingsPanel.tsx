/**
 * VNBOT Web — Settings panel.
 *
 * Single-user personal settings: theme, timezone, locale, LLM config.
 * Per docs/06 §3 (/settings route).
 */

import { useState } from 'react';
import { TopBar } from '@/components/shell/TopBar';
import { useUIStore } from '@/lib/store/ui';
import { apiClient } from '@/lib/api/client';

export function SettingsPanel() {
  const { theme, setTheme, timezone, setTimezone, locale, activeAgent, setActiveAgent } = useUIStore();
  const [savedMessage, setSavedMessage] = useState(false);
  const isDemo = apiClient.isDemoMode();

  const handleSave = () => {
    setSavedMessage(true);
    setTimeout(() => setSavedMessage(false), 2000);
  };

  return (
    <div className="flex flex-col h-screen">
      <TopBar title="Ajustes" />

      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-2xl mx-auto space-y-6">
          {/* Appearance */}
          <SettingsSection title="Apariencia" icon="◐">
            <SettingsRow label="Tema" description="Esquema de colores de la interfaz">
              <select
                value={theme}
                onChange={(e) => setTheme(e.target.value as typeof theme)}
                className="bg-vnbot-bg-1 border border-vnbot-line-soft px-3 py-2 text-vnbot-text font-body text-sm focus:border-vnbot-cyan focus:outline-none"
              >
                <option value="dark">Dark Core (default)</option>
                <option value="amber">Amber Terminal</option>
                <option value="violet">Violet Archive</option>
                <option value="high-contrast">Alto Contraste</option>
              </select>
            </SettingsRow>

            <SettingsRow label="Mascota activa" description="Agente golem mostrado en la interfaz">
              <select
                value={activeAgent}
                onChange={(e) => setActiveAgent(e.target.value as typeof activeAgent)}
                className="bg-vnbot-bg-1 border border-vnbot-line-soft px-3 py-2 text-vnbot-text font-body text-sm focus:border-vnbot-cyan focus:outline-none"
              >
                <option value="guardian">Guardian (Core)</option>
                <option value="chat_assistant">Chat Assistant</option>
                <option value="archivist">Archivist</option>
                <option value="beacon">Beacon</option>
                <option value="navigator">Navigator</option>
                <option value="forge">Forge</option>
                <option value="sentinel">Sentinel</option>
              </select>
            </SettingsRow>
          </SettingsSection>

          {/* Localization */}
          <SettingsSection title="Localización" icon="⌖">
            <SettingsRow label="Zona horaria" description="Para recordatorios y timestamps">
              <select
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                className="bg-vnbot-bg-1 border border-vnbot-line-soft px-3 py-2 text-vnbot-text font-body text-sm focus:border-vnbot-cyan focus:outline-none"
              >
                <option value="America/Caracas">America/Caracas (UTC-4)</option>
                <option value="America/Mexico_City">America/Mexico_City (UTC-6)</option>
                <option value="America/Bogota">America/Bogota (UTC-5)</option>
                <option value="America/Buenos_Aires">America/Buenos_Aires (UTC-3)</option>
                <option value="Europe/Madrid">Europe/Madrid (UTC+1)</option>
                <option value="UTC">UTC</option>
              </select>
            </SettingsRow>

            <SettingsRow label="Idioma" description="Idioma de la interfaz">
              <select
                value={locale}
                onChange={() => {}}
                className="bg-vnbot-bg-1 border border-vnbot-line-soft px-3 py-2 text-vnbot-text font-body text-sm focus:border-vnbot-cyan focus:outline-none"
                disabled
              >
                <option value="es">Español</option>
                <option value="en">English (próximamente)</option>
              </select>
            </SettingsRow>
          </SettingsSection>

          {/* LLM */}
          <SettingsSection title="Modelo de IA" icon="✦">
            {isDemo ? (
              <div className="p-3 border border-vnbot-amber/40 bg-vnbot-amber/5 text-vnbot-amber font-mono text-xs">
                ⚠ Demo mode — sin LLM configurado. Instala VNBOT localmente para usar IA.
              </div>
            ) : (
              <>
                <SettingsRow label="Proveedor" description="LLM para interpretar lenguaje natural">
                  <select
                    className="bg-vnbot-bg-1 border border-vnbot-line-soft px-3 py-2 text-vnbot-text font-body text-sm focus:border-vnbot-cyan focus:outline-none"
                    disabled
                  >
                    <option>Z.AI (glm-4.6) — sin API key</option>
                  </select>
                </SettingsRow>
                <div className="p-3 border border-vnbot-green/30 bg-vnbot-green/5 text-vnbot-green font-mono text-xs">
                  ✓ Sin API key requerida. Fallback heurístico activo cuando LLM no disponible.
                </div>
              </>
            )}
          </SettingsSection>

          {/* Privacy */}
          <SettingsSection title="Privacidad" icon="◈">
            <div className="space-y-2">
              <PrivacyItem
                label="Modo local"
                description="Los datos se guardan solo en este dispositivo"
                enabled
              />
              <PrivacyItem
                label="Cifrado en reposo"
                description="Memorias cifradas con AES-256-GCM"
                enabled
              />
              <PrivacyItem
                label="Telemetría"
                description="No se envían datos a terceros"
                enabled={false}
              />
              <PrivacyItem
                label="Multi-usuario"
                description="VNBOT es single-user — cada quien es dueño de su instancia"
                enabled={false}
              />
            </div>
          </SettingsSection>

          {/* About */}
          <SettingsSection title="Acerca de" icon="ⓘ">
            <div className="space-y-2 font-mono text-xs text-vnbot-text-muted">
              <div>VNBOT v0.1.0 — MVP Phase 0.1</div>
              <div>Licencia: MIT</div>
              <div>Stack: React 19 + Vite + FastAPI + SQLite</div>
              <div>Pixelart: Atropos.js + anime.js + procedural engine</div>
              <div>Tests: 47 unit + 5 E2E passing</div>
              <div>ADRs: 8 arquitectónicos</div>
            </div>
          </SettingsSection>

          {/* Save button */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={handleSave}
              className="px-6 py-2 bg-vnbot-cyan text-vnbot-bg-0 font-mono text-xs uppercase hover:bg-vnbot-cyan/80"
            >
              ✓ Guardar
            </button>
            {savedMessage && (
              <span className="font-mono text-xs text-vnbot-green self-center">
                ✓ Preferencias guardadas
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function SettingsSection({ title, icon, children }: { title: string; icon: string; children: React.ReactNode }) {
  return (
    <div className="border border-vnbot-line-soft bg-vnbot-panel-0">
      <div className="p-4 border-b border-vnbot-line-soft flex items-center gap-2">
        <span className="text-vnbot-cyan text-base" aria-hidden="true">{icon}</span>
        <h3 className="font-display text-sm text-vnbot-text uppercase tracking-wider">{title}</h3>
      </div>
      <div className="p-4 space-y-3">{children}</div>
    </div>
  );
}

function SettingsRow({ label, description, children }: { label: string; description: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <div>
        <div className="font-body text-sm text-vnbot-text">{label}</div>
        <div className="font-mono text-[10px] text-vnbot-text-muted">{description}</div>
      </div>
      {children}
    </div>
  );
}

function PrivacyItem({ label, description, enabled }: { label: string; description: string; enabled: boolean }) {
  return (
    <div className="flex items-center justify-between gap-4 p-2 bg-vnbot-bg-1 border border-vnbot-line-soft">
      <div>
        <div className="font-body text-sm text-vnbot-text">{label}</div>
        <div className="font-mono text-[10px] text-vnbot-text-muted">{description}</div>
      </div>
      <span className={`font-mono text-xs uppercase ${enabled ? 'text-vnbot-green' : 'text-vnbot-text-muted'}`}>
        {enabled ? '✓ Activo' : '✗ Inactivo'}
      </span>
    </div>
  );
}
