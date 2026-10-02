import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';

export function useSystemStatus() {
  const query = useQuery({
    queryKey: ['system-status'],
    queryFn: () => api.getHealth(),
    refetchInterval: 10000, // 10 seconds liveness check
    retry: 1,
  });

  return {
    status: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    isConnected: !query.isError && !!query.data,
    lastSyncTime: query.dataUpdatedAt ? new Date(query.dataUpdatedAt).toISOString() : null,
    refetch: query.refetch,
  };
}
