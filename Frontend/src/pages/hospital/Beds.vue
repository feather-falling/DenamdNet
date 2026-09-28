<script setup lang="ts">
import { ref, computed } from 'vue';
import { useHospitalStore } from '../../stores/hospitalStore';
import type { Bed } from '../../data/mock/hospitalData';
import { Bed as BedIcon, Search, Filter, Info, X, RefreshCw } from 'lucide-vue-next';

const store = useHospitalStore();
const dark = computed(() => store.darkMode);

const filterWard = ref('ALL');
const filterStatus = ref('ALL');
const searchBed = ref('');
const selectedBed = ref<Bed | null>(null);
const panelOpen = ref(false);
const newStatus = ref<Bed['status']>('Available');

const wards = computed(() => [...new Set(store.beds.map(b => b.ward))]);

const filtered = computed(() => {
  let list = [...store.beds];
  if (searchBed.value) {
    const q = searchBed.value.toLowerCase();
    list = list.filter(b => b.id.toLowerCase().includes(q) || b.room.toLowerCase().includes(q) || (b.patient || '').toLowerCase().includes(q));
  }
  if (filterWard.value !== 'ALL') list = list.filter(b => b.ward === filterWard.value);
  if (filterStatus.value !== 'ALL') list = list.filter(b => b.status === filterStatus.value);
  return list;
});

const groupedBeds = computed(() => {
  const groups: Record<string, Bed[]> = {};
  for (const bed of filtered.value) {
    if (!groups[bed.ward]) groups[bed.ward] = [];
    groups[bed.ward].push(bed);
  }
  return groups;
});

const bedStatusClass = (status: Bed['status']) => {
  const map: Record<string, string> = {
    Available:   dark.value ? 'bg-green-900/30 border-green-700/40 text-green-400' : 'bed-available',
    Occupied:    dark.value ? 'bg-red-900/30 border-red-700/40 text-red-400'       : 'bed-occupied',
    Reserved:    dark.value ? 'bg-amber-900/30 border-amber-700/40 text-amber-400' : 'bed-reserved',
    Cleaning:    dark.value ? 'bg-blue-900/30 border-blue-700/40 text-blue-400'    : 'bed-cleaning',
    Maintenance: dark.value ? 'bg-slate-700/40 border-slate-600/40 text-slate-400' : 'bed-maintenance',
    Emergency:   dark.value ? 'bg-purple-900/30 border-purple-700/40 text-purple-400' : 'bed-emergency',
  };
  return map[status] || '';
};

const statTotals = computed(() => {
  const counts: Record<string, number> = { Available: 0, Occupied: 0, Reserved: 0, Cleaning: 0, Maintenance: 0, Emergency: 0 };
  store.beds.forEach(b => { if (b.status in counts) counts[b.status]++; });
  return counts;
});

const openBedPanel = (bed: Bed) => {
  selectedBed.value = bed;
  newStatus.value = bed.status;
  panelOpen.value = true;
};

const applyBedStatus = () => {
  if (selectedBed.value) {
    store.updateBedStatus(selectedBed.value.id, newStatus.value);
    selectedBed.value = { ...selectedBed.value, status: newStatus.value };
  }
};
</script>

<template>
  <div class="page-container py-6 space-y-5">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 stage-0">
      <div>
        <h2 class="text-xl font-bold" :class="dark ? 'text-white' : 'text-slate-900'">Bed Management</h2>
        <p class="text-sm" :class="dark ? 'text-slate-400' : 'text-slate-500'">
          {{ store.stats.totalBeds }} total beds · Interactive bed map
        </p>
      </div>
    </div>

    <!-- Bed Status Summary -->
    <div class="grid grid-cols-3 md:grid-cols-6 gap-3 stage-1">
      <div v-for="(count, status) in statTotals" :key="status"
        class="h-card rounded-xl p-4 text-center"
        :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <div class="text-xl font-bold numeric mb-0.5" :class="dark ? 'text-white' : 'text-slate-800'">{{ count }}</div>
        <div class="text-2xs font-semibold rounded-full px-2 py-0.5 inline-block"
          :class="bedStatusClass(status as Bed['status'])">{{ status }}</div>
      </div>
    </div>

    <!-- Filters -->
    <div class="flex flex-col sm:flex-row gap-3 stage-2">
      <div class="relative flex-1 max-w-xs">
        <Search :size="14" class="absolute left-3 top-1/2 -translate-y-1/2" :class="dark ? 'text-slate-500' : 'text-slate-400'" />
        <input v-model="searchBed" type="text" placeholder="Search beds..." class="h-input pl-9 text-sm" />
      </div>
      <select v-model="filterWard" class="h-input w-full sm:w-40 text-sm">
        <option value="ALL">All Wards</option>
        <option v-for="ward in wards" :key="ward" :value="ward">{{ ward }}</option>
      </select>
      <select v-model="filterStatus" class="h-input w-full sm:w-40 text-sm">
        <option value="ALL">All Status</option>
        <option v-for="s in ['Available','Occupied','Reserved','Cleaning','Maintenance','Emergency']" :key="s" :value="s">{{ s }}</option>
      </select>
    </div>

    <!-- Bed Grid by Ward -->
    <div class="space-y-5 stage-3">
      <div
        v-for="(beds, ward) in groupedBeds"
        :key="ward"
        class="h-card rounded-xl overflow-hidden"
        :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''"
      >
        <div class="flex items-center justify-between px-5 py-3.5 border-b"
          :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
          <div class="flex items-center gap-2.5">
            <BedIcon :size="16" :class="dark ? 'text-teal-400' : 'text-teal-600'" />
            <h3 class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">{{ ward }}</h3>
            <span class="badge badge-info">{{ beds.length }} beds</span>
          </div>
          <div class="flex items-center gap-2 text-2xs" :class="dark ? 'text-slate-500' : 'text-slate-400'">
            <span class="text-green-600 font-semibold">{{ beds.filter(b => b.status === 'Available').length }} available</span>
            <span>·</span>
            <span class="text-red-500 font-semibold">{{ beds.filter(b => b.status === 'Occupied').length }} occupied</span>
          </div>
        </div>
        <div class="p-4 grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-2">
          <button
            v-for="bed in beds"
            :key="bed.id"
            @click="openBedPanel(bed)"
            class="rounded-xl p-3 text-center transition-all hover:scale-105 border text-2xs font-semibold"
            :class="bedStatusClass(bed.status)"
            :title="`${bed.id} — ${bed.status}${bed.patient ? ` · ${bed.patient}` : ''}`"
          >
            <div class="font-bold text-xs mb-0.5">{{ bed.id }}</div>
            <div class="truncate opacity-80">{{ bed.status }}</div>
          </button>
        </div>
      </div>
      <div v-if="Object.keys(groupedBeds).length === 0" class="py-12 text-center">
        <BedIcon :size="40" class="mx-auto mb-3 opacity-20" :class="dark ? 'text-slate-400' : 'text-slate-300'" />
        <p class="text-sm" :class="dark ? 'text-slate-500' : 'text-slate-400'">No beds match the filter</p>
      </div>
    </div>

    <!-- Bed Legend -->
    <div class="h-card p-4 rounded-xl stage-4" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
      <p class="text-xs font-bold mb-3" :class="dark ? 'text-slate-400' : 'text-slate-600'">Status Legend</p>
      <div class="flex flex-wrap gap-3">
        <div v-for="status in ['Available','Occupied','Reserved','Cleaning','Maintenance','Emergency']" :key="status"
          class="flex items-center gap-1.5">
          <span class="w-3 h-3 rounded-sm border" :class="bedStatusClass(status as Bed['status'])"></span>
          <span class="text-2xs" :class="dark ? 'text-slate-400' : 'text-slate-500'">{{ status }}</span>
        </div>
      </div>
    </div>

    <!-- Bed Detail Panel (Drawer) -->
    <Transition
      enter-active-class="transition duration-250"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="panelOpen && selectedBed"
        class="fixed inset-0 z-50 flex justify-end"
        style="background: rgba(0,0,0,0.4); backdrop-filter: blur(3px);"
        @click.self="panelOpen = false">
        <div class="w-full max-w-sm h-full shadow-drawer overflow-y-auto drawer-panel"
          :class="dark ? 'bg-[#111827]' : 'bg-white'">
          <div class="flex items-center justify-between px-6 py-4 border-b sticky top-0 z-10"
            :class="dark ? 'bg-[#111827] border-[#1E293B]' : 'bg-white border-slate-200'">
            <h3 class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">Bed {{ selectedBed.id }}</h3>
            <button @click="panelOpen = false" class="p-1.5 rounded-lg transition-colors"
              :class="dark ? 'text-slate-400 hover:bg-[#1E293B]' : 'text-slate-400 hover:bg-slate-100'">
              <X :size="16" />
            </button>
          </div>
          <div class="p-6 space-y-4">
            <!-- Current Status -->
            <div>
              <p class="text-2xs font-bold uppercase tracking-wider mb-2" :class="dark ? 'text-slate-500' : 'text-slate-400'">Current Status</p>
              <span class="badge text-sm py-1.5 px-4" :class="bedStatusClass(selectedBed.status)">{{ selectedBed.status }}</span>
            </div>

            <!-- Details -->
            <div class="space-y-2.5">
              <div v-for="row in [
                { label: 'Ward', value: selectedBed.ward },
                { label: 'Room', value: selectedBed.room },
                { label: 'Bed Type', value: selectedBed.type },
                { label: 'Patient', value: selectedBed.patient || '—' },
                { label: 'Admitted', value: selectedBed.admittedDate || '—' },
              ]" :key="row.label"
                class="flex items-center justify-between text-xs pb-2.5 border-b"
                :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
                <span class="font-semibold" :class="dark ? 'text-slate-500' : 'text-slate-400'">{{ row.label }}</span>
                <span :class="dark ? 'text-slate-300' : 'text-slate-700'">{{ row.value }}</span>
              </div>
            </div>

            <!-- Update Status -->
            <div>
              <p class="text-2xs font-bold uppercase tracking-wider mb-2" :class="dark ? 'text-slate-500' : 'text-slate-400'">Update Status</p>
              <select v-model="newStatus" class="h-input w-full text-sm mb-3">
                <option v-for="s in ['Available','Occupied','Reserved','Cleaning','Maintenance','Emergency']" :key="s" :value="s">{{ s }}</option>
              </select>
              <button @click="applyBedStatus" class="btn-primary w-full justify-center py-2.5 text-xs">
                <RefreshCw :size="13" /> Apply Status
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>
