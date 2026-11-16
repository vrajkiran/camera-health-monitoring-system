import React from 'react';
import { Camera, CameraStatus, SortField, SortOrder } from '../../types/camera';

interface CameraTableViewProps {
  cameras: Camera[];
  onSelect: (camera: Camera) => void;
  onProbe?: (camera: Camera) => void;
  sortField: SortField;
  onSortFieldChange: (field: SortField) => void;
  sortOrder: SortOrder;
  onToggleSortOrder: () => void;
  selectedCameraId?: number | null;
}

export const CameraTableView: React.FC<CameraTableViewProps> = ({
  cameras,
  onSelect,
  onProbe,
  sortField,
  onSortFieldChange,
  sortOrder,
  onToggleSortOrder,
  selectedCameraId,
}) => {
  const renderSortIndicator = (field: SortField) => {
    if (sortField !== field) return null;
    return (
      <span className="material-symbols-outlined text-[14px] ml-1">
        {sortOrder === 'asc' ? 'arrow_upward' : 'arrow_downward'}
      </span>
    );
  };

  const handleHeaderClick = (field: SortField) => {
    if (sortField === field) {
      onToggleSortOrder();
    } else {
      onSortFieldChange(field);
    }
  };

  const getStatusPill = (status: CameraStatus) => {
    switch (status) {
      case 'ONLINE':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 dark:bg-emerald-950/80 dark:text-emerald-300 font-bold text-[10px] border border-emerald-200/50">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
            Online
          </span>
        );
      case 'OFFLINE':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-rose-50 text-rose-700 dark:bg-rose-950/80 dark:text-rose-300 font-bold text-[10px] border border-rose-200/50">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
            Offline
          </span>
        );
      case 'UNSTABLE':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-amber-50 text-amber-700 dark:bg-amber-950/80 dark:text-amber-300 font-bold text-[10px] border border-amber-200/50">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
            Unstable
          </span>
        );
      case 'STREAM_FAILURE':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-purple-50 text-purple-700 dark:bg-purple-950/80 dark:text-purple-300 font-bold text-[10px] border border-purple-200/50">
            <span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span>
            Stream Fault
          </span>
        );
      case 'MAINTENANCE':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 dark:bg-blue-950/80 dark:text-blue-300 font-bold text-[10px] border border-blue-200/50">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
            Maintenance
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="bg-white dark:bg-[#11192b] rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse min-w-[760px]">
          <thead>
            <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-900/60 text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
              <th
                onClick={() => handleHeaderClick('name')}
                className="py-3 px-4 cursor-pointer hover:text-slate-800 dark:hover:text-slate-200 select-none"
              >
                <div className="flex items-center">
                  <span>Camera Name</span>
                  {renderSortIndicator('name')}
                </div>
              </th>
              <th className="py-3 px-4">Location</th>
              <th className="py-3 px-4">IP Address</th>
              <th className="py-3 px-4">Switch Link</th>
              <th
                onClick={() => handleHeaderClick('status')}
                className="py-3 px-4 cursor-pointer hover:text-slate-800 dark:hover:text-slate-200 select-none"
              >
                <div className="flex items-center">
                  <span>Status</span>
                  {renderSortIndicator('status')}
                </div>
              </th>
              <th
                onClick={() => handleHeaderClick('latency')}
                className="py-3 px-4 cursor-pointer hover:text-slate-800 dark:hover:text-slate-200 select-none"
              >
                <div className="flex items-center">
                  <span>Latency</span>
                  {renderSortIndicator('latency')}
                </div>
              </th>
              <th className="py-3 px-4">Stream Health</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="text-xs divide-y divide-slate-100 dark:divide-slate-800/60 font-medium">
            {cameras.map((camera) => {
              const isSelected = camera.id === selectedCameraId;
              const isHealthyLatency = camera.latency_ms !== null && camera.latency_ms < 100;
              return (
                <tr
                  key={camera.id}
                  onClick={() => onSelect(camera)}
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') onSelect(camera);
                  }}
                  className={`hover:bg-slate-50 dark:hover:bg-slate-900/40 transition-colors cursor-pointer ${
                    isSelected ? 'bg-blue-50/60 dark:bg-blue-950/30' : ''
                  }`}
                >
                  <td className="py-3.5 px-4 font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    <span className="material-symbols-outlined text-blue-600 dark:text-blue-400 text-[18px]">
                      videocam
                    </span>
                    <span>{camera.name}</span>
                  </td>
                  <td className="py-3.5 px-4 text-slate-600 dark:text-slate-300">
                    {camera.location}
                  </td>
                  <td className="py-3.5 px-4 font-mono text-[11px] text-slate-700 dark:text-slate-300">
                    {camera.ip_address}
                  </td>
                  <td className="py-3.5 px-4 text-slate-600 dark:text-slate-400 font-mono text-[11px]">
                    {camera.switch_id || 'SW-CORE-01'}
                  </td>
                  <td className="py-3.5 px-4">{getStatusPill(camera.status)}</td>
                  <td className="py-3.5 px-4 font-mono font-bold">
                    <span
                      className={
                        isHealthyLatency
                          ? 'text-emerald-600 dark:text-emerald-400'
                          : 'text-amber-600 dark:text-amber-400'
                      }
                    >
                      {camera.latency_ms !== null ? `${camera.latency_ms} ms` : 'N/A'}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-slate-500 dark:text-slate-400 text-[11px] truncate max-w-[160px]">
                    {camera.stream_status || 'Active'}
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <div className="flex items-center justify-end gap-1" onClick={(e) => e.stopPropagation()}>
                      {onProbe && (
                        <button
                          onClick={() => onProbe(camera)}
                          aria-label={`Ping probe ${camera.name}`}
                          title="Execute Ping Probe"
                          className="p-1 rounded-lg text-slate-400 hover:text-blue-600 transition-colors"
                        >
                          <span className="material-symbols-outlined text-[16px]">network_ping</span>
                        </button>
                      )}
                      <button
                        onClick={() => onSelect(camera)}
                        aria-label={`Inspect ${camera.name}`}
                        className="px-2 py-1 rounded bg-blue-50 text-blue-700 dark:bg-blue-950/70 dark:text-blue-300 text-[11px] font-bold hover:bg-blue-100 transition-colors"
                      >
                        Inspect
                      </button>
                    </div>
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
