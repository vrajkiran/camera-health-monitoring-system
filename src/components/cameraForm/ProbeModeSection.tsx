import React from 'react';
import { CameraFormData, FormValidationErrors } from '../../types/cameraForm';
import { RTSP_REGEX } from '../../hooks/useCameraForm';

interface ProbeModeSectionProps {
  formData: CameraFormData;
  errors: FormValidationErrors;
  onChange: (field: keyof CameraFormData, value: string) => void;
  disabled?: boolean;
}

export const ProbeModeSection: React.FC<ProbeModeSectionProps> = ({
  formData,
  errors,
  onChange,
  disabled = false,
}) => {
  const isRtspValid = formData.rtsp_url && RTSP_REGEX.test(formData.rtsp_url.trim());

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 pb-2 border-b border-slate-100 dark:border-slate-800">
        <span className="material-symbols-outlined text-blue-600 dark:text-blue-400 text-lg">
          stream
        </span>
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200">
          3. Stream & Monitoring Mode
        </h3>
      </div>

      {/* RTSP Stream URI with Validator (Resolves ISSUE-22) */}
      <div>
        <div className="flex items-center justify-between mb-1.5">
          <label 
            htmlFor="rtspUrlInput" 
            className="block text-xs font-semibold text-slate-700 dark:text-slate-300"
          >
            RTSP Stream URL <span className="text-rose-500">*</span>
          </label>
          {isRtspValid && (
            <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-600 dark:text-emerald-400 font-mono">
              <span className="material-symbols-outlined text-[13px]">check_circle</span>
              Valid RTSP URI
            </span>
          )}
        </div>
        <input
          id="rtspUrlInput"
          type="text"
          required
          value={formData.rtsp_url}
          onChange={(e) => onChange('rtsp_url', e.target.value)}
          disabled={disabled}
          placeholder="rtsp://192.168.10.45/live"
          className={`w-full px-3.5 py-2.5 rounded-xl border text-xs font-mono font-medium bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all ${
            errors.rtsp_url
              ? 'border-rose-400 focus:ring-rose-400'
              : isRtspValid
              ? 'border-emerald-400 focus:ring-emerald-400'
              : 'border-slate-300 dark:border-slate-700'
          }`}
        />
        {errors.rtsp_url && (
          <p className="text-[11px] text-rose-500 mt-1 font-medium">{errors.rtsp_url}</p>
        )}
      </div>

      {/* Probe Mode Radio Selector with Friendly Explanatory Guide (Resolves ISSUE-33) */}
      <div className="space-y-2 pt-1">
        <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300">
          Health Monitoring Probe Method
        </label>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {/* Option 1: Live Probe */}
          <div
            onClick={() => !disabled && onChange('probe_mode', 'LIVE')}
            className={`p-3.5 rounded-xl border transition-all cursor-pointer flex flex-col justify-between ${
              formData.probe_mode === 'LIVE' || !formData.probe_mode
                ? 'bg-blue-50/70 dark:bg-blue-950/40 border-blue-500 dark:border-blue-500 ring-1 ring-blue-500/20'
                : 'bg-slate-50/50 dark:bg-slate-900/50 border-slate-200 dark:border-slate-800 hover:border-slate-300'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                <span className="material-symbols-outlined text-[16px] text-blue-600">videocam</span>
                Live RTSP & Ping Check
              </span>
              <input
                type="radio"
                name="probe_mode"
                checked={formData.probe_mode === 'LIVE' || !formData.probe_mode}
                onChange={() => onChange('probe_mode', 'LIVE')}
                className="w-4 h-4 text-blue-600 focus:ring-blue-500 cursor-pointer"
              />
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-normal">
              Full verification: checks ICMP latency and handshakes port 554 for real-time video stream responsiveness.
            </p>
          </div>

          {/* Option 2: Simulated / ICMP only */}
          <div
            onClick={() => !disabled && onChange('probe_mode', 'SIMULATED')}
            className={`p-3.5 rounded-xl border transition-all cursor-pointer flex flex-col justify-between ${
              formData.probe_mode === 'SIMULATED'
                ? 'bg-blue-50/70 dark:bg-blue-950/40 border-blue-500 dark:border-blue-500 ring-1 ring-blue-500/20'
                : 'bg-slate-50/50 dark:bg-slate-900/50 border-slate-200 dark:border-slate-800 hover:border-slate-300'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                <span className="material-symbols-outlined text-[16px] text-amber-500">network_ping</span>
                ICMP Ping Only (Lightweight)
              </span>
              <input
                type="radio"
                name="probe_mode"
                checked={formData.probe_mode === 'SIMULATED'}
                onChange={() => onChange('probe_mode', 'SIMULATED')}
                className="w-4 h-4 text-blue-600 focus:ring-blue-500 cursor-pointer"
              />
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-normal">
              Lightweight probe: checks network packet round-trip time with zero camera CPU load or streaming bandwidth overhead.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
