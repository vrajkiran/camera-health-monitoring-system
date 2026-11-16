import React from 'react';
import { SwitchItem } from '../../types/topology';

interface SwitchCardGridProps {
  switches: SwitchItem[];
  onSelectSwitch: (sw: SwitchItem) => void;
}

export const SwitchCardGrid: React.FC<SwitchCardGridProps> = ({ switches, onSelectSwitch }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {switches.map((sw) => {
        const isOffline = sw.status === 'OFFLINE';
        const isUnstable = sw.status === 'UNSTABLE';
        const statusBg = isOffline
          ? 'bg-rose-50 text-rose-700 dark:bg-rose-950/40 dark:text-rose-400 border-rose-200 dark:border-rose-800'
          : isUnstable
          ? 'bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400 border-amber-200 dark:border-amber-800'
          : 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800';

        const history = sw.ping_history || [3, 4, 3, 5, 4, 4];
        const maxLatency = Math.max(...history, 10);
        const minLatency = Math.min(...history, 1);
        const points = history
          .map((val, idx) => {
            const x = (idx / (history.length - 1)) * 100;
            const y = 30 - ((val - minLatency) / Math.max(1, maxLatency - minLatency)) * 24;
            return `${x},${y}`;
          })
          .join(' ');

        return (
          <div
            key={sw.switch_id}
            className="p-5 rounded-2xl bg-white dark:bg-[#11192b] border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md transition-all flex flex-col justify-between group"
          >
            <div>
              {/* Header with Switch ID and Status */}
              <div className="flex items-start justify-between gap-3 mb-3">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                      isOffline
                        ? 'bg-rose-100 text-rose-600 dark:bg-rose-900/30'
                        : isUnstable
                        ? 'bg-amber-100 text-amber-600 dark:bg-amber-900/30'
                        : 'bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400'
                    }`}
                  >
                    <span className="material-symbols-outlined text-[22px]">router</span>
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-900 dark:text-white text-base leading-tight">
                      {sw.switch_id}
                    </h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400 truncate max-w-[180px]">
                      {sw.switch_name || 'PoE Access Switch'}
                    </p>
                  </div>
                </div>
                <span
                  className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold border ${statusBg}`}
                >
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      isOffline ? 'bg-rose-500' : isUnstable ? 'bg-amber-500' : 'bg-emerald-500'
                    }`}
                  />
                  {sw.status}
                </span>
              </div>

              {/* IP and Location */}
              <div className="grid grid-cols-2 gap-2 py-3 border-y border-slate-100 dark:border-slate-800/80 text-xs">
                <div>
                  <span className="text-slate-400 block text-[11px]">Management IP</span>
                  <span className="font-mono font-medium text-slate-800 dark:text-slate-200">
                    {sw.ip_address || sw.switch_ip || '192.168.1.1'}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[11px]">Location</span>
                  <span className="text-slate-800 dark:text-slate-200 truncate block">
                    {sw.location || 'Server Rack'}
                  </span>
                </div>
              </div>

              {/* Connected Cameras & Health Stats */}
              <div className="mt-3 flex items-center justify-between text-xs">
                <div>
                  <span className="text-slate-400 text-[11px] block">Connected Cameras</span>
                  <span className="font-bold text-slate-900 dark:text-white">
                    {sw.connected_cameras || sw.cameras?.length || 0} Units
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-slate-400 text-[11px] block">Ping Latency</span>
                  <span className="font-bold text-slate-900 dark:text-white font-mono">
                    {isOffline ? 'Unreachable' : `${sw.avg_latency_ms || 2.8} ms`}
                  </span>
                </div>
              </div>

              {/* Ping Sparkline Chart (ISSUE-29) */}
              <div className="mt-3 pt-2">
                <div className="flex items-center justify-between text-[10px] text-slate-400 mb-1">
                  <span>Latency Sparkline (Last 6 probes)</span>
                  <span>{history[history.length - 1]} ms</span>
                </div>
                <div className="h-8 w-full bg-slate-50 dark:bg-slate-900/60 rounded-lg p-1 overflow-hidden">
                  <svg className="w-full h-full" viewBox="0 0 100 32" preserveAspectRatio="none">
                    <polyline
                      fill="none"
                      stroke={isOffline ? '#f43f5e' : isUnstable ? '#f59e0b' : '#10b981'}
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      points={points}
                    />
                  </svg>
                </div>
              </div>
            </div>

            {/* Action Footer */}
            <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <span className="text-[11px] text-slate-400">
                Health Score: <strong className="text-slate-700 dark:text-slate-300">{sw.health ?? (isOffline ? 0 : 100)}%</strong>
              </span>
              <button
                type="button"
                onClick={() => onSelectSwitch(sw)}
                className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950/40 transition-colors"
              >
                <span>Inspect Switch</span>
                <span className="material-symbols-outlined text-[16px]">chevron_right</span>
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
};
