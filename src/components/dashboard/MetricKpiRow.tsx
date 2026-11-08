import React from 'react';
import { CameraStatistics } from '../../types/dashboard';

interface MetricKpiRowProps {
  stats?: CameraStatistics;
  healthScore?: number;
  maintenanceSessions?: number;
  criticalIssuesCount?: number;
}

export const MetricKpiRow: React.FC<MetricKpiRowProps> = ({
  stats,
  healthScore = 96.2,
  maintenanceSessions = 0,
  criticalIssuesCount = 1,
}) => {
  const totalCameras = stats?.total ?? 26;
  const onlineCameras = stats?.online ?? 25;
  const offlineCameras = stats?.offline ?? 1;
  const totalSwitches = 19;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-4">
      {/* 1. Total Cameras */}
      <div className="bg-white dark:bg-[#11192b] rounded-2xl p-5 border border-slate-200 dark:border-slate-800 border-l-4 border-l-amber-500 shadow-sm hover:shadow-md transition-all">
        <div className="flex justify-between items-start mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Total Cameras
          </span>
          <div className="w-9 h-9 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center">
            <span className="material-symbols-outlined text-[20px]">videocam</span>
          </div>
        </div>
        <div className="text-3xl font-extrabold text-slate-900 dark:text-white mb-3">
          {totalCameras}
        </div>
        <div className="flex flex-wrap gap-2 text-xs font-semibold">
          <span className="inline-flex items-center gap-1 text-emerald-600 dark:text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
            {onlineCameras} Online
          </span>
          <span className="inline-flex items-center gap-1 text-rose-600 dark:text-rose-400">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
            {offlineCameras} Offline
          </span>
        </div>
      </div>

      {/* 2. Total Switches */}
      <div className="bg-white dark:bg-[#11192b] rounded-2xl p-5 border border-slate-200 dark:border-slate-800 border-l-4 border-l-emerald-500 shadow-sm hover:shadow-md transition-all">
        <div className="flex justify-between items-start mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Total Switches
          </span>
          <div className="w-9 h-9 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
            <span className="material-symbols-outlined text-[20px]">router</span>
          </div>
        </div>
        <div className="text-3xl font-extrabold text-slate-900 dark:text-white mb-3">
          {totalSwitches}
        </div>
        <div className="flex items-center gap-1 text-xs font-semibold text-emerald-600 dark:text-emerald-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
          {totalSwitches} Online (100%)
        </div>
      </div>

      {/* 3. Critical Issues */}
      <div className="bg-white dark:bg-[#11192b] rounded-2xl p-5 border border-slate-200 dark:border-slate-800 border-l-4 border-l-rose-500 shadow-sm hover:shadow-md transition-all">
        <div className="flex justify-between items-start mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-rose-600 dark:text-rose-400">
            Critical Issues
          </span>
          <div className="w-9 h-9 rounded-xl bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 flex items-center justify-center">
            <span className="material-symbols-outlined text-[20px]">warning</span>
          </div>
        </div>
        <div className="text-3xl font-extrabold text-rose-600 dark:text-rose-400 mb-3">
          {criticalIssuesCount}
        </div>
        <div className="text-xs text-slate-500 dark:text-slate-400 font-medium">
          Requires immediate triage
        </div>
      </div>

      {/* 4. Maintenance */}
      <div className="bg-white dark:bg-[#11192b] rounded-2xl p-5 border border-slate-200 dark:border-slate-800 border-l-4 border-l-slate-400 dark:border-l-slate-600 shadow-sm hover:shadow-md transition-all">
        <div className="flex justify-between items-start mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Maintenance
          </span>
          <div className="w-9 h-9 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 flex items-center justify-center">
            <span className="material-symbols-outlined text-[20px]">build</span>
          </div>
        </div>
        <div className="text-3xl font-extrabold text-slate-900 dark:text-white mb-3">
          {maintenanceSessions}
        </div>
        <div className="text-xs text-slate-500 dark:text-slate-400 font-medium">
          {maintenanceSessions > 0 ? `${maintenanceSessions} Active session(s)` : 'No active sessions'}
        </div>
      </div>

      {/* 5. System Health */}
      <div className="bg-white dark:bg-[#11192b] rounded-2xl p-5 border border-slate-200 dark:border-slate-800 border-l-4 border-l-blue-600 shadow-sm hover:shadow-md transition-all col-span-2 md:col-span-1 xl:col-span-1">
        <div className="flex justify-between items-start mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            System Health
          </span>
          <div className="w-9 h-9 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center">
            <span className="material-symbols-outlined text-[20px]">monitor_heart</span>
          </div>
        </div>
        <div className="flex items-baseline gap-2 mb-3">
          <span className="text-3xl font-extrabold text-slate-900 dark:text-white">
            {healthScore.toFixed(1)}%
          </span>
          <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 flex items-center">
            <span className="material-symbols-outlined text-[14px]">arrow_upward</span>
            0.5%
          </span>
        </div>
        <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-1.5 overflow-hidden">
          <div
            className="bg-emerald-500 h-1.5 rounded-full transition-all duration-500"
            style={{ width: `${Math.min(100, Math.max(0, healthScore))}%` }}
          />
        </div>
      </div>
    </div>
  );
};
