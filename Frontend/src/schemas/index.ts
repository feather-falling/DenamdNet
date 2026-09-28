import { z } from 'zod';

// ─────────────────────────────────────────────
// Zod Schemas for Runtime Validation
// ─────────────────────────────────────────────

export const RiskLevelSchema = z.enum(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL', 'UNKNOWN']).catch('UNKNOWN');
export const StockStatusSchema = z.enum(['CONTROLLED', 'ATTENTION', 'CRITICAL', 'UNKNOWN']).catch('UNKNOWN');
export const TransferStatusSchema = z.enum(['COMPLETED', 'PENDING', 'FAILED', 'NOT_REQUIRED']).catch('NOT_REQUIRED');
export const AnomalyFlagSchema = z.enum(['DETECTED', 'NOT_DETECTED', 'UNKNOWN']).catch('UNKNOWN');

export const ResourceRecordSchema = z.object({
  phc_id: z.string().optional(),
  phc: z.string().optional(),
  medicine: z.string().optional(),
  current_stock: z.number().optional(),
  forecast_demand: z.number().optional(),
  daily_demand: z.number().optional(),
  stockout_days: z.number().optional(),
  estimated_stockout_date: z.string().optional(),
  safety_stock: z.number().optional(),
  lead_time: z.union([z.number(), z.string()]).optional(),
  risk_level: RiskLevelSchema.optional(),
  stock_status: StockStatusSchema.optional(),
  anomaly: AnomalyFlagSchema.optional(),
  anomaly_detected: z.boolean().optional(),
  country: z.string().optional(),
  state: z.string().optional(),
  district: z.string().optional(),
  transfer_status: TransferStatusSchema.optional(),
  received_units: z.number().optional(),
  sent_units: z.number().optional(),
  transfer_source: z.string().optional(),
  transfer_destination: z.string().optional(),
}).passthrough();

export const NetworkSummarySchema = z.object({
  status: StockStatusSchema.optional(),
  total_phcs: z.number().optional(),
  controlled_phcs: z.number().optional(),
  at_risk_phcs: z.number().optional(),
  critical_phcs: z.number().optional(),
  total_resources: z.number().optional(),
  transfers_completed: z.number().optional(),
  remaining_shortages: z.number().optional(),
  average_risk: z.union([z.number(), z.string()]).optional(),
}).passthrough();

export const TransferRecordSchema = z.object({
  source_phc: z.string().optional(),
  destination_phc: z.string().optional(),
  medicine: z.string().optional(),
  quantity: z.number().optional(),
  status: TransferStatusSchema.optional(),
  transfer_id: z.string().optional(),
}).passthrough();

export const PredictionOutputSchema = z.object({
  run_id: z.string().optional(),
  timestamp: z.string().optional(),
  input_file: z.string().optional(),
  status: z.string().optional(),
  network_summary: NetworkSummarySchema.optional(),
  summary: NetworkSummarySchema.optional(),
  results: z.array(ResourceRecordSchema).optional(),
  records: z.array(ResourceRecordSchema).optional(),
  data: z.array(ResourceRecordSchema).optional(),
  transfers: z.array(TransferRecordSchema).optional(),
  redistribution: z.array(TransferRecordSchema).optional(),
}).passthrough();

export const PHCRecordSchema = z.object({
  phc_id: z.string(),
  name: z.string().optional(),
  district: z.string().optional(),
  state: z.string().optional(),
  country: z.string().optional(),
  lat: z.number().optional(),
  lon: z.number().optional(),
  latitude: z.number().optional(),
  longitude: z.number().optional(),
  region: z.string().optional(),
  type: z.string().optional(),
}).passthrough();

export type ResourceRecordSchema = z.infer<typeof ResourceRecordSchema>;
export type PredictionOutputSchema = z.infer<typeof PredictionOutputSchema>;
export type PHCRecordSchema = z.infer<typeof PHCRecordSchema>;
