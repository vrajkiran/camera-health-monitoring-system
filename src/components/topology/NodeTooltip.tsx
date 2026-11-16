import React from 'react';
import { TopologyNode } from '../../types/topology';

interface NodeTooltipProps {
  node: TopologyNode;
  x: number;
  y: number;
}

export const NodeTooltip: React.FC<NodeTooltipProps> = ({ node, x, y }) => {
  const isSwitch = node.type === 'switch';
  const isOnline = node.status === 'ONLINE';
  const isOffline = node.status === 'OFFLINE';

  const statusColor = isOffline
    ? 'text-rose-600 bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800'
    : node.status === 'UNSTABLE' || node.status === 'STREAM_FAILURE'
    ? 'text-amber-600 bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800'
    : 'text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800';

  return (
    <div
      style={{
        position: 'absolute',
        left: `${x}px`,
        top: `${y}px`,
        transform: 'translate(-50%, -115%)',
        zIndex: 50,
        pointerEvents: 'none',
      }}
      className="w-64 p-3.5 bg-slate-900/95 dark:bg-slate-900/95 text-white backdrop-blur-md rounded-xl shadow-2xl border border-slate-700/80 text-xs transition-opacity animate-in fade-in zoom-in-95 duration-150"
    >
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-[18px] text-blue-400">
            {isSwitch ? 'router' : 'videocam'}
          </span>
          <span className="font-bold text-sm truncate max-w-[140px]">
            {isSwitch ? node.id : node.name || node.id}
          </span>
        </div>
        <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${statusColor}`}>
          {node.status}
        </span>
      </div>

      <div className="mt-2.5 space-y-1.5 text-slate-300">
        <div className="flex justify-between">
          <span className="text-slate-400">IP Address:</span>
          <span className="font-mono text-white">{node.ip_address || node.switch_ip || 'N/A'}</span>
        </div>

        {isSwitch ? (
          <>
            <div className="flex justify-between">
              <span className="text-slate-400">Port Utilization:</span>
              <span className="font-semibold text-emerald-400">
                {node.total_cameras ? `${node.total_cameras}/24 Ports` : 'Active'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Connected Cameras:</span>
              <span className="text-white">
                {node.total_cameras || 0} ({node.offline_cameras || 0} offline)
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Hierarchy Level:</span>
              <span className="text-blue-300 capitalize">{node.level || 'PoE Access'}</span>
            </div>
          </>
        ) : (
          <>
            <div className="flex justify-between">
              <span className="text-slate-400">Location:</span>
              <span className="text-white truncate max-w-[130px]">{node.location || 'Campus'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Ping Latency:</span>
              <span className="font-mono text-emerald-400">
                {node.latency_ms !== null && node.latency_ms !== undefined ? `${node.latency_ms} ms` : 'N/A'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Uplink Switch:</span>
              <span className="font-mono text-blue-300">{node.switch_id || 'Core Fabric'}</span>
            </div>
          </>
        )}
      </div>

      <div className="mt-2 pt-2 border-t border-slate-800 text-[10px] text-slate-400 flex items-center justify-between">
        <span>Click to inspect details</span>
        <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-ping" />
      </div>
    </div>
  );
};
