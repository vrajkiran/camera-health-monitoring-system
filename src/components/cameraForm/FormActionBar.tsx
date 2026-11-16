import React from 'react';

interface FormActionBarProps {
  isEditing: boolean;
  isSubmitting: boolean;
  isDeleting: boolean;
  onCancel?: () => void;
  onDelete?: () => void;
}

export const FormActionBar: React.FC<FormActionBarProps> = ({
  isEditing,
  isSubmitting,
  isDeleting,
  onCancel,
  onDelete,
}) => {
  return (
    <div className="pt-6 border-t border-slate-100 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3">
      {/* Optional Decommission button when editing */}
      <div>
        {isEditing && onDelete && (
          <button
            type="button"
            onClick={onDelete}
            disabled={isSubmitting || isDeleting}
            className="text-xs font-bold text-rose-600 hover:text-rose-700 dark:text-rose-400 dark:hover:text-rose-300 flex items-center gap-1.5 px-3 py-2 rounded-xl hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors disabled:opacity-50 cursor-pointer"
          >
            <span className="material-symbols-outlined text-[16px]">delete_forever</span>
            <span>{isDeleting ? 'Decommissioning...' : 'Decommission Camera Node'}</span>
          </button>
        )}
      </div>

      {/* Main Save / Cancel buttons */}
      <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isSubmitting || isDeleting}
            className="px-5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold text-xs hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors disabled:opacity-50 cursor-pointer"
          >
            Cancel
          </button>
        )}

        <button
          type="submit"
          disabled={isSubmitting || isDeleting}
          className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-bold text-xs shadow-md shadow-blue-600/25 transition-all flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
        >
          {isSubmitting ? (
            <>
              <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <span>Saving Node...</span>
            </>
          ) : (
            <>
              <span className="material-symbols-outlined text-[18px]">save</span>
              <span>{isEditing ? 'Update Camera Node' : 'Save Camera Node'}</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};
