export type NodeStatus = 'ONLINE' | 'OFFLINE' | 'UNSTABLE' | 'STREAM_FAILURE' | 'UNKNOWN';

export interface TopologyNode {
  id: string;
  type: 'switch' | 'camera';
  name?: string;
  camera_id?: number;
  switch_id?: string;
  switch_ip?: string;
  ip_address?: string;
  location?: string;
  status: NodeStatus;
  latency_ms?: number | null;
  stream_status?: string;
  last_checked?: string;
  total_cameras?: number;
  offline_cameras?: number;
  level?: 'core' | 'distribution' | 'access';
}

export interface TopologyEdge {
  source: string;
  target: string;
  health: 'GOOD' | 'DEGRADED' | 'DOWN';
}

export interface TopologyData {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
  probable_switch_failures: string[];
  generated_at: string;
  error?: string;
}

export interface SwitchCameraItem {
  id: number;
  name: string;
  ip_address: string;
  location?: string;
  status: string;
  latency_ms?: number | null;
  stream_status?: string;
  rtsp_url?: string;
}

export interface SwitchItem {
  switch_id: string;
  switch_name?: string;
  ip_address?: string;
  switch_ip?: string;
  location?: string;
  status: 'ONLINE' | 'UNSTABLE' | 'OFFLINE';
  health?: number;
  packet_loss?: number;
  connected_cameras: number;
  cameras?: SwitchCameraItem[];
  avg_latency_ms?: number | null;
  ping_history?: number[];
}

export interface SwitchStatsSummary {
  total: number;
  online: number;
  offline: number;
  avg_latency: number;
}
