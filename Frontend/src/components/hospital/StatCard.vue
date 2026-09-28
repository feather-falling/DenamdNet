<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { TrendingUp, TrendingDown, Minus } from 'lucide-vue-next';
import { useHospitalStore } from '../../stores/hospitalStore';
import type { Component } from 'vue';

const props = defineProps<{
  label: string;
  value: number | string;
  icon: Component;
  trend?: number;
  trendLabel?: string;
  variant?: 'teal' | 'green' | 'red' | 'amber' | 'blue' | 'purple' | 'cyan' | 'slate';
  sublabel?: string;
  loading?: boolean;
  index?: number;
  suffix?: string;
  prefix?: string;
}>();

const store = useHospitalStore();
const displayValue = ref(0);

const accentClass: Record<string, string> = {
  teal:   'metric-accent-teal',
  green:  'metric-accent-green',
  red:    'metric-accent-red',
  amber:  'metric-accent-amber',
  blue:   'metric-accent-blue',
  purple: 'metric-accent-purple',
  cyan:   'metric-accent-cyan',
  slate:  'metric-accent-slate',
};
const iconBgClass: Record<string, string> = {
  teal:   'bg-teal-50 text-teal-600',
  green:  'bg-green-50 text-green-600',
  red:    'bg-red-50 text-red-600',
  amber:  'bg-amber-50 text-amber-600',
  blue:   'bg-blue-50 text-blue-600',
  purple: 'bg-purple-50 text-purple-600',
  cyan:   'bg-cyan-50 text-cyan-600',
  slate:  'bg-slate-100 text-slate-600',
};

const animateCount = () => {
  if (typeof props.value !== 'number') return;
  const duration = 1200;
  const start = Date.now();
  const target = props.value;
  const tick = () => {
    const elapsed = Date.now() - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    displayValue.value = Math.round(target * eased);
    if (progress < 1) requestAnimationFrame(tick);
    else displayValue.value = target;
  };
  requestAnimationFrame(tick);
};

onMounted(() => {
  if (!props.loading && typeof props.value === 'number') {
    setTimeout(() => animateCount(), (props.index ?? 0) * 60);
  }
});
watch(() => props.value, (v) => {
  if (typeof v === 'number') animateCount();
});

const variant = props.variant ?? 'teal';
const accent = accentClass[variant] || 'metric-accent-teal';
const iconBg = iconBgClass[variant] || 'bg-teal-50 text-teal-600';
</script>

<template>
  <!-- Loading Skeleton -->
  <div
    v-if="loading"
    class="h-card p-5 rounded-xl"
    :class="store.darkMode ? 'bg-[#111827] border-[#1E293B]' : 'bg-white border border-slate-200'"
  >
    <div class="flex items-start justify-between mb-3">
      <div class="skeleton w-9 h-9 rounded-lg"></div>
      <div class="skeleton w-12 h-4 rounded"></div>
    </div>
    <div class="skeleton w-20 h-8 rounded mb-2"></div>
    <div class="skeleton w-28 h-3.5 rounded"></div>
  </div>

  <!-- Actual Card -->
  <div
    v-else
    class="h-card p-5 rounded-xl cursor-default"
    :class="[accent, store.darkMode ? 'bg-[#111827] border-[#1E293B]' : '']"
    :style="`animation-delay: ${(index ?? 0) * 60}ms`"
  >
    <div class="flex items-start justify-between mb-3">
      <div class="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
        :class="store.darkMode ? iconBg.replace('bg-', 'bg-opacity-20 bg-') : iconBg">
        <component :is="icon" :size="18" :stroke-width="2" />
      </div>

      <!-- Trend -->
      <div v-if="trend !== undefined" class="flex items-center gap-1 text-2xs font-semibold">
        <TrendingUp v-if="trend > 0" :size="12" class="text-green-500" />
        <TrendingDown v-else-if="trend < 0" :size="12" class="text-red-500" />
        <Minus v-else :size="12" class="text-slate-400" />
        <span :class="trend > 0 ? 'text-green-600' : trend < 0 ? 'text-red-600' : 'text-slate-400'">
          {{ trend > 0 ? '+' : '' }}{{ trend }}%
        </span>
      </div>
    </div>

    <div class="space-y-0.5">
      <p class="text-2xl font-bold numeric tracking-tight leading-none"
        :class="store.darkMode ? 'text-white' : 'text-slate-900'">
        {{ prefix }}{{ typeof value === 'number' ? displayValue.toLocaleString() : value }}{{ suffix }}
      </p>
      <p class="text-xs font-medium" :class="store.darkMode ? 'text-slate-500' : 'text-slate-500'">
        {{ label }}
      </p>
      <p v-if="sublabel" class="text-2xs font-medium" :class="store.darkMode ? 'text-slate-600' : 'text-slate-400'">
        {{ sublabel }}
      </p>
      <p v-if="trendLabel" class="text-2xs" :class="store.darkMode ? 'text-slate-600' : 'text-slate-400'">
        {{ trendLabel }}
      </p>
    </div>
  </div>
</template>
