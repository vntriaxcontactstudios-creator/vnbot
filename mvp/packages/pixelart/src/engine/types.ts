/**
 * VNBOT Pixelart Engine — Types
 * Source: docs/05-DISENO-UI-UX §19 + VNBOT_SPRITESHEET_REFERENCE §4
 */

export type AgentId =
  | 'guardian' // VNBOT Core, general assistant
  | 'chat_assistant' // Capture, conversation, onboarding
  | 'archivist' // Memory, search, graph
  | 'beacon' // Reminders and tasks
  | 'navigator' // Calendar and agenda
  | 'forge' // Creativity, projects, drones
  | 'sentinel'; // Security, vault, permissions

export type MascotState =
  | 'idle'
  | 'listening'
  | 'thinking'
  | 'processing'
  | 'waiting_confirmation'
  | 'success'
  | 'warning'
  | 'error'
  | 'offline'
  | 'sleeping';

export type Emote =
  | 'neutral'
  | 'happy'
  | 'curious'
  | 'focused'
  | 'listening'
  | 'thinking'
  | 'loading'
  | 'confirmed'
  | 'warning'
  | 'error'
  | 'offline'
  | 'sleepy';

export type SpriteSize = 16 | 32 | 64 | 128 | 256;

/**
 * 8 render layers in strict order (per VNBOT_SPRITESHEET_REFERENCE §4.1)
 */
export const LAYER_ORDER = [
  'background',
  'shadow',
  'body',
  'armor',
  'visor',
  'accessories',
  'particles',
  'state_overlay',
] as const;

export type LayerName = (typeof LAYER_ORDER)[number];

/**
 * 7 base templates (per VNBOT_SPRITESHEET_REFERENCE §4.2)
 */
export type BaseTemplate =
  | 'golem_biped_16' // icon 16×16 — emotes, badges, favicon
  | 'golem_biped_32' // chat compact 32×32 — agent list, notifications
  | 'golem_biped_64' // cards 64×64 — Today panel, inspector
  | 'golem_biped_128' // hero/landing 128×128 — BASE for 0.1
  | 'golem_biped_256' // ultra-detail 256×256 — onboarding hero
  | 'golem_hover_64' // floating variants
  | 'golem_sentinel_64' // sentinel variant
  | 'golem_archivist_64'; // archivist variant

/**
 * 7 agent palettes (per VNBOT_SPRITESHEET_REFERENCE §4.3)
 */
export type PaletteName =
  | 'cyan_graphite' // Guardian, Navigator
  | 'white_chat' // Chat Assistant
  | 'violet_archive' // Archivist
  | 'amber_graphite' // Beacon
  | 'magenta_forge' // Forge
  | 'green_sentinel' // Sentinel
  | 'red_error'; // state overlay (not an agent)

export interface Palette {
  name: PaletteName;
  primary: string;
  secondary: string;
  accent: string;
  visor: string;
  shadow: string;
  outline: string;
}

export interface AgentDefinition {
  agent_id: AgentId;
  base_template: BaseTemplate;
  palette: PaletteName;
  visor_pattern: 'stable' | 'pulsing' | 'dots' | 'ring' | 'amber' | 'green' | 'red' | 'off' | 'rest';
  accessory: 'shield' | 'microphone' | 'lenses' | 'beacon_antenna' | 'compass' | 'drones' | 'barrier' | 'none';
  idle_animation: 'hover_low' | 'breathe' | 'rest' | 'none';
  states: MascotState[];
  display_name: string;
  role: string;
}

export interface FrameSpec {
  state: MascotState;
  frame_count: number;
  cycle_ms: number;
}

/**
 * Frame counts per state (per VNBOT_SPRITESHEET_REFERENCE §5)
 * Particles only on processing/success, max 5-8 simultaneous.
 */
export const FRAME_SPECS: Record<MascotState, FrameSpec> = {
  idle: { state: 'idle', frame_count: 4, cycle_ms: 3000 },
  listening: { state: 'listening', frame_count: 2, cycle_ms: 1500 },
  thinking: { state: 'thinking', frame_count: 3, cycle_ms: 1200 },
  processing: { state: 'processing', frame_count: 6, cycle_ms: 1500 },
  waiting_confirmation: { state: 'waiting_confirmation', frame_count: 2, cycle_ms: 3000 },
  success: { state: 'success', frame_count: 2, cycle_ms: 800 },
  warning: { state: 'warning', frame_count: 2, cycle_ms: 2000 },
  error: { state: 'error', frame_count: 2, cycle_ms: 2500 },
  offline: { state: 'offline', frame_count: 1, cycle_ms: 0 },
  sleeping: { state: 'sleeping', frame_count: 2, cycle_ms: 4000 },
};

export interface MascotStateViewProps {
  agent: AgentId;
  state: MascotState;
  size?: SpriteSize;
  reducedMotion?: boolean;
  interactive?: boolean;
  className?: string;
}
