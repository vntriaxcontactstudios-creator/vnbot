/**
 * VNBOT Pixelart — MascotStateView component
 *
 * Renders the procedural golem mascot with state-driven animation.
 * Wraps the canvas in an Atropos parallax 3D hover effect (desktop only).
 *
 * Reference: VNBOT Terreno Preparado §8.2 (Integration pattern)
 *
 * Workaround for Chromium bug 40669825:
 *   image-rendering: pixelated gets blurred when Atropos applies translate3d
 *   to ancestors. Fix: apply pixelated on the wrapper DIRECTLY around the canvas,
 *   not on a distant ancestor. Also force will-change: transform.
 */

import { useEffect, useRef, memo, useState } from 'react';
import { Atropos } from 'atropos/react';
import { composeSprite } from '../engine/composer';
import { getAgent } from '../templates/agents';
import { useFrameCycle } from '../animations/frameCycle';
import type { MascotStateViewProps, SpriteSize } from '../engine/types';

const DEFAULT_SIZE: SpriteSize = 128;

export const MascotStateView = memo(function MascotStateView({
  agent: agentId,
  state,
  size = DEFAULT_SIZE,
  reducedMotion,
  interactive = true,
  className,
}: MascotStateViewProps) {
  const agent = getAgent(agentId);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const { frame } = useFrameCycle({
    state,
    enabled: !reducedMotion,
    containerRef,
  });

  // Detect touch device (Atropos disabled on touch per Terreno Preparado §8.1)
  const [isTouchDevice, setIsTouchDevice] = useState(false);

  useEffect(() => {
    setIsTouchDevice(window.matchMedia('(hover: none)').matches);
  }, []);

  const useAtropos = interactive && !reducedMotion && !isTouchDevice;

  // Render the sprite whenever agent/state/frame/size changes
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext('2d', { alpha: true });
    if (!ctx) return;

    ctx.imageSmoothingEnabled = false;
    ctx.clearRect(0, 0, size, size);

    try {
      const sprite = composeSprite({ agent, state, frame, size });
      ctx.drawImage(sprite, 0, 0);
    } catch (err) {
      // Fallback: draw a simple colored square if composer fails
      console.warn('[MascotStateView] Sprite render failed, using fallback:', err);
      ctx.fillStyle = '#1C4664';
      ctx.fillRect(size * 0.2, size * 0.1, size * 0.6, size * 0.8);
    }
  }, [agent, state, frame, size]);

  // Static version (no Atropos)
  if (!useAtropos) {
    return (
      <div
        ref={containerRef}
        className={className}
        style={{
          display: 'inline-block',
          position: 'relative',
          width: size,
          height: size,
          willChange: 'transform',
        }}
        role="img"
        aria-label={`${agent.display_name} — ${state}`}
      >
        <canvas
          ref={canvasRef}
          style={{
            imageRendering: 'pixelated',
            width: '100%',
            height: '100%',
          }}
        />
      </div>
    );
  }

  // Interactive version with Atropos parallax 3D
  return (
    <div ref={containerRef} style={{ width: size, height: size }}>
      <Atropos
        activeOffset={40}
        shadow={false}
        highlight={false}
        rotateXMax={8}
        rotateYMax={8}
        style={{ width: size, height: size }}
      >
        {/* Layer 0: sprite canvas (base layer at translateZ(0)) */}
        <div
          data-atropos-offset="0"
          style={{
            willChange: 'transform',
            imageRendering: 'pixelated',
          }}
          role="img"
          aria-label={`${agent.display_name} — ${state}`}
        >
          <canvas
            ref={canvasRef}
            style={{
              imageRendering: 'pixelated',
              width: size,
              height: size,
              display: 'block',
            }}
          />
        </div>

        {/* Layer +50: visor glow (parallax depth) */}
        <div
          data-atropos-offset="50"
          aria-hidden="true"
          style={{
            position: 'absolute',
            inset: 0,
            pointerEvents: 'none',
            background:
              'radial-gradient(circle at 50% 25%, rgba(32, 220, 232, 0.15) 0%, transparent 30%)',
            mixBlendMode: 'screen',
          }}
        />

        {/* Layer +80: ambient particles (subtle depth) */}
        <div
          data-atropos-offset="80"
          aria-hidden="true"
          style={{
            position: 'absolute',
            inset: 0,
            pointerEvents: 'none',
            background:
              'radial-gradient(circle at 30% 70%, rgba(138, 108, 255, 0.08) 0%, transparent 40%), radial-gradient(circle at 70% 60%, rgba(255, 200, 61, 0.08) 0%, transparent 40%)',
          }}
        />
      </Atropos>
    </div>
  );
});
