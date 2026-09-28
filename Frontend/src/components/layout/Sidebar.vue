<script setup lang="ts">
import { LayoutDashboard, Brain, BarChart3, MapPin, Settings, ChevronLeft, ChevronRight, ShieldCheck } from 'lucide-vue-next';
import { useAPIHealth } from '../../hooks/useAPIHealth';

defineProps<{
  collapsed: boolean;
}>();

const emit = defineEmits<{
  (e: 'toggle'): void;
}>();

const { data: health } = useAPIHealth();

const NAV_ITEMS = [
  { path: '/overview', label: 'Overview', icon: LayoutDashboard },
  { path: '/prediction', label: 'AI Prediction', icon: Brain },
  { path: '/results', label: 'Results', icon: BarChart3 },
  { path: '/network', label: 'PHC Network', icon: MapPin },
];

const BOTTOM_ITEMS = [
  { path: '/settings', label: 'Settings', icon: Settings },
];
</script>

<template>
  <aside
    class="flex flex-col h-full bg-white border-r border-slate-100 transition-all duration-300 ease-in-out"
    :class="collapsed ? 'w-16' : 'w-60'"
    aria-label="Main navigation"
  >
    <!-- Logo -->
    <div
      class="flex items-center h-14 border-b border-slate-100 flex-shrink-0 px-4 gap-3"
      :class="collapsed && 'justify-center px-0'"
    >
      <div class="w-8 h-8 flex-shrink-0 bg-teal-600 rounded-lg flex items-center justify-center">
        <ShieldCheck :size="16" class="text-white" :stroke-width="2.5" />
      </div>
      <div v-if="!collapsed" class="min-w-0">
        <p class="text-sm font-bold text-slate-800 tracking-tight leading-none">BRICS</p>
        <p class="text-2xs text-teal-600 font-semibold tracking-widest uppercase leading-none mt-0.5">Health Resilience</p>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 overflow-y-auto py-3 px-2">
      <ul class="space-y-0.5">
        <li v-for="item in NAV_ITEMS" :key="item.path">
          <router-link
            :to="item.path"
            v-slot="{ isActive, href, navigate }"
            custom
          >
            <a
              :href="href"
              @click="navigate"
              class="flex items-center gap-3 px-2.5 py-2 rounded-md text-sm font-medium transition-colors duration-100 group"
              :class="[
                collapsed && 'justify-center px-2',
                isActive
                  ? 'bg-teal-50 text-teal-700'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-800'
              ]"
              :title="collapsed ? item.label : undefined"
            >
              <component
                :is="item.icon"
                :size="17"
                :stroke-width="isActive ? 2.5 : 2"
                class="flex-shrink-0"
                :class="isActive ? 'text-teal-700' : 'text-slate-400 group-hover:text-slate-600'"
              />
              <span v-if="!collapsed" class="truncate">{{ item.label }}</span>
              <span
                v-if="!collapsed && isActive"
                class="ml-auto w-1.5 h-1.5 rounded-full bg-teal-500 flex-shrink-0"
              ></span>
            </a>
          </router-link>
        </li>
      </ul>
    </nav>

    <!-- Bottom -->
    <div class="px-2 pb-3 border-t border-slate-100 pt-3 space-y-1">
      <!-- Connection status -->
      <div
        class="flex items-center gap-2 px-2.5 py-2 rounded-md"
        :class="collapsed && 'justify-center'"
      >
        <span
          class="w-2 h-2 rounded-full flex-shrink-0"
          :class="health?.connected ? 'bg-green-500' : 'bg-red-400'"
        ></span>
        <span v-if="!collapsed" class="text-xs text-slate-400">
          {{ health?.connected ? 'Backend Connected' : 'Backend Unavailable' }}
        </span>
      </div>

      <router-link
        v-for="item in BOTTOM_ITEMS"
        :key="item.path"
        :to="item.path"
        v-slot="{ isActive, href, navigate }"
        custom
      >
        <a
          :href="href"
          @click="navigate"
          class="flex items-center gap-3 px-2.5 py-2 rounded-md text-sm font-medium transition-colors duration-100"
          :class="[
            collapsed && 'justify-center px-2',
            isActive
              ? 'bg-teal-50 text-teal-700'
              : 'text-slate-500 hover:bg-slate-50 hover:text-slate-700'
          ]"
          :title="collapsed ? item.label : undefined"
        >
          <component :is="item.icon" :size="17" :stroke-width="2" class="flex-shrink-0 text-slate-400" />
          <span v-if="!collapsed">{{ item.label }}</span>
        </a>
      </router-link>
    </div>

    <!-- Collapse toggle -->
    <button
      @click="emit('toggle')"
      class="flex items-center justify-center h-9 border-t border-slate-100 text-slate-400 hover:text-slate-600 hover:bg-slate-50 transition-colors"
      :aria-label="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
    >
      <ChevronRight v-if="collapsed" :size="14" />
      <ChevronLeft v-else :size="14" />
    </button>
  </aside>
</template>
