/**
 * VNBOT Pixelart — 7 Agent Definitions
 * Source: docs/05-DISENO-UI-UX §13.2, §19.2
 *
 * Each agent is defined by DATA, not a rigid image. The renderer assembles
 * the sprite from this definition + base template + palette + state.
 */

import type { AgentDefinition, AgentId } from '../engine/types';

export const AGENTS: Record<AgentId, AgentDefinition> = {
  guardian: {
    agent_id: 'guardian',
    base_template: 'golem_biped_128',
    palette: 'cyan_graphite',
    visor_pattern: 'stable',
    accessory: 'shield',
    idle_animation: 'breathe',
    states: ['idle', 'listening', 'thinking', 'processing', 'success', 'warning', 'error', 'offline', 'sleeping'],
    display_name: 'Guardian',
    role: 'VNBOT Core, general assistant',
  },
  chat_assistant: {
    agent_id: 'chat_assistant',
    base_template: 'golem_biped_128',
    palette: 'white_chat',
    visor_pattern: 'pulsing',
    accessory: 'microphone',
    idle_animation: 'hover_low',
    states: ['idle', 'listening', 'thinking', 'processing', 'success', 'warning', 'error', 'offline', 'sleeping'],
    display_name: 'Chat Assistant',
    role: 'Capture, conversation, onboarding',
  },
  archivist: {
    agent_id: 'archivist',
    base_template: 'golem_biped_128',
    palette: 'violet_archive',
    visor_pattern: 'dots',
    accessory: 'lenses',
    idle_animation: 'hover_low',
    states: ['idle', 'thinking', 'processing', 'success', 'warning', 'error', 'offline', 'sleeping'],
    display_name: 'Archivist',
    role: 'Memory, search, graph',
  },
  beacon: {
    agent_id: 'beacon',
    base_template: 'golem_biped_128',
    palette: 'amber_graphite',
    visor_pattern: 'ring',
    accessory: 'beacon_antenna',
    idle_animation: 'hover_low',
    states: ['idle', 'thinking', 'processing', 'success', 'warning', 'error', 'offline', 'sleeping'],
    display_name: 'Beacon',
    role: 'Reminders and tasks',
  },
  navigator: {
    agent_id: 'navigator',
    base_template: 'golem_biped_128',
    palette: 'cyan_graphite',
    visor_pattern: 'stable',
    accessory: 'compass',
    idle_animation: 'breathe',
    states: ['idle', 'thinking', 'processing', 'success', 'warning', 'error', 'offline', 'sleeping'],
    display_name: 'Navigator',
    role: 'Calendar and agenda',
  },
  forge: {
    agent_id: 'forge',
    base_template: 'golem_biped_128',
    palette: 'magenta_forge',
    visor_pattern: 'dots',
    accessory: 'drones',
    idle_animation: 'hover_low',
    states: ['idle', 'thinking', 'processing', 'success', 'warning', 'error', 'offline', 'sleeping'],
    display_name: 'Forge',
    role: 'Creativity, projects, drones',
  },
  sentinel: {
    agent_id: 'sentinel',
    base_template: 'golem_biped_128',
    palette: 'green_sentinel',
    visor_pattern: 'stable',
    accessory: 'barrier',
    idle_animation: 'breathe',
    states: ['idle', 'listening', 'waiting_confirmation', 'processing', 'success', 'warning', 'error', 'offline', 'sleeping'],
    display_name: 'Sentinel',
    role: 'Security, vault, permissions',
  },
};

export function getAgent(id: AgentId): AgentDefinition {
  const a = AGENTS[id];
  if (!a) throw new Error(`Unknown agent: ${id}`);
  return a;
}
