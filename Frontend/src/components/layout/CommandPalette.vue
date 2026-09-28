<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import {
  LayoutDashboard, Globe, Sparkles, ArrowRightLeft,
  AlertTriangle, Settings, Pill, Download, FileJson, X, Search
} from 'lucide-vue-next';
import { usePredictionResult } from '../../hooks/usePredictionResult';
import { useHospitalStore } from '../../stores/hospitalStore';
import { downloadJSON } from '../../lib/utils';
import gsap from 'gsap';

const props = defineProps<{ open: boolean }>();
const emit = defineEmits<{ (e: 'update:open', val: boolean): void }>();

const router = useRouter();
const store = useHospitalStore();
const query = ref('');
const activeIndex = ref(0);
const inputRef = ref<HTMLInputElement | null>(null);

const { data: result } = usePredictionResult();

const close = () => {
  emit('update:open', false);
};

const groups = computed(() => [
  {
    label: 'Navigation',
    items: [
      { id: 'nav-map', label: 'BRICS Operations Map', icon: Globe, action: () => { router.push('/map'); close(); }, shortcut: 'M' },
      { id: 'nav-dashboard', label: 'Hospital Dashboard', icon: LayoutDashboard, action: () => { router.push('/dashboard'); close(); }, shortcut: 'D' },
      { id: 'nav-results', label: 'Healthcare AI Analysis', icon: Sparkles, action: () => { router.push('/results'); close(); }, shortcut: 'R' },
      { id: 'nav-portal', label: 'PHC Community Portal', icon: ArrowRightLeft, action: () => { router.push('/phc-portal'); close(); }, shortcut: 'P' },
      { id: 'nav-emergency', label: 'Emergency Center', icon: AlertTriangle, action: () => { router.push('/emergency'); close(); }, shortcut: 'E' },
      { id: 'nav-pharmacy', label: 'Pharmacy & Stock', icon: Pill, action: () => { router.push('/pharmacy'); close(); }, shortcut: 'I' },
      { id: 'nav-settings', label: 'System Settings', icon: Settings, action: () => { router.push('/settings'); close(); }, shortcut: 'S' },
    ],
  },
  {
    label: 'Actions & Utilities',
    items: [
      {
        id: 'toggle-theme', label: store.darkMode ? 'Switch to Light Theme' : 'Switch to Dark Theme', icon: Settings,
        action: () => { store.toggleDarkMode(); close(); }, shortcut: 'T'
      },
      {
        id: 'download-json', label: 'Download Predictions & Data JSON', icon: Download,
        action: () => {
          if (result.value) { downloadJSON(result.value, 'brics-result.json'); }
          close();
        },
      },
      {
        id: 'view-raw', label: 'Inspect Raw System Telemetry', icon: FileJson,
        action: () => { router.push('/results?tab=raw'); close(); },
      },
    ],
  },
]);

const filteredGroups = computed(() => {
  if (!query.value.trim()) return groups.value;
  return groups.value
    .map(g => ({ ...g, items: g.items.filter(i => i.label.toLowerCase().includes(query.value.toLowerCase())) }))
    .filter(g => g.items.length > 0);
});

const flatItems = computed(() => filteredGroups.value.flatMap(g => g.items));

watch(() => props.open, (newVal) => {
  if (newVal) {
    query.value = '';
    activeIndex.value = 0;
    nextTick(() => {
      setTimeout(() => inputRef.value?.focus(), 50);
    });
  }
});

watch(query, () => {
  activeIndex.value = 0;
});

const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'ArrowDown') { e.preventDefault(); activeIndex.value = Math.min(activeIndex.value + 1, flatItems.value.length - 1); }
  if (e.key === 'ArrowUp') { e.preventDefault(); activeIndex.value = Math.max(activeIndex.value - 1, 0); }
  if (e.key === 'Enter') { e.preventDefault(); flatItems.value[activeIndex.value]?.action(); }
  if (e.key === 'Escape') { close(); }
};

// Transition hooks for GSAP
const onEnter = (el: Element, done: () => void) => {
  gsap.fromTo(el, { opacity: 0, scale: 0.97, y: -8 }, { opacity: 1, scale: 1, y: 0, duration: 0.18, ease: "power2.out", onComplete: done });
};
const onLeave = (el: Element, done: () => void) => {
  gsap.to(el, { opacity: 0, scale: 0.97, y: -8, duration: 0.15, ease: "power2.in", onComplete: done });
};
const onBackdropEnter = (el: Element, done: () => void) => {
  gsap.fromTo(el, { opacity: 0 }, { opacity: 1, duration: 0.15, onComplete: done });
};
const onBackdropLeave = (el: Element, done: () => void) => {
  gsap.to(el, { opacity: 0, duration: 0.15, onComplete: done });
};
</script>

<template>
  <teleport to="body">
    <transition @enter="onBackdropEnter" @leave="onBackdropLeave" :css="false">
      <div v-if="open" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm z-50" @click="close"></div>
    </transition>

    <transition @enter="onEnter" @leave="onLeave" :css="false">
      <div
        v-if="open"
        class="fixed top-[15%] left-1/2 -translate-x-1/2 w-full max-w-lg z-50 px-4"
        @keydown="handleKeyDown"
      >
        <div
          class="border rounded-2xl shadow-2xl overflow-hidden transition-colors"
          :class="store.darkMode ? 'bg-[#111827] border-[#1E293B]' : 'bg-white border-slate-200'"
        >
          <!-- Search input -->
          <div class="flex items-center gap-3 px-4 py-3.5 border-b"
            :class="store.darkMode ? 'border-[#1E293B]' : 'border-slate-100'">
            <Search :size="16" class="text-teal-500 flex-shrink-0" />
            <input
              ref="inputRef"
              v-model="query"
              placeholder="Search facilities, screens, or commands..."
              class="flex-1 text-sm outline-none placeholder:text-slate-400 bg-transparent"
              :class="store.darkMode ? 'text-white' : 'text-slate-800'"
            />
            <button @click="close" class="p-1 rounded text-slate-400 hover:text-slate-600 transition-colors">
              <X :size="15" />
            </button>
          </div>

          <!-- Commands list -->
          <div class="max-h-80 overflow-y-auto py-2">
            <template v-if="filteredGroups.length === 0">
              <p class="text-center text-xs py-8" :class="store.darkMode ? 'text-slate-500' : 'text-slate-400'">No matching commands found</p>
            </template>
            <template v-else>
              <div v-for="(group) in filteredGroups" :key="group.label">
                <p class="px-4 py-1.5 text-2xs font-bold uppercase tracking-wider"
                  :class="store.darkMode ? 'text-slate-500' : 'text-slate-400'">{{ group.label }}</p>
                <button
                  v-for="(item) in group.items"
                  :key="item.id"
                  @click="item.action"
                  @mouseenter="activeIndex = flatItems.findIndex(i => i.id === item.id)"
                  class="w-full flex items-center gap-3 px-4 py-2.5 text-xs text-left transition-colors"
                  :class="activeIndex === flatItems.findIndex(i => i.id === item.id)
                    ? (store.darkMode ? 'bg-teal-950/40 text-teal-300' : 'bg-teal-50 text-teal-700')
                    : (store.darkMode ? 'text-slate-300 hover:bg-[#1E293B]' : 'text-slate-700 hover:bg-slate-50')"
                >
                  <component
                    :is="item.icon"
                    :size="15"
                    class="flex-shrink-0"
                    :class="activeIndex === flatItems.findIndex(i => i.id === item.id) ? 'text-teal-500' : 'text-slate-400'"
                  />
                  <span class="flex-1 font-medium">{{ item.label }}</span>
                  <kbd v-if="'shortcut' in item" class="text-2xs font-mono px-1.5 py-0.5 rounded border"
                    :class="store.darkMode ? 'bg-[#1E293B] border-[#334155] text-slate-400' : 'bg-slate-100 border-slate-200 text-slate-500'">
                    {{ (item as any).shortcut }}
                  </kbd>
                </button>
              </div>
            </template>
          </div>

          <!-- Footer hints -->
          <div class="border-t px-4 py-2.5 flex items-center justify-between text-2xs"
            :class="store.darkMode ? 'border-[#1E293B] text-slate-500' : 'border-slate-100 text-slate-400'">
            <div class="flex items-center gap-3">
              <span><kbd class="font-mono font-semibold">↑↓</kbd> navigate</span>
              <span><kbd class="font-mono font-semibold">↵</kbd> execute</span>
              <span><kbd class="font-mono font-semibold">Esc</kbd> close</span>
            </div>
            <span class="font-medium text-teal-600 dark:text-teal-400">Ctrl + K</span>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>
