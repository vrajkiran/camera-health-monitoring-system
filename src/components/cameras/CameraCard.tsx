import React from 'react';
import { Camera, CameraStatus } from '../../types/camera';

interface CameraCardProps {
  camera: Camera;
  onSelect: (camera: Camera) => void;
  onProbe?: (camera: Camera) => void;
  isSelected?: boolean;
}

export const CameraCard: React.FC<CameraCardProps> = ({
  camera,
  onSelect,
  onProbe,
  isSelected = false,
}) => {
  const getStatusBorder = (status: CameraStatus) => {
    switch (status) {
      case 'ONLINE':
        return 'border-l-emerald-500';
      case 'OFFLINE':
        return 'border-l-rose-500';
      case 'UNSTABLE':
        return 'border-l-amber-500';
      case 'STREAM_FAILURE':
        return 'border-l-purple-500';
      case 'MAINTENANCE':
        return 'border-l-blue-500';
      default:
        return 'border-l-slate-400';
    }
  };

  const getStatusBadge = (status: CameraStatus) => {
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

  const latencyDisplay = camera.latency_ms !== null ? `${camera.latency_ms} ms` : 'N/A';
  const isHealthyLatency = camera.latency_ms !== null && camera.latency_ms < 100;

  return (
    <div
      onClick={() => onSelect(camera)}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onSelect(camera);
        }
      }}
      tabIndex={0}
      role="button"
      aria-label={`Inspect camera ${camera.name}, Status ${camera.status}, IP ${camera.ip_address}`}
      className={`bg-white dark:bg-[#11192b] rounded-2xl p-5 border border-slate-200 dark:border-slate-800 border-l-4 ${getStatusBorder(
        camera.status
      )} shadow-sm hover:shadow-md transition-all cursor-pointer flex flex-col justify-between group focus:outline-none focus:ring-2 focus:ring-blue-500 ${
        isSelected ? 'ring-2 ring-blue-600 dark:ring-blue-500' : ''
      }`}
    >
      <div>
        {/* Card Header */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
              {camera.name}
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 flex items-center gap-1">
              <span className="material-symbols-outlined text-[14px]">location_on</span>
              <span>{camera.location}</span>
            </p>
          </div>
          <div>{getStatusBadge(camera.status)}</div>
        </div>

        {/* Metrics Grid (Resolves ISSUE-10 - Always readable, never hidden by hover popups) */}
        <div className="grid grid-cols-2 gap-2.5 p-3 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-100 dark:border-slate-800/80 text-xs">
          <div>
            <span className="block text-[10px] uppercase font-bold text-slate-400 dark:text-slate-500">
              IP Address
            </span>
            <span className="font-mono text-slate-800 dark:text-slate-200 font-semibold text-[11px]">
              {camera.ip_address}
            </span>
          </div>

          <div>
            <span className="block text-[10px] uppercase font-bold text-slate-400 dark:text-slate-500">
              Latency
            </span>
            <span
              className={`font-mono font-bold text-[11px] ${
                isHealthyLatency
                  ? 'text-emerald-600 dark:text-emerald-400'
                  : 'text-amber-600 dark:text-amber-400'
              }`}
            >
              {latencyDisplay}
            </span>
          </div>

          <div>
            <span className="block text-[10px] uppercase font-bold text-slate-400 dark:text-slate-500">
              Uplink Switch
            </span>
            <span className="font-semibold text-slate-700 dark:text-slate-300 text-[11px] flex items-center gap-1">
              <span className="material-symbols-outlined text-[13px] text-blue-500">router</span>
              {camera.switch_id || 'SW-CORE-01'}
            </span>
          </div>

          <div>
            <span className="block text-[10px] uppercase font-bold text-slate-400 dark:text-slate-500">
              RTSP Stream
            </span>
            <span className="text-[11px] text-slate-600 dark:text-slate-400 truncate block">
              {camera.stream_status || 'Port 554 Active'}
            </span>
          </div>
        </div>
      </div>

      {/* Card Footer Quick Actions */}
      <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs">
        <span className="text-[11px] text-slate-400 font-mono">
          Last probe: {camera.last_checked ? camera.last_checked.split('T')[1]?.slice(0, 8) : 'Recent'}
        </span>

        <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
          {onProbe && (
            <button
              onClick={() => onProbe(camera)}
              aria-label={`Ping probe camera ${camera.name}`}
              title="Execute immediate ping probe"
              className="p-1.5 rounded-lg text-slate-500 hover:text-blue-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <span className="material-symbols-outlined text-[16px]">network_ping</span>
            </button>
          )}
          <button
            onClick={() => onSelect(camera)}
            aria-label={`Open telemetry drawer for ${camera.name}`}
            title="Inspect camera telemetry"
            className="px-2 py-1 rounded-lg bg-blue-50 text-blue-700 dark:bg-blue-950/70 dark:text-blue-300 hover:bg-blue-100 font-bold text-[11px] transition-colors flex items-center gap-1"
          >
            <span>Inspect</span>
            <span className="material-symbols-outlined text-[14px]">chevron_right</span>
          </button>
        </div>
      </div>
    </div>
  );
};
