<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { Activity, X, Server, Database, Activity as ActivityPulse, CheckCircle2, AlertTriangle, AlertCircle } from 'lucide-vue-next';
import { useAPIHealth } from '../../hooks/useAPIHealth';
import gsap from 'gsap';

const props = defineProps<{
  open: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:open', val: boolean): void;
}>();

const { data: health, isLoading, isError } = useAPIHealth();

const close = () => {
  emit('update:open', false);
};

const onEnter = (el: Element, done: () => void) => {
  gsap.fromTo(el, { opacity: 0, scale: 0.95, y: 20 }, { opacity: 1, scale: 1, y: 0, duration: 0.3, ease: 'power3.out', onComplete: done });
};
const onLeave = (el: Element, done: () => void) => {
  gsap.to(el, { opacity: 0, scale: 0.95, y: 20, duration: 0.2, ease: 'power3.in', onComplete: done });
};
</script>

<template>
  <transition
    @enter="onEnter"
    @leave="onLeave"
    :css="false"
  >
    <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" @click="close"></div>
      
      <div class="relative w-full max-w-lg bg-white rounded-2xl shadow-2xl overflow-hidden border border-slate-200">
        <div class="flex items-center justify-between px-5 py-4 border-b border-slate-100 bg-slate-50/80">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-lg bg-teal-100 text-teal-700 flex items-center justify-center shadow-xs">
              <Activity :size="16" />
            </div>
            <div>
              <h3 class="text-sm font-bold text-slate-800">System Telemetry</h3>
              <p class="text-2xs font-mono text-slate-500">Node Status & Health</p>
            </div>
          </div>
          <button @click="close" class="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200 transition-colors">
            <X :size="16" />
          </button>
        </div>

        <div class="p-6 space-y-6">
          <div v-if="isLoading" class="flex justify-center py-8">
            <ActivityPulse :size="24" class="text-teal-600 animate-spin" />
          </div>
          <div v-else-if="isError" class="flex flex-col items-center py-6 text-center">
            <AlertCircle :size="32" class="text-red-500 mb-2" />
            <p class="text-sm font-bold text-slate-800">Telemetry Disconnected</p>
            <p class="text-xs text-slate-500 mt-1">Unable to reach BRICS backend cluster.</p>
          </div>
          <div v-else class="space-y-4">
            <div class="grid grid-cols-2 gap-3">
              <div class="bg-slate-50 border border-slate-100 rounded-xl p-4">
                <div class="flex items-center gap-2 mb-2">
                  <Server :size="14" class="text-slate-400" />
                  <span class="text-xs font-semibold text-slate-600">API Gateway</span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                  <span class="text-sm font-bold text-slate-800">{{ health?.status === 'ok' ? 'Online' : 'Degraded' }}</span>
                </div>
              </div>
              <div class="bg-slate-50 border border-slate-100 rounded-xl p-4">
                <div class="flex items-center gap-2 mb-2">
                  <Database :size="14" class="text-slate-400" />
                  <span class="text-xs font-semibold text-slate-600">Latency</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <span class="text-sm font-bold font-mono text-slate-800">142</span>
                  <span class="text-xs text-slate-500">ms</span>
                </div>
              </div>
            </div>

            <div class="bg-teal-50/50 border border-teal-100 rounded-xl p-4">
              <h4 class="text-xs font-bold text-teal-800 mb-3 uppercase tracking-wider">Node Details</h4>
              <div class="space-y-2.5">
                <div class="flex justify-between items-center text-xs">
                  <span class="text-slate-500 font-medium">Version</span>
                  <span class="font-mono text-slate-700 bg-white px-2 py-0.5 rounded border border-slate-200">{{ health?.version || 'v2.4.1' }}</span>
                </div>
                <div class="flex justify-between items-center text-xs">
                  <span class="text-slate-500 font-medium">Environment</span>
                  <span class="font-mono text-slate-700 bg-white px-2 py-0.5 rounded border border-slate-200">production</span>
                </div>
                <div class="flex justify-between items-center text-xs">
                  <span class="text-slate-500 font-medium">Uptime</span>
                  <span class="font-mono text-slate-700 bg-white px-2 py-0.5 rounded border border-slate-200">99.98%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>
