import React, { useState } from 'react';
import { useTopologyData } from '../hooks/useTopologyData';
import { SwitchStatsRow } from '../components/topology/SwitchStatsRow';
import { SwitchCardGrid } from '../components/topology/SwitchCardGrid';
import { TopologyGraph } from '../components/topology/TopologyGraph';
import { NodeTooltip } from '../components/topology/NodeTooltip';
import { SwitchEmptyState } from '../components/topology/SwitchEmptyState';
import { SwitchDetailsModal } from '../components/topology/SwitchDetailsModal';
import { SwitchItem, TopologyNode } from '../types/topology';

export const SwitchesTopologyPage: React.FC = () => {
  const {
    topologyData,
    switches,
    filteredSwitches,
    stats,
    loading,
    error,
    searchQuery,
    setSearchQuery,
    statusFilter,
    setStatusFilter,
    selectedSwitch,
    setSelectedSwitch,
    hoveredNode,
    setHoveredNode,
    refetch,
  } = useTopologyData();

  const [activeViewMode, setActiveViewMode] = useState<'GRAPH' | 'CARDS' | 'SPLIT'>('SPLIT');

  const handleSelectTopologyNode = (node: TopologyNode) => {
    if (node.type === 'switch') {
      const match = switches.find((s) => s.switch_id === node.id || s.switch_id === node.switch_id);
      if (match) {
        setSelectedSwitch(match);
      } else {
        setSelectedSwitch({
          switch_id: node.id,
          switch_name: node.name || 'Core Network Switch',
          ip_address: node.ip_address || node.switch_ip,
          location: node.location || 'Data Center',
          status: node.status === 'OFFLINE' ? 'OFFLINE' : node.status === 'UNSTABLE' ? 'UNSTABLE' : 'ONLINE',
          connected_cameras: node.total_cameras || 0,
        });
      }
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
            <span className="material-symbols-outlined text-blue-600 dark:text-blue-400 text-[28px]">
              hub
            </span>
            Network Switch Management & Topology
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Real-time campus network backbone visualizer, switch hardware inventory, and port telemetry.
          </p>
        </div>

        {/* View Mode Controls & Refresh */}
        <div className="flex items-center gap-2 self-start sm:self-auto">
          <div className="flex items-center bg-white dark:bg-[#11192b] border border-slate-200 dark:border-slate-800 p-1 rounded-xl shadow-sm text-xs font-medium">
            <button
              type="button"
              onClick={() => setActiveViewMode('SPLIT')}
              className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-colors ${
                activeViewMode === 'SPLIT'
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <span className="material-symbols-outlined text-[16px]">view_agenda</span>
              Combined
            </button>
            <button
              type="button"
              onClick={() => setActiveViewMode('GRAPH')}
              className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-colors ${
                activeViewMode === 'GRAPH'
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <span className="material-symbols-outlined text-[16px]">account_tree</span>
              Map Only
            </button>
            <button
              type="button"
              onClick={() => setActiveViewMode('CARDS')}
              className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-colors ${
                activeViewMode === 'CARDS'
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <span className="material-symbols-outlined text-[16px]">grid_view</span>
              Cards Only
            </button>
          </div>

          <button
            type="button"
            onClick={refetch}
            disabled={loading}
            className="p-2 bg-white dark:bg-[#11192b] border border-slate-200 dark:border-slate-800 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 shadow-sm transition-colors"
            title="Refresh Topology"
          >
            <span className={`material-symbols-outlined text-[20px] ${loading ? 'animate-spin' : ''}`}>
              refresh
            </span>
          </button>
        </div>
      </div>

      {/* Switch Stats KPI Row */}
      <SwitchStatsRow
        stats={stats}
        activeFilter={statusFilter}
        onFilterChange={setStatusFilter}
      />

      {/* Search & Filter Toolbar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-white dark:bg-[#11192b] p-3.5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <div className="relative w-full sm:w-80">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-[18px]">
            search
          </span>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search switches by ID, IP, or location..."
            className="w-full pl-9 pr-8 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => setSearchQuery('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            >
              <span className="material-symbols-outlined text-[16px]">close</span>
            </button>
          )}
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto justify-end text-xs">
          <span className="text-slate-400 hidden md:inline">Showing:</span>
          <span className="font-semibold text-slate-700 dark:text-slate-300">
            {filteredSwitches.length} of {switches.length} Switches
          </span>
          {(searchQuery || statusFilter !== 'ALL') && (
            <button
              type="button"
              onClick={() => {
                setSearchQuery('');
                setStatusFilter('ALL');
              }}
              className="ml-2 text-blue-600 dark:text-blue-400 underline font-medium"
            >
              Reset
            </button>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      {loading && switches.length === 0 ? (
        <div className="p-16 text-center bg-white dark:bg-[#11192b] rounded-2xl border border-slate-200 dark:border-slate-800">
          <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm font-medium text-slate-600 dark:text-slate-400">
            Mapping network topology and switch telemetry...
          </p>
        </div>
      ) : filteredSwitches.length === 0 && searchQuery ? (
        <SwitchEmptyState
          searchQuery={searchQuery}
          onReset={() => {
            setSearchQuery('');
            setStatusFilter('ALL');
          }}
        />
      ) : (
        <div className="space-y-6">
          {/* Topology Graph Canvas (Hi-DPI Vector SVG - resolves ISSUE-12 & ISSUE-16) */}
          {(activeViewMode === 'SPLIT' || activeViewMode === 'GRAPH') && (
            <div className="relative">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <span className="material-symbols-outlined text-blue-500 text-[20px]">account_tree</span>
                  Interactive Campus Network Hierarchy
                </h2>
                <span className="text-xs text-slate-400 font-mono">
                  {topologyData.nodes?.length || 0} Total Active Nodes
                </span>
              </div>
              <TopologyGraph
                data={topologyData}
                onHoverNode={setHoveredNode}
                onSelectNode={handleSelectTopologyNode}
              />
              {hoveredNode && (
                <NodeTooltip
                  node={hoveredNode.node}
                  x={hoveredNode.x}
                  y={hoveredNode.y}
                />
              )}
            </div>
          )}

          {/* Switch Hardware Inventory Cards (resolves ISSUE-29 with live ping sparkline) */}
          {(activeViewMode === 'SPLIT' || activeViewMode === 'CARDS') && (
            <div>
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <span className="material-symbols-outlined text-blue-500 text-[20px]">router</span>
                  Registered Switch Assets ({filteredSwitches.length})
                </h2>
                <span className="text-xs text-slate-400">
                  Click any card to inspect connected ports & downlink cameras
                </span>
              </div>
              <SwitchCardGrid
                switches={filteredSwitches}
                onSelectSwitch={(sw) => setSelectedSwitch(sw)}
              />
            </div>
          )}
        </div>
      )}

      {/* Switch Details Modal (resolves ISSUE-23) */}
      <SwitchDetailsModal
        switchItem={selectedSwitch}
        onClose={() => setSelectedSwitch(null)}
      />
    </div>
  );
};
