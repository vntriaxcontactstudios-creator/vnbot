/**
 * VNBOT Pixelart — Accessories Renderer
 *
 * Renders agent-specific accessories:
 *   shield          → Guardian (left arm)
 *   microphone      → Chat Assistant (right side)
 *   lenses          → Archivist (over visor)
 *   beacon_antenna  → Beacon (top of head)
 *   compass         → Navigator (chest)
 *   drones          → Forge (floating around)
 *   barrier         → Sentinel (force field around body)
 *   none            → no accessory
 */

import type { AgentDefinition, Palette } from '../engine/types';

interface RenderAccessoriesOptions {
  size: number;
  agent: AgentDefinition;
  palette: Palette;
  frame: number;
  seed: string;
}

export function renderAccessories(
  ctx: CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D,
  opts: RenderAccessoriesOptions,
): void {
  const { size, agent, palette, frame, seed } = opts;
  void seed; // reserved for future procedural accessory variation

  ctx.save();
  ctx.imageSmoothingEnabled = false;

  switch (agent.accessory) {
    case 'shield':
      drawShield(ctx, size, palette);
      break;
    case 'microphone':
      drawMicrophone(ctx, size, palette, frame);
      break;
    case 'lenses':
      drawLenses(ctx, size, palette);
      break;
    case 'beacon_antenna':
      drawBeaconAntenna(ctx, size, palette, frame);
      break;
    case 'compass':
      drawCompass(ctx, size, palette, frame);
      break;
    case 'drones':
      drawDrones(ctx, size, palette, frame);
      break;
    case 'barrier':
      drawBarrier(ctx, size, palette, frame);
      break;
    case 'none':
      break;
  }

  ctx.restore();
}

function drawShield(
  ctx: CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D,
  size: number,
  palette: Palette,
): void {
  // Left arm shield — angular shape
  const shieldW = size * 0.18;
  const shieldH = size * 0.35;
  const x = size * 0.05;
  const y = size * 0.45;

  ctx.fillStyle = palette.primary;
  ctx.beginPath();
  ctx.moveTo(x, y);
  ctx.lineTo(x + shieldW, y);
  ctx.lineTo(x + shieldW * 0.9, y + shieldH * 0.7);
  ctx.lineTo(x + shieldW * 0.5, y + shieldH);
  ctx.lineTo(x + shieldW * 0.1, y + shieldH * 0.7);
  ctx.closePath();
  ctx.fill();

  // Inner detail
  ctx.fillStyle = palette.accent;
  ctx.fillRect(x + shieldW * 0.3, y + shieldH * 0.2, shieldW * 0.4, shieldH * 0.15);
  ctx.fillRect(x + shieldW * 0.3, y + shieldH * 0.5, shieldW * 0.4, shieldH * 0.15);
}

function drawMicrophone(
  ctx: CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D,
  size: number,
  palette: Palette,
  frame: number,
): void {
  // Microphone at the right side of the head — small boom mic
  const micX = size * 0.78;
  const micY = size * 0.22;
  const micSize = size * 0.08;

  // Mic head (circle)
  ctx.fillStyle = palette.accent;
  ctx.beginPath();
  ctx.arc(micX, micY, micSize, 0, Math.PI * 2);
  ctx.fill();

  // Mic boom (line to head)
  ctx.strokeStyle = palette.secondary;
  ctx.lineWidth = size * 0.02;
  ctx.beginPath();
  ctx.moveTo(micX, micY + micSize);
  ctx.lineTo(micX - size * 0.1, micY + size * 0.06);
  ctx.stroke();

  // Pulse on listening frames
  const pulse = Math.abs(Math.sin(frame * Math.PI));
  if (pulse > 0.5) {
    ctx.strokeStyle = `rgba(32, 220, 232, ${pulse})`;
    ctx.lineWidth = size * 0.01;
    ctx.beginPath();
    ctx.arc(micX, micY, micSize * 1.5, 0, Math.PI * 2);
    ctx.stroke();
  }
}

function drawLenses(
  ctx: CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D,
  size: number,
  palette: Palette,
): void {
  // Two lenses over the visor — archivist data crystal
  const lensY = size * 0.22;
  const lensW = size * 0.15;
  const lensH = size * 0.08;

  // Left lens
  ctx.fillStyle = palette.accent;
  ctx.fillRect(size * 0.3, lensY, lensW, lensH);
  // Right lens
  ctx.fillRect(size * 0.55, lensY, lensW, lensH);

  // Reflection (small white dot)
  ctx.fillStyle = '#ECF6FF';
  ctx.fillRect(size * 0.32, lensY + 1, lensW * 0.15, lensH * 0.2);
  ctx.fillRect(size * 0.57, lensY + 1, lensW * 0.15, lensH * 0.2);
}

function drawBeaconAntenna(
  ctx: CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D,
  size: number,
  palette: Palette,
  frame: number,
): void {
  // Vertical antenna on top of head with pulsing light
  const antennaX = size / 2;
  const antennaTop = size * 0.05;
  const antennaBottom = size * 0.15;

  // Shaft
  ctx.strokeStyle = palette.secondary;
  ctx.lineWidth = size * 0.02;
  ctx.beginPath();
  ctx.moveTo(antennaX, antennaBottom);
  ctx.lineTo(antennaX, antennaTop);
  ctx.stroke();

  // Beacon light (pulsing)
  const pulse = 0.5 + 0.5 * Math.sin(frame * Math.PI);
  ctx.fillStyle = palette.primary;
  ctx.beginPath();
  ctx.arc(antennaX, antennaTop, size * 0.03, 0, Math.PI * 2);
  ctx.fill();

  // Glow
  const glowGradient = ctx.createRadialGradient(antennaX, antennaTop, 0, antennaX, antennaTop, size * 0.08);
  glowGradient.addColorStop(0, `rgba(255, 200, 61, ${pulse * 0.8})`);
  glowGradient.addColorStop(1, 'rgba(255, 200, 61, 0)');
  ctx.fillStyle = glowGradient;
  ctx.fillRect(antennaX - size * 0.08, antennaTop - size * 0.08, size * 0.16, size * 0.16);
}

function drawCompass(
  ctx: CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D,
  size: number,
  palette: Palette,
  frame: number,
): void {
  // Compass on chest — circle with rotating needle
  const cx = size / 2;
  const cy = size * 0.45;
  const r = size * 0.08;

  // Outer ring
  ctx.strokeStyle = palette.accent;
  ctx.lineWidth = size * 0.015;
  ctx.beginPath();
  ctx.arc(cx, cy, r, 0, Math.PI * 2);
  ctx.stroke();

  // Needle (rotates slowly)
  const angle = frame * Math.PI * 0.1;
  ctx.strokeStyle = palette.primary;
  ctx.lineWidth = size * 0.025;
  ctx.beginPath();
  ctx.moveTo(cx, cy);
  ctx.lineTo(cx + Math.cos(angle) * r * 0.7, cy + Math.sin(angle) * r * 0.7);
  ctx.stroke();

  // Center dot
  ctx.fillStyle = palette.primary;
  ctx.beginPath();
  ctx.arc(cx, cy, size * 0.012, 0, Math.PI * 2);
  ctx.fill();
}

function drawDrones(
  ctx: CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D,
  size: number,
  palette: Palette,
  frame: number,
): void {
  // 3 small drones orbiting around the golem
  const cx = size / 2;
  const cy = size / 2;
  const orbitR = size * 0.45;
  const droneSize = size * 0.06;

  for (let i = 0; i < 3; i++) {
    const angle = frame * Math.PI * 0.15 + (i * 2 * Math.PI) / 3;
    const x = cx + Math.cos(angle) * orbitR;
    const y = cy + Math.sin(angle) * orbitR;

    // Drone body (small square)
    ctx.fillStyle = palette.primary;
    ctx.fillRect(x - droneSize / 2, y - droneSize / 2, droneSize, droneSize);

    // Drone light (blinking)
    if ((frame + i) % 4 < 2) {
      ctx.fillStyle = palette.accent;
      ctx.fillRect(x - droneSize / 4, y - droneSize / 4, droneSize / 2, droneSize / 2);
    }
  }
}

function drawBarrier(
  ctx: CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D,
  size: number,
  palette: Palette,
  frame: number,
): void {
  // Force field around the body — hexagonal pattern
  void palette; // barrier uses fixed green color, palette reserved for future variation
  const cx = size / 2;
  const cy = size / 2;
  const r = size * 0.48;

  const pulse = 0.3 + 0.3 * Math.abs(Math.sin(frame * Math.PI * 0.5));

  ctx.strokeStyle = `rgba(91, 223, 130, ${pulse})`;
  ctx.lineWidth = size * 0.015;
  ctx.setLineDash([size * 0.03, size * 0.02]);

  // Hexagon
  ctx.beginPath();
  for (let i = 0; i < 6; i++) {
    const angle = (i * Math.PI) / 3 + frame * Math.PI * 0.02;
    const x = cx + Math.cos(angle) * r;
    const y = cy + Math.sin(angle) * r;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.closePath();
  ctx.stroke();

  ctx.setLineDash([]);
}
