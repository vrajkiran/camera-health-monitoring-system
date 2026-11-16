import React from 'react';
import { CameraFormData, FormValidationErrors } from '../../types/cameraForm';

interface BasicInfoSectionProps {
  formData: CameraFormData;
  errors: FormValidationErrors;
  onChange: (field: keyof CameraFormData, value: string) => void;
  disabled?: boolean;
}

export const BasicInfoSection: React.FC<BasicInfoSectionProps> = ({
  formData,
  errors,
  onChange,
  disabled = false,
}) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 pb-2 border-b border-slate-100 dark:border-slate-800">
        <span className="material-symbols-outlined text-blue-600 dark:text-blue-400 text-lg">
          badge
        </span>
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200">
          1. Basic Node Information
        </h3>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Camera Name */}
        <div>
          <label 
            htmlFor="cameraNameInput" 
            className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5"
          >
            Camera Identifier Name <span className="text-rose-500">*</span>
          </label>
          <input
            id="cameraNameInput"
            type="text"
            required
            value={formData.name}
            onChange={(e) => onChange('name', e.target.value)}
            disabled={disabled}
            placeholder="e.g. Main Gate CAM-01"
            className={`w-full px-3.5 py-2.5 rounded-xl border text-xs font-medium bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all ${
              errors.name
                ? 'border-rose-400 focus:ring-rose-400'
                : 'border-slate-300 dark:border-slate-700'
            }`}
          />
          {errors.name && (
            <p className="text-[11px] text-rose-500 mt-1 font-medium">{errors.name}</p>
          )}
        </div>

        {/* Campus Location */}
        <div>
          <label 
            htmlFor="cameraLocationInput" 
            className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5"
          >
            Campus Zone / Location <span className="text-rose-500">*</span>
          </label>
          <input
            id="cameraLocationInput"
            type="text"
            required
            value={formData.location}
            onChange={(e) => onChange('location', e.target.value)}
            disabled={disabled}
            placeholder="e.g. ECE Department - Floor 2"
            className={`w-full px-3.5 py-2.5 rounded-xl border text-xs font-medium bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all ${
              errors.location
                ? 'border-rose-400 focus:ring-rose-400'
                : 'border-slate-300 dark:border-slate-700'
            }`}
          />
          {errors.location && (
            <p className="text-[11px] text-rose-500 mt-1 font-medium">{errors.location}</p>
          )}
        </div>
      </div>
    </div>
  );
};
