import { apiRequest } from './api';
import { CameraFormData, SwitchOption } from '../types/cameraForm';
import { Camera } from '../types/camera';

export async function fetchSwitches(signal?: AbortSignal): Promise<SwitchOption[]> {
  try {
    const data = await apiRequest<any>('/api/switches', { signal });
    if (Array.isArray(data)) return data;
    if (data && Array.isArray(data.switches)) return data.switches;
    return [];
  } catch (err) {
    console.warn('Failed to fetch switches, using defaults', err);
    return [
      { switch_id: 'SW-A', switch_ip: '192.168.10.2', name: 'Main Campus Core SW-A' },
      { switch_id: 'SW-B', switch_ip: '192.168.10.3', name: 'Academic Block SW-B' },
      { switch_id: 'SW-CORE-01', switch_ip: '192.168.10.1', name: 'Core Distribution Switch' },
    ];
  }
}

export async function createCameraNode(data: CameraFormData, signal?: AbortSignal): Promise<{ ok: boolean; camera: Camera }> {
  return apiRequest<{ ok: boolean; camera: Camera }>('/api/cameras', {
    method: 'POST',
    body: JSON.stringify(data),
    signal,
  });
}

export async function updateCameraNode(id: number, data: CameraFormData, signal?: AbortSignal): Promise<{ ok: boolean; camera: Camera }> {
  return apiRequest<{ ok: boolean; camera: Camera }>(`/api/cameras/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
    signal,
  });
}

export async function deleteCameraNode(id: number, signal?: AbortSignal): Promise<{ ok: boolean; message?: string }> {
  return apiRequest<{ ok: boolean; message?: string }>(`/api/cameras/${id}`, {
    method: 'DELETE',
    signal,
  });
}
