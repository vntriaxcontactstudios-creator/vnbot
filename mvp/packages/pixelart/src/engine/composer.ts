/**
 * VNBOT Pixelart — Sprite Composer
 *
 * Composes a sprite from 8 layers (per VNBOT_SPRITESHEET_REFERENCE §4.1):
 *   background → shadow → body → armor → visor → accessories → particles → state_overlay
 *
 * 3-tier cache for performance:
 *   L1: per-layer OffscreenCanvas cache (keyed by layer+agent+state+frame+size)
 *   L2: composed sprite cache (keyed by agent+state+frame+size) — main hit path
 *   L3: (future) build-time atlas for common states
 *
 * Performance budget (per VNBOT Terreno Preparado §8.4):
 *   - Cold render first sprite: < 5ms
 *   - Hot render (cache hit): < 0.5ms
 *   - Memory per mascot instance: < 50 KB
 *   - Sprite cache hit rate after warmup: > 90%
 */

import type { AgentDefinition, MascotState, SpriteSize, LayerName } from './types';
import { LAYER_ORDER } from './types';
import { renderGolemBody } from '../renderers/renderGolemBody';
import { renderVisor } from '../renderers/renderVisor';
import { renderAccessories } from '../renderers/renderAccessories';
import { renderShadow, renderArmor, renderParticles, renderStateOverlay } from '../renderers/renderExtras';
import { getPalette } from '../palettes';

interface ComposeOptions {
  agent: AgentDefinition;
  state: MascotState;
  frame: number;
  size: SpriteSize;
  seed?: string;
}

interface CacheEntry {
  canvas: HTMLCanvasElement;
  lastUsed: number;
}

const MAX_CACHE_SIZE = 256;
const composedCache = new Map<string, CacheEntry>();

/**
 * Compose a sprite and return a canvas. Uses cache when available.
 *
 * @returns HTMLCanvasElement with the rendered sprite
 */
export function composeSprite(opts: ComposeOptions): HTMLCanvasElement {
  const { agent, state, frame, size, seed = `${agent.agent_id}:${state}` } = opts;
  const cacheKey = `${agent.agent_id}:${state}:${frame}:${size}`;

  // L2 cache hit
  const cached = composedCache.get(cacheKey);
  if (cached) {
    cached.lastUsed = Date.now();
    return cached.canvas;
  }

  // Cache miss — render
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d', { alpha: true })!;
  ctx.imageSmoothingEnabled = false;

  const palette = getPalette(agent.palette);

  // Render each layer in order
  for (const layer of LAYER_ORDER) {
    renderLayer(ctx, layer, {
      agent,
      state,
      frame,
      size,
      palette,
      seed,
    });
  }

  // Store in cache (LRU eviction)
  if (composedCache.size >= MAX_CACHE_SIZE) {
    evictOldest();
  }
  composedCache.set(cacheKey, { canvas, lastUsed: Date.now() });

  return canvas;
}

interface RenderLayerOptions {
  agent: AgentDefinition;
  state: MascotState;
  frame: number;
  size: SpriteSize;
  palette: ReturnType<typeof getPalette>;
  seed: string;
}

function renderLayer(
  ctx: CanvasRenderingContext2D,
  layer: LayerName,
  opts: RenderLayerOptions,
): void {
  const { agent, state, frame, size, palette, seed } = opts;

  switch (layer) {
    case 'background':
      // Transparent — let the container provide background
      break;

    case 'shadow':
      renderShadow(ctx, size, palette);
      break;

    case 'body':
      renderGolemBody(ctx, { size, palette, seed: seed + ':body' });
      break;

    case 'armor':
      renderArmor(ctx, { size, palette, seed: seed + ':armor' });
      break;

    case 'visor':
      renderVisor(ctx, { size, state, palette, frame, seed: seed + ':visor' });
      break;

    case 'accessories':
      renderAccessories(ctx, { agent, palette, frame, size, seed: seed + ':accessory' });
      break;

    case 'particles':
      renderParticles(ctx, { size, state, palette, frame, seed: seed + ':particles' });
      break;

    case 'state_overlay':
      renderStateOverlay(ctx, { size, state, palette, frame });
      break;
  }
}

/**
 * Clear the cache (for testing or low-memory situations).
 */
export function clearSpriteCache(): void {
  composedCache.clear();
}

/**
 * Get current cache size (for debugging).
 */
export function getCacheSize(): number {
  return composedCache.size;
}

/**
 * Evict the oldest entries when cache is full.
 */
function evictOldest(): void {
  let oldestKey: string | null = null;
  let oldestTime = Date.now();

  for (const [key, entry] of composedCache) {
    if (entry.lastUsed < oldestTime) {
      oldestTime = entry.lastUsed;
      oldestKey = key;
    }
  }

  if (oldestKey) {
    composedCache.delete(oldestKey);
  }
}
