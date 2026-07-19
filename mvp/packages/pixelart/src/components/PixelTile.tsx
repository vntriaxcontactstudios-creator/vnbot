/**
 * VNBOT Pixelart — PixelTile (border tiles for PixelPanel/HudFrame)
 *
 * Renders 16×16 border tiles with angular clip-path for cyberpunk HUD frames.
 * Combine in a grid to build full panels.
 */

import { memo } from 'react';

type TileType = 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'top' | 'bottom' | 'left' | 'right' | 'center';

interface PixelTileProps {
  type: TileType;
  size?: 16 | 32;
  color?: string;
  className?: string;
}

export const PixelTile = memo(function PixelTile({
  type,
  size = 16,
  color = '#2A6F8E',
  className,
}: PixelTileProps) {
  const clipPaths: Record<TileType, string> = {
    'top-left': 'polygon(0 0, 100% 0, 100% 75%, 75% 100%, 0 100%)',
    'top-right': 'polygon(0 0, 100% 0, 100% 100%, 25% 100%, 0 75%)',
    'bottom-left': 'polygon(0 0, 75% 0, 100% 25%, 100% 100%, 0 100%)',
    'bottom-right': 'polygon(25% 0, 100% 0, 100% 100%, 0 100%, 0 25%)',
    top: 'polygon(0 0, 100% 0, 100% 100%, 0 100%)',
    bottom: 'polygon(0 0, 100% 0, 100% 100%, 0 100%)',
    left: 'polygon(0 0, 100% 0, 100% 100%, 0 100%)',
    right: 'polygon(0 0, 100% 0, 100% 100%, 0 100%)',
    center: 'polygon(0 0, 100% 0, 100% 100%, 0 100%)',
  };

  return (
    <div
      className={className}
      style={{
        width: size,
        height: size,
        background: type === 'center' ? 'transparent' : color,
        clipPath: clipPaths[type],
      }}
      aria-hidden="true"
    />
  );
});

/**
 * Pre-composed PixelPanel with angular corners (clip-path approach).
 * More efficient than tiling individual PixelTiles for full panels.
 */
interface PixelPanelProps {
  children?: React.ReactNode;
  variant?: 'default' | 'hud' | 'corner-cut';
  accentColor?: string;
  className?: string;
}

export const PixelPanel = memo(function PixelPanel({
  children,
  variant = 'default',
  accentColor,
  className,
}: PixelPanelProps) {
  const clipClass =
    variant === 'hud'
      ? 'clip-path-hud-frame'
      : variant === 'corner-cut'
        ? 'clip-path-corner-cut'
        : 'clip-path-pixel-panel';

  return (
    <div
      className={`${clipClass} ${className ?? ''}`}
      style={{
        background: 'var(--color-vnbot-panel-0, #12243A)',
        border: `1px solid ${accentColor ?? 'var(--color-vnbot-line, #2A6F8E)'}`,
        padding: '12px',
        position: 'relative',
      }}
    >
      {children}
    </div>
  );
});
