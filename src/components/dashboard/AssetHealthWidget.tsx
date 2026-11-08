import React from 'react';
import { AssetHealthSummary } from '../../types/dashboard';

interface AssetHealthWidgetProps {
  assetHealth: AssetHealthSummary;
}

export const AssetHealthWidget: React.FC<AssetHealthWidgetProps> = ({ assetHealth }) => {
  const { total_assets, healthy, warning, critical, maintenance } = assetHealth;

  // Compute percentage stops for CSS conic gradient
  const healthyPct = (healthy / (total_assets || 1)) * 100;
  const warningPct = (warning / (total_assets || 1)) * 100;
  const criticalPct = (critical / (total_assets || 1)) * 100;

  const stop1 = criticalPct;
  const stop2 = stop1 + warningPct;
  const stop3 = stop2 + healthyPct;

  const conicStyle = {
    background: `conic-gradient(
      #ef4444 0% ${stop1}%,
      #f59e0b ${stop1}% ${stop2}%,
      #16a34a ${stop2}% ${stop3}%,
      #94a3b8 ${stop3}% 100%
    )`,
  };

  return (
    <div className="bg-white dark:bg-[#11192b] rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
      <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-6">
        Overall Asset Health
      </h2>

      <div className="flex items-center justify-between gap-6 px-2">
        {/* Multi-segment Donut Chart */}
        <div className="relative w-36 h-36 flex-shrink-0">
          <div className="w-full h-full rounded-full shadow-inner" style={conicStyle} />
          {/* Inner cutout */}
          <div className="absolute inset-3 bg-white dark:bg-[#11192b] rounded-full flex flex-col items-center justify-center text-center shadow-sm">
            <span className="text-2xl font-black text-slate-900 dark:text-white leading-none">
              {total_assets}
            </span>
            <span className="text-[10px] uppercase font-bold text-slate-400 mt-1">
              Total Assets
            </span>
          </div>
        </div>

        {/* Legend */}
        <div className="flex-1 space-y-2.5 text-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
              <span className="text-slate-700 dark:text-slate-300 font-medium">Healthy</span>
            </div>
            <span className="font-bold text-slate-900 dark:text-white">{healthy}</span>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
              <span className="text-slate-700 dark:text-slate-300 font-medium">Warning</span>
            </div>
            <span className="font-bold text-slate-900 dark:text-white">{warning}</span>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
              <span className="text-slate-700 dark:text-slate-300 font-medium">Critical</span>
            </div>
            <span className="font-bold text-slate-900 dark:text-white">{critical}</span>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-slate-400"></span>
              <span className="text-slate-700 dark:text-slate-300 font-medium">Maintenance</span>
            </div>
            <span className="font-bold text-slate-900 dark:text-white">{maintenance}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
