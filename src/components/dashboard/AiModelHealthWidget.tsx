import React from 'react';
import { MLStatistics } from '../../types/dashboard';
import { DonutGauge } from '../common/DonutGauge';

interface AiModelHealthWidgetProps {
  stats?: MLStatistics;
}

export const AiModelHealthWidget: React.FC<AiModelHealthWidgetProps> = ({ stats }) => {
  const accuracy = stats?.accuracy ? Math.round(stats.accuracy * 100) : 100;
  const activeModels = stats?.active_models || '3/3 Online';
  const confidence = stats?.confidence_level || 'High';
  const lastAnalysis = stats?.last_analysis || '2 mins ago';

  return (
    <div className="bg-white dark:bg-[#11192b] rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col">
      <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
        <span className="material-symbols-outlined text-blue-600 dark:text-blue-400">psychology</span>
        AI Model Health
      </h2>

      <div className="flex flex-col items-center justify-center flex-1">
        {/* Visual Donut Gauge (Resolves ISSUE-24) */}
        <div className="mb-6">
          <DonutGauge
            value={accuracy}
            size={136}
            strokeWidth={12}
            colorClass="text-blue-600 dark:text-blue-500"
            label={`${accuracy}%`}
            sublabel="Accuracy"
          />
        </div>

        {/* Breakdown Items */}
        <div className="w-full space-y-3 pt-2 border-t border-slate-100 dark:border-slate-800 text-xs">
          <div className="flex justify-between items-center py-1">
            <span className="text-slate-500 dark:text-slate-400 font-medium">Confidence Level</span>
            <span className="px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 dark:bg-blue-950/80 dark:text-blue-300 font-semibold font-mono text-[11px] border border-blue-200/50 dark:border-blue-800/50">
              {confidence}
            </span>
          </div>
          <div className="flex justify-between items-center py-1 border-t border-slate-100 dark:border-slate-800/50">
            <span className="text-slate-500 dark:text-slate-400 font-medium">Last Analysis</span>
            <span className="font-semibold text-slate-800 dark:text-slate-200">{lastAnalysis}</span>
          </div>
          <div className="flex justify-between items-center py-1 border-t border-slate-100 dark:border-slate-800/50">
            <span className="text-slate-500 dark:text-slate-400 font-medium">Active Models</span>
            <span className="font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              {activeModels}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
