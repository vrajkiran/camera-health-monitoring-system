import React from 'react';
import { useCameraForm } from '../hooks/useCameraForm';
import { BasicInfoSection } from '../components/cameraForm/BasicInfoSection';
import { NetworkConfigSection } from '../components/cameraForm/NetworkConfigSection';
import { ProbeModeSection } from '../components/cameraForm/ProbeModeSection';
import { FormActionBar } from '../components/cameraForm/FormActionBar';
import { Camera } from '../types/camera';

interface CameraManagementPageProps {
  initialCamera?: Camera | null;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export const CameraManagementPage: React.FC<CameraManagementPageProps> = ({
  initialCamera,
  onSuccess,
  onCancel,
}) => {
  const {
    formData,
    errors,
    switches,
    isSubmitting,
    isDeleting,
    isEditing,
    feedback,
    handleChange,
    handleSubmit,
    handleDelete,
  } = useCameraForm({ initialCamera, onSuccess, onCancel });

  return (
    <div className="max-w-3xl mx-auto space-y-6 pb-12">
      {/* Top Header & Breadcrumb */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {onCancel && (
            <button
              onClick={onCancel}
              aria-label="Return to Camera Inventory"
              className="p-2 rounded-xl bg-white dark:bg-[#11192b] border border-slate-200 dark:border-slate-800 text-slate-500 hover:text-slate-900 dark:hover:text-white transition-colors cursor-pointer"
            >
              <span className="material-symbols-outlined text-[20px]">arrow_back</span>
            </button>
          )}
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300">
                {isEditing ? `Edit Mode #${initialCamera?.id}` : 'Node Provisioning'}
              </span>
              <h1 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">
                {isEditing ? `Configure ${initialCamera?.name}` : 'Register New Camera Node'}
              </h1>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Set up IP addressing, connected switch uplink, and stream health monitoring.
            </p>
          </div>
        </div>
      </div>

      {/* Feedback Banner */}
      {feedback && (
        <div
          className={`p-4 rounded-2xl border text-xs flex items-center gap-2.5 animate-fadeIn shadow-xs ${
            feedback.type === 'success'
              ? 'bg-emerald-50 dark:bg-emerald-950/60 border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-200'
              : 'bg-rose-50 dark:bg-rose-950/60 border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-200'
          }`}
        >
          <span className="material-symbols-outlined text-base">
            {feedback.type === 'success' ? 'check_circle' : 'error'}
          </span>
          <span className="font-medium">{feedback.message}</span>
        </div>
      )}

      {/* Main Form Card (Simplified Single-Card Layout) */}
      <form
        onSubmit={handleSubmit}
        className="bg-white dark:bg-[#11192b] rounded-3xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 shadow-sm space-y-6"
      >
        {/* Section 1: Basic Node Info */}
        <BasicInfoSection
          formData={formData}
          errors={errors}
          onChange={handleChange}
          disabled={isSubmitting || isDeleting}
        />

        {/* Section 2: Network & Switch Uplink (Resolves ISSUE-22) */}
        <NetworkConfigSection
          formData={formData}
          errors={errors}
          switches={switches}
          onChange={handleChange}
          disabled={isSubmitting || isDeleting}
        />

        {/* Section 3: Stream & Monitoring Mode (Resolves ISSUE-33) */}
        <ProbeModeSection
          formData={formData}
          errors={errors}
          onChange={handleChange}
          disabled={isSubmitting || isDeleting}
        />

        {/* Actions Strip */}
        <FormActionBar
          isEditing={isEditing}
          isSubmitting={isSubmitting}
          isDeleting={isDeleting}
          onCancel={onCancel}
          onDelete={handleDelete}
        />
      </form>
    </div>
  );
};
