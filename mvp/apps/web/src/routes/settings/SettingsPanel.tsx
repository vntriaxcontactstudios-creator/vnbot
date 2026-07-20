/**
 * VNBOT Web — Settings panel.
 *
 * Single-user personal settings: theme, timezone, locale, LLM config, providers.
 * Per docs/06 §3 (/settings route).
 * Per ADR-0012: shows all LLM providers with status + test buttons.
 */

import { useState, useEffect, useCallback } from 'react';
import { TopBar } from '@/components/shell/TopBar';
import { useUIStore } from '@/lib/store/ui';
import { apiClient } from '@/lib/api/client';
import type { ProviderInfo, TestProviderResponse } from '@/lib/api/client';

const PROVIDER_LABELS: Record<string, { label: string; docs: string; envVar: string }> = {
  zai: { label: 'Z.AI (glm-4.6)', docs: 'https://z.ai', envVar: 'LLM_ZAI_API_KEY (optional)' },
  openai: { label: 'OpenAI (gpt-4o-mini)', docs: 'https://platform.openai.com/api-keys', envVar: 'OPENAI_API_KEY' },
  anthropic: { label: 'Anthropic (claude-3-5-haiku)', docs: 'https://console.anthropic.com', envVar: 'ANTHROPIC_API_KEY' },
  gemini: { label: 'Google Gemini', docs: 'https://aistudio.google.com/app/apikey', envVar: 'GEMINI_API_KEY' },
  ollama: { label: 'Ollama (local)', docs: 'https://ollama.com', envVar: 'OLLAMA_HOST' },
};

export function SettingsPanel() {
  const { theme, setTheme, timezone, setTimezone, locale, activeAgent, setActiveAgent } = useUIStore();
  const [savedMessage, setSavedMessage] = useState(false);
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [testing, setTesting] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<Record<string, TestProviderResponse>>({});

  const loadProviders = useCallback(async () => {
    try {
      const resp = await apiClient.listLLMProviders();
      setProviders(resp.items);
    } catch {
      /* silent */
    }
  }, []);

  useEffect(() => {
    void loadProviders();
  }, [loadProviders]);

  const handleTest = useCallback(async (providerName: string) => {
    setTesting(providerName);
    try {
      const result = await apiClient.testLLMProvider(providerName);
      setTestResults((prev) => ({ ...prev, [providerName]: result }));
    } catch (e) {
      setTestResults((prev) => ({
        ...prev,
        [providerName]: {
          provider: providerName,
          model: '',
          success: false,
          content: null,
          tokens_used: 0,
          latency_ms: 0,
          error: (e as Error).message,
        },
      }));
    } finally {
      setTesting(null);
    }
  }, []);

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

          {/* LLM Providers — ADR-0012 */}
          <SettingsSection title="Modelos de IA (LLM)" icon="✦">
            <div className="p-3 border border-vnbot-cyan/30 bg-vnbot-cyan/5 text-vnbot-cyan font-mono text-[10px]">
              ℹ Multi-LLM con fallback en cadena. Si el primer provider falla, prueba el siguiente automáticamente.
              Orden: zai → openai → anthropic → gemini → ollama → heurísticas.
            </div>

            {providers.length === 0 ? (
              <div className="p-3 text-center font-mono text-xs text-vnbot-text-muted animate-pulse">
                Cargando providers...
              </div>
            ) : (
              <div className="space-y-2">
                {providers.map((provider) => {
                  const labels = PROVIDER_LABELS[provider.name] || {
                    label: provider.name,
                    docs: '',
                    envVar: '',
                  };
                  const testResult = testResults[provider.name];
                  const isTesting = testing === provider.name;

                  return (
                    <div
                      key={provider.name}
                      className={`p-3 border ${
                        provider.enabled
                          ? 'border-vnbot-green/40 bg-vnbot-green/5'
                          : 'border-vnbot-line-soft bg-vnbot-bg-1'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3 mb-2">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="font-body text-sm text-vnbot-text">{labels.label}</span>
                            {provider.is_default && (
                              <span className="font-mono text-[9px] px-1 bg-vnbot-cyan text-vnbot-bg-0 uppercase">
                                default
                              </span>
                            )}
                          </div>
                          <div className="font-mono text-[10px] text-vnbot-text-muted mt-0.5">
                            {provider.model} · {provider.api_shape} · {provider.base_url}
                          </div>
                        </div>
                        <span
                          className={`font-mono text-[10px] uppercase px-2 py-0.5 border ${
                            provider.enabled
                              ? 'border-vnbot-green text-vnbot-green'
                              : 'border-vnbot-text-muted text-vnbot-text-muted'
                          }`}
                        >
                          {provider.enabled ? '✓ enabled' : '✗ disabled'}
                        </span>
                      </div>

                      {!provider.has_api_key && provider.name !== 'zai' && provider.name !== 'ollama' && (
                        <div className="font-mono text-[10px] text-vnbot-amber mb-2">
                          ⚠ Sin API key. Configura <code className="text-vnbot-text">{labels.envVar}</code> en tu .env
                          {labels.docs && (
                            <>
                              {' '}— obtén una en{' '}
                              <a
                                href={labels.docs}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-vnbot-cyan underline"
                              >
                                {labels.docs}
                              </a>
                            </>
                          )}
                        </div>
                      )}

                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => handleTest(provider.name)}
                          disabled={isTesting || !provider.enabled}
                          className={`px-3 py-1 font-mono text-[10px] uppercase border ${
                            provider.enabled
                              ? 'border-vnbot-cyan text-vnbot-cyan hover:bg-vnbot-cyan hover:text-vnbot-bg-0'
                              : 'border-vnbot-line-soft text-vnbot-text-muted cursor-not-allowed'
                          } ${isTesting ? 'animate-pulse' : ''}`}
                        >
                          {isTesting ? '⏳ Probando...' : '⚡ Probar'}
                        </button>

                        {testResult && (
                          <span
                            className={`font-mono text-[10px] ${
                              testResult.success ? 'text-vnbot-green' : 'text-vnbot-red'
                            }`}
                          >
                            {testResult.success
                              ? `✓ ${testResult.latency_ms}ms · ${testResult.tokens_used} tokens`
                              : `✗ ${testResult.error || 'falló'}`}
                          </span>
                        )}
                      </div>

                      {testResult?.success && testResult.content && (
                        <div className="mt-2 p-2 bg-vnbot-bg-0 border border-vnbot-line-soft font-mono text-[10px] text-vnbot-text-muted">
                          → {testResult.content.slice(0, 200)}
                          {testResult.content.length > 200 && '...'}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            <div className="p-3 border border-vnbot-line-soft bg-vnbot-bg-1 font-mono text-[10px] text-vnbot-text-muted">
              💡 Para habilitar un provider, añade su API key en <code>.env</code> y reinicia el backend.
              El chain fallback usa los providers habilitados en orden de prioridad.
            </div>
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
              <div>VNBOT v0.1.0 — MVP Phase 0.9 (Hermes + Multi-LLM)</div>
              <div>Licencia: MIT</div>
              <div>Stack: React 19 + Vite + FastAPI + SQLAlchemy 2 + APScheduler</div>
              <div>LLM: Z.AI / OpenAI / Anthropic / Gemini / Ollama (chain fallback)</div>
              <div>Hermes: Background review + Memory curation + Skill creation</div>
              <div>PWA: Service Worker + manifest + offline shell</div>
              <div>ADRs: 12 arquitectónicos</div>
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
