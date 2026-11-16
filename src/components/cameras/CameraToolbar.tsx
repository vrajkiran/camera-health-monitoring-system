import React from 'react';
import { StatusFilter, SortField, SortOrder, ViewMode } from '../../types/camera';

interface CameraToolbarProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  statusFilter: StatusFilter;
  onStatusFilterChange: (status: StatusFilter) => void;
  statusCounts: Record<string, number>;
  sortField: SortField;
  onSortFieldChange: (field: SortField) => void;
  sortOrder: SortOrder;
  onToggleSortOrder: () => void;
  viewMode: ViewMode;
  onViewModeChange: (mode: ViewMode) => void;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export const CameraToolbar: React.FC<CameraToolbarProps> = ({
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  statusCounts,
  sortField,
  onSortFieldChange,
  sortOrder,
  onToggleSortOrder,
  viewMode,
  onViewModeChange,
  onRefresh,
  isRefreshing,
}) => {
  const filterPills: { id: StatusFilter; label: string; colorClass: string }[] = [
    { id: 'ALL', label: 'All Nodes', colorClass: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300' },
    { id: 'ONLINE', label: 'Online', colorClass: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/70 dark:text-emerald-300 border-emerald-200/50' },
    { id: 'OFFLINE', label: 'Offline', colorClass: 'bg-rose-50 text-rose-700 dark:bg-rose-950/70 dark:text-rose-300 border-rose-200/50' },
    { id: 'UNSTABLE', label: 'Unstable', colorClass: 'bg-amber-50 text-amber-700 dark:bg-amber-950/70 dark:text-amber-300 border-amber-200/50' },
    { id: 'STREAM_FAILURE', label: 'Stream Failure', colorClass: 'bg-purple-50 text-purple-700 dark:bg-purple-950/70 dark:text-purple-300 border-purple-200/50' },
    { id: 'MAINTENANCE', label: 'Maintenance', colorClass: 'bg-blue-50 text-blue-700 dark:bg-blue-950/70 dark:text-blue-300 border-blue-200/50' },
  ];

  return (
    <div className="space-y-4 bg-white dark:bg-[#11192b] p-4 sm:p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
      {/* Top Search & Controls Strip */}
      <div className="flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
        {/* Instant Search Input (Resolves ISSUE-36, ISSUE-19) */}
        <div className="relative flex-1 max-w-lg">
          <span className="material-symbols-outlined absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-[18px]">
            search
          </span>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search by camera name, IP, location, switch..."
            aria-label="Filter cameras by keyword"
            className="w-full pl-10 pr-9 py-2 rounded-xl text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all font-medium"
          />
          {searchQuery && (
            <button
              onClick={() => onSearchChange('')}
              aria-label="Clear search"
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-xs font-bold"
            >
              ✕
            </button>
          )}
        </div>

        {/* View Switcher, Sort & Refresh Controls (Resolves ISSUE-28, ISSUE-30) */}
        <div className="flex items-center gap-2 flex-wrap justify-end">
          {/* Sort Selector */}
          <div className="flex items-center gap-1 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-2 py-1 text-xs">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider pl-1">
              Sort:
            </span>
            <select
              value={sortField}
              onChange={(e) => onSortFieldChange(e.target.value as SortField)}
              aria-label="Sort cameras by field"
              className="bg-transparent border-0 text-xs font-semibold text-slate-800 dark:text-slate-200 focus:outline-none cursor-pointer pr-1"
            >
              <option value="name" className="bg-white dark:bg-slate-900">Name</option>
              <option value="latency" className="bg-white dark:bg-slate-900">Latency</option>
              <option value="status" className="bg-white dark:bg-slate-900">Status</option>
              <option value="last_checked" className="bg-white dark:bg-slate-900">Last Checked</option>
            </select>
            <button
              onClick={onToggleSortOrder}
              aria-label={`Toggle sort order (Current: ${sortOrder})`}
              title={`Sort order: ${sortOrder.toUpperCase()}`}
              className="p-1 text-slate-500 hover:text-blue-600 transition-colors"
            >
              <span className="material-symbols-outlined text-[16px]">
                {sortOrder === 'asc' ? 'arrow_upward' : 'arrow_downward'}
              </span>
            </button>
          </div>

          {/* Grid vs Table View Mode Switch (Resolves ISSUE-30) */}
          <div className="flex items-center p-1 bg-slate-100 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
            <button
              onClick={() => onViewModeChange('grid')}
              aria-label="Switch to Card Grid View"
              className={`p-1.5 rounded-lg text-xs font-semibold flex items-center transition-all ${
                viewMode === 'grid'
                  ? 'bg-white dark:bg-blue-600 text-blue-700 dark:text-white shadow-sm'
                  : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <span className="material-symbols-outlined text-[18px]">grid_view</span>
            </button>
            <button
              onClick={() => onViewModeChange('table')}
              aria-label="Switch to Dense Table View"
              className={`p-1.5 rounded-lg text-xs font-semibold flex items-center transition-all ${
                viewMode === 'table'
                  ? 'bg-white dark:bg-blue-600 text-blue-700 dark:text-white shadow-sm'
                  : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <span className="material-symbols-outlined text-[18px]">table_rows</span>
            </button>
          </div>

          {/* Refresh Action Button */}
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            aria-label="Refresh camera cluster list"
            title="Refresh list"
            className="p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 transition-all flex items-center justify-center cursor-pointer disabled:opacity-50"
          >
            <span className={`material-symbols-outlined text-[18px] ${isRefreshing ? 'animate-spin text-blue-600' : ''}`}>
              refresh
            </span>
          </button>
        </div>
      </div>

      {/* Filter Status Pills (Resolves ISSUE-36) */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
        {filterPills.map((pill) => {
          const count = statusCounts[pill.id] ?? 0;
          const isActive = statusFilter === pill.id;
          return (
            <button
              key={pill.id}
              onClick={() => onStatusFilterChange(pill.id)}
              aria-label={`Filter by ${pill.label} (${count} cameras)`}
              className={`px-3 py-1.5 rounded-xl font-semibold transition-all whitespace-nowrap flex items-center gap-1.5 cursor-pointer border ${
                isActive
                  ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                  : `${pill.colorClass} border-transparent hover:border-slate-300 dark:hover:border-slate-700`
              }`}
            >
              <span>{pill.label}</span>
              <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded-full ${
                isActive ? 'bg-blue-800 text-white' : 'bg-slate-200/70 dark:bg-slate-700 text-slate-700 dark:text-slate-300'
              }`}>
                {count}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
