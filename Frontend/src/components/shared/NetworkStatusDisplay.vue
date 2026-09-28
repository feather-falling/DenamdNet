<script setup lang="ts">
import { computed } from 'vue';
import { getStockStatusConfig } from '../../lib/utils';
import type { StockStatus } from '../../types';

const props = defineProps<{
  status?: string;
}>();

const config = computed(() => getStockStatusConfig(props.status as StockStatus));
</script>

<template>
  <div class="flex flex-col items-start">
    <span class="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-1">Network Status</span>
    <div class="flex items-center gap-2 px-4 py-2 rounded-lg border" :class="[config.bg, config.border]">
      <span class="w-2.5 h-2.5 rounded-full animate-[pulse-dot_2s_ease-in-out_infinite]" :class="config.dot"></span>
      <span class="text-2xl font-bold tracking-tight" :class="config.color">{{ config.label.toUpperCase() }}</span>
    </div>
  </div>
</template>
