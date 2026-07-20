/**
 * VNBOT Web — Graph panel.
 *
 * Visual memory graph with SVG drag & drop.
 * Per docs/06 §3 (/graph route) + VNBOT_SPRITESHEET_REFERENCE §7:
 * - Max 12 visible nodes (hard cap for legibility)
 * - 3 connection types: tag (magenta), type (cyan), time (amber)
 * - Drag & drop with pointer events (touch + mouse)
 * - List alternative view for accessibility
 *
 * Per docs/03 §40:
 * - Default max depth: 3
 * - Top-K max: 50 (default 20)
 * - Max nodes per query: 100
 */

import { useState, useEffect, useCallback, useRef, type PointerEvent as ReactPointerEvent } from 'react';
import { TopBar } from '@/components/shell/TopBar';
import { apiClient, RELATION_TYPES } from '@/lib/api/client';
import type { GraphNode, GraphEdge } from '@/lib/api/client';

const MAX_NODES = 12;
const VIEWBOX = 100;

const TYPE_COLORS: Record<string, string> = {
  note: '#20DCE8',
  event: '#FFC83D',
  preference: '#8A6CFF',
  task: '#5BDF82',
  contact: '#D94BE3',
  note_personal: '#20DCE8',
};

const RELATION_COLORS: Record<string, string> = {
  KNOWS: '#D94BE3',
  PREFERS: '#8A6CFF',
  RELATED_TO: '#20DCE8',
  WORKS_ON: '#FFC83D',
  DEPENDS_ON: '#FF5C6D',
  REMINDER_FOR: '#FFC83D',
  HAPPENS_AT: '#4D9DFF',
  SUPERSEDES: '#5BDF82',
  CONTRADICTS: '#FF5C6D',
  DERIVED_FROM: '#8A6CFF',
  ASSIGNED_TO: '#20DCE8',
  MENTIONED_IN: '#91A9BE',
  LOCATED_AT: '#4D9DFF',
};

export function GraphPanel() {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [positions, setPositions] = useState<Record<string, { x: number; y: number }>>({});
  const [draggingId, setDraggingId] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [showAddEdge, setShowAddEdge] = useState(false);
  const [edgeSource, setEdgeSource] = useState('');
  const [edgeTarget, setEdgeTarget] = useState('');
  const [edgeRelation, setEdgeRelation] = useState('RELATED_TO');
  const [isLoading, setIsLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'graph' | 'list'>('graph');
  const svgRef = useRef<SVGSVGElement>(null);

  const loadGraph = useCallback(async () => {
    setIsLoading(true);
    try {
      const resp = await apiClient.getGraph(50);
      // Limit to MAX_NODES for visualization
      const limited = resp.nodes.slice(0, MAX_NODES);
      setNodes(limited);
      setEdges(resp.edges.filter(e =>
        limited.some(n => n.id === e.source) && limited.some(n => n.id === e.target),
      ));

      // Generate initial layout (concentric rings)
      const newPositions: Record<string, { x: number; y: number }> = {};
      limited.forEach((node, i) => {
        if (i === 0) {
          newPositions[node.id] = { x: 50, y: 50 };
        } else {
          const ring = Math.ceil(i / 5);
          const inRing = (i - 1) % 5;
          const radius = 22 + ring * 18;
          const angle = (inRing / 5) * 2 * Math.PI + ring * 0.3;
          newPositions[node.id] = {
            x: 50 + Math.cos(angle) * radius,
            y: 50 + Math.sin(angle) * radius * 0.6, // ellipse
          };
        }
      });
      setPositions(newPositions);
    } catch {
      // silent
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadGraph();
  }, [loadGraph]);

  // Drag & drop
  const handlePointerDown = useCallback((e: ReactPointerEvent<SVGGElement>, nodeId: string) => {
    e.stopPropagation();
    setDraggingId(nodeId);
    (e.target as Element).setPointerCapture(e.pointerId);
  }, []);

  const handlePointerMove = useCallback((e: ReactPointerEvent<SVGSVGElement>) => {
    if (!draggingId || !svgRef.current) return;
    const rect = svgRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * VIEWBOX;
    const y = ((e.clientY - rect.top) / rect.height) * VIEWBOX;
    // Clamp to viewBox
    setPositions((prev) => ({
      ...prev,
      [draggingId]: { x: Math.max(5, Math.min(95, x)), y: Math.max(5, Math.min(95, y)) },
    }));
  }, [draggingId]);

  const handlePointerUp = useCallback(() => {
    setDraggingId(null);
  }, []);

  const handleAddEdge = useCallback(async () => {
    if (!edgeSource || !edgeTarget || edgeSource === edgeTarget) return;
    try {
      await apiClient.createEdge(edgeSource, edgeTarget, edgeRelation);
      setShowAddEdge(false);
      setEdgeSource('');
      setEdgeTarget('');
      void loadGraph();
    } catch {
      // silent
    }
  }, [edgeSource, edgeTarget, edgeRelation, loadGraph]);

  const handleDeleteEdge = useCallback(async (edgeId: string) => {
    try {
      await apiClient.deleteEdge(edgeId);
      setEdges((prev) => prev.filter((e) => e.id !== edgeId));
    } catch {
      // silent
    }
  }, []);

  return (
    <div className="flex flex-col h-screen">
      <TopBar title="Grafo" />

      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Toolbar */}
          <div className="p-3 border-b border-vnbot-line-soft bg-vnbot-bg-1 flex items-center gap-2">
            <button
              type="button"
              onClick={() => setViewMode('graph')}
              className={`px-3 py-1 font-mono text-[10px] uppercase ${viewMode === 'graph' ? 'bg-vnbot-cyan text-vnbot-bg-0' : 'border border-vnbot-line-soft text-vnbot-text-muted'}`}
            >
              ◐ Grafo
            </button>
            <button
              type="button"
              onClick={() => setViewMode('list')}
              className={`px-3 py-1 font-mono text-[10px] uppercase ${viewMode === 'list' ? 'bg-vnbot-cyan text-vnbot-bg-0' : 'border border-vnbot-line-soft text-vnbot-text-muted'}`}
            >
              ☰ Lista
            </button>
            <span className="font-mono text-[10px] text-vnbot-text-muted ml-2">
              {nodes.length} nodos · {edges.length} aristas
            </span>
            <button
              type="button"
              onClick={() => setShowAddEdge(!showAddEdge)}
              className="ml-auto px-3 py-1 bg-vnbot-violet text-vnbot-bg-0 font-mono text-[10px] uppercase hover:bg-vnbot-violet/80"
            >
              + Relación
            </button>
          </div>

          {/* Add edge form */}
          {showAddEdge && (
            <div className="p-3 border-b border-vnbot-line-soft bg-vnbot-panel-0 flex gap-2 items-end">
              <div>
                <label className="font-mono text-[10px] text-vnbot-text-muted uppercase block mb-1">Origen</label>
                <select value={edgeSource} onChange={(e) => setEdgeSource(e.target.value)} className="bg-vnbot-bg-1 border border-vnbot-line-soft px-2 py-1 text-vnbot-text text-xs">
                  <option value="">Seleccionar...</option>
                  {nodes.map((n) => <option key={n.id} value={n.id}>{n.label}</option>)}
                </select>
              </div>
              <div>
                <label className="font-mono text-[10px] text-vnbot-text-muted uppercase block mb-1">Relación</label>
                <select value={edgeRelation} onChange={(e) => setEdgeRelation(e.target.value)} className="bg-vnbot-bg-1 border border-vnbot-line-soft px-2 py-1 text-vnbot-text text-xs">
                  {RELATION_TYPES.map((r) => <option key={r} value={r}>{r}</option>)}
                </select>
              </div>
              <div>
                <label className="font-mono text-[10px] text-vnbot-text-muted uppercase block mb-1">Destino</label>
                <select value={edgeTarget} onChange={(e) => setEdgeTarget(e.target.value)} className="bg-vnbot-bg-1 border border-vnbot-line-soft px-2 py-1 text-vnbot-text text-xs">
                  <option value="">Seleccionar...</option>
                  {nodes.map((n) => <option key={n.id} value={n.id}>{n.label}</option>)}
                </select>
              </div>
              <button type="button" onClick={handleAddEdge} disabled={!edgeSource || !edgeTarget || edgeSource === edgeTarget} className="px-3 py-1 bg-vnbot-cyan text-vnbot-bg-0 font-mono text-[10px] uppercase disabled:opacity-30">✓ Crear</button>
              <button type="button" onClick={() => setShowAddEdge(false)} className="px-3 py-1 border border-vnbot-line-soft text-vnbot-text-muted font-mono text-[10px] uppercase">✕</button>
            </div>
          )}

          {/* Graph view */}
          {viewMode === 'graph' && !isLoading && (
            <div className="flex-1 relative overflow-hidden">
              <svg
                ref={svgRef}
                viewBox={`0 0 ${VIEWBOX} ${VIEWBOX}`}
                className="w-full h-full"
                style={{ touchAction: 'none' }}
                onPointerMove={handlePointerMove}
                onPointerUp={handlePointerUp}
              >
                {/* Edges */}
                {edges.map((edge) => {
                  const source = positions[edge.source];
                  const target = positions[edge.target];
                  if (!source || !target) return null;
                  const color = RELATION_COLORS[edge.relation] || '#2A6F8E';
                  return (
                    <g key={edge.id} onClick={() => handleDeleteEdge(edge.id)} className="cursor-pointer">
                      <line
                        x1={source.x} y1={source.y}
                        x2={target.x} y2={target.y}
                        stroke={color}
                        strokeWidth={0.3}
                        strokeOpacity={0.6}
                      />
                      {/* Relation label */}
                      <text
                        x={(source.x + target.x) / 2}
                        y={(source.y + target.y) / 2 - 0.5}
                        fill={color}
                        fontSize={1.5}
                        textAnchor="middle"
                        style={{ pointerEvents: 'none' }}
                      >
                        {edge.relation.replace(/_/g, ' ')}
                      </text>
                    </g>
                  );
                })}

                {/* Nodes */}
                {nodes.map((node) => {
                  const pos = positions[node.id];
                  if (!pos) return null;
                  const color = TYPE_COLORS[node.type] || '#20DCE8';
                  const isSelected = selectedNode?.id === node.id;
                  return (
                    <g
                      key={node.id}
                      transform={`translate(${pos.x}, ${pos.y})`}
                      onPointerDown={(e) => handlePointerDown(e, node.id)}
                      onClick={() => setSelectedNode(node)}
                      className="cursor-grab"
                      style={{ touchAction: 'none' }}
                    >
                      {/* Node circle */}
                      <circle
                        r={3}
                        fill={color}
                        fillOpacity={0.3}
                        stroke={color}
                        strokeWidth={isSelected ? 0.5 : 0.3}
                      />
                      {/* Label */}
                      <text
                        y={5}
                        fill="#ECF6FF"
                        fontSize={2}
                        textAnchor="middle"
                        style={{ pointerEvents: 'none', userSelect: 'none' }}
                      >
                        {node.label.length > 12 ? node.label.slice(0, 11) + '…' : node.label}
                      </text>
                      {/* Type badge */}
                      <text
                        y={-4}
                        fill={color}
                        fontSize={1.2}
                        textAnchor="middle"
                        style={{ pointerEvents: 'none', userSelect: 'none' }}
                      >
                        {node.type.toUpperCase()}
                      </text>
                    </g>
                  );
                })}
              </svg>

              {/* Drag hint */}
              <div className="absolute bottom-2 left-2 font-mono text-[10px] text-vnbot-text-muted">
                Arrastra los nodos · Click para seleccionar · Click arista para eliminar
              </div>
            </div>
          )}

          {/* List view (accessibility alternative) */}
          {viewMode === 'list' && !isLoading && (
            <div className="flex-1 overflow-y-auto p-4">
              <div className="max-w-4xl mx-auto space-y-4">
                <div>
                  <h3 className="font-display text-sm text-vnbot-cyan uppercase mb-2">Nodos ({nodes.length})</h3>
                  <div className="space-y-1">
                    {nodes.map((n) => (
                      <div key={n.id} className="flex items-center gap-2 p-2 border border-vnbot-line-soft bg-vnbot-panel-0">
                        <span className="w-3 h-3 rounded-full" style={{ background: TYPE_COLORS[n.type] || '#20DCE8' }} />
                        <span className="font-body text-sm text-vnbot-text">{n.label}</span>
                        <span className="font-mono text-[10px] text-vnbot-text-muted ml-auto">{n.type}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h3 className="font-display text-sm text-vnbot-violet uppercase mb-2">Relaciones ({edges.length})</h3>
                  <div className="space-y-1">
                    {edges.map((e) => {
                      const source = nodes.find((n) => n.id === e.source);
                      const target = nodes.find((n) => n.id === e.target);
                      return (
                        <div key={e.id} className="flex items-center gap-2 p-2 border border-vnbot-line-soft bg-vnbot-panel-0">
                          <span className="font-body text-sm text-vnbot-text">{source?.label ?? '?'}</span>
                          <span className="font-mono text-[10px] px-1.5 py-0.5 border" style={{ color: RELATION_COLORS[e.relation] || '#91A9BE', borderColor: RELATION_COLORS[e.relation] || '#91A9BE' }}>
                            {e.relation}
                          </span>
                          <span className="font-body text-sm text-vnbot-text">{target?.label ?? '?'}</span>
                          <button type="button" onClick={() => handleDeleteEdge(e.id)} className="ml-auto text-vnbot-red font-mono text-[10px]">✕</button>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          )}

          {isLoading && (
            <div className="flex-1 flex items-center justify-center">
              <div className="font-mono text-xs text-vnbot-text-muted uppercase animate-pulse">Cargando grafo...</div>
            </div>
          )}

          {!isLoading && nodes.length === 0 && (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <div className="font-body text-sm text-vnbot-text-muted">Sin memorias para grafar</div>
                <div className="font-mono text-[10px] text-vnbot-text-muted mt-1">Crea memorias primero desde /memory o /today</div>
              </div>
            </div>
          )}
        </div>

        {/* Node inspector */}
        {selectedNode && (
          <aside className="w-full max-w-xs border-l border-vnbot-line-soft bg-vnbot-bg-1 p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-display text-sm text-vnbot-cyan uppercase">Nodo</h3>
              <button type="button" onClick={() => setSelectedNode(null)} className="text-vnbot-text-muted">✕</button>
            </div>
            <div className="space-y-2">
              <div>
                <span className="font-mono text-[10px] text-vnbot-text-muted uppercase">Label</span>
                <p className="font-body text-sm text-vnbot-text">{selectedNode.label}</p>
              </div>
              <div>
                <span className="font-mono text-[10px] text-vnbot-text-muted uppercase">Tipo</span>
                <p className="font-body text-sm text-vnbot-text">{selectedNode.type}</p>
              </div>
              <div>
                <span className="font-mono text-[10px] text-vnbot-text-muted uppercase">Sensibilidad</span>
                <p className="font-body text-sm text-vnbot-text">{selectedNode.sensitivity}</p>
              </div>
              <div>
                <span className="font-mono text-[10px] text-vnbot-text-muted uppercase">ID</span>
                <p className="font-mono text-xs text-vnbot-text-muted break-all">{selectedNode.id}</p>
              </div>
              <div>
                <span className="font-mono text-[10px] text-vnbot-text-muted uppercase">Creado</span>
                <p className="font-body text-xs text-vnbot-text">{new Date(selectedNode.created_at).toLocaleString('es-VE')}</p>
              </div>
              {/* Related edges */}
              <div className="pt-2 border-t border-vnbot-line-soft">
                <span className="font-mono text-[10px] text-vnbot-text-muted uppercase">Relaciones</span>
                <div className="mt-1 space-y-1">
                  {edges.filter(e => e.source === selectedNode.id || e.target === selectedNode.id).map(e => {
                    const other = e.source === selectedNode.id ? nodes.find(n => n.id === e.target) : nodes.find(n => n.id === e.source);
                    return (
                      <div key={e.id} className="flex items-center gap-1">
                        <span className="font-mono text-[10px]" style={{ color: RELATION_COLORS[e.relation] }}>
                          {e.relation}
                        </span>
                        <span className="font-body text-xs text-vnbot-text-muted">→</span>
                        <span className="font-body text-xs text-vnbot-text">{other?.label ?? '?'}</span>
                      </div>
                    );
                  })}
                  {edges.filter(e => e.source === selectedNode.id || e.target === selectedNode.id).length === 0 && (
                    <span className="font-mono text-[10px] text-vnbot-text-muted">Sin relaciones</span>
                  )}
                </div>
              </div>
            </div>
          </aside>
        )}
      </div>
    </div>
  );
}
