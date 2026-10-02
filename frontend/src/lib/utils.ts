import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatTimestamp(dateStr?: string | null): string {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return d.toISOString().replace('T', ' ').substring(0, 19) + ' UTC';
  } catch {
    return dateStr;
  }
}

export function formatRelativeTime(dateStr?: string | null): string {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr);
    const now = new Date();
    const diffSec = Math.floor((now.getTime() - d.getTime()) / 1000);
    if (diffSec < 60) return `${diffSec}s ago`;
    if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
    if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
    return `${Math.floor(diffSec / 86400)}d ago`;
  } catch {
    return dateStr;
  }
}

export function getRiskSeverity(risk: number): 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' {
  if (risk >= 0.8) return 'CRITICAL';
  if (risk >= 0.6) return 'HIGH';
  if (risk >= 0.3) return 'MEDIUM';
  return 'LOW';
}

export function getRiskColorClass(risk: number): string {
  if (risk >= 0.8) return 'text-risk-critical border-risk-critical/30 bg-risk-critical/10';
  if (risk >= 0.6) return 'text-risk-high border-risk-high/30 bg-risk-high/10';
  if (risk >= 0.3) return 'text-risk-medium border-risk-medium/30 bg-risk-medium/10';
  return 'text-risk-low border-risk-low/30 bg-risk-low/10';
}
