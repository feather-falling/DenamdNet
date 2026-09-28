<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { Search, Menu, Sparkles, Clock } from 'lucide-vue-next';
import { useAPIHealth } from '../../hooks/useAPIHealth';

const PAGE_META: Record<string, { title: string; subtitle: string }> = {
  '/overview': { title: 'Overview', subtitle: 'Executive network summary and status' },
  '/prediction': { title: 'AI Prediction', subtitle: 'Upload input and run the ML pipeline' },
  '/results': { title: 'Results', subtitle: 'Prediction output, analytics, and data exploration' },
  '/network': { title: 'PHC Network', subtitle: 'Interactive primary health center map' },
  '/settings': { title: 'Settings', subtitle: 'System configuration' },
};

defineProps<{
  hasSimulator?: boolean;
}>();

const emit = defineEmits<{
  (e: 'menuClick'): void;
  (e: 'commandPalette'): void;
  (e: 'simulatorClick'): void;
  (e: 'telemetryClick'): void;
}>();

const route = useRoute();
const { data: health } = useAPIHealth();

const meta = computed(() => PAGE_META[route.path] ?? { title: 'BRICS Health Resilience', subtitle: '' });

const time = ref('');

onMounted(() => {
  const updateTime = () => {
    const now = new Date();
    time.value = now.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };
  updateTime();
  const interval = setInterval(updateTime, 1000);
  onUnmounted(() => clearInterval(interval));
});
</script>

<template>
  <header class="h-14 bg-white border-b border-slate-100 flex items-center px-4 gap-3 sm:gap-4 flex-shrink-0">
    <!-- Mobile menu -->
    <button
      @click="emit('menuClick')"
      class="lg:hidden p-1.5 rounded-md text-slate-500 hover:bg-slate-50 hover:text-slate-700"
      aria-label="Open menu"
    >
      <Menu :size="18" />
    </button>

    <!-- Page title -->
    <div class="flex-1 min-w-0">
      <h2 class="text-sm font-semibold text-slate-800 truncate">{{ meta.title }}</h2>
      <p class="text-xs text-slate-400 truncate hidden sm:block">{{ meta.subtitle }}</p>
    </div>

    <!-- System Live Clock -->
    <div class="hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-50 border border-slate-100 text-slate-500 font-mono text-2xs">
      <Clock :size="12" class="text-slate-400" />
      <span>{{ time || '--:--:--' }} UTC</span>
    </div>

    <!-- Stress Simulator Button -->
    <button
      v-if="hasSimulator"
      @click="emit('simulatorClick')"
      class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md bg-gradient-to-r from-teal-50 to-emerald-50 hover:from-teal-100 hover:to-emerald-100 text-teal-800 border border-teal-200/80 text-xs font-semibold shadow-2xs hover:shadow-xs transition-all"
      title="Simulate health crisis stress test scenarios"
    >
      <Sparkles :size="13" class="text-teal-600 animate-pulse" />
      <span class="hidden sm:inline">Stress Simulator</span>
      <span class="text-3xs bg-teal-600 text-white font-bold px-1.5 py-0.2 rounded-full uppercase">
        Test
      </span>
    </button>

    <!-- Search / Command -->
    <button
      @click="emit('commandPalette')"
      class="flex items-center gap-2 px-3 py-1.5 rounded-md border border-slate-200 text-xs text-slate-400 bg-slate-50 hover:bg-white hover:border-slate-300 transition-colors duration-150 hidden md:flex"
      aria-label="Open command palette"
    >
      <Search :size="13" />
      <span>Search...</span>
      <kbd class="ml-1.5 px-1.5 py-0.5 text-2xs font-mono bg-white border border-slate-200 rounded text-slate-400">
        Ctrl K
      </kbd>
    </button>

    <!-- Connection indicator -> Clickable for Telemetry -->
    <button
      @click="emit('telemetryClick')"
      class="flex items-center gap-2 px-2.5 py-1.5 rounded-md hover:bg-slate-50 border border-transparent hover:border-slate-200 transition-colors flex-shrink-0 cursor-pointer"
      title="Click to view live network telemetry & diagnostics"
    >
      <div class="relative flex items-center justify-center">
        <span
          class="w-2 h-2 rounded-full"
          :class="health?.connected ? 'bg-emerald-500' : 'bg-red-400'"
        ></span>
        <span
          v-if="health?.connected"
          class="absolute w-3.5 h-3.5 rounded-full bg-emerald-400/40 animate-ping"
        ></span>
      </div>
      <span class="text-xs text-slate-500 font-medium hidden sm:block">
        {{ health?.connected ? `${health.latency_ms ?? 24}ms` : 'Disconnected' }}
      </span>
    </button>
  </header>
</template>
