// ─────────────────────────────────────────────
// Core Domain Types — BRICS Health Resilience
// ─────────────────────────────────────────────

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | 'UNKNOWN';
export type StockStatus = 'CONTROLLED' | 'ATTENTION' | 'CRITICAL' | 'UNKNOWN';
export type TransferStatus = 'COMPLETED' | 'PENDING' | 'FAILED' | 'NOT_REQUIRED';
export type AnomalyFlag = 'DETECTED' | 'NOT_DETECTED' | 'UNKNOWN';
export type JobStatus = 'IDLE' | 'RUNNING' | 'COMPLETED' | 'FAILED';

// ─────────────────────────────────────────────
// PHC Reference (phc.json)
// ─────────────────────────────────────────────

export interface PHCRecord {
  phc_id: string;
  name?: string;
  district?: string;
  state?: string;
  country?: string;
  lat?: number;
  lon?: number;
  latitude?: number;
  longitude?: number;
  region?: string;
  type?: string;
  [key: string]: unknown;
}

// ─────────────────────────────────────────────
// Redistribution / Transfer
// ─────────────────────────────────────────────

export interface TransferRecord {
  source_phc?: string;
  destination_phc?: string;
  medicine?: string;
  quantity?: number;
  status?: TransferStatus;
  transfer_id?: string;
  [key: string]: unknown;
}

// ─────────────────────────────────────────────
// Per-PHC Resource Record (in prediction output)
// ─────────────────────────────────────────────

export interface ResourceRecord {
  phc_id?: string;
  phc?: string;
  medicine?: string;
  current_stock?: number;
  forecast_demand?: number;
  daily_demand?: number;
  stockout_days?: number;
  estimated_stockout_date?: string;
  safety_stock?: number;
  lead_time?: number | string;
  risk_level?: RiskLevel;
  stock_status?: StockStatus;
  anomaly?: AnomalyFlag;
  anomaly_detected?: boolean;
  country?: string;
  state?: string;
  district?: string;
  transfer_status?: TransferStatus;
  received_units?: number;
  sent_units?: number;
  transfer_source?: string;
  transfer_destination?: string;
  [key: string]: unknown;
}

// ─────────────────────────────────────────────
// Prediction Output (from backend ML pipeline)
// ─────────────────────────────────────────────

export interface NetworkSummary {
  status?: StockStatus;
  total_phcs?: number;
  controlled_phcs?: number;
  at_risk_phcs?: number;
  critical_phcs?: number;
  total_resources?: number;
  transfers_completed?: number;
  remaining_shortages?: number;
  average_risk?: number | string;
  [key: string]: unknown;
}

export interface PredictionOutput {
  // Metadata
  run_id?: string;
  timestamp?: string;
  input_file?: string;
  status?: string;

  // Summary / Overview
  network_summary?: NetworkSummary;
  summary?: NetworkSummary;

  // Records
  results?: ResourceRecord[];
  records?: ResourceRecord[];
  data?: ResourceRecord[];

  // Transfers
  transfers?: TransferRecord[];
  redistribution?: TransferRecord[];

  // Raw passthrough — keep everything
  [key: string]: unknown;
}

// ─────────────────────────────────────────────
// API / Job Types
// ─────────────────────────────────────────────

export interface PredictionJob {
  job_id: string;
  status: JobStatus;
  started_at?: string;
  completed_at?: string;
  error?: string;
}

export interface APIHealthStatus {
  connected: boolean;
  status?: string;
  version?: string;
  latency_ms?: number;
}

// ─────────────────────────────────────────────
// UI State Types
// ─────────────────────────────────────────────

export interface FilterState {
  search: string;
  risk: RiskLevel | 'ALL';
  country: string;
  state: string;
  district: string;
  medicine: string;
  anomaly: AnomalyFlag | 'ALL';
  stockStatus: StockStatus | 'ALL';
}

export interface ProcessingStage {
  id: string;
  label: string;
  status: 'pending' | 'active' | 'done' | 'error';
}

export interface CommandItem {
  id: string;
  label: string;
  shortcut?: string;
  icon?: string;
  action: () => void;
  group: string;
}

// ─────────────────────────────────────────────
// Real Pipeline & Daily Orchestration Types
// ─────────────────────────────────────────────

export interface PipelineJobStatus {
  job_id: string;
  status: 'queued' | 'running' | 'completed' | 'failed' | 'idle';
  progress: number;
  stage: string;
  country?: string;
  input_file?: string;
  created_at?: string;
  updated_at?: string;
  error?: string | null;
  summary?: PipelineSummary | null;
}

export interface CountryStat {
  country: string;
  country_code: string;
  phcs_involved: number;
  targets_evaluated: number;
  transfers_executed: number;
  total_units_transferred: number;
  resolved_cases: number;
  transfer_activity_rate: number;
}

export interface PipelineSummary {
  phcs_evaluated: number;
  medicines: number;
  targets_evaluated: number;
  transfers_executed: number;
  total_units_transferred: number;
  fully_resolved: number;
  partially_resolved: number;
  execution_timestamp: string;
  countries: CountryStat[];
}

export interface RedistributionTransfer {
  id?: string;
  target_phc_id: string;
  source_phc_id: string;
  medicine_id: string;
  medicine_name: string;
  required_units_before_transfer: number;
  source_transferable_surplus_before_transfer: number;
  transferred_units: number;
  distance_km: number;
  remaining_target_requirement: number;
  source_remaining_transferable_surplus: number;
  status: 'RESOLVED' | 'PARTIALLY_RESOLVED' | string;
}

export interface MedicineMovement {
  medicine_id: string;
  medicine_name: string;
  transfers_count: number;
  units_moved: number;
  resolved_requirements: number;
}

export interface NextDayInventoryRecord {
  phc_id: string;
  state_region?: string;
  district?: string;
  country_code?: string;
  medicine_id: string;
  medicine_name: string;
  original_stock: number;
  incoming_units: number;
  outgoing_units: number;
  final_stock: number;
  daily_requirement: number;
  protected_stock: number;
  remaining_requirement: number;
  status: 'HEALTHY' | 'RESOLVED' | 'PARTIALLY_RESOLVED' | 'UNRESOLVED' | string;
}

// ─────────────────────────────────────────────
// PHC Portal & PostgreSQL Authentication Types
// ─────────────────────────────────────────────

export interface PHCUser {
  id: number;
  phc_name: string;
  email: string;
  country: string;
  assigned_phc_id?: string;
  created_at: string;
}

export interface AuthSession {
  access_token: string;
  token_type: string;
  user: PHCUser;
}

export interface MedicineRequestItem {
  id?: number;
  request_id: string;
  phc_id?: string;
  requesting_phc_name?: string;
  requesting_phc_id?: string;
  medicine_id: string;
  medicine_name?: string;
  quantity: number;
  urgency: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | string;
  description?: string;
  reason?: string;
  status: 'PENDING' | 'ACCEPTED' | 'APPROVED' | 'COMPLETED' | 'CANCELLED' | 'REJECTED' | string;
  supplied_by_phc_name?: string;
  supplied_by_phc_id?: string;
  supplied_quantity?: number;
  notes?: string;
  created_at: string;
  updated_at?: string;
}

export interface MedicineCatalogItem {
  medicine_id: string;
  name: string;
  unit: string;
  category: string;
}

export interface NotificationItem {
  id: string;
  request_id: string;
  title: string;
  message: string;
  type: string;
  timestamp: string;
  status: string;
}

