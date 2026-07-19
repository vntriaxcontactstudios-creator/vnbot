/**
 * VNBOT Pixelart — PixelBackground component
 *
 * Animated procedural background with starfield, matrix rain, or pixel landscape.
 * Uses Canvas with requestAnimationFrame. Pauses on hidden + reduced-motion.
 */

import { useEffect, useRef, memo } from 'react';
import { createRng } from '../engine/prng';

type BackgroundType = 'starfield' | 'matrix_rain' | 'landscape' | 'circuit_grid';

interface PixelBackgroundProps {
  type?: BackgroundType;
  width?: number;
  height?: number;
  seed?: string;
  className?: string;
  reducedMotion?: boolean;
}

export const PixelBackground = memo(function PixelBackground({
  type = 'starfield',
  width = 256,
  height = 256,
  seed = 'vnbot-bg',
  className,
  reducedMotion,
}: PixelBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rafRef = useRef<number | null>(null);
  const frameRef = useRef(0);
  const stateRef = useRef<{ stars: { x: number; y: number; brightness: number }[]; columns: number[] }>({
    stars: [],
    columns: [],
  });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d', { alpha: true })!;
    ctx.imageSmoothingEnabled = false;

    const rng = createRng(seed);

    // Initialize state per type
    if (type === 'starfield') {
      const starCount = Math.floor((width * height) / 800);
      stateRef.current.stars = Array.from({ length: starCount }, () => ({
        x: Math.floor(rng() * width),
        y: Math.floor(rng() * height),
        brightness: rng(),
      }));
    } else if (type === 'matrix_rain') {
      const colCount = Math.floor(width / 8);
      stateRef.current.columns = Array.from({ length: colCount }, () => Math.floor(rng() * height));
    }

    // Reduced motion: render single static frame
    if (reducedMotion) {
      renderFrame(ctx, type, 0);
      return;
    }

    const tick = () => {
      frameRef.current += 1;
      renderFrame(ctx, type, frameRef.current);
      rafRef.current = requestAnimationFrame(tick);
    };

    rafRef.current = requestAnimationFrame(tick);

    // Pause on hidden
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            if (rafRef.current === null) {
              rafRef.current = requestAnimationFrame(tick);
            }
          } else {
            if (rafRef.current !== null) {
              cancelAnimationFrame(rafRef.current);
              rafRef.current = null;
            }
          }
        }
      },
      { threshold: 0.01 },
    );
    observer.observe(canvas);

    return () => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
      observer.disconnect();
    };
  }, [type, width, height, seed, reducedMotion]);

  function renderFrame(
    ctx: CanvasRenderingContext2D,
    bgType: BackgroundType,
    frame: number,
  ): void {
    ctx.fillStyle = '#070A12';
    ctx.fillRect(0, 0, width, height);

    switch (bgType) {
      case 'starfield':
        renderStarfield(ctx, frame);
        break;
      case 'matrix_rain':
        renderMatrixRain(ctx, frame);
        break;
      case 'landscape':
        renderLandscape(ctx, frame);
        break;
      case 'circuit_grid':
        renderCircuitGrid(ctx, frame);
        break;
    }
  }

  function renderStarfield(ctx: CanvasRenderingContext2D, frame: number): void {
    for (const star of stateRef.current.stars) {
      const twinkle = 0.5 + 0.5 * Math.sin(frame * 0.05 + star.brightness * 10);
      const alpha = star.brightness * twinkle;
      ctx.fillStyle = `rgba(236, 246, 255, ${alpha})`;
      ctx.fillRect(star.x, star.y, 1, 1);
    }
  }

  function renderMatrixRain(ctx: CanvasRenderingContext2D, frame: number): void {
    void frame; // matrix rain uses its own internal state, frame not needed
    // Fade previous frame
    ctx.fillStyle = 'rgba(7, 10, 18, 0.1)';
    ctx.fillRect(0, 0, width, height);

    const cols = stateRef.current.columns;
    ctx.font = '8px "JetBrains Mono", monospace';
    ctx.fillStyle = '#5BDF82';

    for (let i = 0; i < cols.length; i++) {
      const char = String.fromCharCode(0x30a0 + Math.floor(Math.random() * 96));
      const x = i * 8;
      const y = cols[i];
      ctx.fillStyle = `rgba(91, 223, 130, ${Math.random() * 0.8 + 0.2})`;
      ctx.fillText(char, x, y);

      cols[i] += 8;
      if (cols[i] > height && Math.random() > 0.97) cols[i] = 0;
    }
  }

  function renderLandscape(ctx: CanvasRenderingContext2D, _frame: number): void {
    // Pixel landscape — static with subtle color shift
    const horizonY = Math.floor(height * 0.6);

    // Sky gradient (procedural)
    for (let y = 0; y < horizonY; y++) {
      const t = y / horizonY;
      const r = Math.floor(10 + t * 20);
      const g = Math.floor(20 + t * 30);
      const b = Math.floor(40 + t * 50);
      ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
      ctx.fillRect(0, y, width, 1);
    }

    // Distant mountains
    ctx.fillStyle = '#1C4664';
    for (let x = 0; x < width; x += 4) {
      const h = Math.floor(Math.sin(x * 0.05) * 20 + Math.sin(x * 0.1) * 10 + 30);
      ctx.fillRect(x, horizonY - h, 4, h);
    }

    // Ground
    ctx.fillStyle = '#0A1020';
    ctx.fillRect(0, horizonY, width, height - horizonY);

    // Grid lines on ground (perspective)
    ctx.strokeStyle = 'rgba(32, 220, 232, 0.15)';
    ctx.lineWidth = 1;
    for (let i = 0; i < 10; i++) {
      const y = horizonY + Math.pow(i / 10, 2) * (height - horizonY);
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }
  }

  function renderCircuitGrid(ctx: CanvasRenderingContext2D, frame: number): void {
    // Circuit board pattern with pulsing traces
    ctx.fillStyle = '#0A1020';
    ctx.fillRect(0, 0, width, height);

    const gridSize = 16;
    ctx.strokeStyle = 'rgba(32, 220, 232, 0.2)';
    ctx.lineWidth = 1;

    // Grid
    for (let x = 0; x < width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Pulsing nodes
    for (let x = gridSize; x < width; x += gridSize * 2) {
      for (let y = gridSize; y < height; y += gridSize * 2) {
        const pulse = 0.5 + 0.5 * Math.sin(frame * 0.05 + x * 0.01 + y * 0.01);
        ctx.fillStyle = `rgba(32, 220, 232, ${pulse * 0.6})`;
        ctx.fillRect(x - 1, y - 1, 2, 2);
      }
    }
  }

  return (
    <canvas
      ref={canvasRef}
      className={className}
      style={{
        imageRendering: 'pixelated',
        width: '100%',
        height: '100%',
        display: 'block',
      }}
      aria-hidden="true"
    />
  );
});
