import React, { useState, useEffect } from 'react';
import { Camera, PingHistoryEntry } from '../../types/camera';
import { fetchCameraPingHistory, triggerCameraProbe } from '../../services/cameraService';

interface CameraDetailsDrawerProps {
  camera: Camera | null;
  onClose: () => void;
  onRefreshParent?: () => void;
  onEditCamera?: (camera: Camera) => void;
}

export const CameraDetailsDrawer: React.FC<CameraDetailsDrawerProps> = ({
  camera,
  onClose,
  onRefreshParent,
}) => {
  const [history, setHistory] = useState<PingHistoryEntry[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState<boolean>(false);
  const [isProbing, setIsProbing] = useState<boolean>(false);
  const [probeResult, setProbeResult] = useState<string | null>(null);

  // Close on Escape key (Resolves ISSUE-19)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  // Fetch ping history when camera changes
  useEffect(() => {
    if (!camera) return;
    let isMounted = true;
    setIsLoadingHistory(true);
    setProbeResult(null);

    fetchCameraPingHistory(camera.id)
      .then((data) => {
        if (isMounted) {
          setHistory(data);
          setIsLoadingHistory(false);
        }
      })
      .catch(() => {
        if (isMounted) setIsLoadingHistory(false);
      });

    return () => {
      isMounted = false;
    };
  }, [camera]);

  if (!camera) return null;

  const handleManualProbe = async () => {
    setIsProbing(true);
    setProbeResult(null);
    try {
      const res = await triggerCameraProbe(camera.id);
      setProbeResult(res.message || `Probe succeeded (${res.latency_ms ?? 45}ms)`);
      if (onRefreshParent) onRefreshParent();
      // Refetch history
      const updatedHistory = await fetchCameraPingHistory(camera.id);
      setHistory(updatedHistory);
    } catch (err: any) {
      setProbeResult(err.message || 'Probe timeout');
    } finally {
      setIsProbing(false);
      setTimeout(() => setProbeResult(null), 5000);
    }
  };

  // Generate SVG sparkline points
  const pingPoints = history.slice(-20).map((h, i, arr) => {
    const x = (i / (arr.length - 1 || 1)) * 320;
    const lat = h.latency_ms ?? 100;
    const y = 80 - Math.min(75, Math.max(5, (lat / 150) * 80));
    return `${x},${y}`;
  });
  const polylineStr = pingPoints.join(' ');

  return (
    <div className="fixed inset-0 z-50 overflow-hidden" role="dialog" aria-modal="true">
      {/* Backdrop */}
      <div
        onClick={onClose}
        className="absolute inset-0 bg-slate-900/40 backdrop-blur-xs transition-opacity"
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-white dark:bg-[#11192b] shadow-2xl border-l border-slate-200 dark:border-slate-800 flex flex-col justify-between">
          {/* Drawer Header */}
          <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center shadow-md shadow-blue-500/20">
                <span className="material-symbols-outlined text-[22px]">videocam</span>
              </div>
              <div>
                <h2 className="text-base font-bold text-slate-900 dark:text-white">
                  {camera.name}
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  Node #{camera.id} • {camera.location}
                </p>
              </div>
            </div>

            <button
              onClick={onClose}
              aria-label="Close details drawer"
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <span className="material-symbols-outlined text-[20px]">close</span>
            </button>
          </div>

          {/* Drawer Body */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {/* Status & Quick Diagnostic Button */}
            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 flex items-center justify-between">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                  Node Status
                </span>
                <span className="text-sm font-extrabold text-slate-900 dark:text-white">
                  {camera.status}
                </span>
              </div>
              <button
                onClick={handleManualProbe}
                disabled={isProbing}
                aria-label="Execute ping probe"
                className="px-3 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shadow-sm transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
              >
                <span className={`material-symbols-outlined text-[16px] ${isProbing ? 'animate-spin' : ''}`}>
                  {isProbing ? 'refresh' : 'network_ping'}
                </span>
                <span>{isProbing ? 'Probing...' : 'Probe Now'}</span>
              </button>
            </div>

            {probeResult && (
              <div className="p-3 rounded-xl bg-blue-50 dark:bg-blue-950/60 border border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-200 text-xs flex items-center gap-2 animate-fadeIn">
                <span className="material-symbols-outlined text-base">info</span>
                <span>{probeResult}</span>
              </div>
            )}

            {/* Ping Latency Sparkline Chart */}
            <div className="space-y-2">
              <div className="flex justify-between items-center text-xs">
                <span className="font-bold text-slate-800 dark:text-slate-200">
                  Ping Latency Trend
                </span>
                <span className="text-slate-400 font-mono text-[11px]">
                  Current: {camera.latency_ms ?? 'N/A'} ms
                </span>
              </div>
              <div className="h-24 w-full bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 rounded-xl p-2 relative overflow-hidden flex items-end">
                {isLoadingHistory ? (
                  <span className="text-xs text-slate-400 m-auto">Loading telemetry history...</span>
                ) : history.length > 1 ? (
                  <svg className="w-full h-full overflow-visible" viewBox="0 0 320 80">
                    <polyline
                      fill="none"
                      stroke="#2563eb"
                      strokeWidth="2.5"
                      points={polylineStr}
                      strokeLinecap="round"
                    />
                  </svg>
                ) : (
                  <span className="text-xs text-slate-400 m-auto">Telemetry steady at baseline</span>
                )}
              </div>
            </div>

            {/* Network Hardware Specifications */}
            <div className="space-y-3 text-xs">
              <h3 className="font-bold text-slate-900 dark:text-white uppercase tracking-wider text-[11px]">
                Network Configuration
              </h3>
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-100 dark:border-slate-800">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">
                    IPv4 Address
                  </span>
                  <span className="font-mono font-bold text-slate-800 dark:text-slate-200 text-[11px]">
                    {camera.ip_address}
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-100 dark:border-slate-800">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">
                    Uplink Switch
                  </span>
                  <span className="font-mono font-bold text-slate-800 dark:text-slate-200 text-[11px]">
                    {camera.switch_id || 'SW-CORE-01'}
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-100 dark:border-slate-800">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">
                    Switch IP
                  </span>
                  <span className="font-mono font-bold text-slate-800 dark:text-slate-200 text-[11px]">
                    {camera.switch_ip || '192.168.10.1'}
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-100 dark:border-slate-800">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">
                    Maintenance
                  </span>
                  <span className="font-bold text-slate-800 dark:text-slate-200 text-[11px]">
                    {camera.maintenance_status || 'DISABLED'}
                  </span>
                </div>
              </div>

              {/* RTSP Endpoint URI */}
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-100 dark:border-slate-800 space-y-1">
                <span className="text-[10px] uppercase font-bold text-slate-400 block">
                  RTSP Stream Endpoint
                </span>
                <code className="text-[11px] font-mono text-blue-600 dark:text-blue-400 break-all block">
                  {camera.rtsp_url}
                </code>
              </div>
            </div>
          </div>

          {/* Drawer Footer */}
          <div className="p-4 border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 flex justify-between items-center">
            {onEditCamera && (
              <button
                onClick={() => {
                  onClose();
                  onEditCamera(camera);
                }}
                className="px-3.5 py-2 rounded-xl bg-blue-50 text-blue-700 dark:bg-blue-950/70 dark:text-blue-300 font-bold text-xs hover:bg-blue-100 transition-colors flex items-center gap-1.5 cursor-pointer"
              >
                <span className="material-symbols-outlined text-[16px]">edit</span>
                <span>Edit Node</span>
              </button>
            )}
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold text-xs hover:bg-slate-50 transition-colors cursor-pointer"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
