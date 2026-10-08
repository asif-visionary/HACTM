import React from 'react';
import {
  LayoutDashboard,
  Layers,
  FileSearch,
  Users,
  Bot,
  FileBarChart2,
  Settings as SettingsIcon,
  GitFork,
  Brain,
  ShieldCheck,
  Network,
  FlaskConical,
  Mail,
  UserCheck,
  KeyRound,
  CreditCard,
  ChevronLeft,
  ChevronRight,
  Award,
  Sliders,
  RefreshCw,
  Activity,
  Box,
  Laptop,
} from 'lucide-react';
import { cn } from '../../lib/utils';

export type NavigationTab =
  | 'overview'
  | '3d-mesh'
  | 'network'
  | 'phishing'
  | 'device'
  | 'uba'
  | 'identity'
  | 'transaction'
  | 'evidence-fusion'
  | 'cyber-risk'
  | 'memory'
  | 'graph'
  | 'temporal'
  | 'research-lab'
  | 'reliability'
  | 'orchestration'
  | 'zero-trust'
  | 'feedback'
  | 'evaluation'
  | 'research'
  | 'events'
  | 'evidence'
  | 'entities'
  | 'agents'
  | 'reports'
  | 'settings';

interface SidebarProps {
  currentTab: NavigationTab;
  onTabChange: (tab: NavigationTab) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
}

interface NavSection {
  title: string;
  items: Array<{
    id: NavigationTab;
    label: string;
    icon: React.ComponentType<{ size?: number; className?: string }>;
    badge?: string;
  }>;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onTabChange,
  collapsed,
  onToggleCollapse,
}) => {
  const mainNavSections: NavSection[] = [
    {
      title: 'COMMAND',
      items: [
        { id: '3d-mesh', label: '3D AI Orchestrator', icon: Box, badge: '3D SOC' },
        { id: 'overview', label: 'Overview', icon: LayoutDashboard },
        { id: 'events', label: 'Security Events', icon: Layers },
        { id: 'evidence', label: 'Evidence Explorer', icon: FileSearch },
        { id: 'entities', label: 'Entities & Assets', icon: Users },
        { id: 'agents', label: 'Agents Status', icon: Bot, badge: '6 Agents' },
        { id: 'reports', label: 'Reports', icon: FileBarChart2 },
      ],
    },
    {
      title: 'SPECIALIZED AGENTS',
      items: [
        { id: 'network', label: 'Network Security', icon: Network },
        { id: 'phishing', label: 'Phishing Intelligence', icon: Mail },
        { id: 'device', label: 'Device Security', icon: Laptop },
        { id: 'uba', label: 'User Behavior (UBA)', icon: UserCheck },
        { id: 'identity', label: 'Identity & Auth', icon: KeyRound },
        { id: 'transaction', label: 'Transaction Security', icon: CreditCard },
      ],
    },
    {
      title: 'INTELLIGENCE & MESH',
      items: [
        { id: 'evidence-fusion', label: 'Evidence Fusion', icon: GitFork },
        { id: 'cyber-risk', label: 'Cyber Risk Assessment', icon: Brain },
        { id: 'memory', label: 'Adaptive Evidence Memory', icon: Brain },
        { id: 'graph', label: 'Attack Evidence Graph', icon: GitFork },
        { id: 'temporal', label: 'Temporal Analysis', icon: Layers },
        { id: 'research-lab', label: 'Research Lab', icon: FlaskConical },
      ],
    },
    {
      title: 'CONTROL & RESEARCH',
      items: [
        { id: 'reliability', label: 'Reliability & Trust', icon: ShieldCheck },
        { id: 'orchestration', label: 'Orchestration Engine', icon: Sliders },
        { id: 'zero-trust', label: 'Zero-Trust Engine', icon: ShieldCheck },
        { id: 'feedback', label: 'Closed-Loop Adaptation', icon: RefreshCw },
        { id: 'evaluation', label: 'Evaluation Engine', icon: Activity },
        { id: 'research', label: 'Research & Publication', icon: Award },
      ],
    },
  ];

  const settingsItem = { id: 'settings' as NavigationTab, label: 'Settings & Ingestion', icon: SettingsIcon };

  return (
    <aside
      className={cn(
        'bg-[#070B12] border-r border-slate-800/80 flex flex-col transition-all duration-200 z-30 select-none h-full min-h-0 text-slate-100',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Fixed Sidebar Header (Collapse Toggle) */}
      <div className="sidebar-header p-3 border-b border-slate-800/80 flex items-center justify-between flex-shrink-0">
        {!collapsed && (
          <div className="flex items-center gap-2 px-1">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            <span className="text-xs font-mono font-bold tracking-wider text-slate-200">NAVIGATION</span>
          </div>
        )}
        <button
          onClick={onToggleCollapse}
          className="p-1.5 rounded-lg bg-[#0B111A] hover:bg-slate-800/80 text-slate-400 hover:text-white transition-colors border border-slate-800 ml-auto"
          title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          aria-label={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
        </button>
      </div>

      {/* Vertically Scrollable Navigation Area */}
      <nav className="sidebar-navigation flex-1 min-h-0 overflow-y-auto overflow-x-hidden hactm-sidebar-scroll p-3 space-y-6">
        {mainNavSections.map((section, idx) => (
          <div key={idx} className="space-y-1">
            {!collapsed && (
              <h4 className="px-3 text-[10px] font-mono font-semibold tracking-wider text-slate-400 uppercase mb-2">
                {section.title}
              </h4>
            )}
            <div className="space-y-1">
              {section.items.map((item) => {
                const Icon = item.icon;
                const isActive = currentTab === item.id;

                return (
                  <button
                    key={item.id}
                    onClick={() => onTabChange(item.id)}
                    title={collapsed ? item.label : undefined}
                    className={cn(
                      'w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all group relative',
                      isActive
                        ? 'bg-[#101923] text-cyan-400 font-semibold border border-cyan-500/30 shadow-sm shadow-cyan-500/10'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-[#0B111A]/80'
                    )}
                  >
                    {isActive && (
                      <span className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-cyan-400 rounded-r-full" />
                    )}
                    <Icon
                      size={16}
                      className={cn(
                        'flex-shrink-0 transition-colors',
                        isActive ? 'text-cyan-400' : 'text-slate-400 group-hover:text-slate-200'
                      )}
                    />
                    {!collapsed && (
                      <span className="truncate flex-1 text-left">{item.label}</span>
                    )}
                    {!collapsed && item.badge && (
                      <span
                        className={cn(
                          'text-[9px] font-mono font-medium px-1.5 py-0.5 rounded-md border',
                          isActive
                            ? 'bg-cyan-950/80 text-cyan-300 border-cyan-800/60'
                            : 'bg-[#0B111A] text-slate-400 border-slate-800'
                        )}
                      >
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Fixed Sidebar Footer (Settings) */}
      <div className="sidebar-footer p-3 border-t border-slate-800/80 flex-shrink-0 bg-[#070B12]">
        <button
          onClick={() => onTabChange(settingsItem.id)}
          title={collapsed ? settingsItem.label : undefined}
          className={cn(
            'w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all group relative',
            currentTab === settingsItem.id
              ? 'bg-[#101923] text-cyan-400 font-semibold border border-cyan-500/30 shadow-sm shadow-cyan-500/10'
              : 'text-slate-400 hover:text-slate-200 hover:bg-[#0B111A]/80'
          )}
        >
          {currentTab === settingsItem.id && (
            <span className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-cyan-400 rounded-r-full" />
          )}
          <SettingsIcon
            size={16}
            className={cn(
              'flex-shrink-0 transition-colors',
              currentTab === settingsItem.id ? 'text-cyan-400' : 'text-slate-400 group-hover:text-slate-200'
            )}
          />
          {!collapsed && <span className="truncate flex-1 text-left">{settingsItem.label}</span>}
        </button>
      </div>
    </aside>
  );
};
