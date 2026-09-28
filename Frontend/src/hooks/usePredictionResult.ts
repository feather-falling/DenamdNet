import { useQuery } from '@tanstack/vue-query';
import { getPredictionResult } from '../services/api';
import type { MaybeRefOrGetter } from 'vue';
import { toValue } from 'vue';

export function usePredictionResult(jobId?: MaybeRefOrGetter<string | undefined>) {
  return useQuery({
    queryKey: ['prediction-result', () => toValue(jobId) ?? 'latest'],
    queryFn: () => getPredictionResult(toValue(jobId)),
    staleTime: 5 * 60_000,
    retry: 1,
  });
}
