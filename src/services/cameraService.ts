import { apiRequest } from './api';
import { Camera, PingHistoryEntry } from '../types/camera';

export async function fetchCameras(signal?: AbortSignal): Promise<Camera[]> {
  const data = await apiRequest<any>('/api/cameras', { signal });
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.cameras)) return data.cameras;
  return [];
}

export async function fetchCamera(id: number, signal?: AbortSignal): Promise<Camera> {
  return apiRequest<Camera>(`/api/cameras/${id}`, { signal });
}

export async function fetchCameraPingHistory(id: number, signal?: AbortSignal): Promise<PingHistoryEntry[]> {
  try {
    const data = await apiRequest<any>(`/api/cameras/${id}/ping-history`, { signal });
    if (Array.isArray(data)) return data;
    if (data && Array.isArray(data.history)) return data.history;
    return [];
  } catch (err) {
    console.warn(`Failed to fetch ping history for camera ${id}`, err);
    return [];
  }
}

export async function triggerCameraProbe(id: number): Promise<{ success: boolean; message: string; latency_ms?: number }> {
  return apiRequest(`/api/cameras/${id}/probe`, { method: 'POST' });
}

export async function updateCameraStatus(id: number, status: string): Promise<Camera> {
  return apiRequest(`/api/cameras/${id}/status`, {
    method: 'PUT',
    body: JSON.stringify({ status }),
  });
}
