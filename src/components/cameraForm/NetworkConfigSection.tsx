import React from 'react';
import { CameraFormData, FormValidationErrors, SwitchOption } from '../../types/cameraForm';
import { IP_V4_REGEX } from '../../hooks/useCameraForm';

interface NetworkConfigSectionProps {
  formData: CameraFormData;
  errors: FormValidationErrors;
  switches: SwitchOption[];
  onChange: (field: keyof CameraFormData, value: string) => void;
  disabled?: boolean;
}

export const NetworkConfigSection: React.FC<NetworkConfigSectionProps> = ({
  formData,
  errors,
  switches,
  onChange,
  disabled = false,
}) => {
  const isIpValid = formData.ip_address && IP_V4_REGEX.test(formData.ip_address.trim());

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 pb-2 border-b border-slate-100 dark:border-slate-800">
        <span className="material-symbols-outlined text-blue-600 dark:text-blue-400 text-lg">
          router
        </span>
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200">
          2. Network & Uplink Switch
        </h3>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* IPv4 Address with Real-Time Regex Validation Indicator (Resolves ISSUE-22) */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label 
              htmlFor="cameraIpInput" 
              className="block text-xs font-semibold text-slate-700 dark:text-slate-300"
            >
              IPv4 Address <span className="text-rose-500">*</span>
            </label>
            {isIpValid && (
              <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-600 dark:text-emerald-400 font-mono">
                <span className="material-symbols-outlined text-[13px]">check_circle</span>
                Valid IPv4
              </span>
            )}
          </div>
          <div className="relative">
            <input
              id="cameraIpInput"
              type="text"
              required
              value={formData.ip_address}
              onChange={(e) => onChange('ip_address', e.target.value)}
              disabled={disabled}
              placeholder="e.g. 192.168.10.45"
              className={`w-full px-3.5 py-2.5 rounded-xl border text-xs font-mono font-medium bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all ${
                errors.ip_address
                  ? 'border-rose-400 focus:ring-rose-400'
                  : isIpValid
                  ? 'border-emerald-400 focus:ring-emerald-400'
                  : 'border-slate-300 dark:border-slate-700'
              }`}
            />
          </div>
          {errors.ip_address && (
            <p className="text-[11px] text-rose-500 mt-1 font-medium">{errors.ip_address}</p>
          )}
        </div>

        {/* Subnet Mask Placeholder */}
        <div>
          <label 
            htmlFor="subnetMaskInput" 
            className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5"
          >
            Subnet Mask
          </label>
          <input
            id="subnetMaskInput"
            type="text"
            readOnly
            value="255.255.255.0 (/24)"
            className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-800 text-xs font-mono text-slate-500 dark:text-slate-400 bg-slate-100/60 dark:bg-slate-900/40 cursor-not-allowed outline-none"
          />
        </div>

        {/* Uplink Switch Dropdown */}
        <div>
          <label 
            htmlFor="uplinkSwitchSelect" 
            className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5"
          >
            Connected Switch <span className="text-rose-500">*</span>
          </label>
          <div className="relative">
            <select
              id="uplinkSwitchSelect"
              value={formData.switch_id}
              onChange={(e) => onChange('switch_id', e.target.value)}
              disabled={disabled}
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 text-xs font-medium bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all cursor-pointer"
            >
              {switches.map((sw) => (
                <option key={sw.switch_id} value={sw.switch_id} className="bg-white dark:bg-slate-900">
                  {sw.name ? `${sw.name} (${sw.switch_id})` : sw.switch_id} — {sw.switch_ip}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Switch Port */}
        <div>
          <label 
            htmlFor="switchPortInput" 
            className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5"
          >
            Switch Port
          </label>
          <input
            id="switchPortInput"
            type="text"
            value={formData.switch_port || 'Port 01'}
            onChange={(e) => onChange('switch_port', e.target.value)}
            disabled={disabled}
            placeholder="e.g. Port 08 or Gi1/0/12"
            className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 text-xs font-mono font-medium bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
          />
        </div>
      </div>
    </div>
  );
};
