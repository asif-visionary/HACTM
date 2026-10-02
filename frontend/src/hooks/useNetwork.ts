import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import {
  NetworkEvent,
  NetworkDetection,
  NetworkModel,
  NetworkHealth,
  NetworkMetrics,
  EvaluationResult,
} from '../types/network';

export function useNetworkMetrics() {
  return useQuery<NetworkMetrics>({
    queryKey: ['network', 'metrics'],
    queryFn: async () => {
      const res = await api.getNetworkMetrics();
      return res.data;
    },
    refetchInterval: 5000,
  });
}

export function useNetworkHealth() {
  return useQuery<NetworkHealth>({
    queryKey: ['network', 'health'],
    queryFn: async () => {
      const res = await api.getNetworkHealth();
      return res.data;
    },
    refetchInterval: 5000,
  });
}

export function useNetworkDetections(params: {
  page?: number;
  page_size?: number;
  detector_type?: string;
  category?: string;
  severity?: string;
  min_risk?: number;
  event_id?: string;
}) {
  return useQuery({
    queryKey: ['network', 'detections', params],
    queryFn: async () => {
      const res = await api.getNetworkDetections(params);
      return res;
    },
    refetchInterval: 5000,
  });
}

export function useNetworkDetectionById(detectionId: string | null) {
  return useQuery<NetworkDetection>({
    queryKey: ['network', 'detection', detectionId],
    queryFn: async () => {
      if (!detectionId) throw new Error('No detection ID specified');
      const res = await api.getNetworkDetectionById(detectionId);
      return res.data;
    },
    enabled: !!detectionId,
  });
}

export function useNetworkEvents(params: {
  page?: number;
  page_size?: number;
  src_ip?: string;
  dst_ip?: string;
  protocol?: string;
}) {
  return useQuery({
    queryKey: ['network', 'events', params],
    queryFn: async () => {
      const res = await api.getNetworkEvents(params);
      return res;
    },
    refetchInterval: 5000,
  });
}

export function useNetworkModels() {
  return useQuery<NetworkModel[]>({
    queryKey: ['network', 'models'],
    queryFn: async () => {
      const res = await api.getNetworkModels();
      return res.data;
    },
  });
}

export function useNetworkConfig() {
  return useQuery({
    queryKey: ['network', 'config'],
    queryFn: async () => {
      const res = await api.getNetworkConfig();
      return res.data;
    },
  });
}

export function useActivateNetworkModel() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (modelId: string) => {
      return api.activateNetworkModel(modelId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['network', 'models'] });
      queryClient.invalidateQueries({ queryKey: ['network', 'health'] });
    },
  });
}

export function useEvaluateNetworkModel() {
  return useMutation({
    mutationFn: async (testFile: string): Promise<EvaluationResult> => {
      const res = await api.evaluateNetworkModel({ test_file: testFile });
      return res.data;
    },
  });
}

export function useSubmitDetectionFeedback() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { detection_id: string; label: string; analyst_note?: string }) => {
      return api.submitDetectionFeedback(payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['network', 'detections'] });
    },
  });
}
