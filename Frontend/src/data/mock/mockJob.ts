import type { PredictionJob } from '../../types';

export const mockJob: PredictionJob = {
  job_id: 'mock-job-001',
  status: 'COMPLETED',
  started_at: new Date(Date.now() - 8000).toISOString(),
  completed_at: new Date().toISOString(),
};
