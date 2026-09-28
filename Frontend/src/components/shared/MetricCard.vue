<script setup lang="ts">
import { computed } from 'vue';
import { formatNumber } from '../../lib/utils';
import AnimatedCounter from './AnimatedCounter.vue';

const props = withDefaults(defineProps<{
  label: string;
  value?: number | string | null;
  subvalue?: string;
  icon?: any;
  trend?: 'up' | 'down' | 'neutral';
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  loading?: boolean;
  format?: 'number' | 'string' | 'percent';
  index?: number;
}>(), {
  variant: 'default',
  loading: false,
  format: 'number',
  index: 0,
});

const variantStyles = {
  default: {
    card: 'border-slate-200/80 hover:border-slate-300',
    accent: 'bg-teal-500',
    icon: 'bg-teal-50 text-teal-600',
    label: 'text-slate-500',
    glow: 'group-hover:bg-teal-500/5',
  },
  success: {
    card: 'border-green-200/80 hover:border-green-300',
    accent: 'bg-green-500',
    icon: 'bg-green-50 text-green-600',
    label: 'text-green-700',
    glow: 'group-hover:bg-green-500/5',
  },
  warning: {
    card: 'border-amber-200/80 hover:border-amber-300',
    accent: 'bg-amber-500',
    icon: 'bg-amber-50 text-amber-600',
    label: 'text-amber-700',
    glow: 'group-hover:bg-amber-500/5',
  },
  danger: {
    card: 'border-red-200/80 hover:border-red-300',
    accent: 'bg-red-500',
    icon: 'bg-red-50 text-red-600',
    label: 'text-red-700',
    glow: 'group-hover:bg-red-500/5',
  },
  info: {
    card: 'border-blue-200/80 hover:border-blue-300',
    accent: 'bg-blue-500',
    icon: 'bg-blue-50 text-blue-600',
    label: 'text-blue-700',
    glow: 'group-hover:bg-blue-500/5',
  },
};

const styles = computed(() => variantStyles[props.variant]);
const isNumeric = computed(() => typeof props.value === 'number');

const vSlideIn = {
  mounted: (el: Element, binding: any) => {
    import('gsap').then(({ default: gsap }) => {
      gsap.fromTo(el, 
        { opacity: 0, y: 12 },
        { 
          opacity: 1, 
          y: 0, 
          delay: (binding.value ?? 0) * 0.05,
          duration: 0.35, 
          ease: "power2.out" 
        }
      );
      
      el.addEventListener('mouseenter', () => {
        gsap.to(el, { y: -3, duration: 0.18, ease: "power2.out" });
      });
      el.addEventListener('mouseleave', () => {
        gsap.to(el, { y: 0, duration: 0.18, ease: "power2.out" });
      });
    });
  }
};
</script>

<template>
  <div v-if="loading" class="bg-white border rounded-xl p-4 shadow-card" :class="styles.card">
    <div class="flex items-center justify-between mb-3">
      <div class="skeleton w-24 h-3.5 rounded"></div>
      <div class="skeleton w-8 h-8 rounded-lg"></div>
    </div>
    <div class="skeleton w-20 h-7 rounded mb-1.5"></div>
    <div class="skeleton w-16 h-3 rounded"></div>
  </div>

  <div
    v-else
    v-slide-in="index"
    class="group relative bg-white border rounded-xl p-4.5 shadow-card hover:shadow-card-hover transition-all duration-200 cursor-default overflow-hidden"
    :class="styles.card"
  >
    <!-- Top micro accent bar -->
    <div class="absolute top-0 left-0 right-0 h-1 transition-transform origin-left group-hover:scale-x-105" :class="styles.accent"></div>

    <!-- Subtle hover gradient background -->
    <div class="absolute inset-0 pointer-events-none transition-colors duration-300" :class="styles.glow"></div>

    <div class="relative z-10">
      <div class="flex items-center justify-between mb-3">
        <span class="text-xs font-semibold uppercase tracking-wider" :class="styles.label">
          {{ label }}
        </span>
        <div v-if="icon" class="w-8 h-8 rounded-lg flex items-center justify-center transition-transform shadow-xs hover:rotate-6 hover:scale-110" :class="styles.icon">
          <component :is="icon" :size="16" :stroke-width="2.2" />
        </div>
      </div>

      <div class="flex items-baseline gap-2">
        <template v-if="isNumeric">
          <span class="text-2xl font-extrabold text-slate-800 numeric tracking-tight">
            <AnimatedCounter v-if="format === 'percent'" :value="(value as number) * 100" :decimals="1" suffix="%" :duration="1.1" />
            <AnimatedCounter v-else-if="format === 'number'" :value="value as number" :duration="1.1" />
            <template v-else>{{ formatNumber(value as number) }}</template>
          </span>
        </template>
        <template v-else>
          <span class="text-2xl font-extrabold text-slate-800 leading-none">
            {{ value !== undefined && value !== null ? String(value) : '—' }}
          </span>
        </template>
      </div>

      <p v-if="subvalue" class="mt-1 text-xs text-slate-400 font-medium">{{ subvalue }}</p>
    </div>
  </div>
</template>
