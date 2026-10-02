import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';

export function useEvidence(params: {
  page?: number;
  page_size?: number;
  search?: string;
  event_type?: string;
  entity_id?: string;
  agent_id?: string;
  source?: string;
  dataset?: string;
  severity?: string;
  min_risk?: number;
  max_risk?: number;
  start_time?: string;
  end_time?: string;
}) {
  return useQuery({
    queryKey: ['evidence-list', params],
    queryFn: () => api.getEvidence(params),
    placeholderData: (prev) => prev,
  });
}

export function useEvidenceDetail(eventId: string | null) {
  return useQuery({
    queryKey: ['evidence-detail', eventId],
    queryFn: () => (eventId ? api.getEvidenceById(eventId) : null),
    enabled: !!eventId,
  });
}

export function useMetricsOverview() {
  return useQuery({
    queryKey: ['metrics-overview'],
    queryFn: () => api.getMetricsOverview(),
    refetchInterval: 15000,
  });
}

export function useEvidenceTimeline(limit: number = 15) {
  return useQuery({
    queryKey: ['evidence-timeline', limit],
    queryFn: () => api.getEvidenceTimeline(limit),
    refetchInterval: 15000,
  });
}
