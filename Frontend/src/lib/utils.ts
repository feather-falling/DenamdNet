import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { format, parseISO, isValid } from 'date-fns';
import type { RiskLevel, StockStatus, AnomalyFlag } from '../types';

// ─────────────────────────────────────────────
// Class Utility
// ─────────────────────────────────────────────

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// ─────────────────────────────────────────────
// Status Colors & Labels
// ─────────────────────────────────────────────

export function getRiskConfig(risk?: RiskLevel | string) {
  switch (risk?.toUpperCase()) {
    case 'LOW':
      return { label: 'Low', color: 'text-green-700', bg: 'bg-green-50', border: 'border-green-200', dot: 'bg-green-500' };
    case 'MEDIUM':
      return { label: 'Medium', color: 'text-amber-700', bg: 'bg-amber-50', border: 'border-amber-200', dot: 'bg-amber-500' };
    case 'HIGH':
      return { label: 'High', color: 'text-orange-700', bg: 'bg-orange-50', border: 'border-orange-200', dot: 'bg-orange-500' };
    case 'CRITICAL':
      return { label: 'Critical', color: 'text-red-700', bg: 'bg-red-50', border: 'border-red-200', dot: 'bg-red-500' };
    default:
      return { label: 'Unknown', color: 'text-slate-500', bg: 'bg-slate-50', border: 'border-slate-200', dot: 'bg-slate-400' };
  }
}

export function getStockStatusConfig(status?: StockStatus | string) {
  switch (status?.toUpperCase()) {
    case 'CONTROLLED':
      return { label: 'Controlled', color: 'text-green-700', bg: 'bg-green-50', border: 'border-green-200', dot: 'bg-green-500' };
    case 'ATTENTION':
      return { label: 'Attention', color: 'text-amber-700', bg: 'bg-amber-50', border: 'border-amber-200', dot: 'bg-amber-500' };
    case 'CRITICAL':
      return { label: 'Critical', color: 'text-red-700', bg: 'bg-red-50', border: 'border-red-200', dot: 'bg-red-500' };
    default:
      return { label: 'Unknown', color: 'text-slate-500', bg: 'bg-slate-50', border: 'border-slate-200', dot: 'bg-slate-400' };
  }
}

export function getAnomalyConfig(anomaly?: AnomalyFlag | boolean | string) {
  const val = typeof anomaly === 'boolean'
    ? (anomaly ? 'DETECTED' : 'NOT_DETECTED')
    : anomaly?.toUpperCase();

  switch (val) {
    case 'DETECTED':
      return { label: 'Detected', color: 'text-orange-700', bg: 'bg-orange-50', border: 'border-orange-200' };
    case 'NOT_DETECTED':
      return { label: 'Not Detected', color: 'text-green-700', bg: 'bg-green-50', border: 'border-green-200' };
    default:
      return { label: 'Unknown', color: 'text-slate-500', bg: 'bg-slate-50', border: 'border-slate-200' };
  }
}

export function getTransferStatusConfig(status?: string) {
  switch (status?.toUpperCase()) {
    case 'COMPLETED':
      return { label: 'Completed', color: 'text-green-700', bg: 'bg-green-50', border: 'border-green-200' };
    case 'PENDING':
      return { label: 'Pending', color: 'text-blue-700', bg: 'bg-blue-50', border: 'border-blue-200' };
    case 'FAILED':
      return { label: 'Failed', color: 'text-red-700', bg: 'bg-red-50', border: 'border-red-200' };
    case 'NOT_REQUIRED':
      return { label: 'Not Required', color: 'text-slate-500', bg: 'bg-slate-50', border: 'border-slate-200' };
    default:
      return { label: '—', color: 'text-slate-400', bg: 'bg-transparent', border: 'border-transparent' };
  }
}

// ─────────────────────────────────────────────
// Number Formatting
// ─────────────────────────────────────────────

export function formatNumber(n?: number | null, decimals = 0): string {
  if (n === undefined || n === null || isNaN(n)) return '—';
  return new Intl.NumberFormat('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(n);
}

export function formatDays(n?: number | null): string {
  if (n === undefined || n === null || isNaN(n)) return '—';
  return `${n.toFixed(1)} days`;
}

export function formatUnits(n?: number | null): string {
  if (n === undefined || n === null || isNaN(n)) return '—';
  return `${formatNumber(n)} units`;
}

export function formatPercent(n?: number | null): string {
  if (n === undefined || n === null || isNaN(n)) return '—';
  return `${(n * 100).toFixed(1)}%`;
}

// ─────────────────────────────────────────────
// Date Formatting
// ─────────────────────────────────────────────

export function formatDate(dateStr?: string | null): string {
  if (!dateStr) return '—';
  try {
    const d = parseISO(dateStr);
    if (isValid(d)) return format(d, 'dd MMM yyyy, HH:mm');
    return dateStr;
  } catch {
    return dateStr;
  }
}

export function formatDateShort(dateStr?: string | null): string {
  if (!dateStr) return '—';
  try {
    const d = parseISO(dateStr);
    if (isValid(d)) return format(d, 'dd MMM yyyy');
    return dateStr;
  } catch {
    return dateStr;
  }
}

// ─────────────────────────────────────────────
// Data Extraction Helpers
// ─────────────────────────────────────────────

export function getRecords(output?: Record<string, unknown> | null) {
  if (!output) return [];
  const arr = (output.results ?? output.records ?? output.data) as unknown[];
  return Array.isArray(arr) ? arr : [];
}

export function getSummary(output?: Record<string, unknown> | null) {
  if (!output) return null;
  return (output.network_summary ?? output.summary) as Record<string, unknown> | undefined;
}

export function getTransfers(output?: Record<string, unknown> | null) {
  if (!output) return [];
  const arr = (output.transfers ?? output.redistribution) as unknown[];
  return Array.isArray(arr) ? arr : [];
}

export function getPHCLatLng(phc: Record<string, unknown>): [number, number] | null {
  const lat = (phc.lat ?? phc.latitude) as number | undefined;
  const lng = (phc.lon ?? phc.longitude) as number | undefined;
  if (lat !== undefined && lng !== undefined && !isNaN(lat) && !isNaN(lng)) {
    return [lat, lng];
  }
  return null;
}

// ─────────────────────────────────────────────
// JSON Download
// ─────────────────────────────────────────────

export function downloadJSON(data: unknown, filename: string) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export function copyToClipboard(text: string): Promise<void> {
  return navigator.clipboard.writeText(text);
}

// ─────────────────────────────────────────────
// Misc
// ─────────────────────────────────────────────

export function generateRunFilename(prefix = 'brics-result'): string {
  return `${prefix}-${format(new Date(), 'yyyy-MM-dd-HHmmss')}.json`;
}

export function debounce<T extends (...args: unknown[]) => void>(fn: T, delay: number): T {
  let timer: ReturnType<typeof setTimeout>;
  return ((...args: unknown[]) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  }) as T;
}
