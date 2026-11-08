import React from 'react';
import { AIRecommendation } from '../../types/dashboard';

interface AiRecommendationsWidgetProps {
  recommendations: AIRecommendation[];
  onActionClick?: (item: AIRecommendation) => void;
}

export const AiRecommendationsWidget: React.FC<AiRecommendationsWidgetProps> = ({
  recommendations,
  onActionClick,
}) => {
  const items: AIRecommendation[] = recommendations.length > 0 ? recommendations : [
    {
      id: 'rec-1',
      priority: 'HIGH',
      title: 'Dispatch technician to CAM-S-201',
      description: 'Continuous offline state detected. Physical cable and PoE verification required.',
      target_asset: 'CAM-S-201',
    },
    {
      id: 'rec-2',
      priority: 'MEDIUM',
      title: 'Schedule PoE Switch Audit (SW-CORE-02)',
      description: 'Multiple cameras on SW-CORE-02 showing power degradation within 72 hours.',
      target_asset: 'SW-CORE-02',
    },
  ];

  return (
    <div className="bg-white dark:bg-[#11192b] rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col">
      <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
        <span className="material-symbols-outlined text-amber-500">lightbulb</span>
        AI Recommendations
      </h2>

      <div className="space-y-3 flex-1">
        {items.map((rec) => {
          const isHigh = rec.priority === 'HIGH';
          return (
            <div
              key={rec.id}
              onClick={() => onActionClick?.(rec)}
              className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 hover:border-blue-400 dark:hover:border-blue-500 transition-all cursor-pointer group"
            >
              <div className="flex justify-between items-start mb-2">
                <span
                  className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-extrabold uppercase font-mono tracking-wider ${
                    isHigh
                      ? 'bg-rose-100 text-rose-800 dark:bg-rose-950/80 dark:text-rose-300'
                      : 'bg-amber-100 text-amber-800 dark:bg-amber-950/80 dark:text-amber-300'
                  }`}
                >
                  {rec.priority}
                </span>
                <span className="material-symbols-outlined text-slate-400 group-hover:text-blue-600 transition-colors text-[18px]">
                  chevron_right
                </span>
              </div>
              <h3 className="text-xs font-bold text-slate-900 dark:text-white mb-1 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                {rec.title}
              </h3>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                {rec.description}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
};
