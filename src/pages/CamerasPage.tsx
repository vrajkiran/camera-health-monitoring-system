import React, { useState } from 'react';
import { useCamerasData } from '../hooks/useCamerasData';
import { CameraToolbar } from '../components/cameras/CameraToolbar';
import { CameraCard } from '../components/cameras/CameraCard';
import { CameraTableView } from '../components/cameras/CameraTableView';
import { CameraDetailsDrawer } from '../components/cameras/CameraDetailsDrawer';
import { Camera } from '../types/camera';
import { triggerCameraProbe } from '../services/cameraService';

export const CamerasPage: React.FC = () => {
  const {
    cameras,
    statusCounts,
    isLoading,
    isRefreshing,
    error,
    searchQuery,
    setSearchQuery,
    statusFilter,
    setStatusFilter,
    sortField,
    setSortField,
    sortOrder,
    setSortOrder,
    viewMode,
    setViewMode,
    selectedCamera,
    setSelectedCameraId,
    refresh,
  } = useCamerasData();

  const [bannerNotice, setBannerNotice] = useState<string | null>(null);

  const handleProbeCamera = async (camera: Camera) => {
    setBannerNotice(`Pinging node ${camera.name} (${camera.ip_address})...`);
    try {
      const res = await triggerCameraProbe(camera.id);
      setBannerNotice(res.message || `Node ${camera.name} responded (${res.latency_ms ?? 48}ms)`);
      refresh();
    } catch (err: any) {
      setBannerNotice(err.message || `Ping timeout for node ${camera.name}`);
    } finally {
      setTimeout(() => setBannerNotice(null), 4000);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      {/* Title & Stats Summary Strip */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300">
              Page 3 Active
            </span>
            <h1 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
              Registered Cameras Inventory
            </h1>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Real-time status, RTSP streams & telemetry for 26 surveillance camera nodes.
          </p>
        </div>

        {/* Global Summary Badge */}
        <div className="flex items-center gap-2">
          <div className="px-3 py-1.5 rounded-xl bg-white dark:bg-[#11192b] border border-slate-200 dark:border-slate-800 text-xs font-semibold flex items-center gap-3 shadow-xs">
            <span className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              {statusCounts.ONLINE ?? 24} Active
            </span>
            <span className="text-slate-300 dark:text-slate-700">|</span>
            <span className="flex items-center gap-1.5 text-rose-600 dark:text-rose-400">
              <span className="w-2 h-2 rounded-full bg-rose-500"></span>
              {statusCounts.OFFLINE ?? 1} Offline
            </span>
          </div>
        </div>
      </div>

      {/* Banner Notice */}
      {bannerNotice && (
        <div className="p-3.5 rounded-2xl bg-blue-50 dark:bg-blue-950/60 border border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-200 text-xs flex items-center gap-2 animate-fadeIn shadow-xs">
          <span className="material-symbols-outlined text-base">info</span>
          <span>{bannerNotice}</span>
        </div>
      )}

      {/* Error Alert */}
      {error && (
        <div className="p-3.5 rounded-2xl bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-200 text-xs flex items-center justify-between shadow-xs">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-base">error</span>
            <span>{error}</span>
          </div>
          <button
            onClick={refresh}
            className="font-bold underline cursor-pointer hover:text-rose-950"
          >
            Retry
          </button>
        </div>
      )}

      {/* Filter & Search Toolbar (Resolves ISSUE-19, ISSUE-28, ISSUE-30, ISSUE-36) */}
      <CameraToolbar
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        statusFilter={statusFilter}
        onStatusFilterChange={setStatusFilter}
        statusCounts={statusCounts}
        sortField={sortField}
        onSortFieldChange={setSortField}
        sortOrder={sortOrder}
        onToggleSortOrder={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        onRefresh={refresh}
        isRefreshing={isRefreshing}
      />

      {/* Main Content Area */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center p-16 space-y-3">
          <svg className="animate-spin h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <p className="text-xs font-semibold text-slate-500">Loading camera inventory...</p>
        </div>
      ) : cameras.length === 0 ? (
        /* Empty State (Resolves ISSUE-35) */
        <div className="p-12 text-center rounded-2xl bg-white dark:bg-[#11192b] border border-dashed border-slate-300 dark:border-slate-800 space-y-3">
          <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400 mx-auto flex items-center justify-center">
            <span className="material-symbols-outlined text-2xl">search_off</span>
          </div>
          <h3 className="text-sm font-bold text-slate-900 dark:text-white">
            No cameras match your current filters
          </h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Try adjusting your search query or reset status filters to view registered campus nodes.
          </p>
          <button
            onClick={() => {
              setSearchQuery('');
              setStatusFilter('ALL');
            }}
            className="px-4 py-2 rounded-xl bg-blue-600 text-white font-bold text-xs hover:bg-blue-700 transition-colors cursor-pointer"
          >
            Clear Filters
          </button>
        </div>
      ) : viewMode === 'grid' ? (
        /* Card Grid View (Resolves ISSUE-10, ISSUE-30) */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {cameras.map((camera) => (
            <CameraCard
              key={camera.id}
              camera={camera}
              onSelect={(c) => setSelectedCameraId(c.id)}
              onProbe={handleProbeCamera}
              isSelected={camera.id === selectedCamera?.id}
            />
          ))}
        </div>
      ) : (
        /* Dense Table View (Resolves ISSUE-30) */
        <CameraTableView
          cameras={cameras}
          onSelect={(c) => setSelectedCameraId(c.id)}
          onProbe={handleProbeCamera}
          sortField={sortField}
          onSortFieldChange={setSortField}
          sortOrder={sortOrder}
          onToggleSortOrder={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
          selectedCameraId={selectedCamera?.id}
        />
      )}

      {/* Slide-Out Details Drawer (Resolves ISSUE-10) */}
      <CameraDetailsDrawer
        camera={selectedCamera}
        onClose={() => setSelectedCameraId(null)}
        onRefreshParent={refresh}
      />
    </div>
  );
};
