export interface CameraStatistics {
  total: number;
  online: number;
  offline: number;
  unstable: number;
  stream_failure: number;
  avg_latency_ms: number | null;
}

export interface PlatformStatus {
  camera_monitoring: string;
  websocket: string;
  alert_scheduler: string;
  model_scheduler: string;
  last_monitor_tick: string | null;
}

export interface MLStatistics {
  accuracy: number;
  total_predictions: number;
  model_status: string;
  confidence_level?: string;
  last_analysis?: string;
  active_models?: string;
}

export interface PredictionItem {
  id?: number;
  camera_id: number;
  camera_name: string;
  location?: string;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  failure_probability: number;
  confidence_score: number;
  expected_failure_window: string;
  predicted_issue?: string;
  timestamp?: string;
}

export interface RootCauseItem {
  cause: string;
  occurrences: number;
  percentage: number;
}

export interface AssetHealthSummary {
  total_assets: number;
  healthy: number;
  warning: number;
  critical: number;
  maintenance: number;
}

export interface AIRecommendation {
  id: string | number;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  title: string;
  description: string;
  target_asset?: string;
  action_label?: string;
}

export interface IncidentItem {
  id: number;
  camera_id: number;
  camera_name: string;
  severity: 'CRITICAL' | 'WARNING' | 'INFO';
  status: 'OPEN' | 'INVESTIGATING' | 'RESOLVED' | 'ACKNOWLEDGED';
  root_cause: string;
  created_at: string;
  acknowledged_by?: string | null;
}

export interface DashboardSummaryResponse {
  statistics: CameraStatistics;
  health_score: number;
  platform_status: PlatformStatus;
  ml_statistics: MLStatistics;
  diagnosis_summary?: any;
  incident_summary?: any;
  maintenance_summary?: {
    active_sessions?: number;
    scheduled_sessions?: number;
    total_sessions?: number;
  };
  last_synchronization: string;
}

export interface DashboardData {
  summary: DashboardSummaryResponse | null;
  predictions: PredictionItem[];
  recommendations: AIRecommendation[];
  incidents: IncidentItem[];
  rootCauses: RootCauseItem[];
  assetHealth: AssetHealthSummary;
  isLoading: boolean;
  isRefreshing: boolean;
  error: string | null;
  lastUpdated: Date | null;
}
