<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { AlertTriangle, ArrowRightLeft, Activity, ChevronLeft, ChevronRight, Pause, Play, X, Radio, ExternalLink } from 'lucide-vue-next';
import gsap from 'gsap';

interface AlertItem {
  id: string;
  type: 'critical' | 'transfer' | 'ml' | 'sync';
  severity: 'high' | 'medium' | 'info';
  title: string;
  message: string;
  actionText?: string;
  actionRoute?: string;
  timestamp: string;
}

const LIVE_ALERTS: AlertItem[] = [
  {
    id: 'alt-1',
    type: 'critical',
    severity: 'high',
    title: 'CRITICAL SHORTAGE',
    message: 'PHC-IN-002 (Visakhapatnam) Amoxicillin stockout risk in 1.6 days (45 units left)',
    actionText: 'View PHC',
    actionRoute: '/network?phc=IN-AP-VSK-MVP-002',
    timestamp: 'Just now',
  },
  {
    id: 'alt-2',
    type: 'transfer',
    severity: 'medium',
    title: 'DYNAMIC REDISTRIBUTION',
    message: '200 units Oral Rehydration Salts dispatched: MVP-001 (Surplus) ➔ MVP-002 (Deficit)',
    actionText: 'Track Transfer',
    actionRoute: '/results?tab=transfers',
    timestamp: '3m ago',
  },
  {
    id: 'alt-3',
    type: 'ml',
    severity: 'medium',
    title: 'EPIDEMIC SURGE WARNING',
    message: 'Seasonal fever anomaly flagged across 4 coastal PHCs (+28% antibiotic demand forecast)',
    actionText: 'Review Model',
    actionRoute: '/results?tab=analytics',
    timestamp: '7m ago',
  },
  {
    id: 'alt-4',
    type: 'sync',
    severity: 'info',
    title: 'TELEMETRY CONSENSUS',
    message: '24 BRICS nodes connected across 5 nations · Model Latency 142ms · Zero schema drift',
    actionText: 'Network Map',
    actionRoute: '/network',
    timestamp: '12m ago',
  },
];

const router = useRouter();
const currentIndex = ref(0);
const isPaused = ref(false);
const isDismissed = ref(false);

const currentAlert = computed(() => LIVE_ALERTS[currentIndex.value]);

const badgeConfig = computed(() => {
  const config = {
    high: { bg: 'bg-red-500/15 border-red-500/30 text-red-400', icon: AlertTriangle },
    medium: { bg: 'bg-amber-500/15 border-amber-500/30 text-amber-300', icon: ArrowRightLeft },
    info: { bg: 'bg-teal-500/15 border-teal-500/30 text-teal-300', icon: Activity },
  };
  return config[currentAlert.value.severity];
});

let interval: ReturnType<typeof setInterval>;

const startInterval = () => {
  clearInterval(interval);
  interval = setInterval(() => {
    if (!isPaused.value && !isDismissed.value) {
      currentIndex.value = (currentIndex.value + 1) % LIVE_ALERTS.length;
    }
  }, 6000);
};

onMounted(() => {
  startInterval();
});

onUnmounted(() => {
  clearInterval(interval);
});

const nextAlert = () => { currentIndex.value = (currentIndex.value + 1) % LIVE_ALERTS.length; };
const prevAlert = () => { currentIndex.value = (currentIndex.value - 1 + LIVE_ALERTS.length) % LIVE_ALERTS.length; };

const onEnter = (el: Element, done: () => void) => {
  gsap.fromTo(el, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.25, ease: "power2.out", onComplete: done });
};
const onLeave = (el: Element, done: () => void) => {
  gsap.to(el, { opacity: 0, y: -12, duration: 0.25, ease: "power2.in", onComplete: done });
};

</script>

<template>
  <div v-if="isDismissed" class="bg-slate-900 border-b border-slate-800 px-4 py-1.5 flex items-center justify-between text-2xs text-slate-400">
    <div class="flex items-center gap-2">
      <span class="w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse"></span>
      <span>Live Sentinel Monitoring Active ({{ LIVE_ALERTS.length }} operational advisories)</span>
    </div>
    <button @click="isDismissed = false" class="text-teal-400 hover:text-teal-300 font-medium underline underline-offset-2">
      Expand Ticker
    </button>
  </div>
  
  <div
    v-else
    class="bg-slate-950 text-slate-200 border-b border-slate-800/80 px-3 sm:px-4 py-2 flex items-center justify-between gap-3 text-xs overflow-hidden relative"
    @mouseenter="isPaused = true"
    @mouseleave="isPaused = false"
  >
    <div class="absolute inset-0 bg-gradient-to-r from-teal-950/20 via-transparent to-teal-950/20 pointer-events-none"></div>

    <div class="flex items-center gap-2.5 flex-shrink-0 z-10">
      <div class="relative flex items-center justify-center">
        <span class="w-2 h-2 rounded-full bg-teal-400"></span>
        <span class="absolute w-4 h-4 rounded-full bg-teal-400/40 animate-ping"></span>
      </div>
      <div class="flex items-center gap-1.5 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded text-2xs font-bold tracking-wider text-teal-400 uppercase">
        <Radio :size="10" class="animate-pulse" />
        <span>OPS SENTINEL</span>
      </div>
    </div>

    <div class="flex-1 min-w-0 flex items-center justify-start overflow-hidden z-10 relative h-6">
      <transition
        mode="out-in"
        @enter="onEnter"
        @leave="onLeave"
        :css="false"
      >
        <div :key="currentAlert.id" class="absolute flex items-center gap-2 truncate">
          <span
            class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-2xs font-semibold uppercase tracking-wider border"
            :class="badgeConfig.bg"
          >
            <component :is="badgeConfig.icon" :size="10" />
            {{ currentAlert.title }}
          </span>
          <span class="text-slate-300 font-medium truncate">{{ currentAlert.message }}</span>
          <span class="text-slate-500 text-2xs hidden md:inline">· {{ currentAlert.timestamp }}</span>
          <button
            v-if="currentAlert.actionRoute"
            @click="router.push(currentAlert.actionRoute)"
            class="inline-flex items-center gap-1 text-2xs font-semibold text-teal-400 hover:text-teal-300 underline underline-offset-2 ml-1"
          >
            <span>{{ currentAlert.actionText ?? 'View' }}</span>
            <ExternalLink :size="10" />
          </button>
        </div>
      </transition>
    </div>

    <div class="flex items-center gap-1 flex-shrink-0 z-10 text-slate-400">
      <span class="text-2xs font-mono text-slate-500 mr-1 hidden sm:inline">
        {{ currentIndex + 1 }}/{{ LIVE_ALERTS.length }}
      </span>
      <button @click="prevAlert" class="p-1 rounded hover:bg-slate-800 hover:text-white transition-colors" title="Previous Advisory">
        <ChevronLeft :size="13" />
      </button>
      <button @click="isPaused = !isPaused" class="p-1 rounded hover:bg-slate-800 hover:text-white transition-colors" :title="isPaused ? 'Resume Rotation' : 'Pause'">
        <Play v-if="isPaused" :size="11" class="text-teal-400" />
        <Pause v-else :size="11" />
      </button>
      <button @click="nextAlert" class="p-1 rounded hover:bg-slate-800 hover:text-white transition-colors" title="Next Advisory">
        <ChevronRight :size="13" />
      </button>
      <div class="w-px h-3 bg-slate-800 mx-1"></div>
      <button @click="isDismissed = true" class="p-1 rounded hover:bg-slate-800 hover:text-slate-200 transition-colors" title="Minimize Ticker">
        <X :size="13" />
      </button>
    </div>
  </div>
</template>
