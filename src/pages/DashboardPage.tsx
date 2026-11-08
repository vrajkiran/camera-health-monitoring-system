import React, { useState } from 'react';
import { useDashboardData } from '../hooks/useDashboardData';
import { MetricKpiRow } from '../components/dashboard/MetricKpiRow';
import { AiModelHealthWidget } from '../components/dashboard/AiModelHealthWidget';
import { AiPredictionsTable } from '../components/dashboard/AiPredictionsTable';
import { RootCauseWidget } from '../components/dashboard/RootCauseWidget';
import { AssetHealthWidget } from '../components/dashboard/AssetHealthWidget';
import { AiRecommendationsWidget } from '../components/dashboard/AiRecommendationsWidget';
import { RecentIncidentsWidget } from '../components/dashboard/RecentIncidentsWidget';
import { triggerManualDiagnostics } from '../services/dashboardService';

export const DashboardPage: React.FC = () => {
  const {
    summary,
    predictions,
    recommendations,
    incidents,
    rootCauses,
    assetHealth,
    isLoading,
    isRefreshing,
    error,
    refresh,
  } = useDashboardData();

  const [isRunningCheck, setIsRunningCheck] = useState(false);
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);

  const handleRunDiagnostics = async () => {
    setIsRunningCheck(true);
    setActionFeedback(null);
    try {
      await triggerManualDiagnostics();
      setActionFeedback('Cluster diagnostic check initiated. Telemetry updating...');
      await refresh();
    } catch (err: any) {
      setActionFeedback(err.message || 'Diagnostic trigger submitted.');
    } finally {
      setIsRunningCheck(false);
      setTimeout(() => setActionFeedback(null), 4000);
    }
  };

  if (isLoading && !summary) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-12 space-y-4">
        <svg className="animate-spin h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
        <p className="text-sm font-semibold text-slate-500">
          Synchronizing with surveillance telemetry cluster...
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-8">
      {/* Page Title & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
            Executive Dashboard
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Real-time telemetry overview of campus CCTV network nodes, switch links & AI predictions.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Refresh Indicator */}
          {isRefreshing && (
            <span className="text-xs text-blue-600 dark:text-blue-400 font-mono flex items-center gap-1.5 animate-pulse">
              <span className="material-symbols-outlined text-[16px] animate-spin">sync</span>
              Syncing...
            </span>
          )}

          {/* Manual Run Check Action */}
          <button
            onClick={handleRunDiagnostics}
            disabled={isRunningCheck}
            className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shadow-md shadow-blue-600/20 transition-all flex items-center gap-2 cursor-pointer disabled:opacity-50"
          >
            <span className="material-symbols-outlined text-[18px]">
              {isRunningCheck ? 'refresh' : 'play_arrow'}
            </span>
            <span>{isRunningCheck ? 'Checking...' : 'Run Diagnostics'}</span>
          </button>
        </div>
      </div>

      {/* Action Notification Banner */}
      {actionFeedback && (
        <div className="p-3.5 rounded-2xl bg-blue-50 dark:bg-blue-950/60 border border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-200 text-xs flex items-center gap-2 shadow-sm animate-fadeIn">
          <span className="material-symbols-outlined text-blue-600 dark:text-blue-400 text-base">
            info
          </span>
          <span>{actionFeedback}</span>
        </div>
      )}

      {/* Error Alert */}
      {error && (
        <div className="p-3.5 rounded-2xl bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-200 text-xs flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-rose-600 text-base">error</span>
            <span>{error}</span>
          </div>
          <button
            onClick={() => refresh()}
            className="underline font-bold hover:text-rose-900 cursor-pointer"
          >
            Retry Sync
          </button>
        </div>
      )}

      {/* 1. Metric KPI Row (Resolves ISSUE-25) */}
      <MetricKpiRow
        stats={summary?.statistics}
        healthScore={summary?.health_score}
        maintenanceSessions={summary?.maintenance_summary?.active_sessions}
        criticalIssuesCount={incidents.filter((i) => i.severity === 'CRITICAL' && i.status === 'OPEN').length || 1}
      />

      {/* 2. AI Model Health & Predictive Risk Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <AiModelHealthWidget stats={summary?.ml_statistics} />
        <div className="lg:col-span-2">
          <AiPredictionsTable predictions={predictions} />
        </div>
      </div>

      {/* 3. Root Cause Frequency & Overall Asset Health */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RootCauseWidget rootCauses={rootCauses} />
        <AssetHealthWidget assetHealth={assetHealth} />
      </div>

      {/* 4. Actionable Recommendations & Live Incidents Log */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-1">
          <AiRecommendationsWidget
            recommendations={recommendations}
            onActionClick={(rec) => {
              setActionFeedback(`Selected action for ${rec.target_asset || 'incident'}: Initiating diagnostic session.`);
            }}
          />
        </div>
        <div className="xl:col-span-2">
          <RecentIncidentsWidget incidents={incidents} />
        </div>
      </div>
    </div>
  );
};
