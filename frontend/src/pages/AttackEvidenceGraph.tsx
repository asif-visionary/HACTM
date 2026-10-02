import React, { useEffect, useState } from 'react';
import { api } from '../services/api';

export const AttackEvidenceGraphPage: React.FC = () => {
  const [targetEntity, setTargetEntity] = useState<string>('USER-103');
  const [kHop, setKHop] = useState<number>(2);
  const [subgraph, setSubgraph] = useState<any>(null);
  const [attackChains, setAttackChains] = useState<any[]>([]);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadGraph();
  }, [kHop]);

  const loadGraph = async () => {
    setLoading(true);
    try {
      const centerNodeId = `node_user_${targetEntity}`;
      const [sub, chains] = await Promise.all([
        api.getGraphSubgraph(centerNodeId, kHop, 200).catch(() => null),
        api.getAttackChains(targetEntity),
      ]);
      setSubgraph(sub);
      setAttackChains(chains || []);
    } catch (err) {
      console.error('Failed to load attack evidence graph', err);
    } finally {
      setLoading(false);
    }
  };

  const getNodeColor = (type: string) => {
    switch (type) {
      case 'User': return 'bg-cyan-500 text-slate-950 border-cyan-400';
      case 'Account': return 'bg-blue-600 text-white border-blue-400';
      case 'Device': return 'bg-purple-600 text-white border-purple-400';
      case 'IP': return 'bg-emerald-600 text-white border-emerald-400';
      case 'Evidence': return 'bg-rose-600 text-white border-rose-400';
      case 'Transaction': return 'bg-amber-600 text-white border-amber-400';
      default: return 'bg-slate-700 text-slate-200 border-slate-600';
    }
  };

  return (
    <div className="p-6 space-y-6 bg-slate-950 text-slate-100 min-h-screen">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-cyan-400">Attack Evidence Graph</h1>
        <p className="text-sm text-slate-400">
          Bounded, entity-centered evidence relationships and declarative multi-stage attack chain candidate detection.
        </p>
      </div>

      {/* Query & Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-900 p-4 rounded-lg border border-slate-800">
        <div className="flex items-center space-x-3">
          <label className="text-xs font-semibold text-slate-400 uppercase">Target Entity ID:</label>
          <input
            type="text"
            value={targetEntity}
            onChange={(e) => setTargetEntity(e.target.value)}
            className="px-3 py-1.5 bg-slate-950 border border-slate-700 rounded text-xs font-mono text-cyan-300 w-48"
            placeholder="e.g. USER-103"
          />
          <button
            onClick={loadGraph}
            className="px-3.5 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-xs rounded transition"
          >
            Load Subgraph
          </button>
        </div>

        <div className="flex items-center space-x-3">
          <span className="text-xs font-semibold text-slate-400 uppercase">k-Hop Depth:</span>
          {[1, 2, 3, 4].map((k) => (
            <button
              key={k}
              onClick={() => setKHop(k)}
              className={`px-3 py-1 rounded text-xs font-semibold ${
                kHop === k
                  ? 'bg-cyan-500 text-slate-950 font-bold'
                  : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
            >
              k = {k}
            </button>
          ))}
        </div>
      </div>

      {/* Main Graph Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Interactive Subgraph Node View */}
        <div className="lg:col-span-2 bg-slate-900 rounded-lg border border-slate-800 p-4 flex flex-col justify-between min-h-[450px]">
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-md font-semibold text-slate-200">
                Bounded Subgraph (Center: <span className="text-cyan-400 font-mono">{targetEntity}</span>, k={kHop})
              </h2>
              {subgraph && (
                <div className="text-xs font-mono text-slate-400">
                  Nodes: {subgraph.total_nodes} | Edges: {subgraph.total_edges}
                </div>
              )}
            </div>

            {loading ? (
              <div className="text-slate-500 text-sm py-20 text-center">Loading graph nodes and edges...</div>
            ) : !subgraph || !subgraph.nodes || subgraph.nodes.length === 0 ? (
              <div className="text-slate-500 text-sm py-20 text-center">
                No graph nodes found centered at '{targetEntity}'. Ingest security evidence to build the Attack Evidence Graph.
              </div>
            ) : (
              <div className="flex flex-wrap gap-3 p-4 bg-slate-950 rounded border border-slate-800 min-h-[300px] items-center justify-center">
                {subgraph.nodes.map((node: any) => (
                  <button
                    key={node.node_id}
                    onClick={() => setSelectedNode(node)}
                    className={`p-3 rounded-lg border text-xs font-mono flex flex-col items-center shadow-lg transition transform hover:scale-105 ${getNodeColor(
                      node.node_type
                    )} ${selectedNode?.node_id === node.node_id ? 'ring-2 ring-cyan-400 scale-105' : ''}`}
                  >
                    <span className="font-bold">{node.node_type}</span>
                    <span className="text-[11px] opacity-90">{node.display_name}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Graph Legend */}
          <div className="mt-4 pt-3 border-t border-slate-800 flex flex-wrap gap-2 text-[11px] text-slate-400">
            <span className="font-semibold text-slate-300">Legend:</span>
            <span className="px-2 py-0.5 rounded bg-cyan-500 text-slate-950 font-bold">User</span>
            <span className="px-2 py-0.5 rounded bg-blue-600 text-white">Account</span>
            <span className="px-2 py-0.5 rounded bg-purple-600 text-white">Device</span>
            <span className="px-2 py-0.5 rounded bg-emerald-600 text-white">IP</span>
            <span className="px-2 py-0.5 rounded bg-rose-600 text-white">Evidence</span>
            <span className="px-2 py-0.5 rounded bg-amber-600 text-white">Transaction</span>
          </div>
        </div>

        {/* Node Details Inspector */}
        <div className="bg-slate-900 rounded-lg border border-slate-800 p-4 space-y-4">
          <h2 className="text-md font-semibold text-slate-200 border-b border-slate-800 pb-2">Node & Edge Details</h2>
          {selectedNode ? (
            <div className="space-y-3 text-xs">
              <div className="p-3 bg-slate-950 rounded border border-slate-800 space-y-1">
                <div className="font-bold text-cyan-400 font-mono">{selectedNode.display_name}</div>
                <div><span className="text-slate-500">Node ID:</span> <span className="font-mono text-slate-300">{selectedNode.node_id}</span></div>
                <div><span className="text-slate-500">Node Type:</span> <span className="font-semibold text-rose-300">{selectedNode.node_type}</span></div>
                <div><span className="text-slate-500">Canonical ID:</span> <span className="font-mono text-slate-300">{selectedNode.canonical_id}</span></div>
                <div><span className="text-slate-500">First Seen:</span> {new Date(selectedNode.first_seen).toLocaleString()}</div>
                <div><span className="text-slate-500">Last Seen:</span> {new Date(selectedNode.last_seen).toLocaleString()}</div>
              </div>

              <div>
                <div className="font-semibold text-slate-400 mb-1">Attributes</div>
                <pre className="p-2.5 bg-slate-950 rounded border border-slate-800 text-[11px] font-mono text-cyan-300 max-h-36 overflow-y-auto">
                  {JSON.stringify(selectedNode.attributes || {}, null, 2)}
                </pre>
              </div>
            </div>
          ) : (
            <div className="text-slate-500 text-xs py-10 text-center">
              Click any node in the graph to inspect detailed node attributes and relationship provenance.
            </div>
          )}
        </div>
      </div>

      {/* Attack Chain Candidates Section */}
      <div className="bg-slate-900 rounded-lg border border-slate-800 p-4 space-y-4">
        <h2 className="text-md font-semibold text-slate-200">Candidate Multi-Stage Attack Chains</h2>
        {attackChains.length === 0 ? (
          <div className="text-slate-500 text-xs py-6 text-center">
            No attack-chain candidates identified for target entity. Sequence matcher prevents false correlations.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {attackChains.map((chain) => (
              <div key={chain.chain_id} className="p-4 bg-slate-950 rounded border border-rose-500/30 space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-mono font-bold text-rose-400">{chain.pattern_id}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40">
                    {chain.status}
                  </span>
                </div>
                <div className="text-xs text-slate-300 font-medium">Primary Entity: {chain.primary_entity_id}</div>
                <div className="flex space-x-4 text-xs font-mono text-slate-400">
                  <div>Completeness: <span className="text-cyan-400">{Math.round(chain.completeness * 100)}%</span></div>
                  <div>Confidence: <span className="text-emerald-400">{chain.confidence}</span></div>
                </div>
                <pre className="p-2 bg-slate-900 rounded text-[11px] text-slate-300 whitespace-pre-wrap font-mono border border-slate-800 max-h-32 overflow-y-auto">
                  {chain.explanation}
                </pre>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
