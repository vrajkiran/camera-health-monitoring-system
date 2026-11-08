import React from 'react';
import { IncidentItem } from '../../types/dashboard';

interface RecentIncidentsWidgetProps {
  incidents: IncidentItem[];
  onViewAll?: () => void;
}

export const RecentIncidentsWidget: React.FC<RecentIncidentsWidgetProps> = ({
  incidents,
  onViewAll,
}) => {
  const items: IncidentItem[] = incidents.length > 0 ? incidents.slice(0, 4) : [
    {
      id: 1,
      camera_id: 201,
      camera_name: 'CAM-S-201',
      severity: 'CRITICAL',
      status: 'OPEN',
      root_cause: 'Connection Lost (Ping Timeout)',
      created_at: '10:42 AM',
    },
    {
      id: 2,
      camera_id: 102,
      camera_name: 'CAM-N-102',
      severity: 'WARNING',
      status: 'INVESTIGATING',
      root_cause: 'High Latency (120ms)',
      created_at: '08:15 AM',
    },
    {
      id: 3,
      camera_id: 304,
      camera_name: 'SW-EDGE-04',
      severity: 'CRITICAL',
      status: 'RESOLVED',
      root_cause: 'Port 8 Flapping',
      created_at: 'Yesterday, 14:30',
    },
    {
      id: 4,
      camera_id: 305,
      camera_name: 'CAM-W-304',
      severity: 'WARNING',
      status: 'RESOLVED',
      root_cause: 'Video Stream Artifacts',
      created_at: 'Yesterday, 09:12',
    },
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'OPEN':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-mono text-[10px] font-semibold border border-slate-200 dark:border-slate-700">
            Open
          </span>
        );
      case 'INVESTIGATING':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-blue-50 dark:bg-blue-950/70 text-blue-700 dark:text-blue-300 font-mono text-[10px] font-semibold border border-blue-200/60 dark:border-blue-800/60">
            Investigating
          </span>
        );
      case 'RESOLVED':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/70 text-emerald-700 dark:text-emerald-300 font-mono text-[10px] font-semibold border border-emerald-200/60 dark:border-emerald-800/60">
            Resolved
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 text-[10px]">
            {status}
          </span>
        );
    }
  };

  const getSeverityPill = (severity: string) => {
    if (severity === 'CRITICAL') {
      return (
        <span className="text-rose-600 dark:text-rose-400 font-bold text-xs flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
          Critical
        </span>
      );
    }
    return (
      <span className="text-amber-600 dark:text-amber-400 font-bold text-xs flex items-center gap-1">
        <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
        Warning
      </span>
    );
  };

  return (
    <div className="bg-white dark:bg-[#11192b] rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col">
      <div className="flex justify-between items-center mb-5">
        <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <span className="material-symbols-outlined text-rose-500">crisis_alert</span>
          Recent Incidents Log
        </h2>
        {onViewAll && (
          <button
            onClick={onViewAll}
            className="text-xs font-bold text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 uppercase tracking-wider"
          >
            View Full Log
          </button>
        )}
      </div>

      <div className="overflow-x-auto flex-1">
        <table className="w-full text-left border-collapse min-w-[560px]">
          <thead>
            <tr className="border-b border-slate-200 dark:border-slate-800 text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
              <th className="py-2.5 px-3">Time</th>
              <th className="py-2.5 px-3">Asset</th>
              <th className="py-2.5 px-3">Severity</th>
              <th className="py-2.5 px-3">Root Cause</th>
              <th className="py-2.5 px-3 text-right">Status</th>
            </tr>
          </thead>
          <tbody className="text-xs divide-y divide-slate-100 dark:divide-slate-800/60 font-medium">
            {items.map((inc) => (
              <tr
                key={inc.id}
                className="hover:bg-slate-50 dark:hover:bg-slate-900/40 transition-colors"
              >
                <td className="py-3 px-3 text-slate-500 dark:text-slate-400 font-mono text-[11px]">
                  {inc.created_at}
                </td>
                <td className="py-3 px-3 font-bold text-slate-900 dark:text-white">
                  {inc.camera_name}
                </td>
                <td className="py-3 px-3">{getSeverityPill(inc.severity)}</td>
                <td className="py-3 px-3 text-slate-600 dark:text-slate-300">
                  {inc.root_cause}
                </td>
                <td className="py-3 px-3 text-right">{getStatusBadge(inc.status)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
