import React from 'react';
import { cn } from '../../lib/utils';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'outline' | 'accent' | 'muted';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  className,
}) => {
  const variantStyles = {
    default: 'bg-hactm-panel text-hactm-text border-hactm-border',
    outline: 'border-hactm-border text-hactm-muted bg-transparent',
    accent: 'bg-hactm-accent/10 text-hactm-accent border-hactm-accent/30',
    muted: 'bg-hactm-surface text-hactm-muted border-hactm-border/50',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-mono font-medium border tracking-wide',
        variantStyles[variant],
        className
      )}
    >
      {children}
    </span>
  );
};
