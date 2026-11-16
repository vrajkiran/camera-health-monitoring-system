import React from 'react';
import { SwitchStatsSummary } from '../../types/topology';

interface SwitchStatsRowProps {
  stats: SwitchStatsSummary;
  activeFilter: 'ALL' | 'ONLINE' | 'UNSTABLE' | 'OFFLINE';
  onFilterChange: (filter: 'ALL' | 'ONLINE' | 'UNSTABLE' | 'OFFLINE') => void;
}

export const SwitchStatsRow: React.FC<SwitchStatsRowProps> = ({
  stats,
  activeFilter,
  onFilterChange,
}) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Total Switches */}
      <button
        type="button"
        onClick={() => onFilterChange('ALL')}
        className={`p-4 rounded-2xl border text-left transition-all ${
          activeFilter === 'ALL'
            ? 'ring-2 ring-blue-500 bg-blue-50/50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800'
            : 'bg-white dark:bg-[#11192b] border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
        }`}
      >
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Total Switches
          </span>
          <div className="w-9 h-9 rounded-xl bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center">
            <span className="material-symbols-outlined text-[20px]">router</span>
          </div>
        </div>
        <div className="mt-2 flex items-baseline gap-2">
          <span className="text-2xl font-bold text-slate-900 dark:text-white">
            {stats.total}
          </span>
          <span className="text-xs text-slate-500 dark:text-slate-400">Backbone units</span>
        </div>
      </button>

      {/* Online Switches */}
      <button
        type="button"
        onClick={() => onFilterChange('ONLINE')}
        className={`p-4 rounded-2xl border text-left transition-all ${
          activeFilter === 'ONLINE'
            ? 'ring-2 ring-emerald-500 bg-emerald-50/50 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800'
            : 'bg-white dark:bg-[#11192b] border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
        }`}
      >
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Online & Healthy
          </span>
          <div className="w-9 h-9 rounded-xl bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
            <span className="material-symbols-outlined text-[20px]">check_circle</span>
          </div>
        </div>
        <div className="mt-2 flex items-baseline gap-2">
          <span className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
            {stats.online}
          </span>
          <span className="text-xs text-emerald-600/80 dark:text-emerald-400/80">
            {stats.total > 0 ? `${Math.round((stats.online / stats.total) * 100)}% uptime` : '100%'}
          </span>
        </div>
      </button>

      {/* Offline / Fault Alerts */}
      <button
        type="button"
        onClick={() => onFilterChange('OFFLINE')}
        className={`p-4 rounded-2xl border text-left transition-all ${
          activeFilter === 'OFFLINE'
            ? 'ring-2 ring-rose-500 bg-rose-50/50 dark:bg-rose-950/20 border-rose-200 dark:border-rose-800'
            : 'bg-white dark:bg-[#11192b] border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
        }`}
      >
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Offline / Critical
          </span>
          <div className="w-9 h-9 rounded-xl bg-rose-50 dark:bg-rose-900/30 text-rose-600 dark:text-rose-400 flex items-center justify-center">
            <span className="material-symbols-outlined text-[20px]">error</span>
          </div>
        </div>
        <div className="mt-2 flex items-baseline gap-2">
          <span className={`text-2xl font-bold ${stats.offline > 0 ? 'text-rose-600 dark:text-rose-400' : 'text-slate-900 dark:text-white'}`}>
            {stats.offline}
          </span>
          <span className="text-xs text-slate-500 dark:text-slate-400">
            {stats.offline > 0 ? 'Requires attention' : 'Zero link faults'}
          </span>
        </div>
      </button>

      {/* Average Network Ping Latency (ISSUE-29) */}
      <div className="p-4 rounded-2xl border bg-white dark:bg-[#11192b] border-slate-200 dark:border-slate-800">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Avg Ping Latency
          </span>
          <div className="w-9 h-9 rounded-xl bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 flex items-center justify-center">
            <span className="material-symbols-outlined text-[20px]">speed</span>
          </div>
        </div>
        <div className="mt-2 flex items-baseline gap-2">
          <span className="text-2xl font-bold text-slate-900 dark:text-white">
            {stats.avg_latency} ms
          </span>
          <span className="text-xs text-emerald-600 dark:text-emerald-400 flex items-center gap-0.5">
            <span className="material-symbols-outlined text-[14px]">bolt</span>
            Low Jitter
          </span>
        </div>
      </div>
    </div>
  );
};
