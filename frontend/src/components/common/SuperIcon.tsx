import React from 'react';

export type SuperIconStyle = 'color' | 'duotone' | 'two-tone' | 'stroke' | 'fill';

export interface SuperIconProps {
  name: string;
  style?: SuperIconStyle;
  size?: number | string;
  className?: string;
  alt?: string;
  ariaHidden?: boolean;
}

/**
 * SuperIcon: Official SuperIntelligence Isometric SVG Icon Renderer for HACTM.
 * Features:
 * - Direct local asset resolution from /assets/superintelligence/{style}/{name}.svg
 * - Zero remote HTTP calls at runtime
 * - Accessible text handling (alt + aria-hidden)
 * - Motion CSS integration with reduced-motion preference support
 * - HiDPI vector fidelity
 */
export const SuperIcon: React.FC<SuperIconProps> = ({
  name,
  style = 'color',
  size = 20,
  className = '',
  alt,
  ariaHidden = true,
}) => {
  const iconName = name.endsWith('.svg') ? name : `${name}.svg`;
  const src = `/assets/superintelligence/${style}/${iconName}`;

  const dim = typeof size === 'number' ? `${size}px` : size;

  return (
    <img
      src={src}
      width={size}
      height={size}
      alt={alt || (ariaHidden ? '' : `${name} icon`)}
      aria-hidden={ariaHidden}
      loading="eager"
      className={`block flex-shrink-0 select-none ai-icon-motion ${className}`}
      style={{
        width: dim,
        height: dim,
        minWidth: dim,
        minHeight: dim,
        objectFit: 'contain',
      }}
    />
  );
};

