import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface RiskDistributionProps {
  distribution?: {
    LOW: number;
    MEDIUM: number;
    HIGH: number;
    CRITICAL: number;
  };
  isLoading?: boolean;
}

export const RiskDistribution: React.FC<RiskDistributionProps> = ({
  distribution = { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 },
  isLoading = false,
}) => {
  const data = [
    { name: 'LOW', count: distribution.LOW, color: '#10B981', desc: '0.00 – 0.29' },
    { name: 'MEDIUM', count: distribution.MEDIUM, color: '#F59E0B', desc: '0.30 – 0.59' },
    { name: 'HIGH', count: distribution.HIGH, color: '#F97316', desc: '0.60 – 0.79' },
    { name: 'CRITICAL', count: distribution.CRITICAL, color: '#EF4444', desc: '0.80 – 1.00' },
  ];

  const total = data.reduce((acc, cur) => acc + cur.count, 0);

  return (
    <div className="p-5 rounded-lg bg-hactm-card border border-hactm-border shadow-panel flex flex-col justify-between">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-hactm-heading">
            Current Evidence Risk Distribution
          </h3>
          <p className="text-xs text-hactm-muted">
            Observed Cyber Risk Scores across stored telemetry (Not AI-generated detections)
          </p>
        </div>
        <span className="text-xs font-mono px-2 py-0.5 rounded bg-hactm-panel text-hactm-muted border border-hactm-border">
          Total: {total.toLocaleString()}
        </span>
      </div>

      <div className="h-44 w-full">
        {isLoading ? (
          <div className="h-full flex items-center justify-center text-xs text-hactm-muted">
            Computing risk metrics...
          </div>
        ) : total === 0 ? (
          <div className="h-full flex items-center justify-center text-xs text-hactm-muted border border-dashed border-hactm-border/60 rounded">
            No evidence ingested yet.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <XAxis
                dataKey="name"
                stroke="#8A99AD"
                fontSize={11}
                tickLine={false}
                axisLine={{ stroke: '#1E2D3D' }}
              />
              <YAxis
                stroke="#8A99AD"
                fontSize={11}
                tickLine={false}
                axisLine={{ stroke: '#1E2D3D' }}
                allowDecimals={false}
              />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const item = payload[0].payload;
                    return (
                      <div className="p-2 rounded bg-[#0B111A] border border-hactm-border text-xs font-mono shadow-lg">
                        <div className="font-semibold text-white">{item.name} Risk</div>
                        <div className="text-hactm-muted">Score Range: {item.desc}</div>
                        <div className="text-emerald-400 font-bold mt-1">
                          Count: {item.count.toLocaleString()}
                        </div>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Distribution percentages summary */}
      <div className="grid grid-cols-4 gap-2 pt-3 border-t border-hactm-border/60 text-center">
        {data.map((d) => {
          const pct = total > 0 ? ((d.count / total) * 100).toFixed(1) : '0.0';
          return (
            <div key={d.name} className="flex flex-col items-center">
              <span className="text-[10px] text-hactm-muted">{d.name}</span>
              <span className="text-xs font-mono font-bold" style={{ color: d.color }}>
                {pct}%
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
