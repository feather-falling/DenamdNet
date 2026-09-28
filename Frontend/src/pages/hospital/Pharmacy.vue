<script setup lang="ts">
import { ref, computed } from 'vue';
import { useHospitalStore } from '../../stores/hospitalStore';
import { Search, AlertTriangle, Plus, X, TrendingDown } from 'lucide-vue-next';
import type { Medicine } from '../../data/mock/hospitalData';

const store = useHospitalStore();
const dark = computed(() => store.darkMode);

const search = ref('');
const filterStatus = ref('ALL');
const filterCat = ref('ALL');

const categories = computed(() => [...new Set(store.medicines.map(m => m.category))]);

const filtered = computed(() => {
  let list = [...store.medicines];
  if (search.value) {
    const q = search.value.toLowerCase();
    list = list.filter(m => m.name.toLowerCase().includes(q) || m.id.toLowerCase().includes(q) || m.supplier.toLowerCase().includes(q));
  }
  if (filterStatus.value !== 'ALL') list = list.filter(m => m.status === filterStatus.value);
  if (filterCat.value !== 'ALL') list = list.filter(m => m.category === filterCat.value);
  return list;
});

const statusBadgeClass = (status: Medicine['status']) => {
  const map: Record<string, string> = {
    'IN STOCK': 'badge-normal',
    'LOW STOCK': 'badge-high',
    'OUT OF STOCK': 'badge-critical',
    'EXPIRING SOON': 'badge-info',
  };
  return map[status] || 'badge-neutral';
};

const stockPct = (m: Medicine) => Math.min(100, Math.round((m.quantity / m.maxQuantity) * 100));
const stockColor = (m: Medicine) => {
  if (m.status === 'OUT OF STOCK') return 'bg-red-500';
  if (m.status === 'LOW STOCK') return 'bg-amber-500';
  if (m.status === 'EXPIRING SOON') return 'bg-blue-500';
  return 'bg-teal-500';
};

const alertMeds = computed(() => store.medicines.filter(m => m.status !== 'IN STOCK'));
</script>

<template>
  <div class="page-container py-6 space-y-5">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 stage-0">
      <div>
        <h2 class="text-xl font-bold" :class="dark ? 'text-white' : 'text-slate-900'">Pharmacy</h2>
        <p class="text-sm" :class="dark ? 'text-slate-400' : 'text-slate-500'">Medicine inventory & stock management</p>
      </div>
      <button class="btn-primary px-4 py-2"><Plus :size="14" /> Add Medicine</button>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3.5 stage-1">
      <div class="h-card rounded-xl p-5" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <p class="text-2xs font-semibold text-teal-600 mb-1">Total Medicines</p>
        <p class="text-2xl font-bold numeric" :class="dark ? 'text-white' : 'text-slate-800'">{{ store.stats.totalMedicines.toLocaleString() }}</p>
      </div>
      <div class="h-card rounded-xl p-5" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <p class="text-2xs font-semibold text-amber-600 mb-1">⚠ Low Stock</p>
        <p class="text-2xl font-bold numeric text-amber-600">{{ store.stats.lowStock }}</p>
      </div>
      <div class="h-card rounded-xl p-5" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <p class="text-2xs font-semibold text-red-600 mb-1">🚨 Out of Stock</p>
        <p class="text-2xl font-bold numeric text-red-600">{{ store.stats.outOfStock }}</p>
      </div>
      <div class="h-card rounded-xl p-5" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <p class="text-2xs font-semibold text-blue-600 mb-1">⏰ Expiring Soon</p>
        <p class="text-2xl font-bold numeric text-blue-600">{{ store.stats.expiringSoon }}</p>
      </div>
    </div>

    <!-- Medicine Alerts -->
    <div v-if="alertMeds.length" class="h-card rounded-xl overflow-hidden stage-2" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
      <div class="flex items-center gap-2 px-5 py-3.5 border-b"
        :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
        <AlertTriangle :size="16" class="text-amber-500" />
        <h3 class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">Medicine Alerts</h3>
        <span class="badge badge-high">{{ alertMeds.length }}</span>
      </div>
      <div class="p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        <div
          v-for="med in alertMeds"
          :key="med.id"
          class="flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all hover:scale-[1.01]"
          :class="med.status === 'OUT OF STOCK'
            ? (dark ? 'bg-red-900/10 border-red-900/30' : 'bg-red-50 border-red-200')
            : med.status === 'LOW STOCK'
            ? (dark ? 'bg-amber-900/10 border-amber-900/30' : 'bg-amber-50 border-amber-200')
            : (dark ? 'bg-blue-900/10 border-blue-900/30' : 'bg-blue-50 border-blue-200')"
        >
          <span class="text-xl">{{ med.status === 'OUT OF STOCK' ? '🚨' : med.status === 'LOW STOCK' ? '⚠️' : '⏰' }}</span>
          <div class="flex-1 min-w-0">
            <p class="text-xs font-semibold truncate" :class="dark ? 'text-slate-200' : 'text-slate-700'">{{ med.name }}</p>
            <p class="text-2xs" :class="med.status === 'OUT OF STOCK' ? 'text-red-600' : med.status === 'LOW STOCK' ? 'text-amber-600' : 'text-blue-600'">
              {{ med.status === 'OUT OF STOCK' ? 'Out of stock' : med.status === 'LOW STOCK' ? `${med.quantity} units remaining` : `Expires ${med.expiryDate}` }}
            </p>
          </div>
          <span class="badge flex-shrink-0" :class="statusBadgeClass(med.status)">{{ med.status.split(' ')[0] }}</span>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="flex flex-col sm:flex-row gap-3 stage-3">
      <div class="relative flex-1">
        <Search :size="14" class="absolute left-3 top-1/2 -translate-y-1/2" :class="dark ? 'text-slate-500' : 'text-slate-400'" />
        <input v-model="search" type="text" placeholder="Search medicines..." class="h-input pl-9 text-sm" />
      </div>
      <select v-model="filterStatus" class="h-input w-full sm:w-44 text-sm">
        <option value="ALL">All Status</option>
        <option value="IN STOCK">In Stock</option>
        <option value="LOW STOCK">Low Stock</option>
        <option value="OUT OF STOCK">Out of Stock</option>
        <option value="EXPIRING SOON">Expiring Soon</option>
      </select>
      <select v-model="filterCat" class="h-input w-full sm:w-44 text-sm">
        <option value="ALL">All Categories</option>
        <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
      </select>
    </div>

    <!-- Medicine Table -->
    <div class="h-card rounded-xl overflow-hidden stage-4" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
      <div class="overflow-table-scroll">
        <table class="w-full min-w-[900px]">
          <thead>
            <tr :class="dark ? 'bg-[#1E293B]/60' : 'bg-slate-50'">
              <th class="table-header-cell text-left">Medicine Name</th>
              <th class="table-header-cell text-left">ID</th>
              <th class="table-header-cell text-left">Category</th>
              <th class="table-header-cell text-left">Stock</th>
              <th class="table-header-cell text-left">Unit</th>
              <th class="table-header-cell text-left">Min Stock</th>
              <th class="table-header-cell text-left">Expiry</th>
              <th class="table-header-cell text-left">Supplier</th>
              <th class="table-header-cell text-left">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="med in filtered"
              :key="med.id"
              class="table-row-hover border-t"
              :class="dark ? 'border-[#1E293B]' : 'border-slate-100'"
            >
              <td class="table-cell">
                <span class="text-xs font-semibold" :class="dark ? 'text-slate-200' : 'text-slate-700'">{{ med.name }}</span>
              </td>
              <td class="table-cell font-mono text-2xs" :class="dark ? 'text-slate-500' : 'text-slate-400'">{{ med.id }}</td>
              <td class="table-cell text-xs" :class="dark ? 'text-slate-400' : 'text-slate-500'">{{ med.category }}</td>
              <td class="table-cell w-40">
                <div class="flex items-center gap-2">
                  <div class="flex-1 progress-bar">
                    <div class="progress-fill" :class="stockColor(med)" :style="`width: ${stockPct(med)}%`"></div>
                  </div>
                  <span class="text-2xs font-semibold numeric flex-shrink-0 w-16 text-right" :class="dark ? 'text-slate-300' : 'text-slate-600'">
                    {{ med.quantity }}/{{ med.maxQuantity }}
                  </span>
                </div>
              </td>
              <td class="table-cell text-xs" :class="dark ? 'text-slate-400' : 'text-slate-500'">{{ med.unit }}</td>
              <td class="table-cell text-xs numeric" :class="dark ? 'text-slate-400' : 'text-slate-500'">{{ med.minStock }}</td>
              <td class="table-cell text-xs" :class="dark ? 'text-slate-400' : 'text-slate-500'">{{ med.expiryDate }}</td>
              <td class="table-cell text-xs" :class="dark ? 'text-slate-300' : 'text-slate-600'">{{ med.supplier }}</td>
              <td class="table-cell">
                <span class="badge" :class="statusBadgeClass(med.status)">{{ med.status }}</span>
              </td>
            </tr>
            <tr v-if="filtered.length === 0">
              <td colspan="9" class="py-12 text-center">
                <p class="text-sm" :class="dark ? 'text-slate-500' : 'text-slate-400'">No medicines found</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
