export type CameraStatus = 'ONLINE' | 'OFFLINE' | 'UNSTABLE' | 'STREAM_FAILURE' | 'MAINTENANCE';

export interface Camera {
  id: number;
  name: string;
  location: string;
  ip_address: string;
  switch_id: string;
  switch_ip?: string;
  rtsp_url: string;
  status: CameraStatus;
  last_checked: string;
  latency_ms: number | null;
  stream_status?: string;
  stream_response_ms?: number | null;
  last_stream_check?: string;
  maintenance_status?: 'ENABLED' | 'DISABLED';
  maintenance_reason?: string;
  maintenance_technician?: string;
  maintenance_start_time?: string;
  maintenance_expected_end_time?: string;
  maintenance_completion_time?: string;
  maintenance_notes?: string;
  probe_mode?: string;
}

export interface PingHistoryEntry {
  id: number;
  camera_id: number;
  recorded_at: string;
  latency_ms: number | null;
  status: string;
}

export type ViewMode = 'grid' | 'table';
export type StatusFilter = 'ALL' | CameraStatus;
export type SortField = 'name' | 'latency' | 'status' | 'last_checked';
export type SortOrder = 'asc' | 'desc';
