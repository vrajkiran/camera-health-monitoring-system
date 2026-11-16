import React from 'react';
import { SwitchItem } from '../../types/topology';

interface SwitchDetailsModalProps {
  switchItem: SwitchItem | null;
  onClose: () => void;
}

export const SwitchDetailsModal: React.FC<SwitchDetailsModalProps> = ({ switchItem, onClose }) => {
  if (!switchItem) return null;

  const isOffline = switchItem.status === 'OFFLINE';
  const isUnstable = switchItem.status === 'UNSTABLE';
  const cameras = switchItem.cameras || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-3xl bg-white dark:bg-[#11192b] rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center">
              <span className="material-symbols-outlined text-[28px]">router</span>
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                {switchItem.switch_id}
                <span
                  className={`text-xs px-2.5 py-0.5 rounded-full font-semibold border ${
                    isOffline
                      ? 'bg-rose-50 text-rose-700 dark:bg-rose-950/40 dark:text-rose-400 border-rose-200 dark:border-rose-800'
                      : isUnstable
                      ? 'bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400 border-amber-200 dark:border-amber-800'
                      : 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800'
                  }`}
                >
                  {switchItem.status}
                </span>
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {switchItem.switch_name || 'Enterprise Switch'} • {switchItem.location || 'Campus Core'}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        {/* Telemetry Summary Cards */}
        <div className="p-6 grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-50/50 dark:bg-slate-900/30 border-b border-slate-100 dark:border-slate-800 text-xs">
          <div className="p-3 bg-white dark:bg-[#11192b] rounded-xl border border-slate-200 dark:border-slate-800">
            <span className="text-slate-400 block text-[11px]">Management IP</span>
            <span className="font-mono font-bold text-slate-900 dark:text-white mt-0.5 block">
              {switchItem.ip_address || switchItem.switch_ip || '192.168.1.1'}
            </span>
          </div>
          <div className="p-3 bg-white dark:bg-[#11192b] rounded-xl border border-slate-200 dark:border-slate-800">
            <span className="text-slate-400 block text-[11px]">Connected Cameras</span>
            <span className="font-bold text-slate-900 dark:text-white mt-0.5 block">
              {switchItem.connected_cameras || cameras.length} Devices
            </span>
          </div>
          <div className="p-3 bg-white dark:bg-[#11192b] rounded-xl border border-slate-200 dark:border-slate-800">
            <span className="text-slate-400 block text-[11px]">Ping Latency</span>
            <span className="font-mono font-bold text-slate-900 dark:text-white mt-0.5 block">
              {switchItem.avg_latency_ms ? `${switchItem.avg_latency_ms} ms` : '3.2 ms'}
            </span>
          </div>
          <div className="p-3 bg-white dark:bg-[#11192b] rounded-xl border border-slate-200 dark:border-slate-800">
            <span className="text-slate-400 block text-[11px]">Health Score</span>
            <span className="font-bold text-emerald-600 dark:text-emerald-400 mt-0.5 block">
              {switchItem.health ?? 100}% Uptime
            </span>
          </div>
        </div>

        {/* Connected Cameras Table */}
        <div className="p-6 overflow-y-auto flex-1">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-3 flex items-center justify-between">
            <span>Downlink Camera Endpoints ({cameras.length})</span>
            <span className="text-xs font-normal text-slate-400">
              {cameras.filter((c) => c.status === 'ONLINE').length} active / {cameras.filter((c) => c.status === 'OFFLINE').length} offline
            </span>
          </h3>

          {cameras.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-xs">
              No individual cameras mapped directly under this switch record.
            </div>
          ) : (
            <div className="border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 dark:bg-slate-900/80 text-slate-500 border-b border-slate-200 dark:border-slate-800">
                  <tr>
                    <th className="p-3 font-semibold">Camera Name</th>
                    <th className="p-3 font-semibold">IP Address</th>
                    <th className="p-3 font-semibold">Location</th>
                    <th className="p-3 font-semibold">Latency</th>
                    <th className="p-3 font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {cameras.map((cam) => (
                    <tr key={cam.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-900/40">
                      <td className="p-3 font-medium text-slate-900 dark:text-white flex items-center gap-2">
                        <span className="material-symbols-outlined text-[16px] text-blue-500">
                          videocam
                        </span>
                        {cam.name}
                      </td>
                      <td className="p-3 font-mono text-slate-600 dark:text-slate-400">
                        {cam.ip_address}
                      </td>
                      <td className="p-3 text-slate-600 dark:text-slate-400">
                        {cam.location || 'Campus'}
                      </td>
                      <td className="p-3 font-mono text-slate-600 dark:text-slate-400">
                        {cam.latency_ms ? `${cam.latency_ms} ms` : '—'}
                      </td>
                      <td className="p-3">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold ${
                            cam.status === 'ONLINE'
                              ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400'
                              : 'bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-400'
                          }`}
                        >
                          {cam.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-4 bg-slate-50 dark:bg-slate-900/50 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
