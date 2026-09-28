<script setup lang="ts">
import { computed, ref } from 'vue';
import { useHospitalStore } from '../../stores/hospitalStore';
import { Search, Phone, UserCog } from 'lucide-vue-next';

const store = useHospitalStore();
const dark = computed(() => store.darkMode);
const search = ref('');
const filterStatus = ref('ALL');

const mockDoctors = [
  { id: 'D-001', name: 'Dr. Arun Sharma',    specialty: 'Cardiology',       department: 'Cardiology',      status: 'On Duty',    patients: 8,  experience: '18 years', contact: '+91-9876000001', avatar: 'AS' },
  { id: 'D-002', name: 'Dr. Priya Mehta',    specialty: 'Obstetrics',       department: 'Obstetrics',      status: 'On Duty',    patients: 5,  experience: '12 years', contact: '+91-9876000002', avatar: 'PM' },
  { id: 'D-003', name: 'Dr. Rajiv Gupta',    specialty: 'Neurology',        department: 'Neurology',       status: 'In Surgery', patients: 3,  experience: '22 years', contact: '+91-9876000003', avatar: 'RG' },
  { id: 'D-004', name: 'Dr. Suresh Verma',   specialty: 'General Medicine', department: 'General Medicine',status: 'On Duty',    patients: 12, experience: '15 years', contact: '+91-9876000004', avatar: 'SV' },
  { id: 'D-005', name: 'Dr. Khalid Khan',    specialty: 'Emergency',        department: 'Emergency',       status: 'On Duty',    patients: 6,  experience: '10 years', contact: '+91-9876000005', avatar: 'KK' },
  { id: 'D-006', name: 'Dr. Anitha Pillai',  specialty: 'Orthopedics',      department: 'Orthopedics',     status: 'On Duty',    patients: 7,  experience: '14 years', contact: '+91-9876000006', avatar: 'AP' },
  { id: 'D-007', name: 'Dr. Sunil Bose',     specialty: 'Pediatrics',       department: 'Pediatrics',      status: 'On Leave',   patients: 0,  experience: '9 years',  contact: '+91-9876000007', avatar: 'SB' },
  { id: 'D-008', name: 'Dr. Rekha Rao',      specialty: 'Surgery',          department: 'Surgery',         status: 'In Surgery', patients: 2,  experience: '20 years', contact: '+91-9876000008', avatar: 'RR' },
  { id: 'D-009', name: 'Dr. Amita Chandra',  specialty: 'Pulmonology',      department: 'Pulmonology',     status: 'On Duty',    patients: 9,  experience: '16 years', contact: '+91-9876000009', avatar: 'AC' },
  { id: 'D-010', name: 'Dr. Farhan Shah',    specialty: 'Endocrinology',    department: 'Endocrinology',   status: 'On Duty',    patients: 4,  experience: '11 years', contact: '+91-9876000010', avatar: 'FS' },
  { id: 'D-011', name: 'Dr. Vijay Jain',     specialty: 'Radiology',        department: 'Radiology',       status: 'On Duty',    patients: 0,  experience: '13 years', contact: '+91-9876000011', avatar: 'VJ' },
  { id: 'D-012', name: 'Dr. Nita Singh',     specialty: 'Laboratory',       department: 'Laboratory',      status: 'Off Duty',   patients: 0,  experience: '8 years',  contact: '+91-9876000012', avatar: 'NS' },
];

const filtered = computed(() => {
  let list = [...mockDoctors];
  if (search.value) {
    const q = search.value.toLowerCase();
    list = list.filter(d => d.name.toLowerCase().includes(q) || d.specialty.toLowerCase().includes(q) || d.department.toLowerCase().includes(q));
  }
  if (filterStatus.value !== 'ALL') list = list.filter(d => d.status === filterStatus.value);
  return list;
});

const statusBadge = (s: string) => ({
  'On Duty':    'badge-normal',
  'In Surgery': 'badge-high',
  'Off Duty':   'badge-neutral',
  'On Leave':   'badge-info',
})[s] || 'badge-neutral';

const avatarGradient = (name: string) =>
  `linear-gradient(135deg, hsl(${(name.charCodeAt(0) * 50) % 360},55%,45%), hsl(${(name.charCodeAt(0) * 50 + 40) % 360},55%,38%))`;

const statCounts = computed(() => ({
  'On Duty':    mockDoctors.filter(d => d.status === 'On Duty').length,
  'In Surgery': mockDoctors.filter(d => d.status === 'In Surgery').length,
  'Off Duty':   mockDoctors.filter(d => d.status === 'Off Duty').length,
  'On Leave':   mockDoctors.filter(d => d.status === 'On Leave').length,
}));
</script>

<template>
  <div class="page-container py-6 space-y-5">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 stage-0">
      <div>
        <h2 class="text-xl font-bold" :class="dark ? 'text-white' : 'text-slate-900'">Doctors</h2>
        <p class="text-sm mt-0.5" :class="dark ? 'text-slate-400' : 'text-slate-500'">{{ mockDoctors.length }} medical staff · {{ statCounts['On Duty'] + statCounts['In Surgery'] }} on duty</p>
      </div>
    </div>

    <!-- Status Quick Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3.5 stage-1">
      <div v-for="(count, status) in statCounts" :key="status"
        class="h-card rounded-xl p-4 cursor-pointer transition-all hover:scale-[1.02]"
        :class="[
          dark ? 'bg-[#111827] border-[#1E293B]' : '',
          filterStatus === status && (dark ? 'ring-2 ring-teal-500/50' : 'ring-2 ring-teal-400/50'),
        ]"
        @click="filterStatus = filterStatus === status ? 'ALL' : status"
      >
        <div class="flex items-center gap-2 mb-1">
          <span class="w-2 h-2 rounded-full"
            :class="status === 'On Duty' ? 'bg-green-500' : status === 'In Surgery' ? 'bg-amber-500 animate-pulse' : 'bg-slate-400'"></span>
          <span class="text-2xs font-semibold" :class="dark ? 'text-slate-400' : 'text-slate-500'">{{ status }}</span>
        </div>
        <p class="text-2xl font-bold numeric" :class="dark ? 'text-white' : 'text-slate-800'">{{ count }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="flex flex-col sm:flex-row gap-3 stage-2">
      <div class="relative flex-1 max-w-sm">
        <Search :size="14" class="absolute left-3 top-1/2 -translate-y-1/2" :class="dark ? 'text-slate-500' : 'text-slate-400'" />
        <input v-model="search" type="text" placeholder="Search doctors..." class="h-input pl-9 text-sm" />
      </div>
      <select v-model="filterStatus" class="h-input w-full sm:w-40 text-sm">
        <option value="ALL">All Status</option>
        <option>On Duty</option>
        <option>In Surgery</option>
        <option>Off Duty</option>
        <option>On Leave</option>
      </select>
    </div>

    <!-- Doctor Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 stage-3">
      <div
        v-for="(doc, i) in filtered"
        :key="doc.id"
        class="h-card rounded-xl overflow-hidden transition-all hover:scale-[1.01]"
        :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''"
        :style="`animation-delay: ${i * 40}ms`"
      >
        <div class="flex items-center gap-4 p-5">
          <div class="w-14 h-14 rounded-2xl flex items-center justify-center text-white text-lg font-bold flex-shrink-0"
            :style="`background: ${avatarGradient(doc.name)}`">
            {{ doc.avatar }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-bold truncate" :class="dark ? 'text-white' : 'text-slate-800'">{{ doc.name }}</p>
            <p class="text-xs" :class="dark ? 'text-slate-400' : 'text-slate-500'">{{ doc.specialty }}</p>
            <div class="flex items-center gap-2 mt-1.5">
              <span class="badge" :class="statusBadge(doc.status)">{{ doc.status }}</span>
            </div>
          </div>
        </div>

        <div class="px-5 pb-4 grid grid-cols-3 gap-3 border-t" :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
          <div class="text-center pt-3">
            <p class="text-base font-bold numeric" :class="dark ? 'text-white' : 'text-slate-800'">{{ doc.patients }}</p>
            <p class="text-2xs" :class="dark ? 'text-slate-500' : 'text-slate-400'">Patients</p>
          </div>
          <div class="text-center pt-3">
            <p class="text-base font-bold" :class="dark ? 'text-white' : 'text-slate-800'">{{ doc.experience.split(' ')[0] }}</p>
            <p class="text-2xs" :class="dark ? 'text-slate-500' : 'text-slate-400'">Yrs Exp.</p>
          </div>
          <div class="text-center pt-3">
            <p class="text-2xs font-medium" :class="dark ? 'text-slate-400' : 'text-slate-500'">{{ doc.department }}</p>
            <p class="text-2xs" :class="dark ? 'text-slate-500' : 'text-slate-400'">Dept.</p>
          </div>
        </div>

        <div class="px-5 pb-4 flex items-center gap-2">
          <button class="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-semibold transition-colors border"
            :class="dark ? 'border-[#334155] text-slate-300 hover:bg-[#1E293B]' : 'border-slate-200 text-slate-600 hover:bg-slate-50'">
            <Phone :size="12" /> Contact
          </button>
          <button class="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-semibold transition-colors"
            :class="dark ? 'bg-teal-900/20 text-teal-400 hover:bg-teal-900/30' : 'bg-teal-50 text-teal-700 hover:bg-teal-100'">
            <UserCog :size="12" /> Profile
          </button>
        </div>
      </div>

      <div v-if="filtered.length === 0" class="col-span-full py-12 text-center">
        <UserCog :size="40" class="mx-auto mb-3 opacity-20" :class="dark ? 'text-slate-400' : 'text-slate-300'" />
        <p class="text-sm" :class="dark ? 'text-slate-500' : 'text-slate-400'">No doctors found</p>
      </div>
    </div>
  </div>
</template>
