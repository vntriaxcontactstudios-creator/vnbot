/**
 * VNBOT Pixelart — Public API
 */

// Engine
export { hashStringToSeed, mulberry32, createRng, pick, randInt, randFloat } from './engine/prng';
export { makeValueNoise2D, makeFractalNoise2D, hashNoise2D } from './engine/noise';
export { composeSprite, clearSpriteCache, getCacheSize } from './engine/composer';
export {
  LAYER_ORDER,
  FRAME_SPECS,
} from './engine/types';
export type {
  AgentId,
  MascotState,
  Emote,
  SpriteSize,
  LayerName,
  BaseTemplate,
  PaletteName,
  Palette,
  AgentDefinition,
  FrameSpec,
  MascotStateViewProps,
} from './engine/types';

// Palettes & agents
export { PALETTES, getPalette } from './palettes';
export { AGENTS, getAgent } from './templates/agents';

// Renderers (low-level, exposed for testing)
export { renderGolemBody } from './renderers/renderGolemBody';
export { renderVisor } from './renderers/renderVisor';
export { renderAccessories } from './renderers/renderAccessories';
export { renderShadow, renderArmor, renderParticles, renderStateOverlay } from './renderers/renderExtras';

// Components
export { MascotStateView } from './components/MascotStateView';
export { PixelBackground } from './components/PixelBackground';
export { PixelAvatar } from './components/PixelAvatar';
export { PixelTile, PixelPanel } from './components/PixelTile';

// Hooks
export { useFrameCycle } from './animations/frameCycle';
