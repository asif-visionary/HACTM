import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { Laptop, ShieldAlert, AlertTriangle, CheckCircle2, Lock, Cpu, HardDrive } from 'lucide-react';

export const DeviceSecurity: React.FC = () => {
  const [page, setPage] = useState(1);

  const sampleDetections = [
    {
      detection_id: 'det_dev_01',
      event_id: 'EV-9020',
      device_id: 'dev_mac_4091',
      category: 'fingerprint_mismatch',
      risk_score: 0.78,
      explanation: 'Hardware fingerprint MAC address & OS build mismatch on macOS endpoint',
    },
    {
      detection_id: 'det_dev_02',
      event_id: 'EV-9014',
      device_id: 'dev_win_8812',
      category: 'unsigned_process',
      risk_score: 0.82,
      explanation: 'Unsigned executable spawned from memory temp directory',
    },
    {
      detection_id: 'det_dev_03',
      event_id: 'EV-9008',
      device_id: 'dev_ios_1092',
      category: 'posture_degraded',
      risk_score: 0.64,
      explanation: 'Endpoint compliance check failed: missing EDR agent process',
    },
  ];

  return (
    <div className="space-y-6 text-slate-100">
      {/* Top Banner Header */}
      <div className="flex items-center justify-between bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-xl border border-emerald-500/30">
            <Laptop size={28} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Device & Endpoint Security Agent</h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Endpoint Posture, Device Fingerprinting & Process Anomaly Engine (Agent ID: <code className="text-emerald-400 font-mono">device-security-agent</code>)
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="px-3 py-1 text-xs font-mono rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5 font-bold">
            <CheckCircle2 size={14} /> OPERATIONAL
          </span>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="text-xs font-mono text-slate-400 uppercase">Device Telemetry Events</div>
          <div className="text-2xl font-bold text-white mt-1">182</div>
          <div className="text-[11px] text-slate-400 mt-1">Rate: 184 evts/sec</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="text-xs font-mono text-slate-400 uppercase">Device Posture Anomaly</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">78 / 100</div>
          <div className="text-[11px] text-slate-400 mt-1">Medium-High Risk Level</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="text-xs font-mono text-slate-400 uppercase">Model Version</div>
          <div className="text-2xl font-bold text-cyan-400 mt-1">DeviceGuard v2.1</div>
          <div className="text-[11px] text-slate-400 mt-1">Confidence: 91%</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="text-xs font-mono text-slate-400 uppercase">Privacy Invariant</div>
          <div className="text-sm font-bold text-emerald-400 mt-1 flex items-center gap-1">
            <Lock size={14} /> ZERO PRIVACY LEAK
          </div>
          <div className="text-[11px] text-slate-400 mt-1">Hashed Hardware Signatures</div>
        </div>
      </div>

      {/* Detections Stream */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
        <h2 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
          Device & Endpoint Security Detections
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 border-b border-slate-800 text-slate-400 font-mono uppercase">
              <tr>
                <th className="p-3">Event ID</th>
                <th className="p-3">Device / Endpoint</th>
                <th className="p-3">Category</th>
                <th className="p-3">Risk Score</th>
                <th className="p-3">Explanation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200 font-mono">
              {sampleDetections.map((det) => (
                <tr key={det.detection_id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="p-3 text-cyan-400 font-bold">{det.event_id}</td>
                  <td className="p-3">{det.device_id}</td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold uppercase">
                      {det.category}
                    </span>
                  </td>
                  <td className="p-3 font-bold text-amber-400">{det.risk_score.toFixed(2)}</td>
                  <td className="p-3 text-slate-300 font-sans">{det.explanation}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
