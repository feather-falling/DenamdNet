<script setup lang="ts">
import { computed, ref } from 'vue';
import { useHospitalStore } from '../../stores/hospitalStore';
import { Bell, CheckCheck, Filter } from 'lucide-vue-next';
import type { Notification } from '../../data/mock/hospitalData';

const store = useHospitalStore();
const dark = computed(() => store.darkMode);

const filterCat = ref('ALL');
const filterRead = ref('ALL');

const categories = ['Emergency', 'Patients', 'Beds', 'Pharmacy', 'Inventory', 'Appointments', 'Staff'];

const filtered = computed(() => {
  let list = [...store.notifications];
  if (filterCat.value !== 'ALL') list = list.filter(n => n.category === filterCat.value);
  if (filterRead.value === 'unread') list = list.filter(n => !n.read);
  if (filterRead.value === 'read') list = list.filter(n => n.read);
  return list;
});

const severityConfig: Record<string, { dot: string; badge: string }> = {
  critical: { dot: 'bg-red-500 animate-pulse',  badge: 'badge-critical' },
  high:     { dot: 'bg-amber-500',               badge: 'badge-high' },
  medium:   { dot: 'bg-blue-400',                badge: 'badge-info' },
  low:      { dot: 'bg-green-400',               badge: 'badge-normal' },
};

const catIcon: Record<string, string> = {
  Emergency:    '🚨',
  Patients:     '👤',
  Beds:         '🛏️',
  Pharmacy:     '💊',
  Inventory:    '📦',
  Appointments: '📅',
  Staff:        '👨‍⚕️',
};

const markRead = (id: string) => store.markNotificationRead(id);
</script>

<template>
  <div class="page-container py-6 space-y-5">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 stage-0">
      <div>
        <h2 class="text-xl font-bold" :class="dark ? 'text-white' : 'text-slate-900'">Notifications</h2>
        <p class="text-sm mt-0.5" :class="dark ? 'text-slate-400' : 'text-slate-500'">
          {{ store.unreadNotifications }} unread notifications
        </p>
      </div>
      <button @click="store.markAllNotificationsRead()" class="btn-secondary px-4 py-2 text-xs">
        <CheckCheck :size="13" /> Mark all read
      </button>
    </div>

    <!-- Category Filter Tabs -->
    <div class="flex flex-wrap gap-2 stage-1">
      <button
        @click="filterCat = 'ALL'"
        class="px-3 py-1.5 rounded-lg text-xs font-semibold border transition-colors"
        :class="filterCat === 'ALL'
          ? 'bg-teal-600 text-white border-teal-600'
          : dark ? 'border-[#334155] text-slate-400 hover:bg-[#1E293B]' : 'border-slate-200 text-slate-600 hover:bg-slate-50'"
      >All</button>
      <button
        v-for="cat in categories"
        :key="cat"
        @click="filterCat = cat"
        class="px-3 py-1.5 rounded-lg text-xs font-semibold border transition-colors flex items-center gap-1.5"
        :class="filterCat === cat
          ? 'bg-teal-600 text-white border-teal-600'
          : dark ? 'border-[#334155] text-slate-400 hover:bg-[#1E293B]' : 'border-slate-200 text-slate-600 hover:bg-slate-50'"
      >
        {{ catIcon[cat] }} {{ cat }}
      </button>
    </div>

    <!-- Read Filter -->
    <div class="flex gap-2 stage-2">
      <button
        v-for="opt in [{ v: 'ALL', l: 'All' }, { v: 'unread', l: 'Unread' }, { v: 'read', l: 'Read' }]"
        :key="opt.v"
        @click="filterRead = opt.v"
        class="px-3 py-1.5 rounded-lg text-xs font-semibold border transition-colors"
        :class="filterRead === opt.v
          ? 'bg-slate-800 text-white border-slate-800'
          : dark ? 'border-[#334155] text-slate-400 hover:bg-[#1E293B]' : 'border-slate-200 text-slate-600 hover:bg-slate-50'"
      >{{ opt.l }}</button>
    </div>

    <!-- Notifications List -->
    <div class="space-y-2 stage-3">
      <div
        v-for="notif in filtered"
        :key="notif.id"
        @click="markRead(notif.id)"
        class="h-card rounded-xl p-4 cursor-pointer transition-all hover:scale-[1.005]"
        :class="[
          dark ? 'bg-[#111827] border-[#1E293B]' : '',
          !notif.read && (dark ? 'border-l-4 border-l-teal-500/60 bg-teal-900/5' : 'border-l-4 border-l-teal-500 bg-teal-50/30'),
        ]"
      >
        <div class="flex items-start gap-3">
          <span class="text-xl flex-shrink-0 mt-0.5">{{ catIcon[notif.category] }}</span>
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between gap-3">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="badge text-2xs" :class="severityConfig[notif.severity].badge">
                  {{ notif.severity.toUpperCase() }}
                </span>
                <span class="badge badge-neutral text-2xs">{{ notif.category }}</span>
                <p class="text-xs font-bold" :class="dark ? 'text-slate-200' : 'text-slate-700'">{{ notif.title }}</p>
              </div>
              <div class="flex items-center gap-2 flex-shrink-0">
                <span class="text-2xs font-medium" :class="dark ? 'text-slate-500' : 'text-slate-400'">{{ notif.time }}</span>
                <span
                  v-if="!notif.read"
                  class="w-2 h-2 rounded-full flex-shrink-0"
                  :class="severityConfig[notif.severity].dot"
                ></span>
              </div>
            </div>
            <p class="text-xs mt-1.5" :class="dark ? 'text-slate-400' : 'text-slate-600'">{{ notif.message }}</p>
          </div>
        </div>
      </div>

      <div v-if="filtered.length === 0" class="py-16 text-center h-card rounded-xl"
        :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <Bell :size="40" class="mx-auto mb-3 opacity-20" :class="dark ? 'text-slate-400' : 'text-slate-300'" />
        <p class="text-sm font-medium" :class="dark ? 'text-slate-500' : 'text-slate-400'">No notifications found</p>
        <p class="text-2xs mt-1" :class="dark ? 'text-slate-600' : 'text-slate-300'">Try changing the filters</p>
      </div>
    </div>
  </div>
</template>
