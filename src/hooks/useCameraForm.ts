import { useState, useEffect, useCallback, useRef } from 'react';
import { CameraFormData, FormValidationErrors, SwitchOption } from '../types/cameraForm';
import { Camera } from '../types/camera';
import { fetchSwitches, createCameraNode, updateCameraNode, deleteCameraNode } from '../services/cameraFormService';

// Real-time regex validators (Resolves ISSUE-22)
export const IP_V4_REGEX = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
export const RTSP_REGEX = /^rtsp:\/\/[a-zA-Z0-9_.\-]+(:[0-9]{1,5})?(\/.*)?$/i;

interface UseCameraFormProps {
  initialCamera?: Camera | null;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function useCameraForm({ initialCamera, onSuccess, onCancel }: UseCameraFormProps = {}) {
  const isEditing = Boolean(initialCamera?.id);

  const [formData, setFormData] = useState<CameraFormData>({
    name: initialCamera?.name || '',
    location: initialCamera?.location || '',
    ip_address: initialCamera?.ip_address || '',
    switch_id: initialCamera?.switch_id || 'SW-A',
    switch_ip: initialCamera?.switch_ip || '192.168.10.2',
    switch_port: 'Port 01',
    rtsp_url: initialCamera?.rtsp_url || 'rtsp://192.168.10.21/live',
    probe_mode: (initialCamera?.probe_mode as any) || 'LIVE',
  });

  const [errors, setErrors] = useState<FormValidationErrors>({});
  const [switches, setSwitches] = useState<SwitchOption[]>([]);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  // Load switch list (Resolves ISSUE-17 with AbortController)
  useEffect(() => {
    const controller = new AbortController();
    abortControllerRef.current = controller;

    fetchSwitches(controller.signal)
      .then((data) => {
        setSwitches(data);
        if (data.length > 0 && !formData.switch_id) {
          setFormData((prev) => ({
            ...prev,
            switch_id: data[0].switch_id,
            switch_ip: data[0].switch_ip,
          }));
        }
      })
      .catch((err) => {
        if (err.name !== 'AbortError') console.error('Failed to load switches:', err);
      });

    return () => controller.abort();
  }, []);

  // Update form if initialCamera changes
  useEffect(() => {
    if (initialCamera) {
      setFormData({
        name: initialCamera.name || '',
        location: initialCamera.location || '',
        ip_address: initialCamera.ip_address || '',
        switch_id: initialCamera.switch_id || 'SW-A',
        switch_ip: initialCamera.switch_ip || '192.168.10.2',
        switch_port: 'Port 01',
        rtsp_url: initialCamera.rtsp_url || '',
        probe_mode: (initialCamera.probe_mode as any) || 'LIVE',
      });
      setErrors({});
      setFeedback(null);
    }
  }, [initialCamera]);

  // Real-time field validation (Resolves ISSUE-22)
  const validateField = useCallback((field: keyof CameraFormData, value: string): string | undefined => {
    switch (field) {
      case 'name':
        if (!value.trim()) return 'Camera name is required.';
        if (value.trim().length < 3) return 'Name must be at least 3 characters.';
        return undefined;
      case 'location':
        if (!value.trim()) return 'Campus location is required.';
        return undefined;
      case 'ip_address':
        if (!value.trim()) return 'IPv4 address is required.';
        if (!IP_V4_REGEX.test(value.trim())) return 'Invalid IPv4 address format (e.g. 192.168.10.55).';
        return undefined;
      case 'rtsp_url':
        if (!value.trim()) return 'RTSP Stream URL is required.';
        if (!RTSP_REGEX.test(value.trim())) return 'Must start with rtsp:// (e.g. rtsp://192.168.10.55/live).';
        return undefined;
      default:
        return undefined;
    }
  }, []);

  const handleChange = (field: keyof CameraFormData, value: string) => {
    setFormData((prev) => {
      const updated = { ...prev, [field]: value };
      // Auto-update switch_ip if switch_id changed
      if (field === 'switch_id') {
        const matchingSwitch = switches.find((s) => s.switch_id === value);
        if (matchingSwitch) {
          updated.switch_ip = matchingSwitch.switch_ip;
        }
      }
      return updated;
    });

    // Real-time validation update
    const errorMsg = validateField(field, value);
    setErrors((prev) => ({ ...prev, [field]: errorMsg }));
  };

  const validateAll = (): boolean => {
    const newErrors: FormValidationErrors = {};
    (['name', 'location', 'ip_address', 'rtsp_url'] as (keyof CameraFormData)[]).forEach((f) => {
      const err = validateField(f, formData[f] || '');
      if (err) newErrors[f] = err;
    });
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFeedback(null);

    if (!validateAll()) {
      setFeedback({ type: 'error', message: 'Please correct the highlighted fields before saving.' });
      return;
    }

    setIsSubmitting(true);
    const controller = new AbortController();

    try {
      if (isEditing && initialCamera?.id) {
        await updateCameraNode(initialCamera.id, formData, controller.signal);
        setFeedback({ type: 'success', message: `Camera node "${formData.name}" updated successfully.` });
      } else {
        await createCameraNode(formData, controller.signal);
        setFeedback({ type: 'success', message: `Camera node "${formData.name}" provisioned successfully.` });
      }

      setTimeout(() => {
        if (onSuccess) onSuccess();
      }, 900);
    } catch (err: any) {
      setFeedback({ type: 'error', message: err.message || 'Operation failed. Please verify network parameters.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!initialCamera?.id) return;
    const confirmDelete = window.confirm(
      `Are you sure you want to decommission and delete camera "${initialCamera.name}"? This removes all historical telemetry and ping logs.`
    );
    if (!confirmDelete) return;

    setIsDeleting(true);
    try {
      await deleteCameraNode(initialCamera.id);
      setFeedback({ type: 'success', message: 'Camera node decommissioned successfully.' });
      setTimeout(() => {
        if (onSuccess) onSuccess();
      }, 700);
    } catch (err: any) {
      setFeedback({ type: 'error', message: err.message || 'Failed to delete camera.' });
    } finally {
      setIsDeleting(false);
    }
  };

  return {
    formData,
    errors,
    switches,
    isSubmitting,
    isDeleting,
    isEditing,
    feedback,
    handleChange,
    handleSubmit,
    handleDelete,
    onCancel,
  };
}
