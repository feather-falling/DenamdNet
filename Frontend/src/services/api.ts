// ─────────────────────────────────────────────
// API Service Layer — BRICS Health Resilience
// ─────────────────────────────────────────────
// All backend communication goes through this file.
// Supports both Real FastAPI + PostgreSQL Backend and Mock Mode Fallback.
// ─────────────────────────────────────────────

import type {
  PredictionJob,
  PredictionOutput,
  APIHealthStatus,
  PipelineJobStatus,
  PipelineSummary,
  RedistributionTransfer,
  MedicineMovement,
  NextDayInventoryRecord,
  PHCUser,
  AuthSession,
  MedicineRequestItem,
  MedicineCatalogItem,
  NotificationItem
} from '../types';
import { PredictionOutputSchema } from '../schemas';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';
const IS_MOCK = import.meta.env.VITE_MOCK_MODE === 'true';

const TOKEN_KEY = 'brics_jwt_token';
const USER_KEY = 'brics_phc_user';

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setStoredSession(token: string, user: PHCUser): void {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearStoredSession(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getStoredUser(): PHCUser | null {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

// ─────────────────────────────────────────────
// Fetch helper
// ─────────────────────────────────────────────

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const token = getStoredToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options?.headers as Record<string, string> ?? {}),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let detail = 'Unknown error';
    try {
      const errJson = await response.json();
      detail = errJson.detail || errJson.message || JSON.stringify(errJson);
    } catch {
      detail = await response.text().catch(() => 'Unknown error');
    }
    throw new APIError(response.status, detail);
  }

  return response.json() as Promise<T>;
}

// ─────────────────────────────────────────────
// Error type
// ─────────────────────────────────────────────

export class APIError extends Error {
  constructor(
    public readonly status: number,
    public readonly detail: string,
  ) {
    super(`API Error ${status}: ${detail}`);
    this.name = 'APIError';
  }
}

// ─────────────────────────────────────────────
// Health check
// ─────────────────────────────────────────────

export async function getBackendHealth(): Promise<APIHealthStatus> {
  if (IS_MOCK) {
    const { mockHealth } = await import('../data/mock/mockHealth');
    return mockHealth;
  }

  try {
    const start = Date.now();
    const data = await apiFetch<{ status?: string; version?: string }>('/health');
    return {
      connected: true,
      status: data.status ?? 'ok',
      version: data.version,
      latency_ms: Date.now() - start,
    };
  } catch {
    return { connected: false };
  }
}

// ─────────────────────────────────────────────
// Daily Operational Pipeline (Today's JSON -> ML -> Redistribution)
// ─────────────────────────────────────────────

export async function uploadTodayJson(
  file: File,
  country = 'all'
): Promise<{ job_id: string; status: string; progress: number; stage: string }> {
  if (IS_MOCK) {
    return {
      job_id: 'mock-job-101',
      status: 'running',
      progress: 0,
      stage: 'Uploading input'
    };
  }

  const formData = new FormData();
  formData.append('file', file);
  formData.append('country', country);

  const response = await fetch(`${BASE_URL}/api/run-daily/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let msg = 'Upload failed';
    try {
      const err = await response.json();
      msg = err.detail || msg;
    } catch {
      msg = await response.text();
    }
    throw new APIError(response.status, msg);
  }

  return response.json();
}

export async function runDailyPipeline(
  country = 'all',
  inputFile = 'input/input_today.json'
): Promise<{ job_id: string; status: string; progress: number; stage: string }> {
  if (IS_MOCK) {
    return {
      job_id: 'mock-job-101',
      status: 'running',
      progress: 17,
      stage: 'Validating operational data'
    };
  }

  return apiFetch<{ job_id: string; status: string; progress: number; stage: string }>('/api/run-daily', {
    method: 'POST',
    body: JSON.stringify({ country, input_file: inputFile })
  });
}

export async function getPipelineStatus(jobId: string): Promise<PipelineJobStatus> {
  if (IS_MOCK) {
    return {
      job_id: jobId,
      status: 'completed',
      progress: 100,
      stage: 'Dashboard results ready'
    };
  }

  return apiFetch<PipelineJobStatus>(`/api/run-daily/status/${jobId}`);
}

export async function getLatestPipelineStatus(): Promise<PipelineJobStatus> {
  if (IS_MOCK) {
    return {
      job_id: 'mock-latest',
      status: 'completed',
      progress: 100,
      stage: 'Dashboard results ready'
    };
  }

  return apiFetch<PipelineJobStatus>('/api/run-daily/latest');
}

// ─────────────────────────────────────────────
// Real Results Dashboard APIs
// ─────────────────────────────────────────────

export async function getPipelineResults(): Promise<PipelineSummary> {
  if (IS_MOCK) {
    return {
      phcs_evaluated: 163,
      medicines: 18,
      targets_evaluated: 2697,
      transfers_executed: 1075,
      total_units_transferred: 239974,
      fully_resolved: 874,
      partially_resolved: 2,
      execution_timestamp: new Date().toISOString(),
      countries: [
        {
          country: 'India',
          country_code: 'IN',
          phcs_involved: 54,
          targets_evaluated: 257,
          transfers_executed: 277,
          total_units_transferred: 21371,
          resolved_cases: 257,
          transfer_activity_rate: 100
        },
        {
          country: 'Brazil',
          country_code: 'BR',
          phcs_involved: 54,
          targets_evaluated: 252,
          transfers_executed: 301,
          total_units_transferred: 42773,
          resolved_cases: 252,
          transfer_activity_rate: 100
        },
        {
          country: 'South Africa',
          country_code: 'ZA',
          phcs_involved: 55,
          targets_evaluated: 390,
          transfers_executed: 497,
          total_units_transferred: 175830,
          resolved_cases: 365,
          transfer_activity_rate: 93.6
        }
      ]
    };
  }

  return apiFetch<PipelineSummary>('/api/results/summary');
}

export async function getResultsTransfers(params?: {
  search?: string;
  medicine_id?: string;
  country_code?: string;
  status?: string;
  limit?: number;
  offset?: number;
}): Promise<{ total: number; transfers: RedistributionTransfer[] }> {
  if (IS_MOCK) {
    return { total: 0, transfers: [] };
  }

  const query = new URLSearchParams();
  if (params?.search) query.set('search', params.search);
  if (params?.medicine_id) query.set('medicine_id', params.medicine_id);
  if (params?.country_code) query.set('country_code', params.country_code);
  if (params?.status) query.set('status', params.status);
  if (params?.limit) query.set('limit', String(params.limit));
  if (params?.offset) query.set('offset', String(params.offset));

  const qs = query.toString();
  return apiFetch<{ total: number; transfers: RedistributionTransfer[] }>(`/api/results/transfers${qs ? `?${qs}` : ''}`);
}

export async function getMedicineMovements(): Promise<MedicineMovement[]> {
  if (IS_MOCK) {
    return [
      { medicine_id: 'MED-001', medicine_name: 'Paracetamol 500 mg tablet', transfers_count: 180, units_moved: 32400, resolved_requirements: 180 },
      { medicine_id: 'MED-002', medicine_name: 'ORS sachet 20.5g', transfers_count: 140, units_moved: 28900, resolved_requirements: 140 },
      { medicine_id: 'MED-003', medicine_name: 'IV Normal Saline 0.9% 500 mL', transfers_count: 95, units_moved: 18200, resolved_requirements: 95 },
    ];
  }

  return apiFetch<MedicineMovement[]>('/api/results/medicines');
}

export async function getNextDayInventory(params?: {
  phc_id?: string;
  country_code?: string;
  status?: string;
  limit?: number;
  offset?: number;
}): Promise<{ total: number; records: NextDayInventoryRecord[] }> {
  if (IS_MOCK) {
    return { total: 0, records: [] };
  }

  const query = new URLSearchParams();
  if (params?.phc_id) query.set('phc_id', params.phc_id);
  if (params?.country_code) query.set('country_code', params.country_code);
  if (params?.status) query.set('status', params.status);
  if (params?.limit) query.set('limit', String(params.limit));
  if (params?.offset) query.set('offset', String(params.offset));

  const qs = query.toString();
  return apiFetch<{ total: number; records: NextDayInventoryRecord[] }>(`/api/results/inventory${qs ? `?${qs}` : ''}`);
}

export async function downloadOutputFile(
  fileKey: 'next-day-phc-data' | 'redistribution-results' | 'unresolved-requirements'
): Promise<void> {
  const url = `${BASE_URL}/api/results/download/${fileKey}`;
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `${fileKey.replace(/-/g, '_')}.json`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// ─────────────────────────────────────────────
// PHC Authentication & PostgreSQL Portal
// ─────────────────────────────────────────────

export async function registerPHC(data: {
  phc_name: string;
  email: string;
  password: string;
  country?: string;
}): Promise<AuthSession> {
  const session = await apiFetch<AuthSession>('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify(data)
  });
  setStoredSession(session.access_token, session.user);
  return session;
}

export async function loginPHC(data: {
  email: string;
  password: string;
}): Promise<AuthSession> {
  const session = await apiFetch<AuthSession>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(data)
  });
  setStoredSession(session.access_token, session.user);
  return session;
}

export async function logoutPHC(): Promise<void> {
  try {
    await apiFetch('/api/auth/logout', { method: 'POST' });
  } catch {
    // Ignore server error on logout
  } finally {
    clearStoredSession();
  }
}

export async function getCurrentPHC(): Promise<PHCUser> {
  const user = await apiFetch<PHCUser>('/api/auth/me');
  const token = getStoredToken();
  if (token) {
    setStoredSession(token, user);
  }
  return user;
}

export async function getMedicineCatalog(): Promise<MedicineCatalogItem[]> {
  try {
    return await apiFetch<MedicineCatalogItem[]>('/api/requests/catalog');
  } catch {
    return [
      { medicine_id: 'MED-001', name: 'Paracetamol 500 mg tablet', unit: 'tablet', category: 'analgesic_antipyretic' },
      { medicine_id: 'MED-002', name: 'ORS sachet 20.5g', unit: 'sachet', category: 'rehydration' },
      { medicine_id: 'MED-003', name: 'IV Normal Saline 0.9% 500 mL', unit: 'bag', category: 'iv_fluid' },
      { medicine_id: 'MED-004', name: 'Artemether-Lumefantrine tablet', unit: 'tablet', category: 'antimalarial' },
      { medicine_id: 'MED-005', name: 'Amoxicillin 500 mg capsule', unit: 'capsule', category: 'antibiotic' },
    ];
  }
}

export async function createMedicineRequest(data: {
  medicine_id: string;
  quantity: number;
  description?: string;
  urgency?: string;
  reason?: string;
}): Promise<MedicineRequestItem> {
  return apiFetch<MedicineRequestItem>('/api/requests', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

export async function getMyRequests(): Promise<MedicineRequestItem[]> {
  try {
    return await apiFetch<MedicineRequestItem[]>('/api/requests/my');
  } catch {
    return [];
  }
}

export async function getAvailableRequests(): Promise<MedicineRequestItem[]> {
  try {
    return await apiFetch<MedicineRequestItem[]>('/api/requests/available');
  } catch {
    return [];
  }
}

export async function approveRequest(
  requestId: string,
  data: { units_to_send: number; notes?: string }
): Promise<MedicineRequestItem> {
  return apiFetch<MedicineRequestItem>(`/api/requests/${requestId}/approve`, {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

export async function cancelRequest(
  requestId: string,
  notes?: string
): Promise<MedicineRequestItem> {
  return apiFetch<MedicineRequestItem>(`/api/requests/${requestId}/cancel`, {
    method: 'POST',
    body: JSON.stringify({ notes })
  });
}

export async function getRequestNotifications(): Promise<NotificationItem[]> {
  try {
    return await apiFetch<NotificationItem[]>('/api/requests/notifications');
  } catch {
    return [];
  }
}

// ─────────────────────────────────────────────
// Legacy Prediction Methods (Preserved for backwards compatibility)
// ─────────────────────────────────────────────

export async function runPrediction(inputFile: File): Promise<PredictionJob> {
  if (IS_MOCK) {
    const { mockJob } = await import('../data/mock/mockJob');
    return mockJob;
  }

  const form = new FormData();
  form.append('file', inputFile);

  const response = await fetch(`${BASE_URL}/predict`, {
    method: 'POST',
    body: form,
  });

  if (!response.ok) {
    const text = await response.text().catch(() => 'Unknown error');
    throw new APIError(response.status, text);
  }

  return response.json() as Promise<PredictionJob>;
}

export async function getPredictionStatus(jobId: string): Promise<PredictionJob> {
  if (IS_MOCK) {
    const { mockJob } = await import('../data/mock/mockJob');
    return { ...mockJob, status: 'COMPLETED' };
  }

  return apiFetch<PredictionJob>(`/predict/status/${jobId}`);
}

export async function getPredictionResult(jobId?: string): Promise<PredictionOutput> {
  if (IS_MOCK) {
    const { mockPredictionOutput } = await import('../data/mock/mockPredictionOutput');
    return mockPredictionOutput;
  }

  const path = jobId ? `/predict/result/${jobId}` : '/predict/result/latest';
  const raw = await apiFetch<unknown>(path);

  const parsed = PredictionOutputSchema.safeParse(raw);
  if (!parsed.success) {
    console.warn('[BRICS] Backend response has unexpected shape:', parsed.error);
    return raw as PredictionOutput;
  }
  return parsed.data as PredictionOutput;
}

export async function downloadPredictionResult(jobId?: string): Promise<Blob> {
  if (IS_MOCK) {
    const { mockPredictionOutput } = await import('../data/mock/mockPredictionOutput');
    return new Blob([JSON.stringify(mockPredictionOutput, null, 2)], { type: 'application/json' });
  }

  const path = jobId ? `/predict/download/${jobId}` : '/predict/download/latest';
  const response = await fetch(`${BASE_URL}${path}`);
  if (!response.ok) {
    throw new APIError(response.status, 'Download failed');
  }
  return response.blob();
}
