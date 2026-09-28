<script setup lang="ts">
import { ref, computed } from 'vue';
import { Users, Search, Filter, ChevronDown, Eye, Edit, Plus, X, ChevronLeft, ChevronRight } from 'lucide-vue-next';
import { useHospitalStore } from '../../stores/hospitalStore';
import type { Patient } from '../../data/mock/hospitalData';

const store = useHospitalStore();
const dark = computed(() => store.darkMode);

const search = ref('');
const filterPriority = ref<string>('ALL');
const filterDept = ref<string>('ALL');
const filterStatus = ref<string>('ALL');
const sortKey = ref<keyof Patient>('name');
const sortDir = ref<'asc' | 'desc'>('asc');
const page = ref(1);
const perPage = 8;
const selectedPatient = ref<Patient | null>(null);
const drawerOpen = ref(false);

const departments = computed(() => [...new Set(store.patients.map(p => p.department))]);

const filtered = computed(() => {
  let list = [...store.patients];
  if (search.value) {
    const q = search.value.toLowerCase();
    list = list.filter(p =>
      p.name.toLowerCase().includes(q) ||
      p.id.toLowerCase().includes(q) ||
      p.department.toLowerCase().includes(q) ||
      p.doctor.toLowerCase().includes(q)
    );
  }
  if (filterPriority.value !== 'ALL') list = list.filter(p => p.priority === filterPriority.value);
  if (filterDept.value !== 'ALL') list = list.filter(p => p.department === filterDept.value);
  if (filterStatus.value !== 'ALL') list = list.filter(p => p.status === filterStatus.value);
  list.sort((a, b) => {
    const va = String(a[sortKey.value] ?? '');
    const vb = String(b[sortKey.value] ?? '');
    return sortDir.value === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va);
  });
  return list;
});

const totalPages = computed(() => Math.ceil(filtered.value.length / perPage));
const paginated = computed(() => filtered.value.slice((page.value - 1) * perPage, page.value * perPage));

const toggleSort = (key: keyof Patient) => {
  if (sortKey.value === key) sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc';
  else { sortKey.value = key; sortDir.value = 'asc'; }
};

const openPatient = (p: Patient) => {
  selectedPatient.value = p;
  drawerOpen.value = true;
};

const priorityBadge = (p: string) => p === 'CRITICAL' ? 'badge-critical' : p === 'HIGH' ? 'badge-high' : 'badge-normal';
const statusBadge = (s: string) => {
  if (s === 'Critical') return 'badge-critical';
  if (s === 'In Surgery') return 'badge-high';
  if (s === 'Under Observation') return 'badge-info';
  return 'badge-normal';
};
</script>

<template>
  <div class="page-container py-6 space-y-5">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 stage-0">
      <div>
        <h2 class="text-xl font-bold" :class="dark ? 'text-white' : 'text-slate-900'">Patient Management</h2>
        <p class="text-sm" :class="dark ? 'text-slate-400' : 'text-slate-500'">
          {{ store.patients.length }} total patients · {{ store.criticalPatients.length }} critical
        </p>
      </div>
      <button class="btn-primary px-4 py-2">
        <Plus :size="14" /> Add Patient
      </button>
    </div>

    <!-- Filters Bar -->
    <div class="h-card p-4 rounded-xl stage-1" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
      <div class="flex flex-col sm:flex-row gap-3">
        <!-- Search -->
        <div class="relative flex-1">
          <Search :size="15" class="absolute left-3 top-1/2 -translate-y-1/2" :class="dark ? 'text-slate-500' : 'text-slate-400'" />
          <input
            v-model="search"
            type="text"
            placeholder="Search patients by name, ID, department..."
            class="h-input pl-9 pr-4 text-sm"
          />
        </div>
        <!-- Priority Filter -->
        <select v-model="filterPriority"
          class="h-input w-full sm:w-36 text-sm">
          <option value="ALL">All Priority</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="NORMAL">Normal</option>
        </select>
        <!-- Department Filter -->
        <select v-model="filterDept"
          class="h-input w-full sm:w-44 text-sm">
          <option value="ALL">All Departments</option>
          <option v-for="dept in departments" :key="dept" :value="dept">{{ dept }}</option>
        </select>
        <!-- Status Filter -->
        <select v-model="filterStatus"
          class="h-input w-full sm:w-40 text-sm">
          <option value="ALL">All Status</option>
          <option>Admitted</option>
          <option>Critical</option>
          <option>In Surgery</option>
          <option>Under Observation</option>
          <option>Discharged</option>
        </select>
        <!-- Clear -->
        <button
          v-if="search || filterPriority !== 'ALL' || filterDept !== 'ALL' || filterStatus !== 'ALL'"
          @click="search = ''; filterPriority = 'ALL'; filterDept = 'ALL'; filterStatus = 'ALL'"
          class="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm text-red-600 border border-red-200 hover:bg-red-50 transition-colors flex-shrink-0"
        >
          <X :size="14" /> Clear
        </button>
      </div>
      <p class="text-2xs mt-2.5" :class="dark ? 'text-slate-500' : 'text-slate-400'">
        Showing {{ paginated.length }} of {{ filtered.length }} patients
      </p>
    </div>

    <!-- Table -->
    <div class="h-card rounded-xl overflow-hidden stage-2" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
      <div class="overflow-table-scroll">
        <table class="w-full min-w-[900px]">
          <thead>
            <tr :class="dark ? 'bg-[#1E293B]/60' : 'bg-slate-50'">
              <th class="table-header-cell text-left cursor-pointer hover:text-slate-600" @click="toggleSort('id')">
                ID <span v-if="sortKey === 'id'">{{ sortDir === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="table-header-cell text-left cursor-pointer hover:text-slate-600" @click="toggleSort('name')">
                Patient <span v-if="sortKey === 'name'">{{ sortDir === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="table-header-cell text-left">Age/Gender</th>
              <th class="table-header-cell text-left cursor-pointer hover:text-slate-600" @click="toggleSort('department')">
                Department <span v-if="sortKey === 'department'">{{ sortDir === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="table-header-cell text-left">Doctor</th>
              <th class="table-header-cell text-left">Bed</th>
              <th class="table-header-cell text-left">Priority</th>
              <th class="table-header-cell text-left">Admission</th>
              <th class="table-header-cell text-left">Status</th>
              <th class="table-header-cell text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="patient in paginated"
              :key="patient.id"
              class="table-row-hover border-t cursor-pointer"
              :class="[
                dark ? 'border-[#1E293B]' : 'border-slate-100',
                patient.priority === 'CRITICAL' && (dark ? 'bg-red-900/5' : 'bg-red-50/30'),
              ]"
              @click="openPatient(patient)"
            >
              <td class="table-cell font-mono text-xs" :class="dark ? 'text-slate-400' : 'text-slate-500'">{{ patient.id }}</td>
              <td class="table-cell">
                <div class="flex items-center gap-2.5">
                  <div class="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
                    :style="`background: linear-gradient(135deg, hsl(${(patient.name.charCodeAt(0) * 40) % 360},55%,45%), hsl(${(patient.name.charCodeAt(0) * 40 + 30) % 360},55%,38%))`">
                    {{ patient.name.split(' ').map((n: string) => n[0]).join('').slice(0, 2) }}
                  </div>
                  <div>
                    <p class="font-semibold text-xs" :class="dark ? 'text-slate-200' : 'text-slate-700'">{{ patient.name }}</p>
                    <p class="text-2xs" :class="dark ? 'text-slate-500' : 'text-slate-400'">{{ patient.bloodGroup }}</p>
                  </div>
                </div>
              </td>
              <td class="table-cell text-xs" :class="dark ? 'text-slate-400' : 'text-slate-600'">{{ patient.age }}y · {{ patient.gender }}</td>
              <td class="table-cell text-xs" :class="dark ? 'text-slate-300' : 'text-slate-700'">{{ patient.department }}</td>
              <td class="table-cell text-xs" :class="dark ? 'text-slate-300' : 'text-slate-700'">{{ patient.doctor }}</td>
              <td class="table-cell font-mono text-2xs" :class="dark ? 'text-slate-400' : 'text-slate-500'">{{ patient.room }}</td>
              <td class="table-cell">
                <span class="badge" :class="priorityBadge(patient.priority)">{{ patient.priority }}</span>
              </td>
              <td class="table-cell text-2xs" :class="dark ? 'text-slate-400' : 'text-slate-500'">{{ patient.admissionDate }}</td>
              <td class="table-cell">
                <span class="badge" :class="statusBadge(patient.status)">{{ patient.status }}</span>
              </td>
              <td class="table-cell" @click.stop>
                <div class="flex items-center gap-1.5">
                  <button @click="openPatient(patient)"
                    class="p-1.5 rounded-md transition-colors"
                    :class="dark ? 'text-slate-400 hover:bg-[#1E293B]' : 'text-slate-400 hover:bg-slate-100'">
                    <Eye :size="14" />
                  </button>
                  <button
                    class="p-1.5 rounded-md transition-colors"
                    :class="dark ? 'text-slate-400 hover:bg-[#1E293B]' : 'text-slate-400 hover:bg-slate-100'">
                    <Edit :size="14" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="paginated.length === 0">
              <td colspan="10" class="py-12 text-center">
                <div class="text-slate-400">
                  <Users :size="40" class="mx-auto mb-2 opacity-30" />
                  <p class="text-sm font-medium">No patients found</p>
                  <p class="text-2xs mt-1">Try adjusting your search or filters</p>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="flex items-center justify-between px-5 py-3.5 border-t" :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
        <p class="text-xs" :class="dark ? 'text-slate-500' : 'text-slate-400'">
          Page {{ page }} of {{ totalPages }} · {{ filtered.length }} results
        </p>
        <div class="flex items-center gap-1">
          <button
            @click="page = Math.max(1, page - 1)"
            :disabled="page === 1"
            class="p-1.5 rounded-md transition-colors disabled:opacity-40"
            :class="dark ? 'text-slate-400 hover:bg-[#1E293B]' : 'text-slate-400 hover:bg-slate-100'"
          >
            <ChevronLeft :size="16" />
          </button>
          <button
            v-for="p in totalPages"
            :key="p"
            @click="page = p"
            class="w-7 h-7 rounded-md text-xs font-medium transition-colors"
            :class="p === page
              ? 'bg-teal-600 text-white'
              : dark ? 'text-slate-400 hover:bg-[#1E293B]' : 'text-slate-500 hover:bg-slate-100'"
          >{{ p }}</button>
          <button
            @click="page = Math.min(totalPages, page + 1)"
            :disabled="page === totalPages"
            class="p-1.5 rounded-md transition-colors disabled:opacity-40"
            :class="dark ? 'text-slate-400 hover:bg-[#1E293B]' : 'text-slate-400 hover:bg-slate-100'"
          >
            <ChevronRight :size="16" />
          </button>
        </div>
      </div>
    </div>

    <!-- Patient Drawer -->
    <Transition
      enter-active-class="transition duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="drawerOpen && selectedPatient" class="fixed inset-0 z-50 flex justify-end"
        style="background: rgba(0,0,0,0.4); backdrop-filter: blur(3px);"
        @click.self="drawerOpen = false">
        <div class="w-full max-w-md h-full shadow-drawer overflow-y-auto drawer-panel"
          :class="dark ? 'bg-[#111827]' : 'bg-white'">
          <!-- Drawer Header -->
          <div class="flex items-center justify-between px-6 py-5 border-b sticky top-0 z-10"
            :class="dark ? 'bg-[#111827] border-[#1E293B]' : 'bg-white border-slate-200'">
            <div class="flex items-center gap-3">
              <div class="w-11 h-11 rounded-full flex items-center justify-center text-white text-sm font-bold"
                :style="`background: linear-gradient(135deg, hsl(${(selectedPatient.name.charCodeAt(0) * 40) % 360},55%,45%), hsl(${(selectedPatient.name.charCodeAt(0) * 40 + 30) % 360},55%,38%))`">
                {{ selectedPatient.name.split(' ').map((n: string) => n[0]).join('').slice(0, 2) }}
              </div>
              <div>
                <p class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">{{ selectedPatient.name }}</p>
                <p class="text-2xs" :class="dark ? 'text-slate-500' : 'text-slate-400'">{{ selectedPatient.id }} · {{ selectedPatient.age }}y {{ selectedPatient.gender }}</p>
              </div>
            </div>
            <button @click="drawerOpen = false"
              class="p-2 rounded-lg transition-colors"
              :class="dark ? 'text-slate-400 hover:bg-[#1E293B]' : 'text-slate-400 hover:bg-slate-100'">
              <X :size="18" />
            </button>
          </div>

          <!-- Drawer Content -->
          <div class="p-6 space-y-5">
            <!-- Priority Badge -->
            <div class="flex items-center gap-2">
              <span class="badge" :class="priorityBadge(selectedPatient.priority)">{{ selectedPatient.priority }} PRIORITY</span>
              <span class="badge" :class="statusBadge(selectedPatient.status)">{{ selectedPatient.status }}</span>
            </div>

            <!-- Vitals -->
            <div>
              <p class="text-xs font-bold uppercase tracking-wider mb-2" :class="dark ? 'text-slate-500' : 'text-slate-400'">Vitals</p>
              <div class="grid grid-cols-2 gap-2">
                <div class="rounded-xl p-3 border" :class="dark ? 'bg-[#1E293B] border-[#334155]' : 'bg-slate-50 border-slate-200'">
                  <p class="text-2xs font-semibold" :class="dark ? 'text-slate-500' : 'text-slate-400'">Blood Pressure</p>
                  <p class="text-base font-bold text-red-500 numeric">{{ selectedPatient.vitals.bp }}</p>
                </div>
                <div class="rounded-xl p-3 border" :class="dark ? 'bg-[#1E293B] border-[#334155]' : 'bg-slate-50 border-slate-200'">
                  <p class="text-2xs font-semibold" :class="dark ? 'text-slate-500' : 'text-slate-400'">Pulse Rate</p>
                  <p class="text-base font-bold" :class="selectedPatient.vitals.pulse > 100 ? 'text-red-500' : 'text-green-600'">{{ selectedPatient.vitals.pulse }} bpm</p>
                </div>
                <div class="rounded-xl p-3 border" :class="dark ? 'bg-[#1E293B] border-[#334155]' : 'bg-slate-50 border-slate-200'">
                  <p class="text-2xs font-semibold" :class="dark ? 'text-slate-500' : 'text-slate-400'">Temperature</p>
                  <p class="text-base font-bold" :class="selectedPatient.vitals.temp > 100 ? 'text-amber-500' : 'text-teal-600'">{{ selectedPatient.vitals.temp }}°F</p>
                </div>
                <div class="rounded-xl p-3 border" :class="dark ? 'bg-[#1E293B] border-[#334155]' : 'bg-slate-50 border-slate-200'">
                  <p class="text-2xs font-semibold" :class="dark ? 'text-slate-500' : 'text-slate-400'">SpO₂</p>
                  <p class="text-base font-bold" :class="selectedPatient.vitals.spo2 < 94 ? 'text-red-500' : 'text-green-600'">{{ selectedPatient.vitals.spo2 }}%</p>
                </div>
              </div>
            </div>

            <!-- Patient Info -->
            <div>
              <p class="text-xs font-bold uppercase tracking-wider mb-2" :class="dark ? 'text-slate-500' : 'text-slate-400'">Patient Details</p>
              <div class="space-y-2.5">
                <div v-for="row in [
                  { label: 'Department', value: selectedPatient.department },
                  { label: 'Doctor', value: selectedPatient.doctor },
                  { label: 'Room / Bed', value: `${selectedPatient.room} · ${selectedPatient.bed}` },
                  { label: 'Blood Group', value: selectedPatient.bloodGroup },
                  { label: 'Diagnosis', value: selectedPatient.diagnosis },
                  { label: 'Admission Date', value: selectedPatient.admissionDate },
                  { label: 'Insurance', value: selectedPatient.insurance },
                  { label: 'Contact', value: selectedPatient.contact },
                ]" :key="row.label"
                  class="flex items-start justify-between gap-3 pb-2.5 border-b"
                  :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
                  <p class="text-xs font-semibold" :class="dark ? 'text-slate-500' : 'text-slate-400'">{{ row.label }}</p>
                  <p class="text-xs text-right" :class="dark ? 'text-slate-300' : 'text-slate-700'">{{ row.value }}</p>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="grid grid-cols-2 gap-2 pt-2">
              <button class="btn-primary justify-center py-2.5 text-xs">Edit Patient</button>
              <button class="btn-secondary justify-center py-2.5 text-xs">Print Record</button>
              <button class="btn-secondary justify-center py-2.5 text-xs text-amber-600 border-amber-200 hover:bg-amber-50">Assign Bed</button>
              <button class="btn-secondary justify-center py-2.5 text-xs text-blue-600 border-blue-200 hover:bg-blue-50">Medical Notes</button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>
