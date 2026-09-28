<script setup lang="ts">
import { ref, computed } from 'vue';
import { useHospitalStore } from '../../stores/hospitalStore';
import { Ambulance as AmbulanceIcon, MapPin, Clock, Phone, User, CheckCircle, AlertCircle, Settings, RefreshCw } from 'lucide-vue-next';
import type { Ambulance } from '../../data/mock/hospitalData';

const store = useHospitalStore();
const dark = computed(() => store.darkMode);

const filterStatus = ref('ALL');

const filtered = computed(() => {
  if (filterStatus.value === 'ALL') return store.ambulances;
  return store.ambulances.filter(a => a.status === filterStatus.value);
});

const statusConfig: Record<Ambulance['status'], { label: string; badge: string; dotColor: string }> = {
  Available:   { label: 'Available',   badge: 'badge-normal',   dotColor: 'bg-green-500' },
  'On Mission':{ label: 'On Mission',  badge: 'badge-critical', dotColor: 'bg-red-500 animate-pulse' },
  Returning:   { label: 'Returning',   badge: 'badge-high',     dotColor: 'bg-amber-500' },
  Maintenance: { label: 'Maintenance', badge: 'badge-neutral',  dotColor: 'bg-slate-400' },
};

const statCounts = computed(() => {
  const counts: Record<string, number> = { Available: 0, 'On Mission': 0, Returning: 0, Maintenance: 0 };
  store.ambulances.forEach(a => { counts[a.status]++; });
  return counts;
});
</script>

<template>
  <div class="page-container py-6 space-y-5">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 stage-0">
      <div>
        <h2 class="text-xl font-bold" :class="dark ? 'text-white' : 'text-slate-900'">Ambulance Management</h2>
        <p class="text-sm" :class="dark ? 'text-slate-400' : 'text-slate-500'">Fleet status & dispatch control</p>
      </div>
    </div>

    <!-- Stat Cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3.5 stage-1">
      <div v-for="(count, status) in statCounts" :key="status"
        class="h-card rounded-xl p-5 cursor-pointer transition-all hover:scale-[1.02]"
        :class="[
          dark ? 'bg-[#111827] border-[#1E293B]' : '',
          filterStatus === status && (dark ? 'ring-2 ring-teal-500/50' : 'ring-2 ring-teal-400/50')
        ]"
        @click="filterStatus = filterStatus === status ? 'ALL' : status"
      >
        <div class="flex items-center gap-2 mb-2">
          <span class="w-2.5 h-2.5 rounded-full" :class="statusConfig[status as Ambulance['status']].dotColor"></span>
          <span class="text-2xs font-semibold" :class="dark ? 'text-slate-400' : 'text-slate-500'">{{ status }}</span>
        </div>
        <p class="text-3xl font-bold numeric" :class="dark ? 'text-white' : 'text-slate-800'">{{ count }}</p>
      </div>
    </div>

    <!-- Filter -->
    <div class="flex gap-2 stage-2">
      <button
        v-for="s in ['ALL', 'Available', 'On Mission', 'Returning', 'Maintenance']"
        :key="s"
        @click="filterStatus = s"
        class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors border"
        :class="filterStatus === s
          ? 'bg-teal-600 text-white border-teal-600'
          : dark ? 'border-[#334155] text-slate-400 hover:bg-[#1E293B]' : 'border-slate-200 text-slate-600 hover:bg-slate-50'"
      >{{ s }}</button>
    </div>

    <!-- Ambulance Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 stage-3">
      <div
        v-for="amb in filtered"
        :key="amb.id"
        class="h-card rounded-xl overflow-hidden transition-all hover:scale-[1.01]"
        :class="[
          dark ? 'bg-[#111827] border-[#1E293B]' : '',
          amb.status === 'On Mission' && (dark ? 'emergency-glow' : 'border-red-200'),
        ]"
      >
        <!-- Card Header -->
        <div class="flex items-center justify-between px-5 py-4 border-b"
          :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center"
              :class="amb.status === 'Available' ? (dark ? 'bg-green-900/20' : 'bg-green-50') : amb.status === 'On Mission' ? (dark ? 'bg-red-900/20' : 'bg-red-50') : (dark ? 'bg-amber-900/20' : 'bg-amber-50')">
              <AmbulanceIcon :size="18"
                :class="amb.status === 'Available' ? 'text-green-500' : amb.status === 'On Mission' ? 'text-red-500' : 'text-amber-500'"
              />
            </div>
            <div>
              <p class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">{{ amb.id }}</p>
              <p class="text-2xs font-mono" :class="dark ? 'text-slate-500' : 'text-slate-400'">{{ amb.regNumber }}</p>
            </div>
          </div>
          <span class="badge" :class="statusConfig[amb.status].badge">{{ amb.status }}</span>
        </div>

        <!-- Card Body -->
        <div class="px-5 py-4 space-y-2.5">
          <div class="flex items-center gap-2 text-xs" :class="dark ? 'text-slate-400' : 'text-slate-600'">
            <User :size="13" class="flex-shrink-0" :class="dark ? 'text-slate-500' : 'text-slate-400'" />
            <span class="font-medium">{{ amb.driver }}</span>
          </div>
          <div class="flex items-center gap-2 text-xs" :class="dark ? 'text-slate-400' : 'text-slate-600'">
            <Phone :size="13" class="flex-shrink-0" :class="dark ? 'text-slate-500' : 'text-slate-400'" />
            <span>{{ amb.contact }}</span>
          </div>
          <div class="flex items-center gap-2 text-xs" :class="dark ? 'text-slate-400' : 'text-slate-600'">
            <MapPin :size="13" class="flex-shrink-0" :class="dark ? 'text-slate-500' : 'text-slate-400'" />
            <span>{{ amb.location }}</span>
          </div>
          <template v-if="amb.destination">
            <div class="flex items-center gap-2 text-xs" :class="dark ? 'text-slate-400' : 'text-slate-600'">
              <MapPin :size="13" class="flex-shrink-0 text-red-400" />
              <span>→ {{ amb.destination }}</span>
            </div>
          </template>
          <template v-if="amb.eta">
            <div class="flex items-center gap-2 text-xs font-semibold" :class="dark ? 'text-amber-400' : 'text-amber-600'">
              <Clock :size="13" class="flex-shrink-0" />
              <span>ETA: {{ amb.eta }}</span>
            </div>
          </template>
        </div>

        <!-- Card Footer -->
        <div class="px-5 py-3 border-t flex items-center justify-between"
          :class="dark ? 'border-[#1E293B] bg-[#1E293B]/30' : 'border-slate-100 bg-slate-50/50'">
          <span class="text-2xs" :class="dark ? 'text-slate-500' : 'text-slate-400'">Last service: {{ amb.lastService }}</span>
          <div class="flex items-center gap-1.5">
            <button class="flex items-center gap-1 px-2.5 py-1 rounded-md text-2xs font-semibold transition-colors"
              :class="dark ? 'bg-blue-900/20 text-blue-400 hover:bg-blue-900/30' : 'bg-blue-50 text-blue-600 hover:bg-blue-100'">
              <Phone :size="11" /> Call
            </button>
            <button
              v-if="amb.status === 'Available'"
              class="flex items-center gap-1 px-2.5 py-1 rounded-md text-2xs font-semibold transition-colors"
              :class="dark ? 'bg-red-900/20 text-red-400 hover:bg-red-900/30' : 'bg-red-50 text-red-600 hover:bg-red-100'">
              Dispatch
            </button>
          </div>
        </div>
      </div>

      <div v-if="filtered.length === 0" class="col-span-full py-12 text-center">
        <AmbulanceIcon :size="40" class="mx-auto mb-3 opacity-20" :class="dark ? 'text-slate-400' : 'text-slate-300'" />
        <p class="text-sm" :class="dark ? 'text-slate-500' : 'text-slate-400'">No ambulances match filter</p>
      </div>
    </div>
  </div>
</template>
