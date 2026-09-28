<script setup lang="ts">
import { computed, ref } from 'vue';
import { useHospitalStore } from '../../stores/hospitalStore';
import { Search, Package, AlertTriangle, Plus } from 'lucide-vue-next';
import type { InventoryItem } from '../../data/mock/hospitalData';

const store = useHospitalStore();
const dark = computed(() => store.darkMode);
const search = ref('');
const filterCat = ref('ALL');
const filterStatus = ref('ALL');

const categories = computed(() => [...new Set(store.inventory.map(i => i.category))]);

const filtered = computed(() => {
  let list = [...store.inventory];
  if (search.value) {
    const q = search.value.toLowerCase();
    list = list.filter(i => i.name.toLowerCase().includes(q) || i.id.toLowerCase().includes(q));
  }
  if (filterCat.value !== 'ALL') list = list.filter(i => i.category === filterCat.value);
  if (filterStatus.value !== 'ALL') list = list.filter(i => i.status === filterStatus.value);
  return list;
});

const statusBadge = (s: InventoryItem['status']) => {
  const map: Record<string, string> = {
    'In Stock':      'badge-normal',
    'Low Stock':     'badge-high',
    'Critical Stock':'badge-critical',
    'Out of Stock':  'badge-critical',
  };
  return map[s] || 'badge-neutral';
};

const stockPct = (item: InventoryItem) => Math.min(100, Math.round((item.quantity / Math.max(item.minQuantity, 1)) * 100));
const stockColor = (item: InventoryItem) => {
  if (item.status === 'Out of Stock') return 'bg-red-500';
  if (item.status === 'Critical Stock') return 'bg-red-500';
  if (item.status === 'Low Stock') return 'bg-amber-500';
  return 'bg-teal-500';
};

const summaryStats = computed(() => ({
  total: store.inventory.length,
  lowStock: store.inventory.filter(i => i.status === 'Low Stock' || i.status === 'Critical Stock').length,
  outOfStock: store.inventory.filter(i => i.status === 'Out of Stock').length,
}));
</script>

<template>
  <div class="page-container py-6 space-y-5">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 stage-0">
      <div>
        <h2 class="text-xl font-bold" :class="dark ? 'text-white' : 'text-slate-900'">Hospital Inventory</h2>
        <p class="text-sm mt-0.5" :class="dark ? 'text-slate-400' : 'text-slate-500'">Supplies, equipment & resource management</p>
      </div>
      <button class="btn-primary px-4 py-2"><Plus :size="14" /> Add Item</button>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-3 gap-3.5 stage-1">
      <div class="h-card rounded-xl p-5" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <p class="text-2xs font-semibold text-teal-600 mb-1">Total Items</p>
        <p class="text-2xl font-bold numeric" :class="dark ? 'text-white' : 'text-slate-800'">{{ summaryStats.total }}</p>
      </div>
      <div class="h-card rounded-xl p-5" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <p class="text-2xs font-semibold text-amber-600 mb-1">⚠ Low/Critical</p>
        <p class="text-2xl font-bold numeric text-amber-600">{{ summaryStats.lowStock }}</p>
      </div>
      <div class="h-card rounded-xl p-5" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <p class="text-2xs font-semibold text-red-600 mb-1">🚨 Out of Stock</p>
        <p class="text-2xl font-bold numeric text-red-600">{{ summaryStats.outOfStock }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="flex flex-col sm:flex-row gap-3 stage-2">
      <div class="relative flex-1">
        <Search :size="14" class="absolute left-3 top-1/2 -translate-y-1/2" :class="dark ? 'text-slate-500' : 'text-slate-400'" />
        <input v-model="search" type="text" placeholder="Search inventory..." class="h-input pl-9 text-sm" />
      </div>
      <select v-model="filterCat" class="h-input w-full sm:w-44 text-sm">
        <option value="ALL">All Categories</option>
        <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
      </select>
      <select v-model="filterStatus" class="h-input w-full sm:w-40 text-sm">
        <option value="ALL">All Status</option>
        <option>In Stock</option>
        <option>Low Stock</option>
        <option>Critical Stock</option>
        <option>Out of Stock</option>
      </select>
    </div>

    <!-- Inventory Table -->
    <div class="h-card rounded-xl overflow-hidden stage-3" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
      <div class="overflow-table-scroll">
        <table class="w-full min-w-[800px]">
          <thead>
            <tr :class="dark ? 'bg-[#1E293B]/60' : 'bg-slate-50'">
              <th class="table-header-cell text-left">Item Name</th>
              <th class="table-header-cell text-left">ID</th>
              <th class="table-header-cell text-left">Category</th>
              <th class="table-header-cell text-left">Stock Level</th>
              <th class="table-header-cell text-left">Location</th>
              <th class="table-header-cell text-left">Last Updated</th>
              <th class="table-header-cell text-left">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in filtered"
              :key="item.id"
              class="table-row-hover border-t"
              :class="dark ? 'border-[#1E293B]' : 'border-slate-100'"
            >
              <td class="table-cell">
                <div class="flex items-center gap-2">
                  <div class="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0"
                    :class="dark ? 'bg-[#1E293B]' : 'bg-slate-100'">
                    <Package :size="13" :class="dark ? 'text-slate-400' : 'text-slate-500'" />
                  </div>
                  <span class="text-xs font-semibold" :class="dark ? 'text-slate-200' : 'text-slate-700'">{{ item.name }}</span>
                </div>
              </td>
              <td class="table-cell font-mono text-2xs" :class="dark ? 'text-slate-500' : 'text-slate-400'">{{ item.id }}</td>
              <td class="table-cell text-xs" :class="dark ? 'text-slate-400' : 'text-slate-500'">{{ item.category }}</td>
              <td class="table-cell w-48">
                <div class="flex items-center gap-2">
                  <div class="flex-1 progress-bar">
                    <div class="progress-fill" :class="stockColor(item)" :style="`width: ${stockPct(item)}%`"></div>
                  </div>
                  <span class="text-2xs font-semibold numeric flex-shrink-0 w-20 text-right" :class="dark ? 'text-slate-300' : 'text-slate-600'">
                    {{ item.quantity }}/{{ item.minQuantity }} min
                  </span>
                </div>
              </td>
              <td class="table-cell text-xs" :class="dark ? 'text-slate-400' : 'text-slate-500'">{{ item.location }}</td>
              <td class="table-cell text-xs" :class="dark ? 'text-slate-400' : 'text-slate-500'">{{ item.lastUpdated }}</td>
              <td class="table-cell">
                <span class="badge" :class="statusBadge(item.status)">{{ item.status }}</span>
              </td>
            </tr>
            <tr v-if="filtered.length === 0">
              <td colspan="7" class="py-12 text-center">
                <Package :size="40" class="mx-auto mb-3 opacity-20" :class="dark ? 'text-slate-400' : 'text-slate-300'" />
                <p class="text-sm" :class="dark ? 'text-slate-500' : 'text-slate-400'">No inventory items found</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
