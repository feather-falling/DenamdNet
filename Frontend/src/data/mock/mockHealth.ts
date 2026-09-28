import type { APIHealthStatus } from '../../types';

export const mockHealth: APIHealthStatus = {
  connected: true,
  status: 'ok (mock)',
  version: '1.0.0',
  latency_ms: 12,
};
