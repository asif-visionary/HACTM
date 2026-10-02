import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';

export function useEntities(params: {
  page?: number;
  page_size?: number;
  query?: string;
  entity_type?: string;
}) {
  return useQuery({
    queryKey: ['entities-list', params],
    queryFn: () => api.getEntities(params),
    placeholderData: (prev) => prev,
  });
}

export function useEntityDetail(entityId: string | null) {
  return useQuery({
    queryKey: ['entity-detail', entityId],
    queryFn: () => (entityId ? api.getEntityById(entityId) : null),
    enabled: !!entityId,
  });
}
