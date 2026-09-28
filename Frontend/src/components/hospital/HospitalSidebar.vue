<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import {
  LayoutDashboard, AlertTriangle, Pill,
  Package, Ambulance, BarChart3, Bell, Settings,
  ChevronLeft, ChevronRight, Activity, Heart, X, Sparkles, ArrowRightLeft, Globe
} from 'lucide-vue-next';

import { useHospitalStore } from '../../stores/hospitalStore';

const props = defineProps<{ collapsed: boolean }>();
const emit = defineEmits<{ (e: 'toggle'): void; (e: 'close'): void; }>();

const store = useHospitalStore();
const route = useRoute();

const NAV_ITEMS = [
  { path: '/dashboard',     label: 'Dashboard',           icon: LayoutDashboard,  group: 'main' },
  { path: '/map',           label: 'Operations Map',      icon: Globe,            group: 'intelligence' },
  { path: '/results',       label: 'Healthcare Analysis', icon: Sparkles,         group: 'intelligence' },
  { path: '/phc-portal',    label: 'PHC Portal',          icon: ArrowRightLeft,   group: 'intelligence' },
  { path: '/emergency',     label: 'Emergency',           icon: AlertTriangle,    group: 'main', badge: 'emergency' },
  { path: '/pharmacy',      label: 'Pharmacy',            icon: Pill,             group: 'inventory', badge: 'medicine' },
  { path: '/inventory',     label: 'Inventory',           icon: Package,          group: 'inventory' },
  { path: '/ambulance',     label: 'Ambulance',           icon: Ambulance,        group: 'operations' },
  { path: '/analytics',     label: 'Analytics',           icon: BarChart3,        group: 'reports' },
  { path: '/notifications', label: 'Notifications',       icon: Bell,             group: 'reports', badge: 'notifications' },
  { path: '/settings',      label: 'Settings',            icon: Settings,         group: 'reports' },
];

const GROUPS = [
  { key: 'main',         label: 'Main' },
  { key: 'intelligence', label: 'BRICS Intelligence' },
  { key: 'inventory',    label: 'Inventory' },
  { key: 'operations',   label: 'Operations' },
  { key: 'reports',      label: 'Reports & Admin' },
];


const isActive = (path: string) => route.path === path;

const getBadgeCount = (badge: string | undefined) => {
  if (!badge) return 0;
  if (badge === 'emergency')     return store.unacknowledgedAlerts;
  if (badge === 'notifications') return store.unreadNotifications;
  if (badge === 'medicine')      return store.stats.lowStock + store.stats.outOfStock;
  return 0;
};

const groupedNav = computed(() =>
  GROUPS.map(g => ({ ...g, items: NAV_ITEMS.filter(n => n.group === g.key) }))
);
</script>

<template>
  <aside
    class="flex flex-col h-full dark-transition"
    :class="[
      collapsed ? 'w-16' : 'w-64',
      store.darkMode
        ? 'bg-[#111827] border-r border-[#1E293B]'
        : 'bg-white border-r border-slate-100'
    ]"
    style="transition: width 0.28s cubic-bezier(0.22,1,0.36,1);"
    aria-label="Hospital navigation"
  >
    <!-- Logo -->
    <div
      class="flex items-center h-16 flex-shrink-0 px-4 gap-3 border-b"
      :class="[collapsed && 'justify-center px-0', store.darkMode ? 'border-[#1E293B]' : 'border-slate-100']"
    >
      <div class="w-9 h-9 flex-shrink-0 rounded-xl flex items-center justify-center shadow-sm"
        style="background: linear-gradient(135deg, #0F766E, #0d9488);">
        <Heart :size="18" class="text-white" :stroke-width="2.5" />
      </div>
      <div v-if="!collapsed" class="min-w-0 flex-1">
        <p class="text-sm font-bold tracking-tight leading-none" :class="store.darkMode ? 'text-white' : 'text-slate-800'">MediCore</p>
        <p class="text-2xs font-semibold tracking-widest uppercase leading-none mt-0.5" style="color: #0d9488;">Hospital System</p>
      </div>
      <button
        v-if="!collapsed"
        @click="emit('close')"
        class="lg:hidden p-1 rounded-md hover:bg-slate-100 text-slate-400"
      >
        <X :size="15" />
      </button>
    </div>

    <!-- Live Status (when not collapsed) -->
    <div v-if="!collapsed" class="px-3 pt-3 pb-1">
      <div class="flex items-center gap-2 px-3 py-2 rounded-lg"
        :class="store.darkMode ? 'bg-[#1E293B]' : 'bg-slate-50'">
        <div class="pulse-dot-wrapper pulse-green">
          <span class="w-2 h-2 rounded-full bg-green-500 block"></span>
        </div>
        <span class="text-2xs font-medium" :class="store.darkMode ? 'text-slate-400' : 'text-slate-500'">City General Hospital</span>
        <span class="ml-auto text-2xs font-semibold text-green-600">LIVE</span>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 overflow-y-auto py-2 px-2">
      <template v-for="group in groupedNav" :key="group.key">
        <!-- Group Label -->
        <p
          v-if="!collapsed && group.items.length"
          class="px-3 pt-3 pb-1 text-2xs font-bold uppercase tracking-widest"
          :class="store.darkMode ? 'text-slate-600' : 'text-slate-400'"
        >{{ group.label }}</p>

        <ul class="space-y-0.5">
          <li v-for="item in group.items" :key="item.path">
            <router-link :to="item.path" v-slot="{ href, navigate }" custom>
              <a
                :href="href"
                @click="navigate"
                class="flex items-center gap-3 px-2.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 group relative"
                :class="[
                  collapsed && 'justify-center px-2',
                  isActive(item.path)
                    ? store.darkMode
                      ? 'bg-teal-900/40 text-teal-300'
                      : 'nav-active-glow text-teal-700'
                    : store.darkMode
                      ? 'text-slate-400 hover:bg-[#1E293B] hover:text-slate-200'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-800'
                ]"
                :title="collapsed ? item.label : undefined"
                :aria-current="isActive(item.path) ? 'page' : undefined"
              >
                <!-- Active Indicator Bar -->
                <span
                  v-if="isActive(item.path) && !collapsed"
                  class="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-r-full bg-teal-500"
                ></span>

                <component
                  :is="item.icon"
                  :size="17"
                  :stroke-width="isActive(item.path) ? 2.5 : 2"
                  class="flex-shrink-0 transition-colors"
                  :class="isActive(item.path)
                    ? 'text-teal-600'
                    : store.darkMode ? 'text-slate-500 group-hover:text-slate-300' : 'text-slate-400 group-hover:text-slate-600'"
                />
                <span v-if="!collapsed" class="truncate flex-1">{{ item.label }}</span>

                <!-- Badge -->
                <span
                  v-if="!collapsed && getBadgeCount(item.badge) > 0"
                  class="text-2xs font-bold px-1.5 py-0.5 rounded-full"
                  :class="item.badge === 'emergency'
                    ? 'bg-red-500 text-white'
                    : 'bg-amber-500 text-white'"
                >{{ getBadgeCount(item.badge) }}</span>

                <!-- Collapsed badge dot -->
                <span
                  v-if="collapsed && getBadgeCount(item.badge) > 0"
                  class="absolute top-1 right-1 w-2 h-2 rounded-full"
                  :class="item.badge === 'emergency' ? 'bg-red-500' : 'bg-amber-500'"
                ></span>
              </a>
            </router-link>
          </li>
        </ul>
      </template>
    </nav>

    <!-- Bottom: Quick Emergency Button -->
    <div class="px-2 pb-2 border-t flex-shrink-0 pt-2"
      :class="store.darkMode ? 'border-[#1E293B]' : 'border-slate-100'">
      <button
        v-if="!collapsed"
        @click="store.triggerEmergency({ patient: '', priority: 'CRITICAL', department: 'Emergency', required: 'ICU Bed', doctor: 'On-Call Doctor' })"
        class="btn-emergency w-full justify-center py-2.5 text-xs"
        style="animation: none;"
      >
        <AlertTriangle :size="14" />
        🚨 Trigger Emergency
      </button>
      <button
        v-else
        @click="store.triggerEmergency({ patient: '', priority: 'CRITICAL', department: 'Emergency', required: 'ICU Bed', doctor: 'On-Call Doctor' })"
        class="flex items-center justify-center w-full p-2.5 rounded-lg bg-red-50 hover:bg-red-100 text-red-600 transition-colors"
        title="Trigger Emergency"
      >
        <AlertTriangle :size="17" :stroke-width="2.5" />
      </button>
    </div>

    <!-- Collapse Toggle -->
    <button
      @click="emit('toggle')"
      class="flex items-center justify-center h-9 border-t text-slate-400 hover:text-slate-600 transition-colors flex-shrink-0"
      :class="[
        store.darkMode
          ? 'border-[#1E293B] hover:bg-[#1E293B] text-slate-600 hover:text-slate-400'
          : 'border-slate-100 hover:bg-slate-50'
      ]"
      :aria-label="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
    >
      <ChevronRight v-if="collapsed" :size="14" />
      <ChevronLeft v-else :size="14" />
    </button>
  </aside>
</template>
