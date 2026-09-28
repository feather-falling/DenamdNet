import { useQuery } from '@tanstack/vue-query';
import { getBackendHealth } from '../services/api';

export function useAPIHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: getBackendHealth,
    refetchInterval: 30_000,
    staleTime: 20_000,
    retry: 1,
  });
}
