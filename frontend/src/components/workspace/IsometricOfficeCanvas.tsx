/**
 * Interactive Isometric AI-Agent Cyber Operations Office Canvas.
 * Original high-performance procedural Canvas 2D engine with HiDPI support,
 * animated agents, pulsing data conduits, status halos, pan/zoom, and depth sorting.
 */

import React, { useRef, useEffect, useState, useCallback } from 'react';
import {
  OfficeDepartment,
  WorkspaceAgentState,
  AgentOfficeStatus,
  OfficeDepartmentId,
} from '../../types/workspace';
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  RotateCcw,
  Shield,
  Layers,
  Radio,
} from 'lucide-react';
import { SuperIcon } from '../common/SuperIcon';

interface IsometricOfficeCanvasProps {
  agents: WorkspaceAgentState[];
  departments: OfficeDepartment[];
  selectedAgentId: string | null;
  onSelectAgent: (agentId: string) => void;
  onSelectDepartment: (departmentId: OfficeDepartmentId) => void;
  highlightedIncidentId?: string | null;
  onSelectSupervisorStation?: () => void;
  activeAnomaliesCount?: number;
}

// 30-degree isometric projection constants
const TILE_WIDTH = 64;
const TILE_HEIGHT = 32;

// Isometric transformation
function gridToScreen(gx: number, gy: number, originX: number, originY: number, scale: number) {
  const sx = originX + (gx - gy) * (TILE_WIDTH / 2) * scale;
  const sy = originY + (gx + gy) * (TILE_HEIGHT / 2) * scale;
  return { x: sx, y: sy };
}

function screenToGrid(sx: number, sy: number, originX: number, originY: number, scale: number) {
  const dx = (sx - originX) / scale;
  const dy = (sy - originY) / scale;
  const gx = (dx / (TILE_WIDTH / 2) + dy / (TILE_HEIGHT / 2)) / 2;
  const gy = (dy / (TILE_HEIGHT / 2) - dx / (TILE_WIDTH / 2)) / 2;
  return { gx, gy };
}

// Status color scheme
const STATUS_COLORS: Record<AgentOfficeStatus, { main: string; glow: string; text: string }> = {
  IDLE: { main: '#64748b', glow: 'rgba(100, 116, 139, 0.4)', text: '#94a3b8' },
  QUEUED: { main: '#38bdf8', glow: 'rgba(56, 189, 248, 0.5)', text: '#7dd3fc' },
  ASSIGNED: { main: '#0ea5e9', glow: 'rgba(14, 165, 233, 0.6)', text: '#38bdf8' },
  ANALYSING: { main: '#00f0ff', glow: 'rgba(0, 240, 255, 0.8)', text: '#00f0ff' },
  GENERATING_EVIDENCE: { main: '#10b981', glow: 'rgba(16, 185, 129, 0.8)', text: '#34d399' },
  COMMUNICATING: { main: '#8b5cf6', glow: 'rgba(139, 92, 246, 0.8)', text: '#a78bfa' },
  HANDOFF: { main: '#d946ef', glow: 'rgba(217, 70, 239, 0.8)', text: '#e879f9' },
  WAITING_FOR_APPROVAL: { main: '#f59e0b', glow: 'rgba(245, 158, 11, 0.9)', text: '#fbbf24' },
  COMPLETED: { main: '#22c55e', glow: 'rgba(34, 197, 94, 0.7)', text: '#4ade80' },
  DEGRADED: { main: '#eab308', glow: 'rgba(234, 179, 8, 0.7)', text: '#fde047' },
  ISOLATED: { main: '#ef4444', glow: 'rgba(239, 68, 68, 0.9)', text: '#f87171' },
  FAILED: { main: '#dc2626', glow: 'rgba(220, 38, 38, 0.9)', text: '#fca5a5' },
};

// SuperIntelligence isometric icon assets for Canvas 2D rendering
const CANVAS_ASSETS = {
  monitoring: '/assets/superintelligence/color/monitoring.svg',
  orchestration: '/assets/superintelligence/color/orchestration.svg',
  agent: '/assets/superintelligence/color/agent.svg',
  sandbox: '/assets/superintelligence/color/sandbox.svg',
  tools: '/assets/superintelligence/color/tools.svg',
  permissions: '/assets/superintelligence/color/permissions.svg',
  humanApproval: '/assets/superintelligence/color/human-approval.svg',
  evaluation: '/assets/superintelligence/color/evaluation.svg',
  alignment: '/assets/superintelligence/color/alignment.svg',
  citations: '/assets/superintelligence/color/citations.svg',
  reasoning: '/assets/superintelligence/color/reasoning.svg',
  knowledgeGraph: '/assets/superintelligence/color/knowledge-graph.svg',
  memory: '/assets/superintelligence/color/memory.svg',
  dataset: '/assets/superintelligence/color/dataset.svg',
  task: '/assets/superintelligence/color/task.svg',
  a2a: '/assets/superintelligence/color/a2a.svg',
};

// Pre-cached HTMLImageElement map to eliminate image decoding overhead on animation frames
const ICON_IMG_CACHE = new Map<string, HTMLImageElement>();

function getOrLoadCanvasIcon(src: string): HTMLImageElement | null {
  let img = ICON_IMG_CACHE.get(src);
  if (!img) {
    img = new Image();
    img.src = src;
    ICON_IMG_CACHE.set(src, img);
    return null;
  }
  return img.complete && img.naturalWidth > 0 ? img : null;
}

if (typeof window !== 'undefined') {
  Object.values(CANVAS_ASSETS).forEach((src) => {
    getOrLoadCanvasIcon(src);
  });
}

/** Traces an isometric diamond centred at (cx, cy) with half-width rx and half-height ry. */
function traceIsoDiamond(
  ctx: CanvasRenderingContext2D,
  cx: number,
  cy: number,
  rx: number,
  ry: number
) {
  ctx.beginPath();
  ctx.moveTo(cx, cy - ry);
  ctx.lineTo(cx + rx, cy);
  ctx.lineTo(cx, cy + ry);
  ctx.lineTo(cx - rx, cy);
  ctx.closePath();
}

/** Draws a cached SuperIntelligence icon centred horizontally at cx and vertically at cy. */
function drawCanvasIcon(
  ctx: CanvasRenderingContext2D,
  src: string,
  cx: number,
  cy: number,
  size: number
) {
  const img = getOrLoadCanvasIcon(src);
  if (img) {
    ctx.drawImage(img, cx - size / 2, cy - size / 2, size, size);
  }
}

/**
 * Renders the AI Trust & Governance Control Room inside the existing governance_trust tile.
 * Coordinates stay inside x in [-2.2, 2.2], y in [-10.2, -6.9] and items sort by isometric depth.
 */
function drawGovernanceSecurityStation(
  ctx: CanvasRenderingContext2D,
  dept: OfficeDepartment,
  hasRegisteredGovAgent: boolean,
  originX: number,
  originY: number,
  zoom: number,
  t: number
) {
  const cx = dept.gridX + dept.width / 2; // 0
  const cy = dept.gridY + dept.height / 2; // -8.5

  const stationItems: Array<{ depth: number; draw: () => void }> = [
    // 1. Governance Monitoring Workstation + Dual Glowing Monitors + Decorative Emblem
    {
      depth: cx - 1.35 + (cy - 1.25),
      draw: () => {
        const pos = gridToScreen(cx - 1.35, cy - 1.25, originX, originY, zoom);
        ctx.save();

        // Workstation desk plinth
        traceIsoDiamond(ctx, pos.x, pos.y, 28 * zoom, 14 * zoom);
        ctx.fillStyle = '#162032';
        ctx.fill();
        ctx.strokeStyle = 'rgba(56, 189, 248, 0.55)';
        ctx.lineWidth = 1.2 * zoom;
        ctx.stroke();

        // Decorative holographic sentinel emblem when no registered governance agent exists
        if (!hasRegisteredGovAgent) {
          const emblemBob = Math.sin(t * 2.2) * 2.5 * zoom;
          const ex = pos.x - 16 * zoom;
          const ey = pos.y - 14 * zoom + emblemBob;

          ctx.strokeStyle = 'rgba(139, 92, 246, 0.55)';
          ctx.lineWidth = 1 * zoom;
          traceIsoDiamond(ctx, pos.x - 16 * zoom, pos.y + 3 * zoom, 9 * zoom, 4.5 * zoom);
          ctx.stroke();

          // Translucent holographic diamond sentinel (clearly decorative emblem, not a specialist avatar)
          ctx.beginPath();
          ctx.moveTo(ex, ey - 10 * zoom);
          ctx.lineTo(ex + 6.5 * zoom, ey - 2 * zoom);
          ctx.lineTo(ex, ey + 6 * zoom);
          ctx.lineTo(ex - 6.5 * zoom, ey - 2 * zoom);
          ctx.closePath();
          ctx.fillStyle = 'rgba(56, 189, 248, 0.25)';
          ctx.fill();
          ctx.strokeStyle = '#00f0ff';
          ctx.lineWidth = 1.2 * zoom;
          ctx.stroke();
        }

        // Left Glowing Monitor: Continuous Telemetry
        const m1x = pos.x - 9 * zoom;
        const m1y = pos.y - 25 * zoom;
        ctx.fillStyle = '#090f1d';
        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 1 * zoom;
        ctx.fillRect(m1x, m1y, 17 * zoom, 11 * zoom);
        ctx.strokeRect(m1x, m1y, 17 * zoom, 11 * zoom);

        // Animated telemetry waveform inside left monitor
        ctx.beginPath();
        for (let i = 0; i <= 4; i++) {
          const wx = m1x + (2.5 + i * 3) * zoom;
          const wy = m1y + (5.5 + Math.sin(t * 4 + i * 1.4) * 2.2) * zoom;
          if (i === 0) ctx.moveTo(wx, wy);
          else ctx.lineTo(wx, wy);
        }
        ctx.strokeStyle = '#00f0ff';
        ctx.lineWidth = 1.2 * zoom;
        ctx.stroke();

        // Right Glowing Monitor: Policy Alignment Indicators
        const m2x = pos.x + 10 * zoom;
        const m2y = pos.y - 22 * zoom;
        ctx.fillStyle = '#090f1d';
        ctx.strokeStyle = '#8b5cf6';
        ctx.lineWidth = 1 * zoom;
        ctx.fillRect(m2x, m2y, 15 * zoom, 10 * zoom);
        ctx.strokeRect(m2x, m2y, 15 * zoom, 10 * zoom);

        for (let b = 0; b < 3; b++) {
          const activeRatio = 0.45 + 0.45 * Math.sin(t * 2.5 + b * 1.3);
          ctx.fillStyle = b === 1 ? '#a78bfa' : '#10b981';
          ctx.fillRect(m2x + 2 * zoom, m2y + (2 + b * 2.6) * zoom, 10 * zoom * activeRatio, 1.5 * zoom);
        }

        // Monitoring & Alignment SuperIntelligence SVG badges
        drawCanvasIcon(ctx, CANVAS_ASSETS.monitoring, m1x + 8.5 * zoom, m1y - 8 * zoom, 13 * zoom);
        drawCanvasIcon(ctx, CANVAS_ASSETS.alignment, m2x + 7.5 * zoom, m2y - 8 * zoom, 13 * zoom);

        ctx.fillStyle = '#7dd3fc';
        ctx.font = `600 ${Math.max(7, Math.floor(8 * zoom))}px Inter, system-ui, sans-serif`;
        ctx.textAlign = 'center';
        ctx.fillText('GOV MONITOR', pos.x + 5 * zoom, pos.y + 16 * zoom);
        ctx.restore();
      },
    },

    // 2. Agent Permission-Control Terminal (Left Wing)
    {
      depth: cx - 1.7 + (cy + 0.85),
      draw: () => {
        const pos = gridToScreen(cx - 1.7, cy + 0.85, originX, originY, zoom);
        ctx.save();

        // Base plinth
        traceIsoDiamond(ctx, pos.x, pos.y, 18 * zoom, 9 * zoom);
        ctx.fillStyle = '#121c2e';
        ctx.fill();
        ctx.strokeStyle = 'rgba(139, 92, 246, 0.7)';
        ctx.lineWidth = 1.2 * zoom;
        ctx.stroke();

        // Pedestal column + vertical permission screen
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(pos.x - 9 * zoom, pos.y - 24 * zoom, 18 * zoom, 16 * zoom);
        ctx.strokeStyle = '#8b5cf6';
        ctx.lineWidth = 1.1 * zoom;
        ctx.strokeRect(pos.x - 9 * zoom, pos.y - 24 * zoom, 18 * zoom, 16 * zoom);

        // Permission check rows + animated verification scan bar
        for (let r = 0; r < 3; r++) {
          ctx.fillStyle = r === 2 ? 'rgba(56, 189, 248, 0.45)' : 'rgba(167, 139, 250, 0.45)';
          ctx.fillRect(pos.x - 6 * zoom, pos.y - (21 - r * 4) * zoom, 12 * zoom, 2 * zoom);
        }
        const scanProgress = (t * 0.7) % 1;
        const scanY = pos.y - 23 * zoom + scanProgress * 14 * zoom;
        ctx.strokeStyle = '#00f0ff';
        ctx.lineWidth = 1.3 * zoom;
        ctx.beginPath();
        ctx.moveTo(pos.x - 8 * zoom, scanY);
        ctx.lineTo(pos.x + 8 * zoom, scanY);
        ctx.stroke();

        drawCanvasIcon(ctx, CANVAS_ASSETS.permissions, pos.x, pos.y - 32 * zoom, 14 * zoom);

        ctx.fillStyle = '#c4b5fd';
        ctx.font = `600 ${Math.max(7, Math.floor(7.5 * zoom))}px Inter, system-ui, sans-serif`;
        ctx.textAlign = 'center';
        ctx.fillText('PERMISSIONS', pos.x, pos.y + 15 * zoom);
        ctx.restore();
      },
    },

    // 3. Central Holographic Cybersecurity Shield (Department Core)
    {
      depth: cx + cy,
      draw: () => {
        const pos = gridToScreen(cx, cy, originX, originY, zoom);
        ctx.save();

        // Pulsing isometric base rings
        const ringPulse1 = (t * 0.55) % 1;
        const ringPulse2 = (t * 0.55 + 0.5) % 1;
        [ringPulse1, ringPulse2].forEach((p, idx) => {
          const rx = (20 + p * 22) * zoom;
          const ry = (10 + p * 11) * zoom;
          ctx.beginPath();
          ctx.ellipse(pos.x, pos.y, rx, ry, 0, 0, Math.PI * 2);
          ctx.strokeStyle =
            idx === 0
              ? `rgba(0, 240, 255, ${(1 - p) * 0.65})`
              : `rgba(139, 92, 246, ${(1 - p) * 0.6})`;
          ctx.lineWidth = 1.4 * zoom;
          ctx.stroke();
        });

        // Illuminated pedestal emitter
        traceIsoDiamond(ctx, pos.x, pos.y, 20 * zoom, 10 * zoom);
        ctx.fillStyle = '#0b1324';
        ctx.fill();
        ctx.strokeStyle = '#00f0ff';
        ctx.lineWidth = 1.5 * zoom;
        ctx.stroke();

        // Vertical holographic projection cone
        const bob = Math.sin(t * 2) * 3 * zoom;
        const shieldY = pos.y - 32 * zoom + bob;
        const coneGrad = ctx.createLinearGradient(pos.x, pos.y, pos.x, shieldY - 12 * zoom);
        coneGrad.addColorStop(0, 'rgba(0, 240, 255, 0.25)');
        coneGrad.addColorStop(0.6, 'rgba(139, 92, 246, 0.14)');
        coneGrad.addColorStop(1, 'rgba(0, 240, 255, 0.02)');
        ctx.beginPath();
        ctx.moveTo(pos.x - 14 * zoom, pos.y);
        ctx.lineTo(pos.x + 14 * zoom, pos.y);
        ctx.lineTo(pos.x + 22 * zoom, shieldY - 10 * zoom);
        ctx.lineTo(pos.x - 22 * zoom, shieldY - 10 * zoom);
        ctx.closePath();
        ctx.fillStyle = coneGrad;
        ctx.fill();

        // Rotating holographic rings around shield
        ctx.beginPath();
        ctx.ellipse(pos.x, shieldY, 24 * zoom, 10 * zoom, t * 0.9, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(0, 240, 255, 0.75)';
        ctx.lineWidth = 1.4 * zoom;
        ctx.stroke();

        ctx.beginPath();
        ctx.ellipse(pos.x, shieldY, 19 * zoom, 8 * zoom, -t * 1.2, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(139, 92, 246, 0.75)';
        ctx.lineWidth = 1.2 * zoom;
        ctx.stroke();

        // Rotating orbit node
        const orbitAngle = t * 1.4;
        const ox = pos.x + Math.cos(orbitAngle) * 23 * zoom;
        const oy = shieldY + Math.sin(orbitAngle) * 9 * zoom;
        ctx.beginPath();
        ctx.arc(ox, oy, 2.3 * zoom, 0, Math.PI * 2);
        ctx.fillStyle = '#00f0ff';
        ctx.fill();

        // Central Cybersecurity Shield Hologram Shape
        const sw = 13 * zoom;
        const sh = 16 * zoom;
        ctx.beginPath();
        ctx.moveTo(pos.x, shieldY - sh);
        ctx.lineTo(pos.x + sw, shieldY - sh * 0.55);
        ctx.lineTo(pos.x + sw * 0.85, shieldY + sh * 0.35);
        ctx.lineTo(pos.x, shieldY + sh);
        ctx.lineTo(pos.x - sw * 0.85, shieldY + sh * 0.35);
        ctx.lineTo(pos.x - sw, shieldY - sh * 0.55);
        ctx.closePath();

        const shieldGrad = ctx.createLinearGradient(pos.x - sw, shieldY - sh, pos.x + sw, shieldY + sh);
        shieldGrad.addColorStop(0, 'rgba(0, 240, 255, 0.45)');
        shieldGrad.addColorStop(1, 'rgba(139, 92, 246, 0.45)');
        ctx.fillStyle = shieldGrad;
        ctx.fill();
        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 1.8 * zoom;
        ctx.stroke();

        // Trust evaluation & safety seal inside holographic crest
        drawCanvasIcon(ctx, CANVAS_ASSETS.evaluation, pos.x, shieldY - 1 * zoom, 13 * zoom);

        ctx.fillStyle = '#67e8f9';
        ctx.font = `700 ${Math.max(7.5, Math.floor(8.5 * zoom))}px Inter, system-ui, sans-serif`;
        ctx.textAlign = 'center';
        ctx.fillText('TRUST SHIELD', pos.x, pos.y + 17 * zoom);
        ctx.restore();
      },
    },

    // 4. Human Approval Console (Right Wing)
    {
      depth: cx + 1.45 + (cy - 1.25),
      draw: () => {
        const pos = gridToScreen(cx + 1.45, cy - 1.25, originX, originY, zoom);
        ctx.save();

        traceIsoDiamond(ctx, pos.x, pos.y, 19 * zoom, 9.5 * zoom);
        ctx.fillStyle = '#162032';
        ctx.fill();
        ctx.strokeStyle = 'rgba(245, 158, 11, 0.65)';
        ctx.lineWidth = 1.2 * zoom;
        ctx.stroke();

        // Console display unit
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(pos.x - 9 * zoom, pos.y - 22 * zoom, 18 * zoom, 14 * zoom);
        ctx.strokeStyle = '#f59e0b';
        ctx.lineWidth = 1.1 * zoom;
        ctx.strokeRect(pos.x - 9 * zoom, pos.y - 22 * zoom, 18 * zoom, 14 * zoom);

        // Pulsing HITL approval ring indicator on screen
        const gatePulse = 0.55 + 0.45 * Math.sin(t * 3);
        ctx.beginPath();
        ctx.arc(pos.x, pos.y - 15 * zoom, 3.5 * zoom, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(245, 158, 11, ${gatePulse})`;
        ctx.fill();

        drawCanvasIcon(ctx, CANVAS_ASSETS.humanApproval, pos.x, pos.y - 31 * zoom, 14 * zoom);

        ctx.fillStyle = '#fcd34d';
        ctx.font = `600 ${Math.max(7, Math.floor(7.5 * zoom))}px Inter, system-ui, sans-serif`;
        ctx.textAlign = 'center';
        ctx.fillText('HITL GATE', pos.x, pos.y + 15 * zoom);
        ctx.restore();
      },
    },

    // 5. Isolation / Sandbox Containment Bay Display (Front-Left)
    {
      depth: cx - 0.35 + (cy + 1.25),
      draw: () => {
        const pos = gridToScreen(cx - 0.35, cy + 1.25, originX, originY, zoom);
        ctx.save();

        traceIsoDiamond(ctx, pos.x, pos.y, 17 * zoom, 8.5 * zoom);
        ctx.fillStyle = '#11192a';
        ctx.fill();
        ctx.strokeStyle = 'rgba(16, 185, 129, 0.6)';
        ctx.lineWidth = 1.1 * zoom;
        ctx.stroke();

        // Containment wireframe arc
        ctx.beginPath();
        ctx.ellipse(pos.x, pos.y - 7 * zoom, 11 * zoom, 5.5 * zoom, 0, 0, Math.PI * 2);
        ctx.setLineDash([3 * zoom, 2.5 * zoom]);
        ctx.strokeStyle = 'rgba(16, 185, 129, 0.75)';
        ctx.lineWidth = 1.1 * zoom;
        ctx.stroke();
        ctx.setLineDash([]);

        drawCanvasIcon(ctx, CANVAS_ASSETS.sandbox, pos.x, pos.y - 16 * zoom, 13 * zoom);

        ctx.fillStyle = '#6ee7b7';
        ctx.font = `600 ${Math.max(7, Math.floor(7.5 * zoom))}px Inter, system-ui, sans-serif`;
        ctx.textAlign = 'center';
        ctx.fillText('SANDBOX', pos.x, pos.y + 14 * zoom);
        ctx.restore();
      },
    },

    // 6. Small Holographic Audit & Verification Display (Front-Right)
    {
      depth: cx + 1.45 + (cy + 0.65),
      draw: () => {
        const pos = gridToScreen(cx + 1.45, cy + 0.65, originX, originY, zoom);
        ctx.save();

        traceIsoDiamond(ctx, pos.x, pos.y, 17 * zoom, 8.5 * zoom);
        ctx.fillStyle = '#11192a';
        ctx.fill();
        ctx.strokeStyle = 'rgba(0, 240, 255, 0.55)';
        ctx.lineWidth = 1.1 * zoom;
        ctx.stroke();

        // Floating translucent holographic audit panel
        ctx.fillStyle = 'rgba(15, 23, 42, 0.88)';
        ctx.fillRect(pos.x - 10 * zoom, pos.y - 21 * zoom, 20 * zoom, 13 * zoom);
        ctx.strokeStyle = 'rgba(56, 189, 248, 0.8)';
        ctx.lineWidth = 1 * zoom;
        ctx.strokeRect(pos.x - 10 * zoom, pos.y - 21 * zoom, 20 * zoom, 13 * zoom);

        // Scrolling audit hash verification bars
        for (let line = 0; line < 3; line++) {
          const pulse = 0.4 + 0.6 * ((Math.sin(t * 2.5 + line * 1.1) + 1) / 2);
          ctx.fillStyle = `rgba(56, 189, 248, ${pulse})`;
          ctx.fillRect(pos.x - 7 * zoom, pos.y - (18 - line * 3.5) * zoom, (11 + (line % 2) * 3) * zoom, 1.5 * zoom);
        }

        drawCanvasIcon(ctx, CANVAS_ASSETS.citations, pos.x, pos.y - 29 * zoom, 13 * zoom);

        ctx.fillStyle = '#a5f3fc';
        ctx.font = `600 ${Math.max(7, Math.floor(7.5 * zoom))}px Inter, system-ui, sans-serif`;
        ctx.textAlign = 'center';
        ctx.fillText('AUDIT CHAIN', pos.x, pos.y + 14 * zoom);
        ctx.restore();
      },
    },
  ];

  // Strict painter's algorithm ordering inside the control room
  stationItems.sort((a, b) => a.depth - b.depth);
  stationItems.forEach((item) => item.draw());
}

export const IsometricOfficeCanvas: React.FC<IsometricOfficeCanvasProps> = ({
  agents,
  departments,
  selectedAgentId,
  onSelectAgent,
  onSelectDepartment,
  highlightedIncidentId,
  onSelectSupervisorStation,
  activeAnomaliesCount,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Pan and Zoom viewport state
  const [zoom, setZoom] = useState<number>(1.0);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [hoveredAgentId, setHoveredAgentId] = useState<string | null>(null);
  const [hoveredDeptId, setHoveredDeptId] = useState<OfficeDepartmentId | null>(null);

  // Animation frame references
  const animTimeRef = useRef<number>(0);
  const frameIdRef = useRef<number>(0);

  // Reset viewport to center
  const handleResetView = useCallback(() => {
    if (!containerRef.current) return;
    const { clientWidth, clientHeight } = containerRef.current;
    setZoom(1.0);
    setPan({ x: clientWidth / 2, y: clientHeight / 3.2 });
  }, []);

  // Initialize view position on mount
  useEffect(() => {
    handleResetView();
  }, [handleResetView]);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (!canvasRef.current || !containerRef.current) return;
      const dpr = window.devicePixelRatio || 1;
      const rect = containerRef.current.getBoundingClientRect();
      canvasRef.current.width = rect.width * dpr;
      canvasRef.current.height = rect.height * dpr;
      canvasRef.current.style.width = `${rect.width}px`;
      canvasRef.current.style.height = `${rect.height}px`;
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Mouse wheel zoom
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.1 : 0.9;
    setZoom((prev) => Math.min(Math.max(prev * factor, 0.45), 2.2));
  };

  // Mouse drag pan
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return;
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
      return;
    }

    // Hover detection
    if (!canvasRef.current || !containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    let foundAgent: string | null = null;
    for (const ag of agents) {
      const screenPos = gridToScreen(ag.deskPosition.gridX, ag.deskPosition.gridY, pan.x, pan.y, zoom);
      const dist = Math.hypot(mouseX - screenPos.x, mouseY - (screenPos.y - 25 * zoom));
      if (dist < 32 * zoom) {
        foundAgent = ag.agent_id;
        break;
      }
    }
    setHoveredAgentId(foundAgent);

    // Check department hover if no agent
    if (!foundAgent) {
      const { gx, gy } = screenToGrid(mouseX, mouseY, pan.x, pan.y, zoom);
      const foundDept = departments.find(
        (d) =>
          gx >= d.gridX &&
          gx <= d.gridX + d.width &&
          gy >= d.gridY &&
          gy <= d.gridY + d.height
      );
      setHoveredDeptId(foundDept ? foundDept.id : null);
    } else {
      setHoveredDeptId(null);
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleClick = (e: React.MouseEvent) => {
    if (!canvasRef.current || !containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Check if clicked near CAS station (grid position 2, 0)
    const casScreen = gridToScreen(2, 0, pan.x, pan.y, zoom);
    const casDist = Math.hypot(mouseX - casScreen.x, mouseY - (casScreen.y - 15 * zoom));
    if (casDist < 35 * zoom && onSelectSupervisorStation) {
      onSelectSupervisorStation();
      return;
    }

    if (hoveredAgentId) {
      onSelectAgent(hoveredAgentId);
    } else if (hoveredDeptId) {
      onSelectDepartment(hoveredDeptId);
    }
  };

  // Main Render Loop
  useEffect(() => {
    let lastTimestamp = performance.now();

    const render = (now: number) => {
      if (document.hidden) return;
      const dt = Math.min(Math.max((now - lastTimestamp) / 1000, 0), 0.1);
      lastTimestamp = now;
      animTimeRef.current += dt;

      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      const dpr = window.devicePixelRatio || 1;
      const width = canvas.width / dpr;
      const height = canvas.height / dpr;

      ctx.save();
      ctx.scale(dpr, dpr);

      // 1. Clear background - Deep Cyber Space
      ctx.fillStyle = '#070a13';
      ctx.fillRect(0, 0, width, height);

      // Subtle isometric ambient background grid
      ctx.strokeStyle = 'rgba(15, 23, 42, 0.6)';
      ctx.lineWidth = 1;
      const bgGridSize = 24;
      for (let x = -bgGridSize; x <= bgGridSize; x += 4) {
        const p1 = gridToScreen(x, -bgGridSize, pan.x, pan.y, zoom);
        const p2 = gridToScreen(x, bgGridSize, pan.x, pan.y, zoom);
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.stroke();
      }
      for (let y = -bgGridSize; y <= bgGridSize; y += 4) {
        const p1 = gridToScreen(-bgGridSize, y, pan.x, pan.y, zoom);
        const p2 = gridToScreen(bgGridSize, y, pan.x, pan.y, zoom);
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.stroke();
      }

      // 2. Draw Departments (Floors & Boundaries)
      departments.forEach((dept) => {
        const isHovered = hoveredDeptId === dept.id;
        const pTop = gridToScreen(dept.gridX, dept.gridY, pan.x, pan.y, zoom);
        const pRight = gridToScreen(dept.gridX + dept.width, dept.gridY, pan.x, pan.y, zoom);
        const pBottom = gridToScreen(dept.gridX + dept.width, dept.gridY + dept.height, pan.x, pan.y, zoom);
        const pLeft = gridToScreen(dept.gridX, dept.gridY + dept.height, pan.x, pan.y, zoom);

        // Floor polygon
        ctx.beginPath();
        ctx.moveTo(pTop.x, pTop.y);
        ctx.lineTo(pRight.x, pRight.y);
        ctx.lineTo(pBottom.x, pBottom.y);
        ctx.lineTo(pLeft.x, pLeft.y);
        ctx.closePath();

        // Floor gradient
        const isCommand = dept.id === 'command_center';
        const isGovernance = dept.id === 'governance_trust';
        const centerX = (pTop.x + pBottom.x) / 2;
        const centerY = (pTop.y + pBottom.y) / 2;
        if (isCommand) {
          const grad = ctx.createRadialGradient(
            centerX,
            centerY,
            10 * zoom,
            centerX,
            centerY,
            90 * zoom
          );
          grad.addColorStop(0, 'rgba(14, 165, 233, 0.25)');
          grad.addColorStop(1, 'rgba(8, 14, 28, 0.85)');
          ctx.fillStyle = grad;
        } else if (isGovernance) {
          const govGrad = ctx.createRadialGradient(
            centerX,
            centerY,
            8 * zoom,
            centerX,
            centerY,
            115 * zoom
          );
          govGrad.addColorStop(0, isHovered ? 'rgba(34, 211, 238, 0.18)' : 'rgba(14, 165, 233, 0.14)');
          govGrad.addColorStop(0.55, isHovered ? 'rgba(139, 92, 246, 0.16)' : 'rgba(99, 102, 241, 0.12)');
          govGrad.addColorStop(1, 'rgba(10, 18, 36, 0.86)');
          ctx.fillStyle = govGrad;
        } else {
          ctx.fillStyle = isHovered ? 'rgba(30, 41, 59, 0.7)' : 'rgba(15, 23, 42, 0.75)';
        }
        ctx.fill();

        // Department perimeter border
        ctx.strokeStyle = isHovered
          ? dept.color
          : isCommand
          ? '#00f0ff'
          : isGovernance
          ? 'rgba(56, 189, 248, 0.55)'
          : 'rgba(71, 85, 105, 0.4)';
        ctx.lineWidth = isHovered || isCommand ? 2 * zoom : isGovernance ? 1.5 * zoom : 1 * zoom;
        ctx.stroke();

        // Department Header Label in isometric floor
        const centerPos = gridToScreen(
          dept.gridX + dept.width / 2,
          dept.gridY + dept.height / 2,
          pan.x,
          pan.y,
          zoom
        );
        ctx.fillStyle = isCommand ? '#38bdf8' : '#94a3b8';
        ctx.font = `600 ${Math.max(10, Math.floor(12 * zoom))}px Inter, system-ui, sans-serif`;
        ctx.textAlign = 'center';
        ctx.fillText(dept.name.toUpperCase(), centerPos.x, pBottom.y - 12 * zoom);
      });

      // 3. Draw Cyber Conduits (Lines connecting each department to Command Center)
      const cmdCenter = departments.find((d) => d.id === 'command_center');
      if (cmdCenter) {
        const cmdPos = gridToScreen(
          cmdCenter.gridX + cmdCenter.width / 2,
          cmdCenter.gridY + cmdCenter.height / 2,
          pan.x,
          pan.y,
          zoom
        );

        departments.forEach((dept) => {
          if (dept.id === 'command_center') return;
          const deptPos = gridToScreen(
            dept.gridX + dept.width / 2,
            dept.gridY + dept.height / 2,
            pan.x,
            pan.y,
            zoom
          );

          const dx = cmdPos.x - deptPos.x;
          const dy = cmdPos.y - deptPos.y;
          const len = Math.hypot(dx, dy) || 1;
          const nx = -dy / len;
          const ny = dx / len;

          const conduitTracks =
            dept.id === 'governance_trust'
              ? [
                  {
                    offset: -4.5 * zoom,
                    lineColor: 'rgba(0, 240, 255, 0.34)',
                    pulseColor: '#00f0ff',
                    phase: 0,
                    speed: 0.48,
                    radius: 3.6,
                    width: 2.2,
                  },
                  {
                    offset: 4.5 * zoom,
                    lineColor: 'rgba(139, 92, 246, 0.34)',
                    pulseColor: '#8b5cf6',
                    phase: 0.45,
                    speed: 0.48,
                    radius: 3.6,
                    width: 2.2,
                  },
                ]
              : [
                  {
                    offset: 0,
                    lineColor: 'rgba(14, 165, 233, 0.2)',
                    pulseColor: dept.color,
                    phase: (dept.gridX % 3) * 0.3,
                    speed: 0.4,
                    radius: 3.5,
                    width: 2,
                  },
                ];

          conduitTracks.forEach((track) => {
            const ox = nx * track.offset;
            const oy = ny * track.offset;
            const startX = deptPos.x + ox;
            const startY = deptPos.y + oy;
            const endX = cmdPos.x + ox;
            const endY = cmdPos.y + oy;

            // Conduit cable line
            ctx.beginPath();
            ctx.moveTo(startX, startY);
            ctx.lineTo(endX, endY);
            ctx.strokeStyle = track.lineColor;
            ctx.lineWidth = track.width * zoom;
            if (dept.id === 'governance_trust') {
              ctx.shadowColor = track.pulseColor;
              ctx.shadowBlur = 6 * zoom;
            }
            ctx.stroke();
            ctx.shadowBlur = 0;

            // Animated data pulse packet traveling along the conduit
            const pulseProgress =
              (((animTimeRef.current * track.speed + track.phase) % 1.0) + 1.0) % 1.0;
            const pulseX = startX + (endX - startX) * pulseProgress;
            const pulseY = startY + (endY - startY) * pulseProgress;

            ctx.beginPath();
            ctx.arc(pulseX, pulseY, track.radius * zoom, 0, Math.PI * 2);
            ctx.fillStyle = track.pulseColor;
            ctx.shadowColor = track.pulseColor;
            ctx.shadowBlur = 8 * zoom;
            ctx.fill();
            ctx.shadowBlur = 0; // reset
          });
        });
      }

      // 4. Draw Central Holographic Core in Command Center
      if (cmdCenter) {
        const corePos = gridToScreen(
          cmdCenter.gridX + cmdCenter.width / 2,
          cmdCenter.gridY + cmdCenter.height / 2,
          pan.x,
          pan.y,
          zoom
        );
        const bob = Math.sin(animTimeRef.current * 2) * 5 * zoom;
        const coreY = corePos.y - 45 * zoom + bob;

        // Holographic rings
        ctx.save();
        ctx.strokeStyle = 'rgba(0, 240, 255, 0.7)';
        ctx.lineWidth = 1.5 * zoom;
        ctx.beginPath();
        ctx.ellipse(corePos.x, coreY, 28 * zoom, 12 * zoom, animTimeRef.current, 0, Math.PI * 2);
        ctx.stroke();

        ctx.strokeStyle = 'rgba(147, 51, 234, 0.7)';
        ctx.beginPath();
        ctx.ellipse(corePos.x, coreY, 22 * zoom, 9 * zoom, -animTimeRef.current * 1.5, 0, Math.PI * 2);
        ctx.stroke();

        // Core glowing crystal
        ctx.fillStyle = '#00f0ff';
        ctx.shadowColor = '#00f0ff';
        ctx.shadowBlur = 15 * zoom;
        ctx.beginPath();
        ctx.arc(corePos.x, coreY, 8 * zoom, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;

        // Draw SuperIntelligence Orchestration Icon beside core crystal
        const orchIcon = getOrLoadCanvasIcon(CANVAS_ASSETS.orchestration);
        if (orchIcon) {
          const isz = 20 * zoom;
          ctx.drawImage(orchIcon, corePos.x - isz / 2, coreY - 26 * zoom, isz, isz);
        }

        ctx.restore();
      }

      // 4b. Draw Central Agent Supervisor (CAS) Station in Command Centre
      const casDeskScreen = gridToScreen(2, 0, pan.x, pan.y, zoom);

      ctx.save();
      ctx.fillStyle = '#0f172a';
      ctx.strokeStyle = '#f59e0b';
      ctx.lineWidth = 1.5 * zoom;
      const cdw = 28 * zoom;
      const cdh = 14 * zoom;
      ctx.beginPath();
      ctx.moveTo(casDeskScreen.x, casDeskScreen.y - cdh);
      ctx.lineTo(casDeskScreen.x + cdw, casDeskScreen.y);
      ctx.lineTo(casDeskScreen.x, casDeskScreen.y + cdh);
      ctx.lineTo(casDeskScreen.x - cdw, casDeskScreen.y);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();

      // SuperIntelligence Monitoring Icon at CAS Desk
      const monIcon = getOrLoadCanvasIcon(CANVAS_ASSETS.monitoring);
      if (monIcon) {
        const isz = 26 * zoom;
        ctx.drawImage(monIcon, casDeskScreen.x - isz / 2, casDeskScreen.y - 26 * zoom, isz, isz);
      } else {
        // Fallback Terminal
        ctx.fillStyle = '#f59e0b';
        ctx.shadowColor = '#f59e0b';
        ctx.shadowBlur = 8 * zoom;
        ctx.fillRect(casDeskScreen.x - 12 * zoom, casDeskScreen.y - 24 * zoom, 24 * zoom, 12 * zoom);
        ctx.shadowBlur = 0;
      }

      // Label CAS SUPERVISOR
      ctx.fillStyle = '#fbbf24';
      ctx.font = `bold ${Math.max(8, Math.floor(9 * zoom))}px Inter, system-ui, sans-serif`;
      ctx.textAlign = 'center';
      ctx.fillText('CAS SUPERVISOR', casDeskScreen.x, casDeskScreen.y + 24 * zoom);

      // Radar scan beam sweeping across all departments
      const radarAngle = animTimeRef.current * 1.5;
      const radarRadius = 260 * zoom;
      ctx.beginPath();
      ctx.moveTo(casDeskScreen.x, casDeskScreen.y);
      ctx.arc(casDeskScreen.x, casDeskScreen.y, radarRadius, radarAngle, radarAngle + Math.PI / 4);
      ctx.closePath();
      ctx.fillStyle = 'rgba(0, 240, 255, 0.05)';
      ctx.fill();

      // Supervisory trace beams to any anomalous or isolated agents
      agents.forEach((ag) => {
        if (ag.isIsolated || ag.status === 'ISOLATED' || ag.status === 'FAILED' || ag.status === 'DEGRADED') {
          const targetScreen = gridToScreen(ag.deskPosition.gridX, ag.deskPosition.gridY, pan.x, pan.y, zoom);
          ctx.beginPath();
          ctx.moveTo(casDeskScreen.x, casDeskScreen.y - 12 * zoom);
          ctx.lineTo(targetScreen.x, targetScreen.y - 20 * zoom);
          ctx.strokeStyle = 'rgba(239, 68, 68, 0.6)';
          ctx.setLineDash([4 * zoom, 4 * zoom]);
          ctx.lineWidth = 1.5 * zoom;
          ctx.stroke();
          ctx.setLineDash([]);
        }
      });
      ctx.restore();

      // 4c. AI Trust & Governance Security Station
      const govDept = departments.find((d) => d.id === 'governance_trust');
      if (govDept) {
        const hasRegisteredGovAgent = agents.some(
          (ag) => ag.departmentId === 'governance_trust'
        );
        drawGovernanceSecurityStation(
          ctx,
          govDept,
          hasRegisteredGovAgent,
          pan.x,
          pan.y,
          zoom,
          animTimeRef.current
        );
      }

      // 5. Draw Furniture (Desks, Dual Monitors, Server Racks)
      agents.forEach((ag) => {
        const deskScreen = gridToScreen(ag.deskPosition.gridX, ag.deskPosition.gridY, pan.x, pan.y, zoom);

        // Desk top diamond
        const dw = 32 * zoom;
        const dh = 16 * zoom;
        ctx.fillStyle = '#1e293b';
        ctx.beginPath();
        ctx.moveTo(deskScreen.x, deskScreen.y - dh);
        ctx.lineTo(deskScreen.x + dw, deskScreen.y);
        ctx.lineTo(deskScreen.x, deskScreen.y + dh);
        ctx.lineTo(deskScreen.x - dw, deskScreen.y);
        ctx.closePath();
        ctx.fill();
        ctx.strokeStyle = '#334155';
        ctx.lineWidth = 1 * zoom;
        ctx.stroke();

        // Dual Curved Computer Monitors
        const screenColor = ag.status === 'ISOLATED' ? '#ef4444' : ag.status === 'ANALYSING' ? '#00f0ff' : '#0ea5e9';
        // Main monitor
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(deskScreen.x - 14 * zoom, deskScreen.y - 28 * zoom, 18 * zoom, 12 * zoom);
        ctx.fillStyle = screenColor;
        ctx.shadowColor = screenColor;
        ctx.shadowBlur = ag.status === 'ANALYSING' ? 8 * zoom : 2 * zoom;
        ctx.fillRect(deskScreen.x - 13 * zoom, deskScreen.y - 27 * zoom, 16 * zoom, 10 * zoom);
        ctx.shadowBlur = 0;

        // Secondary terminal monitor
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(deskScreen.x + 6 * zoom, deskScreen.y - 25 * zoom, 14 * zoom, 10 * zoom);
        ctx.fillStyle = ag.accentColor;
        ctx.fillRect(deskScreen.x + 7 * zoom, deskScreen.y - 24 * zoom, 12 * zoom, 8 * zoom);
      });

      // 6. Draw Agents with Animated Avatars & Status Indicators
      // Sort agents by grid depth for correct painter's algorithm
      const sortedAgents = [...agents].sort((a, b) => {
        return a.deskPosition.gridX + a.deskPosition.gridY - (b.deskPosition.gridX + b.deskPosition.gridY);
      });

      sortedAgents.forEach((ag) => {
        const basePos = gridToScreen(ag.deskPosition.gridX, ag.deskPosition.gridY, pan.x, pan.y, zoom);
        const isSelected = selectedAgentId === ag.agent_id;
        const isHovered = hoveredAgentId === ag.agent_id;
        const statusConfig = STATUS_COLORS[ag.status] || STATUS_COLORS.IDLE;

        // Animation offsets
        const isAnalysing = ag.status === 'ANALYSING' || ag.status === 'GENERATING_EVIDENCE';
        const typingOffset = isAnalysing ? Math.sin(animTimeRef.current * 12) * 1.5 * zoom : 0;
        const breatheOffset = Math.sin(animTimeRef.current * 3 + ag.deskPosition.gridX) * 1.5 * zoom;

        const agentScreenX = basePos.x - 6 * zoom;
        const agentScreenY = basePos.y - 12 * zoom + breatheOffset;

        // Selection / Hover Halo Ring
        if (isSelected || isHovered) {
          ctx.save();
          ctx.beginPath();
          ctx.ellipse(agentScreenX, basePos.y + 6 * zoom, 22 * zoom, 10 * zoom, 0, 0, Math.PI * 2);
          ctx.strokeStyle = isSelected ? '#00f0ff' : 'rgba(255, 255, 255, 0.6)';
          ctx.lineWidth = isSelected ? 2.5 * zoom : 1.5 * zoom;
          ctx.shadowColor = isSelected ? '#00f0ff' : 'white';
          ctx.shadowBlur = 10 * zoom;
          ctx.stroke();
          ctx.shadowBlur = 0;
          ctx.restore();
        }

        // Agent Avatar - Vector Cyber Specialist
        // Chair
        ctx.fillStyle = '#1e293b';
        ctx.beginPath();
        ctx.arc(agentScreenX, agentScreenY + 12 * zoom, 7 * zoom, 0, Math.PI * 2);
        ctx.fill();

        // Agent Body / Torso
        ctx.fillStyle = ag.isIsolated ? '#7f1d1d' : '#1e293b';
        ctx.beginPath();
        ctx.roundRect(agentScreenX - 8 * zoom, agentScreenY - 10 * zoom, 16 * zoom, 16 * zoom, 4 * zoom);
        ctx.fill();
        ctx.strokeStyle = ag.accentColor;
        ctx.lineWidth = 1 * zoom;
        ctx.stroke();

        // Agent Head
        ctx.fillStyle = ag.isIsolated ? '#b91c1c' : '#0f172a';
        ctx.beginPath();
        ctx.arc(agentScreenX, agentScreenY - 18 * zoom, 8 * zoom, 0, Math.PI * 2);
        ctx.fill();

        // Visor / Cyber Eye Glow
        ctx.fillStyle = statusConfig.main;
        ctx.shadowColor = statusConfig.main;
        ctx.shadowBlur = 6 * zoom;
        ctx.fillRect(agentScreenX - 5 * zoom, agentScreenY - 20 * zoom, 10 * zoom, 4 * zoom);
        ctx.shadowBlur = 0;

        // Animated Hands / Typing Action
        ctx.fillStyle = '#94a3b8';
        ctx.beginPath();
        ctx.arc(agentScreenX - 6 * zoom, agentScreenY + typingOffset, 2.5 * zoom, 0, Math.PI * 2);
        ctx.arc(agentScreenX + 6 * zoom, agentScreenY - typingOffset, 2.5 * zoom, 0, Math.PI * 2);
        ctx.fill();

        // Status Beacon / Activity Orb (above agent head)
        const beaconY = agentScreenY - 32 * zoom;
        ctx.beginPath();
        ctx.arc(agentScreenX, beaconY, 4 * zoom, 0, Math.PI * 2);
        ctx.fillStyle = statusConfig.main;
        ctx.shadowColor = statusConfig.glow;
        ctx.shadowBlur = 12 * zoom;
        ctx.fill();
        ctx.shadowBlur = 0;

        // Draw SuperIntelligence Role / Activity System Icon above agent
        let roleIconSrc = CANVAS_ASSETS.agent;
        if (ag.isIsolated || ag.status === 'ISOLATED') {
          roleIconSrc = CANVAS_ASSETS.sandbox;
        } else if (ag.status === 'WAITING_FOR_APPROVAL') {
          roleIconSrc = CANVAS_ASSETS.humanApproval;
        } else if (ag.status === 'COMMUNICATING' || ag.status === 'HANDOFF') {
          roleIconSrc = CANVAS_ASSETS.a2a;
        } else if (ag.status === 'GENERATING_EVIDENCE') {
          roleIconSrc = CANVAS_ASSETS.tools;
        } else if (ag.departmentId === 'network_ops') {
          roleIconSrc = CANVAS_ASSETS.tools;
        } else if (ag.departmentId === 'phishing_intel') {
          roleIconSrc = CANVAS_ASSETS.reasoning;
        } else if (ag.departmentId === 'behaviour_intel') {
          roleIconSrc = CANVAS_ASSETS.memory;
        } else if (ag.departmentId === 'identity_sec') {
          roleIconSrc = CANVAS_ASSETS.permissions;
        } else if (ag.departmentId === 'transaction_sec') {
          roleIconSrc = CANVAS_ASSETS.dataset;
        } else if (ag.departmentId === 'governance_trust') {
          roleIconSrc = CANVAS_ASSETS.permissions;
        }

        const roleImg = getOrLoadCanvasIcon(roleIconSrc);
        if (roleImg) {
          const rSize = 13 * zoom;
          ctx.drawImage(roleImg, agentScreenX - rSize / 2, beaconY - 26 * zoom, rSize, rSize);
        }

        // Pulsing rings for waiting for approval or isolated
        if (ag.status === 'WAITING_FOR_APPROVAL' || ag.status === 'ISOLATED') {
          const pulseRadius = (4 + (Math.sin(animTimeRef.current * 4) + 1) * 3) * zoom;
          ctx.strokeStyle = statusConfig.main;
          ctx.lineWidth = 1.5 * zoom;
          ctx.beginPath();
          ctx.arc(agentScreenX, beaconY, pulseRadius, 0, Math.PI * 2);
          ctx.stroke();
        }

        // Agent Short Tag & Status Badge
        ctx.fillStyle = '#f8fafc';
        ctx.font = `700 ${Math.max(9, Math.floor(10 * zoom))}px Inter, system-ui, sans-serif`;
        ctx.textAlign = 'center';
        ctx.fillText(ag.shortName, agentScreenX, beaconY - 8 * zoom);

        ctx.fillStyle = statusConfig.text;
        ctx.font = `600 ${Math.max(8, Math.floor(8.5 * zoom))}px Inter, system-ui, sans-serif`;
        ctx.fillText(ag.status.replace(/_/g, ' '), agentScreenX, beaconY - 18 * zoom);

        // Active task balloon if actively working
        if (ag.currentTask && isSelected) {
          ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
          ctx.strokeStyle = '#00f0ff';
          ctx.lineWidth = 1 * zoom;
          const bubbleW = 120 * zoom;
          const bubbleH = 24 * zoom;
          const bx = agentScreenX - bubbleW / 2;
          const by = beaconY - 44 * zoom;
          ctx.beginPath();
          ctx.roundRect(bx, by, bubbleW, bubbleH, 4 * zoom);
          ctx.fill();
          ctx.stroke();

          ctx.fillStyle = '#38bdf8';
          ctx.font = `500 ${Math.max(8, Math.floor(9 * zoom))}px Inter, system-ui, sans-serif`;
          ctx.fillText(
            ag.currentTask.length > 20 ? ag.currentTask.slice(0, 19) + '…' : ag.currentTask,
            agentScreenX,
            by + 16 * zoom
          );
        }
      });

      // 7. Interactive Hover Tooltip for Agents
      if (hoveredAgentId && !isDragging) {
        const ag = agents.find((a) => a.agent_id === hoveredAgentId);
        if (ag) {
          const basePos = gridToScreen(ag.deskPosition.gridX, ag.deskPosition.gridY, pan.x, pan.y, zoom);
          const tX = basePos.x + 25 * zoom;
          const tY = basePos.y - 70 * zoom;
          const tW = 180;
          const tH = 80;

          ctx.fillStyle = 'rgba(15, 23, 42, 0.95)';
          ctx.strokeStyle = '#38bdf8';
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.roundRect(tX, tY, tW, tH, 6);
          ctx.fill();
          ctx.stroke();

          ctx.fillStyle = '#ffffff';
          ctx.font = 'bold 12px Inter, system-ui, sans-serif';
          ctx.textAlign = 'left';
          ctx.fillText(ag.name, tX + 10, tY + 20);

          ctx.fillStyle = STATUS_COLORS[ag.status]?.text || '#94a3b8';
          ctx.font = '600 10px Inter, system-ui, sans-serif';
          ctx.fillText(`Status: ${ag.status}`, tX + 10, tY + 36);

          ctx.fillStyle = '#94a3b8';
          ctx.font = '10px Inter, system-ui, sans-serif';
          ctx.fillText(`Reliability: ${(ag.reliabilityScore * 100).toFixed(1)}%`, tX + 10, tY + 52);
          ctx.fillText(`Processed: ${ag.eventsProcessed} events`, tX + 10, tY + 66);
        }
      }

      ctx.restore();

      // Loop only if tab visible
      if (!document.hidden) {
        frameIdRef.current = requestAnimationFrame(render);
      }
    };

    frameIdRef.current = requestAnimationFrame(render);

    const handleVisibilityChange = () => {
      if (!document.hidden) {
        lastTimestamp = performance.now();
        frameIdRef.current = requestAnimationFrame(render);
      } else {
        cancelAnimationFrame(frameIdRef.current);
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      cancelAnimationFrame(frameIdRef.current);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [agents, departments, pan, zoom, isDragging, dragStart, hoveredAgentId, hoveredDeptId, selectedAgentId]);

  return (
    <div
      ref={containerRef}
      className="relative w-full h-full min-h-[560px] bg-[#070a13] overflow-hidden select-none cursor-grab active:cursor-grabbing"
      onWheel={handleWheel}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onClick={handleClick}
    >
      <canvas ref={canvasRef} className="block w-full h-full" />

      {/* Floating Canvas Viewport HUD Controls */}
      <div className="absolute bottom-4 right-4 flex items-center space-x-2 bg-slate-900/80 backdrop-blur border border-slate-700/60 rounded-lg p-1.5 shadow-xl">
        <button
          onClick={(e) => {
            e.stopPropagation();
            setZoom((z) => Math.min(z * 1.2, 2.2));
          }}
          className="p-1.5 text-slate-300 hover:text-cyan-400 hover:bg-slate-800 rounded transition"
          title="Zoom In"
        >
          <ZoomIn size={16} />
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            setZoom((z) => Math.max(z / 1.2, 0.45));
          }}
          className="p-1.5 text-slate-300 hover:text-cyan-400 hover:bg-slate-800 rounded transition"
          title="Zoom Out"
        >
          <ZoomOut size={16} />
        </button>
        <div className="w-px h-4 bg-slate-700" />
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleResetView();
          }}
          className="p-1.5 text-slate-300 hover:text-cyan-400 hover:bg-slate-800 rounded transition"
          title="Reset View"
        >
          <RotateCcw size={16} />
        </button>
      </div>

      {/* Office Department Quick Navigator */}
      <div className="absolute top-4 left-4 flex flex-wrap gap-1.5 max-w-xl pointer-events-auto">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onSelectSupervisorStation?.();
          }}
          className="px-2.5 py-1 text-xs font-semibold rounded-full border transition-all flex items-center space-x-1.5 backdrop-blur shadow-sm bg-amber-950/80 text-amber-300 border-amber-500/60 hover:bg-amber-900"
        >
          <SuperIcon name="monitoring" style="color" size={14} className="mr-0.5" />
          <span>CAS Supervisor ({activeAnomaliesCount || 0} Alerts)</span>
        </button>
        {departments.map((dept) => {
          const isSelected = hoveredDeptId === dept.id;
          const deptIconName =
            dept.id === 'command_center' ? 'orchestration' :
            dept.id === 'network_ops' ? 'tools' :
            dept.id === 'phishing_intel' ? 'reasoning' :
            dept.id === 'identity_sec' ? 'permissions' :
            dept.id === 'behaviour_intel' ? 'memory' :
            dept.id === 'transaction_sec' ? 'dataset' :
            dept.id === 'governance_trust' ? 'permissions' : 'agent';

          return (
            <button
              key={dept.id}
              onClick={(e) => {
                e.stopPropagation();
                onSelectDepartment(dept.id);
                // Center view on department
                if (containerRef.current) {
                  const { clientWidth, clientHeight } = containerRef.current;
                  const targetScreen = gridToScreen(
                    dept.gridX + dept.width / 2,
                    dept.gridY + dept.height / 2,
                    0,
                    0,
                    zoom
                  );
                  setPan({
                    x: clientWidth / 2 - targetScreen.x,
                    y: clientHeight / 2 - targetScreen.y,
                  });
                }
              }}
              className={`px-2.5 py-1 text-xs font-medium rounded-full border transition-all flex items-center space-x-1.5 backdrop-blur shadow-sm ${
                isSelected
                  ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500'
                  : 'bg-slate-900/70 text-slate-300 border-slate-700/60 hover:border-slate-500'
              }`}
            >
              <SuperIcon name={deptIconName} style="duotone" size={13} className="mr-0.5" />
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: dept.color }} />
              <span>{dept.name}</span>
            </button>
          );
        })}
      </div>

      {/* Live Mesh Status Overlay Pill */}
      <div className="absolute top-4 right-4 flex items-center space-x-2 bg-slate-900/80 backdrop-blur border border-slate-700/60 rounded-full px-3 py-1 shadow-lg text-xs">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
        </span>
        <span className="text-slate-200 font-mono">ISOMETRIC AI SOC ACTIVE</span>
        <span className="text-slate-400">|</span>
        <span className="text-cyan-400 font-mono">{(zoom * 100).toFixed(0)}% ZOOM</span>
      </div>
    </div>
  );
};

