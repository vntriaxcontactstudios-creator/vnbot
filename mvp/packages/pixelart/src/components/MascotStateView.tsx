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

import { forwardRef, useEffect, useRef, memo } from 'react';
import { Atropos } from 'atropos/react';
import type { AtroposProps } from 'atropos/react';
import { composeSprite } from '../engine/composer';
import { getAgent } from '../templates/agents';
import { useFrameCycleWithRef } from '../animations/frameCycle';
import { FRAME_SPECS, type MascotStateViewProps, type SpriteSize } from '../engine/types';

const DEFAULT_SIZE: SpriteSize = 128;

export const MascotStateView = memo(
  forwardRef<HTMLCanvasElement, MascotStateViewProps>(function MascotStateView(
    { agent: agentId, state, size = DEFAULT_SIZE, reducedMotion, interactive = true, className },
    ref,
  ) {
    const agent = getAgent(agentId);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const wrapperRef = useRef<HTMLDivElement>(null);

    // Forward the canvas ref to parent
    useEffect(() => {
      if (typeof ref === 'function') ref(canvasRef.current);
      else if (ref) (ref as React.MutableRefObject<HTMLCanvasElement | null>).current = canvasRef.current;
    }, [ref]);

    const { frame, setRef } = useFrameCycleWithRef({ state, enabled: !reducedMotion });

    // Detect touch device (Atropos disabled on touch per Terreno Preparado §8.1)
    const isTouchDevice =
      typeof window !== 'undefined' && window.matchMedia('(hover: none)').matches;
    const useAtropos = interactive && !reducedMotion && !isTouchDevice;

    // Render the sprite whenever agent/state/frame/size changes
    useEffect(() => {
      const canvas = canvasRef.current;
      if (!canvas) return;

      canvas.width = size;
      canvas.height = size;
      const ctx = canvas.getContext('2d', { alpha: true })!;
      ctx.imageSmoothingEnabled = false;
      ctx.clearRect(0, 0, size, size);

      const sprite = composeSprite({ agent, state, frame, size });
      ctx.drawImage(sprite, 0, 0);
    }, [agent, state, frame, size]);

    // Static version (no Atropos)
    if (!useAtropos) {
      return (
        <div
          ref={(el) => {
            wrapperRef.current = el;
            setRef(el);
          }}
          className={className}
          style={{
            display: 'inline-block',
            position: 'relative',
            width: size,
            height: size,
            // Workaround for Chromium bug 40669825
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
    const atroposProps: AtroposProps = {
      activeOffset: 40,
      shadow: false,
      highlight: false,
      rotateXMax: 8,
      rotateYMax: 8,
      style: { width: size, height: size },
    };

    return (
      <Atropos {...atroposProps}>
        {/* Layer 0: sprite canvas (base layer at translateZ(0)) */}
        <div
          ref={(el) => {
            wrapperRef.current = el;
            setRef(el);
          }}
          data-atropos-offset="0"
          style={{
            willChange: 'transform',
            // Workaround for Chromium bug 40669825
            // Apply pixelated HERE, directly on the canvas wrapper
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
    );
  }),
);
