/**
 * VNBOT Pixelart — PixelAvatar (deterministic identicon by seed)
 *
 * Generates a 16×16 (or 32×32) deterministic avatar from a string seed.
 * Used for: users, integrations, skills, agents in compact lists.
 *
 * Algorithm: hashStringToSeed → mulberry32 → symmetric 4×4 grid pattern (mirrored)
 */

import { memo, useEffect, useRef } from 'react';
import { hashStringToSeed, mulberry32 } from '../engine/prng';

interface PixelAvatarProps {
  seed: string;
  size?: 16 | 32 | 64;
  className?: string;
}

const COLORS = [
  '#20DCE8', // cyan
  '#4D9DFF', // blue
  '#D94BE3', // magenta
  '#8A6CFF', // violet
  '#FFC83D', // amber
  '#5BDF82', // green
];

export const PixelAvatar = memo(function PixelAvatar({
  seed,
  size = 32,
  className,
}: PixelAvatarProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext('2d', { alpha: true })!;
    ctx.imageSmoothingEnabled = false;
    ctx.clearRect(0, 0, size, size);

    // Generate deterministic pattern
    const seedNum = hashStringToSeed(seed);
    const rng = mulberry32(seedNum);
    const bgColor = COLORS[Math.floor(rng() * COLORS.length)];
    const fgColor = COLORS[Math.floor(rng() * COLORS.length)];

    // Background
    ctx.fillStyle = bgColor;
    ctx.fillRect(0, 0, size, size);

    // 4×4 grid, mirrored (only render left half, then mirror)
    const grid = 4;
    const cellSize = size / grid;
    const half = grid / 2;

    ctx.fillStyle = fgColor;
    for (let y = 0; y < grid; y++) {
      for (let x = 0; x < half; x++) {
        if (rng() > 0.5) {
          // Left cell
          ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
          // Mirror to right
          ctx.fillRect((grid - 1 - x) * cellSize, y * cellSize, cellSize, cellSize);
        }
      }
    }

    // Border
    ctx.strokeStyle = '#070A12';
    ctx.lineWidth = Math.max(1, size * 0.05);
    ctx.strokeRect(0, 0, size, size);
  }, [seed, size]);

  return (
    <canvas
      ref={canvasRef}
      className={className}
      style={{
        imageRendering: 'pixelated',
        width: size,
        height: size,
        display: 'block',
      }}
      role="img"
      aria-label={`Avatar for ${seed}`}
    />
  );
});
