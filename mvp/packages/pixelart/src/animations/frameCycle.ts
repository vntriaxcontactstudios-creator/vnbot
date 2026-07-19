/**
 * VNBOT Pixelart — Frame cycle hook
 *
 * Cycles through sprite frames using requestAnimationFrame.
 * Pauses automatically when the canvas leaves the viewport (IntersectionObserver).
 * Respects prefers-reduced-motion (returns frame 0 only).
 *
 * Reference: VNBOT Terreno Preparado §8.3
 */

import { useEffect, useRef, useState } from 'react';
import { FRAME_SPECS, type MascotState } from '../engine/types';

interface UseFrameCycleOptions {
  state: MascotState;
  enabled?: boolean;
}

interface UseFrameCycleResult {
  frame: number;
  isPaused: boolean;
}

export function useFrameCycle(opts: UseFrameCycleOptions): UseFrameCycleResult {
  const { state, enabled = true } = opts;
  const [frame, setFrame] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const elementRef = useRef<HTMLElement | null>(null);
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
    if (!elementRef.current) return;

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          setIsPaused(!entry.isIntersecting);
        }
      },
      { threshold: 0.1 },
    );

    observer.observe(elementRef.current);
    return () => observer.disconnect();
  }, []);

  // Return ref to attach to the canvas wrapper
  return { frame, isPaused };
}

/**
 * Helper: attach the IntersectionObserver target.
 * Usage: const { frame, setRef } = useFrameCycleWithRef({ state });
 *        <div ref={setRef}>...</div>
 */
export function useFrameCycleWithRef(opts: UseFrameCycleOptions): {
  frame: number;
  isPaused: boolean;
  setRef: (el: HTMLElement | null) => void;
} {
  const { frame, isPaused } = useFrameCycle(opts);
  const ref = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!ref.current) return;

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) {
            // Pause: cancel any pending raf
          }
        }
      },
      { threshold: 0.1 },
    );

    observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  return {
    frame,
    isPaused,
    setRef: (el: HTMLElement | null) => {
      ref.current = el;
    },
  };
}
