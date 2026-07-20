/**
 * VNBOT Web — Skills panel.
 *
 * Catalog of 38 planned skills across 8 categories.
 * Per skills/README.md + docs/09 §13.
 */

import { useState } from 'react';
import { TopBar } from '@/components/shell/TopBar';

interface Skill {
  id: string;
  name: string;
  description: string;
  risk: 'Bajo' | 'Medio' | 'Alto';
  autonomy: 0 | 1 | 2 | 3;
  phase: string;
  status: 'planned' | 'available';
}

interface Category {
  name: string;
  icon: string;
  color: string;
  skills: Skill[];
}

const CATEGORIES: Category[] = [
  {
    name: 'Ciencias', icon: '🧪', color: 'cyan',
    skills: [
      { id: 'science.math.solve', name: 'Math Solve', description: 'Resolución de problemas matemáticos simbólicos y numéricos', risk: 'Bajo', autonomy: 2, phase: 'Post-1.0', status: 'planned' },
      { id: 'science.physics.calculate', name: 'Physics Calculate', description: 'Cálculos de física (mecánica, electromagnetismo)', risk: 'Bajo', autonomy: 2, phase: 'Post-1.0', status: 'planned' },
      { id: 'science.chemistry.lookup', name: 'Chemistry Lookup', description: 'Lookup de propiedades químicas, balanceo de ecuaciones', risk: 'Bajo', autonomy: 1, phase: 'Post-1.0', status: 'planned' },
      { id: 'science.units.convert', name: 'Units Convert', description: 'Conversión de unidades (SI, imperiales)', risk: 'Bajo', autonomy: 0, phase: 'Post-1.0', status: 'planned' },
      { id: 'science.statistics.analyze', name: 'Statistics Analyze', description: 'Análisis estadístico descriptivo e inferencial', risk: 'Bajo', autonomy: 2, phase: 'Post-1.0', status: 'planned' },
    ],
  },
  {
    name: 'Planificación', icon: '📅', color: 'amber',
    skills: [
      { id: 'planning.schedule.optimize', name: 'Schedule Optimize', description: 'Optimización de horarios con prioridades y deadlines', risk: 'Medio', autonomy: 2, phase: '0.9', status: 'planned' },
      { id: 'planning.task.breakdown', name: 'Task Breakdown', description: 'Descompone una tarea grande en sub-tareas accionables', risk: 'Bajo', autonomy: 1, phase: '0.9', status: 'planned' },
      { id: 'planning.goal.track', name: 'Goal Track', description: 'Tracking de objetivos de largo plazo con milestones', risk: 'Bajo', autonomy: 2, phase: '0.9', status: 'planned' },
      { id: 'planning.decision.support', name: 'Decision Support', description: 'Decisiones estructuradas (pros/contras, matriz, SWOT)', risk: 'Medio', autonomy: 1, phase: '0.9', status: 'planned' },
      { id: 'planning.pomodoro.run', name: 'Pomodoro Run', description: 'Ejecuta ciclos pomodoro con notificaciones', risk: 'Bajo', autonomy: 3, phase: '0.7', status: 'planned' },
    ],
  },
  {
    name: 'Trading', icon: '💹', color: 'green',
    skills: [
      { id: 'trading.market.lookup', name: 'Market Lookup', description: 'Precios actuales e históricos de mercados (read-only)', risk: 'Medio', autonomy: 0, phase: 'Post-1.0', status: 'planned' },
      { id: 'trading.technical.analyze', name: 'Technical Analyze', description: 'Análisis técnico (RSI, MACD, medias móviles)', risk: 'Alto', autonomy: 0, phase: 'Post-1.0', status: 'planned' },
      { id: 'trading.portfolio.track', name: 'Portfolio Track', description: 'Tracking de portfolio con P&L', risk: 'Medio', autonomy: 0, phase: 'Post-1.0', status: 'planned' },
      { id: 'trading.news.aggregate', name: 'News Aggregate', description: 'Agregación de noticias financieras', risk: 'Bajo', autonomy: 0, phase: 'Post-1.0', status: 'planned' },
    ],
  },
  {
    name: 'Documentos', icon: '📄', color: 'violet',
    skills: [
      { id: 'doc.pdf.extract', name: 'PDF Extract', description: 'Extracción de texto, tablas y metadata de PDFs', risk: 'Bajo', autonomy: 2, phase: '0.8', status: 'planned' },
      { id: 'doc.pdf.summarize', name: 'PDF Summarize', description: 'Resumen de PDFs largos', risk: 'Medio', autonomy: 1, phase: '0.8', status: 'planned' },
      { id: 'doc.ocr.scan', name: 'OCR Scan', description: 'OCR de imágenes escaneadas', risk: 'Medio', autonomy: 2, phase: '0.8', status: 'planned' },
      { id: 'doc.word.parse', name: 'Word Parse', description: 'Parsing y edición de .docx', risk: 'Bajo', autonomy: 2, phase: '0.8', status: 'planned' },
      { id: 'doc.markdown.render', name: 'Markdown Render', description: 'Renderizado de Markdown a HTML/PDF', risk: 'Bajo', autonomy: 2, phase: '0.8', status: 'planned' },
      { id: 'doc.translate', name: 'Translate', description: 'Traducción preservando formato', risk: 'Medio', autonomy: 2, phase: '0.8', status: 'planned' },
    ],
  },
  {
    name: 'Storytelling', icon: '📖', color: 'magenta',
    skills: [
      { id: 'story.plot.generate', name: 'Plot Generate', description: 'Generación de plots narrativos (3 actos, viaje del héroe)', risk: 'Bajo', autonomy: 1, phase: 'Post-1.0', status: 'planned' },
      { id: 'story.character.develop', name: 'Character Develop', description: 'Desarrollo de personajes con arcos y motivaciones', risk: 'Bajo', autonomy: 1, phase: 'Post-1.0', status: 'planned' },
      { id: 'story.continue', name: 'Story Continue', description: 'Continúa una historia manteniendo coherencia', risk: 'Bajo', autonomy: 1, phase: 'Post-1.0', status: 'planned' },
      { id: 'story.dialogue.write', name: 'Dialogue Write', description: 'Escritura de diálogos con voces distintivas', risk: 'Bajo', autonomy: 1, phase: 'Post-1.0', status: 'planned' },
      { id: 'story.outline.structure', name: 'Outline Structure', description: 'Estructura outlines (beat sheets, sinopsis)', risk: 'Bajo', autonomy: 1, phase: 'Post-1.0', status: 'planned' },
    ],
  },
  {
    name: 'Ideación', icon: '💡', color: 'amber',
    skills: [
      { id: 'idea.brainstorm.divergent', name: 'Brainstorm Divergent', description: 'Brainstorming divergente (cantidad > calidad)', risk: 'Bajo', autonomy: 1, phase: '0.9', status: 'planned' },
      { id: 'idea.brainstorm.convergent', name: 'Brainstorm Convergent', description: 'Convergencia y agrupación de ideas', risk: 'Bajo', autonomy: 2, phase: '0.9', status: 'planned' },
      { id: 'idea.mindmap.generate', name: 'Mindmap Generate', description: 'Mapas mentales desde un tema central', risk: 'Bajo', autonomy: 1, phase: '0.9', status: 'planned' },
      { id: 'idea.analogy.find', name: 'Analogy Find', description: 'Búsqueda de analogías cross-domain', risk: 'Bajo', autonomy: 1, phase: '0.9', status: 'planned' },
      { id: 'idea.scamper.apply', name: 'SCAMPER Apply', description: 'Técnica SCAMPER para creatividad', risk: 'Bajo', autonomy: 1, phase: '0.9', status: 'planned' },
    ],
  },
  {
    name: 'Análisis', icon: '🔍', color: 'cyan',
    skills: [
      { id: 'analysis.document.deep', name: 'Document Deep Analysis', description: 'Análisis profundo (argumentos, falacias, sesgos)', risk: 'Medio', autonomy: 1, phase: '0.9', status: 'planned' },
      { id: 'analysis.sentiment.run', name: 'Sentiment Analysis', description: 'Análisis de sentimiento de texto', risk: 'Bajo', autonomy: 2, phase: '0.9', status: 'planned' },
      { id: 'analysis.network.graph', name: 'Network Graph Analysis', description: 'Análisis de redes (centralidad, comunidades)', risk: 'Bajo', autonomy: 2, phase: '0.9', status: 'planned' },
      { id: 'analysis.trend.detect', name: 'Trend Detect', description: 'Detección de tendencias en series temporales', risk: 'Medio', autonomy: 2, phase: '0.9', status: 'planned' },
      { id: 'analysis.comparative.run', name: 'Comparative Analysis', description: 'Análisis comparativo de opciones/datasets', risk: 'Medio', autonomy: 1, phase: '0.9', status: 'planned' },
      { id: 'analysis.risk.assess', name: 'Risk Assess', description: 'Evaluación de riesgos (FMEA, SWOT, PESTLE)', risk: 'Alto', autonomy: 1, phase: '0.9', status: 'planned' },
    ],
  },
  {
    name: 'Referencia', icon: '📚', color: 'blue',
    skills: [
      { id: 'ref.wikipedia.lookup', name: 'Wikipedia Lookup', description: 'Lookup de artículos de Wikipedia', risk: 'Bajo', autonomy: 0, phase: '0.8', status: 'planned' },
      { id: 'ref.dictionary.define', name: 'Dictionary Define', description: 'Definiciones, sinónimos, antónimos', risk: 'Bajo', autonomy: 0, phase: '0.8', status: 'planned' },
      { id: 'ref.currency.convert', name: 'Currency Convert', description: 'Conversión de monedas con tasas actuales', risk: 'Bajo', autonomy: 0, phase: '0.8', status: 'planned' },
      { id: 'ref.timezone.convert', name: 'Timezone Convert', description: 'Conversión de zonas horarias', risk: 'Bajo', autonomy: 0, phase: '0.8', status: 'planned' },
      { id: 'ref.code.snippet', name: 'Code Snippet', description: 'Búsqueda de snippets de código', risk: 'Bajo', autonomy: 0, phase: '0.8', status: 'planned' },
      { id: 'ref.recipe.find', name: 'Recipe Find', description: 'Búsqueda de recetas por ingredientes', risk: 'Bajo', autonomy: 0, phase: '0.8', status: 'planned' },
    ],
  },
];

const RISK_COLORS = { 'Bajo': 'text-vnbot-green', 'Medio': 'text-vnbot-amber', 'Alto': 'text-vnbot-red' };
const AUTONOMY_LABELS = ['answer_only', 'propose', 'internal_actions', 'external_confirmed'];

export function SkillsPanel() {
  const [expanded, setExpanded] = useState<string | null>(null);
  const totalSkills = CATEGORIES.reduce((sum, c) => sum + c.skills.length, 0);

  return (
    <div className="flex flex-col h-screen">
      <TopBar title="Skills" />
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {/* Summary */}
          <div className="grid grid-cols-4 gap-3">
            <div className="border border-vnbot-cyan/30 bg-vnbot-panel-0 p-3">
              <div className="font-mono text-[10px] text-vnbot-cyan uppercase">Total</div>
              <div className="font-display text-2xl text-vnbot-cyan">{totalSkills}</div>
            </div>
            <div className="border border-vnbot-green/30 bg-vnbot-panel-0 p-3">
              <div className="font-mono text-[10px] text-vnbot-green uppercase">Riesgo bajo</div>
              <div className="font-display text-2xl text-vnbot-green">{CATEGORIES.reduce((s,c) => s + c.skills.filter(sk => sk.risk === 'Bajo').length, 0)}</div>
            </div>
            <div className="border border-vnbot-amber/30 bg-vnbot-panel-0 p-3">
              <div className="font-mono text-[10px] text-vnbot-amber uppercase">Riesgo medio</div>
              <div className="font-display text-2xl text-vnbot-amber">{CATEGORIES.reduce((s,c) => s + c.skills.filter(sk => sk.risk === 'Medio').length, 0)}</div>
            </div>
            <div className="border border-vnbot-red/30 bg-vnbot-panel-0 p-3">
              <div className="font-mono text-[10px] text-vnbot-red uppercase">Riesgo alto</div>
              <div className="font-display text-2xl text-vnbot-red">{CATEGORIES.reduce((s,c) => s + c.skills.filter(sk => sk.risk === 'Alto').length, 0)}</div>
            </div>
          </div>

          {/* Categories */}
          {CATEGORIES.map((cat) => (
            <div key={cat.name} className="border border-vnbot-line-soft bg-vnbot-panel-0">
              <button
                type="button"
                onClick={() => setExpanded(expanded === cat.name ? null : cat.name)}
                className="w-full flex items-center justify-between p-4 hover:bg-vnbot-panel-1 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-lg" aria-hidden="true">{cat.icon}</span>
                  <span className="font-display text-sm text-vnbot-text uppercase">{cat.name}</span>
                  <span className="font-mono text-[10px] text-vnbot-text-muted">{cat.skills.length} skills</span>
                </div>
                <span className={`text-vnbot-text-muted transition-transform ${expanded === cat.name ? 'rotate-90' : ''}`}>▶</span>
              </button>

              {expanded === cat.name && (
                <div className="border-t border-vnbot-line-soft divide-y divide-vnbot-line-soft">
                  {cat.skills.map((skill) => (
                    <div key={skill.id} className="p-3 flex items-start gap-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-body text-sm text-vnbot-text">{skill.name}</span>
                          <span className="font-mono text-[10px] text-vnbot-text-muted">{skill.id}</span>
                        </div>
                        <p className="font-body text-xs text-vnbot-text-muted">{skill.description}</p>
                        <div className="flex items-center gap-3 mt-1">
                          <span className={`font-mono text-[10px] ${RISK_COLORS[skill.risk]}`}>{skill.risk}</span>
                          <span className="font-mono text-[10px] text-vnbot-violet">L{skill.autonomy}: {AUTONOMY_LABELS[skill.autonomy]}</span>
                          <span className="font-mono text-[10px] text-vnbot-text-muted">{skill.phase}</span>
                        </div>
                      </div>
                      <span className="font-mono text-[10px] px-2 py-1 border border-vnbot-amber/30 text-vnbot-amber uppercase">Planificada</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}

          {/* Info */}
          <div className="border border-vnbot-violet/30 bg-vnbot-panel-0 p-4">
            <div className="font-mono text-[10px] text-vnbot-violet uppercase mb-2">Sobre las skills</div>
            <p className="font-body text-sm text-vnbot-text-muted">
              Las skills son capacidades versionadas con manifest YAML, input/output JSON Schema, tests y security review.
              En la Fase 0.7 se implementarán las 6 skills iniciales: <span className="text-vnbot-cyan">memory.save</span>,{' '}
              <span className="text-vnbot-cyan">reminder.create</span>, <span className="text-vnbot-cyan">list.manage</span>,{' '}
              <span className="text-vnbot-cyan">briefing.daily</span>, <span className="text-vnbot-cyan">graph.explore</span>,{' '}
              <span className="text-vnbot-cyan">mcp.connect</span>.
              El formato agentskills.io (ADR-0009) las hará compatibles con Hermes, Claude Code y Cursor.
            </p>
            <div className="mt-2 font-mono text-[10px] text-vnbot-text-muted">
              VNBOT NO ejecuta trades. Las skills de trading son solo análisis e información (PRD §6.4).
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
