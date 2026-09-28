<script setup lang="ts">
import { computed } from 'vue';
import { getRiskConfig, getStockStatusConfig } from '../../lib/utils';
import type { RiskLevel, StockStatus } from '../../types';

const props = withDefaults(defineProps<{
  type: 'risk' | 'status' | 'anomaly' | 'transfer';
  value?: string | boolean;
  showDot?: boolean;
}>(), {
  showDot: true
});

const config = computed(() => {
  if (props.type === 'risk') {
    return { ...getRiskConfig(props.value as RiskLevel), dot: getRiskConfig(props.value as RiskLevel).dot };
  } else if (props.type === 'status') {
    const sc = getStockStatusConfig(props.value as StockStatus);
    return { ...sc, dot: sc.dot };
  } else if (props.type === 'anomaly') {
    if (props.value === true || String(props.value).toUpperCase() === 'DETECTED') {
      return { label: 'Anomaly', color: 'text-orange-700', bg: 'bg-orange-50', border: 'border-orange-200', dot: 'bg-orange-500' };
    } else if (props.value === false || String(props.value).toUpperCase() === 'NOT_DETECTED') {
      return { label: 'Normal', color: 'text-green-700', bg: 'bg-green-50', border: 'border-green-200', dot: 'bg-green-500' };
    }
  } else if (props.type === 'transfer') {
    const s = String(props.value).toUpperCase();
    if (s === 'COMPLETED') return { label: 'Completed', color: 'text-green-700', bg: 'bg-green-50', border: 'border-green-200', dot: 'bg-green-500' };
    else if (s === 'PENDING') return { label: 'Pending', color: 'text-blue-700', bg: 'bg-blue-50', border: 'border-blue-200', dot: 'bg-blue-500' };
    else if (s === 'FAILED') return { label: 'Failed', color: 'text-red-700', bg: 'bg-red-50', border: 'border-red-200', dot: 'bg-red-500' };
    else if (s === 'NOT_REQUIRED') return { label: 'N/A', color: 'text-slate-400', bg: 'bg-slate-50', border: 'border-slate-100', dot: 'bg-slate-300' };
  }
  return { label: '—', color: 'text-slate-400', bg: 'bg-transparent', border: 'border-transparent', dot: 'bg-slate-300' };
});
</script>

<template>
  <span
    class="inline-flex items-center gap-1.5 px-2 py-0.5 text-xs font-semibold rounded border whitespace-nowrap"
    :class="[config.color, config.bg, config.border]"
  >
    <span v-if="showDot" class="w-1.5 h-1.5 rounded-full flex-shrink-0" :class="config.dot"></span>
    {{ config.label }}
  </span>
</template>
