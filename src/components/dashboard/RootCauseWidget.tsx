import React from 'react';
import { RootCauseItem } from '../../types/dashboard';

interface RootCauseWidgetProps {
  rootCauses: RootCauseItem[];
}

export const RootCauseWidget: React.FC<RootCauseWidgetProps> = ({ rootCauses }) => {
  const causes: RootCauseItem[] = rootCauses.length > 0 ? rootCauses : [
    { cause: 'Network Latency > 100ms', occurrences: 14, percentage: 45 },
    { cause: 'RTSP Service Timeout', occurrences: 8, percentage: 25 },
    { cause: 'Power Fluctuation (PoE)', occurrences: 5, percentage: 15 },
    { cause: 'Authentication Failure', occurrences: 2, percentage: 6 },
  ];

  const getColorClass = (index: number) => {
    switch (index) {
      case 0:
        return 'bg-amber-500';
      case 1:
        return 'bg-blue-600';
      case 2:
        return 'bg-purple-600';
      default:
        return 'bg-slate-400';
    }
  };

  return (
    <div className="bg-white dark:bg-[#11192b] rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col">
      <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
        <span className="material-symbols-outlined text-blue-600 dark:text-blue-400">plumbing</span>
        Top Root Causes (30 Days)
      </h2>

      <div className="space-y-4">
        {causes.map((item, index) => (
          <div key={item.cause}>
            <div className="flex justify-between items-center text-xs font-medium mb-1.5">
              <span className="text-slate-800 dark:text-slate-200 font-semibold">
                {item.cause}
              </span>
              <span className="text-slate-500 dark:text-slate-400 text-[11px] font-mono">
                {item.occurrences} occurrences ({item.percentage}%)
              </span>
            </div>
            <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
              <div
                className={`h-2 rounded-full transition-all duration-700 ${getColorClass(index)}`}
                style={{ width: `${Math.min(100, Math.max(2, item.percentage))}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
