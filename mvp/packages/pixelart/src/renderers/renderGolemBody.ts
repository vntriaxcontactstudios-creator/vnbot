/**
 * VNBOT Pixelart — Golem Body Renderer
 *
 * Renders the biped body of the golem using mask-mirror algorithm + fractal noise.
 * The body is symmetric (left-right), so we render the left half and mirror.
 *
 * Reference: VNBOT Terreno Preparado §7.2 (8 layer pipeline)
 * Inspired by: zfedoran/pixel-sprite-generator (mask-mirror)
 *
 * Output: an OffscreenCanvas (or HTMLCanvasElement) of size × size pixels.
 */

import type { Palette } from '../engine/types';
import { createRng } from '../engine/prng';
import { makeFractalNoise2D } from '../engine/noise';

interface RenderBodyOptions {
  size: number;
  palette: Palette;
  seed: string;
}

/**
 * Render the body layer of a golem.
 * Uses a coarse pixel grid (size/4) for the silhouette + fractal noise for texture.
 *
 * @param ctx canvas 2D context to draw into
 * @param size canvas width = height
 */
export function renderGolemBody(
  ctx: CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D,
  opts: RenderBodyOptions,
): void {
  const { size, palette, seed } = opts;
  const rng = createRng(seed);
  const noise = makeFractalNoise2D(createRng(seed + ':noise')(), 4);

  // Fixed 16x16 grid for the body silhouette — independent of sprite size.
  // This keeps the golem proportions consistent across 16/32/64/128/256.
  // The grid is then scaled to fit the sprite size.
  const gridSize = 16;
  const cellSize = size / gridSize;
  const halfGrid = Math.floor(gridSize / 2); // 8

  // Define body silhouette as a grid mask.
  // 1 = body, 0 = empty. We render only left half, then mirror.
  // The golem is a biped: head (top), torso (middle), legs (bottom).
  const mask: number[][] = Array.from({ length: gridSize }, () => new Array(halfGrid).fill(0));

  // Head (rows 1-4, cols 1-3)
  for (let y = 1; y <= 4; y++) {
    for (let x = 1; x <= 3; x++) {
      mask[y][x] = 1;
    }
  }

  // Neck (row 5, cols 2)
  mask[5][2] = 1;

  // Torso (rows 6-10, cols 1-4) — wider than head
  for (let y = 6; y <= 10; y++) {
    for (let x = 1; x <= 4; x++) {
      mask[y][x] = 1;
    }
  }

  // Arms (rows 7-10, col 0 and col 5 after mirror)
  for (let y = 7; y <= 10; y++) {
    mask[y][0] = 1;
  }

  // Waist (row 11, cols 2-3)
  mask[11][2] = 1;
  mask[11][3] = 1;

  // Legs (rows 12-15, cols 1-2 and 3-4 after mirror)
  for (let y = 12; y <= 15; y++) {
    mask[y][1] = 1;
    mask[y][2] = 1;
  }

  // Feet (row 15, cols 0 and 3 after mirror)
  mask[15][0] = 1;

  // Render the mask with palette colors + fractal noise texture
  ctx.save();
  ctx.imageSmoothingEnabled = false;

  // Fill body cells with primary color
  ctx.fillStyle = palette.secondary;
  for (let y = 0; y < gridSize; y++) {
    for (let x = 0; x < halfGrid; x++) {
      if (mask[y][x] === 1) {
        // Left half
        ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
        // Mirror to right half
        const mirroredX = (gridSize - 1 - x) * cellSize;
        ctx.fillRect(mirroredX, y * cellSize, cellSize, cellSize);
      }
    }
  }

  // Overlay fractal noise for texture (only on body cells)
  // Use ImageData for per-pixel control
  const imageData = ctx.getImageData(0, 0, size, size);
  const data = imageData.data;

  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const idx = (y * size + x) * 4;
      const alpha = data[idx + 3];
      if (alpha === 0) continue; // skip transparent (non-body)

      // Sample noise at this position — frequency scaled to look organic
      const n = noise(x / (size / 4), y / (size / 4));
      // If noise > 0.6, brighten with primary; if < 0.3, darken with outline
      if (n > 0.65) {
        // Bright spot — primary color
        blendPixel(data, idx, palette.primary, 0.6);
      } else if (n < 0.3) {
        // Dark spot — outline color
        blendPixel(data, idx, palette.outline, 0.5);
      }
      // mid-range: keep secondary
    }
  }

  ctx.putImageData(imageData, 0, 0);

  // Add rivets/clusters at random positions on the body (deterministic by seed)
  ctx.fillStyle = palette.accent;
  const rivetCount = 3 + Math.floor(rng() * 4); // 3-6 rivets
  for (let i = 0; i < rivetCount; i++) {
    const cellY = 6 + Math.floor(rng() * 5); // torso region
    const cellX = 1 + Math.floor(rng() * 3);
    if (mask[cellY]?.[cellX] === 1) {
      const px = cellX * cellSize + cellSize / 2;
      const py = cellY * cellSize + cellSize / 2;
      const r = Math.max(1, cellSize / 6);
      ctx.beginPath();
      ctx.arc(px, py, r, 0, Math.PI * 2);
      ctx.fill();
      // Mirror
      const mirroredPx = (gridSize - 1 - cellX) * cellSize + cellSize / 2;
      ctx.beginPath();
      ctx.arc(mirroredPx, py, r, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  ctx.restore();
}

/** Blend a hex color into a pixel at given index with given alpha. */
function blendPixel(data: Uint8ClampedArray, idx: number, hex: string, alpha: number): void {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  data[idx] = Math.round(data[idx] * (1 - alpha) + r * alpha);
  data[idx + 1] = Math.round(data[idx + 1] * (1 - alpha) + g * alpha);
  data[idx + 2] = Math.round(data[idx + 2] * (1 - alpha) + b * alpha);
}
