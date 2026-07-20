/**
 * VNBOT Web — Skills panel (placeholder).
 */

import { TopBar } from '@/components/shell/TopBar';

export function SkillsPanel() {
  return (
    <div className="flex flex-col h-screen">
      <TopBar title="Skills" />
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="font-display text-lg text-vnbot-text-muted mb-2">
            Skills Panel
          </div>
          <div className="font-body text-sm text-vnbot-text-muted">
            38 skills planificadas en 8 categorías. Disponible en Fase 0.7.
          </div>
        </div>
      </div>
    </div>
  );
}
