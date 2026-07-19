/**
 * VNBOT Pixelart — Frame cycle hook
 *
 * Cycles through sprite frames using requestAnimationFrame.
 * Pauses automatically when the container leaves the viewport (IntersectionObserver).
 * Respects prefers-reduced-motion (returns frame 0 only).
 *
 * Reference: VNBOT Terreno Preparado §8.3
 */

import { useEffect, useRef, useState, type RefObject } from 'react';
import { FRAME_SPECS, type MascotState } from '../engine/types';

interface UseFrameCycleOptions {
  state: MascotState;
  enabled?: boolean;
  containerRef: RefObject<HTMLElement | null>;
}

interface UseFrameCycleResult {
  frame: number;
  isPaused: boolean;
}

export function useFrameCycle(opts: UseFrameCycleOptions): UseFrameCycleResult {
  const { state, enabled = true, containerRef } = opts;
  const [frame, setFrame] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const rafRef = useRef<number | null>(null);
  const lastFrameTimeRef = useRef<number>(0);

  // Check prefers-reduced-motion
  const prefersReducedMotion =
    typeof window !== 'undefined' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  useEffect(() => {
    if (prefersReducedMotion) {
      setFrame(0);
      return;
    }

    const spec = FRAME_SPECS[state];
    if (!spec || spec.frame_count <= 1 || spec.cycle_ms === 0) {
      setFrame(0);
      return;
    }

    if (!enabled || isPaused) return;

    const tick = (now: number) => {
      if (now - lastFrameTimeRef.current >= spec.cycle_ms / spec.frame_count) {
        setFrame((prev) => (prev + 1) % spec.frame_count);
        lastFrameTimeRef.current = now;
      }
      rafRef.current = requestAnimationFrame(tick);
    };

    rafRef.current = requestAnimationFrame(tick);

    return () => {
      if (rafRef.current !== null) {
        cancelAnimationFrame(rafRef.current);
      }
    };
  }, [state, enabled, isPaused, prefersReducedMotion]);

  // IntersectionObserver to pause off-screen
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          setIsPaused(!entry.isIntersecting);
        }
      },
      { threshold: 0.1 },
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [containerRef]);

  return { frame, isPaused };
}
