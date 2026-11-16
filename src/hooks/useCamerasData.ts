import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { Camera, CameraStatus, StatusFilter, SortField, SortOrder, ViewMode } from '../types/camera';
import { fetchCameras } from '../services/cameraService';

const POLLING_INTERVAL_MS = 30000;
const WS_DEBOUNCE_BUFFER_MS = 250;

export function useCamerasData() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Filters & Sorting state (Resolves ISSUE-28, ISSUE-36)
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('ALL');
  const [sortField, setSortField] = useState<SortField>('name');
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');

  // Selected camera for slide-out drawer (Resolves ISSUE-10)
  const [selectedCameraId, setSelectedCameraId] = useState<number | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);
  const wsBufferRef = useRef<Record<number, Partial<Camera>>>({});
  const wsDebounceTimerRef = useRef<any>(null);

  // Fetch initial/polling cameras
  const loadCameras = useCallback(async (isBackground: boolean = false) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const controller = new AbortController();
    abortControllerRef.current = controller;

    if (!isBackground) setIsLoading(true);
    setIsRefreshing(isBackground);
    setError(null);

    try {
      const data = await fetchCameras(controller.signal);
      setCameras(data);
      setIsLoading(false);
      setIsRefreshing(false);
    } catch (err: any) {
      if (err.name === 'AbortError') return;
      console.error('Failed to load cameras:', err);
      setError(err.message || 'Failed to synchronize cameras.');
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  // Flush batched WebSocket events (Resolves ISSUE-14)
  const flushWsBuffer = useCallback(() => {
    const updates = wsBufferRef.current;
    if (Object.keys(updates).length === 0) return;

    setCameras((prev) =>
      prev.map((cam) => {
        const update = updates[cam.id];
        return update ? { ...cam, ...update } : cam;
      })
    );
    wsBufferRef.current = {};
  }, []);

  // WebSocket Connection with 250ms Debounced Batch Window (Resolves ISSUE-14)
  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: any = null;

    const connectWebSocket = () => {
      try {
        ws = new WebSocket('ws://127.0.0.1:8001');

        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            if (message.type === 'camera_update' && message.camera) {
              const cam = message.camera;
              wsBufferRef.current[cam.id] = cam;

              // Batch debounce
              if (wsDebounceTimerRef.current) {
                clearTimeout(wsDebounceTimerRef.current);
              }
              wsDebounceTimerRef.current = setTimeout(flushWsBuffer, WS_DEBOUNCE_BUFFER_MS);
            }
          } catch {
            // Ignore non-json packets
          }
        };

        ws.onclose = () => {
          reconnectTimeout = setTimeout(connectWebSocket, 5000);
        };

        ws.onerror = () => {
          ws?.close();
        };
      } catch {
        // Fallback gracefully to polling if WebSocket is offline
      }
    };

    connectWebSocket();

    return () => {
      if (ws) ws.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (wsDebounceTimerRef.current) clearTimeout(wsDebounceTimerRef.current);
    };
  }, [flushWsBuffer]);

  // Polling loop
  useEffect(() => {
    loadCameras(false);
    const interval = setInterval(() => {
      loadCameras(true);
    }, POLLING_INTERVAL_MS);

    return () => {
      clearInterval(interval);
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [loadCameras]);

  // Filtered and Sorted Cameras
  const filteredCameras = useMemo(() => {
    let list = [...cameras];

    // Status filter
    if (statusFilter !== 'ALL') {
      list = list.filter((c) => c.status === statusFilter);
    }

    // Search query filter (matches name, location, IP, switch)
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      list = list.filter(
        (c) =>
          c.name.toLowerCase().includes(q) ||
          c.location.toLowerCase().includes(q) ||
          c.ip_address.toLowerCase().includes(q) ||
          c.switch_id.toLowerCase().includes(q)
      );
    }

    // Sort order
    list.sort((a, b) => {
      let comp = 0;
      if (sortField === 'name') {
        comp = a.name.localeCompare(b.name);
      } else if (sortField === 'latency') {
        const latA = a.latency_ms ?? 9999;
        const latB = b.latency_ms ?? 9999;
        comp = latA - latB;
      } else if (sortField === 'status') {
        comp = a.status.localeCompare(b.status);
      } else if (sortField === 'last_checked') {
        comp = new Date(a.last_checked || 0).getTime() - new Date(b.last_checked || 0).getTime();
      }
      return sortOrder === 'asc' ? comp : -comp;
    });

    return list;
  }, [cameras, statusFilter, searchQuery, sortField, sortOrder]);

  // Status counts for filter pills
  const statusCounts = useMemo(() => {
    const counts: Record<string, number> = {
      ALL: cameras.length,
      ONLINE: 0,
      OFFLINE: 0,
      UNSTABLE: 0,
      STREAM_FAILURE: 0,
      MAINTENANCE: 0,
    };
    cameras.forEach((c) => {
      if (counts[c.status] !== undefined) {
        counts[c.status] += 1;
      }
    });
    return counts;
  }, [cameras]);

  const selectedCamera = useMemo(() => {
    return cameras.find((c) => c.id === selectedCameraId) || null;
  }, [cameras, selectedCameraId]);

  return {
    cameras: filteredCameras,
    allCameras: cameras,
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
    selectedCameraId,
    setSelectedCameraId,
    refresh: () => loadCameras(true),
  };
}
