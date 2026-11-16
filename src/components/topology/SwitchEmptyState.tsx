import React from 'react';

interface SwitchEmptyStateProps {
  searchQuery: string;
  onReset: () => void;
}

export const SwitchEmptyState: React.FC<SwitchEmptyStateProps> = ({ searchQuery, onReset }) => {
  return (
    <div className="p-12 text-center bg-white dark:bg-[#11192b] rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col items-center justify-center my-6">
      <div className="w-16 h-16 rounded-2xl bg-slate-100 dark:bg-slate-800/80 text-slate-400 dark:text-slate-500 flex items-center justify-center mb-4">
        <span className="material-symbols-outlined text-[32px]">search_off</span>
      </div>
      <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-1">
        No Matching Network Assets Found
      </h3>
      <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md mx-auto mb-6">
        {searchQuery ? (
          <>
            No switches or topology nodes matched the search query{' '}
            <strong className="text-slate-700 dark:text-slate-300">"{searchQuery}"</strong>. Please verify the IP address, switch ID, or location filter.
          </>
        ) : (
          'There are currently no network switches registered under this filter.'
        )}
      </p>
      <button
        type="button"
        onClick={onReset}
        className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold bg-blue-600 text-white hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-500 transition-colors shadow-sm"
      >
        <span className="material-symbols-outlined text-[18px]">filter_alt_off</span>
        <span>Clear Filters & Reset</span>
      </button>
    </div>
  );
};
