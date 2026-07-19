/**
 * VNBOT Pixelart Engine — PRNG (deterministic pseudo-random number generator)
 *
 * Chain: hashStringToSeed (FNV-1a) → mulberry32 (PRNG)
 *
 * Critical: same seed = same sprite. This enables:
 * - Stable user avatars across sessions
 * - Visual regression tests with golden PNGs
 * - Reproducible procedural generation
 *
 * Reference: VNBOT Terreno Preparado §7.3
 */

/**
 * FNV-1a 32-bit hash — converts a string to a uint32 seed.
 * Uses Math.imul for 32-bit integer multiplication (browser-safe).
 */
export function hashStringToSeed(str: string): number {
  let h = 0x811c9dc5; // FNV-1a 32-bit offset basis
  for (let i = 0; i < str.length; i++) {
    h = Math.imul(h ^ str.charCodeAt(i), 0x01000193); // FNV prime
  }
  return h >>> 0; // coerce to uint32
}

/**
 * mulberry32 PRNG — small, fast, good statistical quality.
 * Returns a function that produces uniform floats in [0, 1).
 *
 * @param seed uint32 seed (from hashStringToSeed)
 * @returns function returning pseudo-random float in [0, 1)
 */
export function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return function () {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/**
 * Seeded RNG instance — combines hashStringToSeed + mulberry32.
 * Convenience wrapper: pass any string, get a function returning [0,1).
 */
export function createRng(seedString: string): () => number {
  return mulberry32(hashStringToSeed(seedString));
}

/**
 * Pick a random item from an array (deterministic given the RNG).
 */
export function pick<T>(rng: () => number, arr: readonly T[]): T {
  return arr[Math.floor(rng() * arr.length)];
}

/**
 * Random integer in [min, max] inclusive.
 */
export function randInt(rng: () => number, min: number, max: number): number {
  return Math.floor(rng() * (max - min + 1)) + min;
}

/**
 * Random float in [min, max).
 */
export function randFloat(rng: () => number, min: number, max: number): number {
  return rng() * (max - min) + min;
}
