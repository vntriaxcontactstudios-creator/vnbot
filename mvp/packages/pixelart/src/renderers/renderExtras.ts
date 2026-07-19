/**
 * VNBOT Pixelart — Armor, Shadow, Particles, State Overlay renderers
 *
 * These complete the 8-layer pipeline:
 *   background → shadow → body → armor → visor → accessories → particles → state_overlay
 */

import type { MascotState, Palette } from '../engine/types';

// ──────────────────────────────────────────────────────────────────────────────
// Shadow
// ──────────────────────────────────────────────────────────────────────────────

export function renderShadow(
  ctx: CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D,
  size: number,
  palette: Palette,
): void {
  // Elliptical shadow under the golem
  const cx = size / 2;
  const cy = size * 0.92;
  const rx = size * 0.3;
  const ry = size * 0.05;

  ctx.save();
  const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, rx);
  gradient.addColorStop(0, palette.shadow);
  gradient.addColorStop(1, 'rgba(7, 10, 18, 0)');
  ctx.fillStyle = gradient;
  ctx.beginPath();
  ctx.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

// ──────────────────────────────────────────────────────────────────────────────
// Armor (overlay on top of body — plates and segments)
// ──────────────────────────────────────────────────────────────────────────────

interface RenderArmorOptions {
  size: number;
  palette: Palette;
  seed: string;
}

export function renderArmor(
  ctx: CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D,
  opts: RenderArmorOptions,
): void {
  const { size, palette, seed } = opts;
  void seed; // reserved for future procedural armor variation

  ctx.save();
  ctx.imageSmoothingEnabled = false;

  // Chest plate (centered rectangle on torso)
  const plateX = size * 0.35;
  const plateY = size * 0.42;
  const plateW = size * 0.3;
  const plateH = size * 0.18;

  ctx.fillStyle = palette.primary;
  ctx.fillRect(plateX, plateY, plateW, plateH);

  // Plate border
  ctx.strokeStyle = palette.accent;
  ctx.lineWidth = Math.max(1, size * 0.012);
  ctx.strokeRect(plateX, plateY, plateW, plateH);

  // Center rivet
  ctx.fillStyle = palette.accent;
  ctx.beginPath();
  ctx.arc(plateX + plateW / 2, plateY + plateH / 2, size * 0.025, 0, Math.PI * 2);
  ctx.fill();

  // Shoulder pads (left + right, symmetric)
  const shoulderY = size * 0.4;
  const shoulderW = size * 0.12;
  const shoulderH = size * 0.08;

  // Left shoulder
  ctx.fillStyle = palette.primary;
  ctx.fillRect(size * 0.18, shoulderY, shoulderW, shoulderH);
  ctx.strokeStyle = palette.accent;
  ctx.strokeRect(size * 0.18, shoulderY, shoulderW, shoulderH);

  // Right shoulder (mirror)
  ctx.fillStyle = palette.primary;
  ctx.fillRect(size * 0.7, shoulderY, shoulderW, shoulderH);
  ctx.strokeRect(size * 0.7, shoulderY, shoulderW, shoulderH);

  // Leg armor plates (2 vertical stripes on legs)
  ctx.fillStyle = hexToRgba(palette.primary, 0.4);
  ctx.fillRect(size * 0.4, size * 0.72, size * 0.04, size * 0.18);
  ctx.fillRect(size * 0.56, size * 0.72, size * 0.04, size * 0.18);

  ctx.restore();
}

// ──────────────────────────────────────────────────────────────────────────────
// Particles (only on processing + success, max 5-8 simultaneous)
// ──────────────────────────────────────────────────────────────────────────────

interface RenderParticlesOptions {
  size: number;
  state: MascotState;
  palette: Palette;
  frame: number;
  seed: string;
}

export function renderParticles(
  ctx: CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D,
  opts: RenderParticlesOptions,
): void {
  const { size, state, palette, frame, seed } = opts;
  void seed; // reserved for future particle variation

  // Only render particles on processing and success states (per UI §19.7)
  if (state !== 'processing' && state !== 'success') return;

  const particleCount = state === 'success' ? 5 : 8;

  ctx.save();
  ctx.globalCompositeOperation = 'lighter'; // additive blend for glow

  for (let i = 0; i < particleCount; i++) {
    // Each particle has a deterministic position + animated drift
    const baseAngle = (i * Math.PI * 2) / particleCount;
    const driftAngle = baseAngle + frame * 0.1;
    const radius = size * (0.3 + 0.1 * Math.sin(frame * 0.2 + i));
    const cx = size / 2 + Math.cos(driftAngle) * radius;
    const cy = size * 0.4 + Math.sin(driftAngle) * radius * 0.5;
    const pSize = size * (0.015 + 0.01 * Math.sin(frame * 0.3 + i));

    const color = i % 2 === 0 ? palette.primary : palette.accent;
    ctx.fillStyle = hexToRgba(color, 0.7);
    ctx.fillRect(cx - pSize / 2, cy - pSize / 2, pSize, pSize);
  }

  ctx.restore();
}

// ──────────────────────────────────────────────────────────────────────────────
// State overlay (color tint by state)
// ──────────────────────────────────────────────────────────────────────────────

interface RenderStateOverlayOptions {
  size: number;
  state: MascotState;
  palette: Palette;
  frame: number;
}

export function renderStateOverlay(
  ctx: CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D,
  opts: RenderStateOverlayOptions,
): void {
  const { size, state, frame } = opts;

  ctx.save();

  switch (state) {
    case 'success': {
      // Brief green flash on first frame
      if (frame === 0) {
        ctx.fillStyle = 'rgba(91, 223, 130, 0.3)';
        ctx.fillRect(0, 0, size, size);
      }
      break;
    }
    case 'error': {
      // Brief red flash on first frame, then quiet
      if (frame === 0) {
        ctx.fillStyle = 'rgba(255, 92, 109, 0.4)';
        ctx.fillRect(0, 0, size, size);
      }
      break;
    }
    case 'warning': {
      // Subtle amber tint on odd frames (slow blink)
      if (frame % 2 === 0) {
        ctx.fillStyle = 'rgba(255, 200, 61, 0.1)';
        ctx.fillRect(0, 0, size, size);
      }
      break;
    }
    case 'offline': {
      // Darken the whole sprite
      ctx.fillStyle = 'rgba(7, 10, 18, 0.4)';
      ctx.fillRect(0, 0, size, size);
      break;
    }
    case 'sleeping': {
      // Very subtle blue tint
      ctx.fillStyle = 'rgba(42, 111, 142, 0.15)';
      ctx.fillRect(0, 0, size, size);
      break;
    }
    default:
      // No overlay for idle, listening, thinking, processing, waiting_confirmation
      break;
  }

  ctx.restore();
}

function hexToRgba(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}
