import { useState, useEffect, useCallback, useMemo } from 'react';
import { TopologyData, SwitchItem, SwitchStatsSummary, TopologyNode } from '../types/topology';
import { topologyService } from '../services/topologyService';

export function useTopologyData() {
  const [topologyData, setTopologyData] = useState<TopologyData>({
    nodes: [],
    edges: [],
    probable_switch_failures: [],
    generated_at: '',
  });
  const [switches, setSwitches] = useState<SwitchItem[]>([]);
  const [stats, setStats] = useState<SwitchStatsSummary>({
    total: 0,
    online: 0,
    offline: 0,
    avg_latency: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'ONLINE' | 'UNSTABLE' | 'OFFLINE'>('ALL');
  const [selectedSwitch, setSelectedSwitch] = useState<SwitchItem | null>(null);
  const [hoveredNode, setHoveredNode] = useState<{ node: TopologyNode; x: number; y: number } | null>(null);

  const fetchData = useCallback(async (signal?: AbortSignal) => {
    try {
      setLoading(true);
      setError(null);
      const [topo, swList, swStats] = await Promise.all([
        topologyService.getTopology(signal),
        topologyService.getSwitches(signal),
        topologyService.getSwitchStats(signal),
      ]);

      if (!signal?.aborted) {
        setTopologyData(topo);
        setSwitches(swList);

        // Derive avg latency from switches list if available
        const validLatencies = swList
          .map((s) => s.avg_latency_ms)
          .filter((lat): lat is number => typeof lat === 'number' && !isNaN(lat));
        const derivedAvgLatency = validLatencies.length
          ? Math.round((validLatencies.reduce((a, b) => a + b, 0) / validLatencies.length) * 10) / 10
          : swStats.avg_latency || 2.4;

        setStats({
          ...swStats,
          total: swList.length || swStats.total,
          online: swList.filter((s) => s.status === 'ONLINE').length || swStats.online,
          offline: swList.filter((s) => s.status === 'OFFLINE').length || swStats.offline,
          avg_latency: derivedAvgLatency,
        });
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        setError(err.message || 'Failed to load topology data');
      }
    } finally {
      if (!signal?.aborted) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    fetchData(controller.signal);

    const interval = setInterval(() => {
      fetchData(controller.signal);
    }, 15000); // 15s polling

    return () => {
      controller.abort();
      clearInterval(interval);
    };
  }, [fetchData]);

  const filteredSwitches = useMemo(() => {
    return switches.filter((sw) => {
      const q = searchQuery.toLowerCase().trim();
      const matchesSearch =
        !q ||
        sw.switch_id.toLowerCase().includes(q) ||
        (sw.switch_name && sw.switch_name.toLowerCase().includes(q)) ||
        (sw.ip_address && sw.ip_address.toLowerCase().includes(q)) ||
        (sw.switch_ip && sw.switch_ip.toLowerCase().includes(q)) ||
        (sw.location && sw.location.toLowerCase().includes(q));

      const matchesStatus =
        statusFilter === 'ALL' ||
        (statusFilter === 'ONLINE' && sw.status === 'ONLINE') ||
        (statusFilter === 'UNSTABLE' && sw.status === 'UNSTABLE') ||
        (statusFilter === 'OFFLINE' && sw.status === 'OFFLINE');

      return matchesSearch && matchesStatus;
    });
  }, [switches, searchQuery, statusFilter]);

  return {
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
    refetch: () => fetchData(),
  };
}
