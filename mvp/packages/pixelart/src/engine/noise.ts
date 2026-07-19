/**
 * VNBOT Pixelart Engine — Noise functions
 *
 * - makeValueNoise2D: smooth 2D value noise (256×256 table + smoothstep + bilinear)
 * - makeFractalNoise2D: multi-octave fBm (fractal Brownian motion) — No Man's Sky style organic detail
 *
 * Reference: VNBOT Terreno Preparado §7.3
 * Inspired by: attilabuti/SimplexNoise, marian42/proceduralart
 */

import { mulberry32 } from './prng';

/**
 * Smoothstep interpolation — Hermite curve, C1 continuous.
 * Standard for value noise.
 */
function smoothstep(t: number): number {
  return t * t * (3 - 2 * t);
}

/**
 * Create a 2D value noise function seeded by `seed`.
 *
 * Implementation:
 * - Pre-generate a 256×256 table of random floats in [0, 1)
 * - For query (x, y), look up 4 corner values, bilinearly interpolate with smoothstep
 * - Wraps via & 255 for seamless tiling
 *
 * @param seed uint32 seed
 * @returns function (x, y) → float in [0, 1)
 */
export function makeValueNoise2D(seed: number): (x: number, y: number) => number {
  const rng = mulberry32(seed);
  const SIZE = 256;
  const table = new Float32Array(SIZE * SIZE);
  for (let i = 0; i < table.length; i++) table[i] = rng();

  return (x: number, y: number): number => {
    const xi = Math.floor(x) & 255;
    const yi = Math.floor(y) & 255;
    const xf = x - Math.floor(x);
    const yf = y - Math.floor(y);

    const x1 = (xi + 1) & 255;
    const y1 = (yi + 1) & 255;

    const tl = table[yi * SIZE + xi];
    const tr = table[yi * SIZE + x1];
    const bl = table[y1 * SIZE + xi];
    const br = table[y1 * SIZE + x1];

    const u = smoothstep(xf);
    const v = smoothstep(yf);

    const top = tl + (tr - tl) * u;
    const bot = bl + (br - bl) * u;
    return top + (bot - top) * v;
  };
}

/**
 * Create a fractal Brownian motion (fBm) noise function.
 * Sums multiple octaves of value noise with decreasing amplitude + increasing frequency.
 * Produces organic detail like No Man's Sky planets/creatures.
 *
 * @param seed uint32 seed
 * @param octaves default 4 (more = smoother detail, slower)
 * @param persistence default 0.5 (amplitude decay per octave)
 * @param lacunarity default 2.0 (frequency growth per octave)
 * @returns function (x, y) → float in [0, 1)
 */
export function makeFractalNoise2D(
  seed: number,
  octaves = 4,
  persistence = 0.5,
  lacunarity = 2.0,
): (x: number, y: number) => number {
  // Each octave uses its own seeded noise function (different table)
  const noises = Array.from({ length: octaves }, (_, i) => makeValueNoise2D(seed + i * 7919));

  return (x: number, y: number): number => {
    let total = 0;
    let amplitude = 1;
    let frequency = 1;
    let max = 0;

    for (let i = 0; i < octaves; i++) {
      total += noises[i](x * frequency, y * frequency) * amplitude;
      max += amplitude;
      amplitude *= persistence;
      frequency *= lacunarity;
    }

    return total / max; // normalize to [0, 1]
  };
}

/**
 * Hash-based deterministic noise (no table) — for tiny sprites where 256×256 is overkill.
 * Faster but lower quality than value noise.
 */
export function hashNoise2D(x: number, y: number, seed: number): number {
  const h = Math.imul(Math.imul(x | 0, 374761393) ^ Math.imul(y | 0, 668265263), seed | 0);
  return ((h ^ (h >>> 13)) >>> 0) / 4294967296;
}
