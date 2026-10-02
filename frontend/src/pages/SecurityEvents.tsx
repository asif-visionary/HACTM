import React, { useState } from 'react';
import {
  Layers,
  Search,
  RefreshCw,
  AlertTriangle,
  ShieldAlert,
  Clock,
  Activity,
  Filter,
  Eye,
  X,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { useEvidence } from '../hooks/useEvidence';
import { SecurityEvidence } from '../types/evidence';
import { RiskBadge } from '../components/common/RiskBadge';
import { Badge } from '../components/common/Badge';
import { ErrorState } from '../components/common/ErrorState';
import { formatTimestamp } from '../lib/utils';

export const SecurityEvents: React.FC = () => {
  const [page, setPage] = useState(1);
  const pageSize = 25;
  const [search, setSearch] = useState('');
  const [eventType, setEventType] = useState('');
  const [severity, setSeverity] = useState('');
  const [selectedEvent, setSelectedEvent] = useState<SecurityEvidence | null>(null);

  const queryParams = {
    page,
    page_size: pageSize,
    search: search.trim() || undefined,
    event_type: eventType || undefined,
    severity: severity || undefined,
  };

  const { data, isLoading, isError, refetch } = useEvidence(queryParams);

  const handleReset = () => {
    setSearch('');
    setEventType('');
    setSeverity('');
    setPage(1);
  };

  if (isError) {
    return (
      <ErrorState
        title="Failed to Load Security Events"
        message="An error occurred while retrieving detected security events from the telemetry stream."
        onRetry={() => refetch()}
      />
    );
  }

  const events = data?.data || [];
  const total = data?.pagination?.total || 0;
  const totalPages = Math.ceil(total / pageSize) || 1;

  const highSeverityCount = events.filter(
    (e) => e.severity === 'HIGH' || e.severity === 'CRITICAL' || e.risk_score >= 0.70
  ).length;

  return (
    <div className="space-y-6 animate-in fade-in duration-150 text-slate-100">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-3">
            <div className="p-2.5 bg-indigo-600/20 text-indigo-400 rounded-xl border border-indigo-500/30">
              <Layers className="w-6 h-6" />
            </div>
            <span>Security Events</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time activity stream and historical log of detected security events across all network and multi-domain agents.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => refetch()}
            className="flex items-center space-x-2 px-3.5 py-2 bg-slate-900 hover:bg-slate-800 text-slate-200 rounded-xl text-xs font-medium transition-colors border border-slate-800"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-indigo-400' : ''}`} />
            <span>Refresh Stream</span>
          </button>
        </div>
      </div>

      {/* KPI Overview Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Total Detected Events</span>
            <div className="text-xl font-bold text-white mt-1">{total.toLocaleString()}</div>
          </div>
          <Activity className="w-6 h-6 text-indigo-400 opacity-80" />
        </div>

        <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">High / Critical Alerts</span>
            <div className="text-xl font-bold text-rose-400 mt-1">{highSeverityCount}</div>
          </div>
          <ShieldAlert className="w-6 h-6 text-rose-400 opacity-80" />
        </div>

        <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Stream Status</span>
            <div className="text-xs font-bold text-emerald-400 mt-1 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              LIVE_MONITORING
            </div>
          </div>
          <Clock className="w-6 h-6 text-emerald-400 opacity-80" />
        </div>
      </div>

      {/* Event Search & Filter Bar */}
      <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-2xl space-y-3">
        <div className="flex flex-col md:flex-row gap-3">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              placeholder="Search security events by Event ID, Entity IP, or keyword..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
            />
          </div>

          {/* Event Type Filter */}
          <select
            value={eventType}
            onChange={(e) => {
              setEventType(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Event Types</option>
            <option value="NETWORK">NETWORK</option>
            <option value="PHISHING">PHISHING</option>
            <option value="UBA">UBA</option>
            <option value="IDENTITY">IDENTITY</option>
            <option value="TRANSACTION">TRANSACTION</option>
          </select>

          {/* Severity Filter */}
          <select
            value={severity}
            onChange={(e) => {
              setSeverity(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Severities</option>
            <option value="LOW">LOW</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="HIGH">HIGH</option>
            <option value="CRITICAL">CRITICAL</option>
          </select>

          {(search || eventType || severity) && (
            <button
              onClick={handleReset}
              className="px-3 py-2 text-xs text-slate-400 hover:text-slate-200 transition-colors"
            >
              Reset Filters
            </button>
          )}
        </div>
      </div>

      {/* Security Events Stream Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-xs text-slate-400 flex flex-col items-center gap-2">
            <RefreshCw className="w-6 h-6 animate-spin text-indigo-400" />
            <span>Loading security events stream...</span>
          </div>
        ) : events.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-400">
            No security events matched your query.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-950 text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
                  <th className="py-3 px-4">Event ID</th>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Source Agent</th>
                  <th className="py-3 px-4">Target Entity</th>
                  <th className="py-3 px-4">Risk & Severity</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {events.map((event) => (
                  <tr
                    key={event.event_id}
                    className="hover:bg-slate-800/40 transition-colors group cursor-pointer"
                    onClick={() => setSelectedEvent(event)}
                  >
                    <td className="py-3.5 px-4 font-mono font-semibold text-indigo-400 group-hover:text-indigo-300">
                      {event.event_id}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-400 whitespace-nowrap">
                      {formatTimestamp(event.timestamp)}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-[10px] font-mono text-slate-300">
                        {event.event_type}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-300 font-mono text-[11px]">
                      {event.agent_id || event.source || 'agent-network'}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-300 truncate max-w-[180px]">
                      {event.entity_id}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-2">
                        <RiskBadge score={event.risk_score} />
                        <span className="text-[10px] text-slate-500 font-mono">({(event.risk_score * 100).toFixed(0)}%)</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedEvent(event);
                        }}
                        className="p-1.5 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-white transition-colors"
                        title="View Event Details"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Table Footer & Pagination */}
        {events.length > 0 && (
          <div className="p-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400 bg-slate-950">
            <div>
              Showing <span className="text-white font-medium">{(page - 1) * pageSize + 1}</span> to{' '}
              <span className="text-white font-medium">{Math.min(page * pageSize, total)}</span> of{' '}
              <span className="text-white font-medium">{total}</span> events
            </div>

            <div className="flex items-center space-x-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
                className="p-1.5 bg-slate-900 border border-slate-800 rounded-lg disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800 text-slate-200"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="font-mono text-xs text-slate-300 px-2">
                Page {page} of {totalPages}
              </span>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage(page + 1)}
                className="p-1.5 bg-slate-900 border border-slate-800 rounded-lg disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800 text-slate-200"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Event Details Drawer / Modal */}
      {selectedEvent && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex justify-end animate-in fade-in duration-150">
          <div className="w-full max-w-2xl bg-slate-950 border-l border-slate-800 h-full p-6 overflow-y-auto space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-lg font-bold text-white font-mono">{selectedEvent.event_id}</h3>
                <p className="text-xs text-slate-400 mt-0.5">Detected Event Payload & Technical Telemetry</p>
              </div>
              <button
                onClick={() => setSelectedEvent(null)}
                className="p-2 hover:bg-slate-800 rounded-xl text-slate-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3 p-4 bg-slate-900/60 border border-slate-800 rounded-xl">
                <div>
                  <span className="text-slate-500 font-medium">Event Type</span>
                  <p className="font-mono text-slate-200 mt-0.5">{selectedEvent.event_type}</p>
                </div>
                <div>
                  <span className="text-slate-500 font-medium">Agent Source</span>
                  <p className="font-mono text-indigo-400 mt-0.5">{selectedEvent.agent_id || selectedEvent.source}</p>
                </div>
                <div>
                  <span className="text-slate-500 font-medium">Target Entity</span>
                  <p className="font-mono text-slate-200 mt-0.5">{selectedEvent.entity_id}</p>
                </div>
                <div>
                  <span className="text-slate-500 font-medium">Observed Time</span>
                  <p className="font-mono text-slate-300 mt-0.5">{formatTimestamp(selectedEvent.timestamp)}</p>
                </div>
              </div>

              <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-2">
                <span className="text-slate-500 font-medium">Risk & Uncertainty Assessment</span>
                <div className="flex items-center justify-between pt-1">
                  <div className="flex items-center gap-2">
                    <RiskBadge score={selectedEvent.risk_score} />
                    <span className="font-mono text-slate-300">Score: {selectedEvent.risk_score.toFixed(4)}</span>
                  </div>
                  <div className="text-right font-mono text-slate-400 text-[11px]">
                    Confidence: {(selectedEvent.confidence * 100).toFixed(1)}% | Uncertainty: {(selectedEvent.uncertainty * 100).toFixed(1)}%
                  </div>
                </div>
              </div>

              {selectedEvent.evidence && (
                <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-2">
                  <span className="text-slate-500 font-medium">Evidence Data</span>
                  <pre className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-[11px] font-mono text-slate-300 overflow-x-auto whitespace-pre-wrap">
                    {JSON.stringify(selectedEvent.evidence, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
