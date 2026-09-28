<script setup lang="ts">
import { computed } from 'vue';
import { useHospitalStore } from '../../stores/hospitalStore';

const store = useHospitalStore();
const dark = computed(() => store.darkMode);

const statusColor: Record<string, string> = {
  Normal:   dark.value ? 'text-green-400 bg-green-900/20 border-green-900/30' : 'text-green-700 bg-green-50 border-green-200',
  Busy:     dark.value ? 'text-amber-400 bg-amber-900/20 border-amber-900/30' : 'text-amber-700 bg-amber-50 border-amber-200',
  Critical: dark.value ? 'text-red-400 bg-red-900/20 border-red-900/30'       : 'text-red-700 bg-red-50 border-red-200',
  Full:     dark.value ? 'text-purple-400 bg-purple-900/20 border-purple-900/30' : 'text-purple-700 bg-purple-50 border-purple-200',
};

const deptAccentColor: Record<string, string> = {
  red:    'border-t-4 border-t-red-500',
  orange: 'border-t-4 border-t-orange-500',
  pink:   'border-t-4 border-t-pink-500',
  purple: 'border-t-4 border-t-purple-500',
  blue:   'border-t-4 border-t-blue-500',
  amber:  'border-t-4 border-t-amber-500',
  teal:   'border-t-4 border-t-teal-500',
  indigo: 'border-t-4 border-t-indigo-500',
  cyan:   'border-t-4 border-t-cyan-500',
  green:  'border-t-4 border-t-green-500',
  violet: 'border-t-4 border-t-violet-500',
};
</script>

<template>
  <div class="page-container py-6 space-y-5">
    <div class="stage-0">
      <h2 class="text-xl font-bold" :class="dark ? 'text-white' : 'text-slate-900'">Departments</h2>
      <p class="text-sm mt-0.5" :class="dark ? 'text-slate-400' : 'text-slate-500'">Department overview & performance metrics</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 stage-1">
      <div
        v-for="(dept, i) in store.departments"
        :key="dept.id"
        class="h-card rounded-xl overflow-hidden transition-all hover:scale-[1.01]"
        :class="[dark ? 'bg-[#111827] border-[#1E293B]' : '', deptAccentColor[dept.color], `stage-${Math.min(i, 8)}`]"
        :style="`animation-delay: ${i * 50}ms`"
      >
        <!-- Header -->
        <div class="flex items-center justify-between px-5 py-4">
          <div class="flex items-center gap-3">
            <span class="text-2xl">{{ dept.icon }}</span>
            <div>
              <p class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">{{ dept.name }}</p>
              <p class="text-2xs" :class="dark ? 'text-slate-500' : 'text-slate-400'">Head: {{ dept.head }}</p>
            </div>
          </div>
          <span class="badge border text-2xs" :class="statusColor[dept.status]">{{ dept.status }}</span>
        </div>

        <!-- Stats -->
        <div class="px-5 pb-4 grid grid-cols-3 gap-3">
          <div class="text-center">
            <p class="text-lg font-bold numeric" :class="dark ? 'text-white' : 'text-slate-800'">{{ dept.patients }}</p>
            <p class="text-2xs" :class="dark ? 'text-slate-500' : 'text-slate-400'">Patients</p>
          </div>
          <div class="text-center">
            <p class="text-lg font-bold numeric" :class="dark ? 'text-white' : 'text-slate-800'">{{ dept.doctors }}</p>
            <p class="text-2xs" :class="dark ? 'text-slate-500' : 'text-slate-400'">Doctors</p>
          </div>
          <div class="text-center">
            <p class="text-lg font-bold numeric" :class="dark ? 'text-white' : 'text-slate-800'">{{ dept.nurses }}</p>
            <p class="text-2xs" :class="dark ? 'text-slate-500' : 'text-slate-400'">Nurses</p>
          </div>
        </div>

        <!-- Bed Occupancy (for patient-facing depts) -->
        <div v-if="dept.totalBeds > 0" class="px-5 pb-4">
          <div class="flex items-center justify-between mb-1">
            <span class="text-2xs font-semibold" :class="dark ? 'text-slate-500' : 'text-slate-400'">Bed Occupancy</span>
            <span class="text-2xs font-bold" :class="dark ? 'text-slate-300' : 'text-slate-600'">
              {{ dept.totalBeds - dept.availableBeds }}/{{ dept.totalBeds }}
              ({{ Math.round(((dept.totalBeds - dept.availableBeds) / dept.totalBeds) * 100) }}%)
            </span>
          </div>
          <div class="progress-bar">
            <div
              class="progress-fill"
              :class="dept.status === 'Critical' ? 'bg-red-500' : dept.status === 'Busy' ? 'bg-amber-500' : dept.status === 'Full' ? 'bg-purple-500' : 'bg-teal-500'"
              :style="`width: ${Math.round(((dept.totalBeds - dept.availableBeds) / dept.totalBeds) * 100)}%`"
            ></div>
          </div>
          <p class="text-2xs mt-1.5" :class="dark ? 'text-slate-500' : 'text-slate-400'">
            {{ dept.availableBeds }} beds available
          </p>
        </div>
        <div v-else class="px-5 pb-4">
          <p class="text-2xs italic" :class="dark ? 'text-slate-600' : 'text-slate-300'">Outpatient / Lab department</p>
        </div>
      </div>
    </div>
  </div>
</template>
