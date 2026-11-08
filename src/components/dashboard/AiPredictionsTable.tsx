import React from 'react';
import { PredictionItem } from '../../types/dashboard';

interface AiPredictionsTableProps {
  predictions: PredictionItem[];
  onViewAll?: () => void;
}

export const AiPredictionsTable: React.FC<AiPredictionsTableProps> = ({
  predictions,
  onViewAll,
}) => {
  // Fallback demo data matching the Stitch design if backend hasn't generated predictions yet
  const items: PredictionItem[] = predictions.length > 0 ? predictions : [
    {
      camera_id: 102,
      camera_name: 'CAM-N-102',
      location: 'North Gate Perimeter',
      risk_level: 'HIGH',
      failure_probability: 0.89,
      confidence_score: 89,
      expected_failure_window: '72 HOURS (PoE Degradation)',
      predicted_issue: 'Voltage Drop / PoE Instability',
    },
    {
      camera_id: 405,
      camera_name: 'CAM-E-405',
      location: 'East Wing Hallway',
      risk_level: 'MEDIUM',
      failure_probability: 0.82,
      confidence_score: 82,
      expected_failure_window: '5 DAYS (Lens Motor Wear)',
      predicted_issue: 'Lens Focus Delay',
    },
    {
      camera_id: 202,
      camera_name: 'SW-CORE-02',
      location: 'Server Room B Rack 4',
      risk_level: 'MEDIUM',
      failure_probability: 0.76,
      confidence_score: 76,
      expected_failure_window: '14 DAYS (Thermal Anomaly)',
      predicted_issue: 'Chassis Fan Degradation',
    },
  ];

  return (
    <div className="bg-white dark:bg-[#11192b] rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col">
      <div className="flex justify-between items-center mb-5">
        <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <span className="material-symbols-outlined text-blue-600 dark:text-blue-400">online_prediction</span>
          AI Failure Predictions
        </h2>
        {onViewAll && (
          <button
            onClick={onViewAll}
            className="text-xs font-bold text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 uppercase tracking-wider"
          >
            View All
          </button>
        )}
      </div>

      <div className="flex-1 overflow-x-auto">
        <table className="w-full text-left border-collapse min-w-[520px]">
          <thead>
            <tr className="border-b border-slate-200 dark:border-slate-800 text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
              <th className="py-2.5 px-3">Asset</th>
              <th className="py-2.5 px-3">Location</th>
              <th className="py-2.5 px-3">Expected Failure</th>
              <th className="py-2.5 px-3 text-right">Confidence</th>
            </tr>
          </thead>
          <tbody className="text-xs divide-y divide-slate-100 dark:divide-slate-800/60 font-medium">
            {items.map((item, index) => {
              const isSwitch = item.camera_name.startsWith('SW-');
              return (
                <tr
                  key={item.id ?? index}
                  className="hover:bg-slate-50 dark:hover:bg-slate-900/40 transition-colors"
                >
                  <td className="py-3 px-3 flex items-center gap-2 text-slate-900 dark:text-white font-semibold">
                    <span className="material-symbols-outlined text-amber-500 text-[18px]">
                      {isSwitch ? 'router' : 'videocam'}
                    </span>
                    <span>{item.camera_name}</span>
                  </td>
                  <td className="py-3 px-3 text-slate-500 dark:text-slate-400">
                    {item.location || 'Campus Perimeter'}
                  </td>
                  <td className="py-3 px-3">
                    <span className="text-amber-600 dark:text-amber-400 font-semibold">
                      {item.expected_failure_window}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-right">
                    <span className="inline-flex items-center justify-center px-2 py-0.5 rounded-full bg-blue-50 dark:bg-blue-950/70 text-blue-700 dark:text-blue-300 font-mono text-[11px] font-bold border border-blue-200/50 dark:border-blue-800/50">
                      {item.confidence_score}%
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
