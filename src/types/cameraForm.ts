export interface CameraFormData {
  name: string;
  location: string;
  ip_address: string;
  switch_id: string;
  switch_ip: string;
  switch_port?: string;
  rtsp_url: string;
  probe_mode: 'LIVE' | 'SIMULATED' | '';
}

export type FormValidationErrors = Partial<Record<keyof CameraFormData, string>>;

export interface SwitchOption {
  switch_id: string;
  switch_ip: string;
  name?: string;
  model?: string;
  location?: string;
}
