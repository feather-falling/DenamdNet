<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { Sparkles, X, Activity, Zap, ShieldAlert, ArrowRight } from 'lucide-vue-next';
import gsap from 'gsap';

const props = defineProps<{
  open: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:open', val: boolean): void;
}>();

const router = useRouter();

const scenarios = [
  { id: 'cyclone', name: 'Coastal Cyclone Surge', desc: 'Simulates a Category 4 cyclone hitting the eastern seaboard, spiking demand for antibiotics and trauma supplies.', icon: ShieldAlert, color: 'text-amber-500', bg: 'bg-amber-100' },
  { id: 'vaccine', name: 'Mass Immunization Drive', desc: 'Stresses cold-chain logistics across all regions simultaneously for a sudden pediatric vaccine rollout.', icon: Zap, color: 'text-blue-500', bg: 'bg-blue-100' },
  { id: 'supply_chain', name: 'Global Supply Disruption', desc: 'Models a 40% reduction in incoming coastal freight, forcing reliance on existing inland buffers.', icon: Activity, color: 'text-red-500', bg: 'bg-red-100' },
];

const selected = ref(scenarios[0].id);
const simulating = ref(false);

const close = () => {
  if (simulating.value) return;
  emit('update:open', false);
};

const runSimulation = () => {
  simulating.value = true;
  setTimeout(() => {
    simulating.value = false;
    emit('update:open', false);
    router.push('/results?tab=analytics');
  }, 2500);
};

const onEnter = (el: Element, done: () => void) => {
  gsap.fromTo(el, { opacity: 0, scale: 0.95, y: 20 }, { opacity: 1, scale: 1, y: 0, duration: 0.3, ease: 'power3.out', onComplete: done });
};
const onLeave = (el: Element, done: () => void) => {
  gsap.to(el, { opacity: 0, scale: 0.95, y: 20, duration: 0.2, ease: 'power3.in', onComplete: done });
};
</script>

<template>
  <transition @enter="onEnter" @leave="onLeave" :css="false">
    <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" @click="close"></div>
      
      <div class="relative w-full max-w-2xl bg-white rounded-2xl shadow-2xl overflow-hidden border border-slate-200">
        <div class="flex items-center justify-between px-6 py-5 border-b border-slate-100 bg-slate-50">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-teal-100 text-teal-700 flex items-center justify-center shadow-xs">
              <Sparkles :size="20" class="animate-pulse" />
            </div>
            <div>
              <h3 class="text-base font-bold text-slate-800 tracking-tight">Scenario Simulator</h3>
              <p class="text-xs text-slate-500">Test AI resilience against high-impact crises</p>
            </div>
          </div>
          <button :disabled="simulating" @click="close" class="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200 transition-colors disabled:opacity-50">
            <X :size="18" />
          </button>
        </div>

        <div class="p-6">
          <div v-if="simulating" class="py-12 flex flex-col items-center text-center space-y-4">
            <Sparkles :size="40" class="text-teal-600 animate-spin" />
            <div>
              <h4 class="text-lg font-bold text-slate-800">Injecting Stress Vectors...</h4>
              <p class="text-sm text-slate-500">Running XGBoost distributed inference</p>
            </div>
            <div class="w-64 h-2 bg-slate-100 rounded-full overflow-hidden mt-4">
              <div class="h-full bg-teal-500 rounded-full w-full animate-[progress_2.5s_ease-in-out]"></div>
            </div>
          </div>
          <div v-else class="space-y-4">
            <h4 class="text-sm font-bold text-slate-700 mb-2 uppercase tracking-wider">Select Scenario Vector</h4>
            <div class="space-y-3">
              <button
                v-for="s in scenarios"
                :key="s.id"
                @click="selected = s.id"
                class="w-full flex items-start gap-4 p-4 rounded-xl border text-left transition-all"
                :class="selected === s.id ? 'border-teal-500 bg-teal-50/50 shadow-md ring-1 ring-teal-500/20' : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'"
              >
                <div class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" :class="[s.bg, s.color]">
                  <component :is="s.icon" :size="20" />
                </div>
                <div>
                  <h5 class="text-sm font-bold text-slate-800">{{ s.name }}</h5>
                  <p class="text-xs text-slate-500 mt-1 leading-relaxed">{{ s.desc }}</p>
                </div>
                <div class="ml-auto flex items-center">
                  <div class="w-5 h-5 rounded-full border-2 flex items-center justify-center" :class="selected === s.id ? 'border-teal-500 bg-teal-500' : 'border-slate-300'">
                    <div v-if="selected === s.id" class="w-2 h-2 rounded-full bg-white"></div>
                  </div>
                </div>
              </button>
            </div>
            <div class="pt-6 border-t border-slate-100 flex justify-end gap-3">
              <button @click="close" class="px-5 py-2.5 text-sm font-semibold text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded-xl transition-colors">
                Cancel
              </button>
              <button @click="runSimulation" class="flex items-center gap-2 px-6 py-2.5 text-sm font-bold text-white bg-teal-600 hover:bg-teal-700 rounded-xl shadow-md hover:shadow-teal-500/30 transition-all">
                <span>Run Scenario</span>
                <ArrowRight :size="16" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<style>
@keyframes progress {
  0% { width: 0%; }
  100% { width: 100%; }
}
</style>
