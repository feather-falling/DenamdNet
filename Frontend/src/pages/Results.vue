<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { BarChart3, Download, FileJson, Search, X, ChevronDown, Copy, Check, ArrowRightLeft, Table as TableIcon } from 'lucide-vue-next';
import PageHeader from '../components/shared/PageHeader.vue';
import SectionHeader from '../components/shared/SectionHeader.vue';
import MetricCard from '../components/shared/MetricCard.vue';
import NetworkStatusDisplay from '../components/shared/NetworkStatusDisplay.vue';
import StatusBadge from '../components/shared/StatusBadge.vue';
import EmptyState from '../components/shared/EmptyState.vue';
import TableSkeleton from '../components/shared/TableSkeleton.vue';
import RedistributionFlow from '../components/shared/RedistributionFlow.vue';
import { usePredictionResult } from '../hooks/usePredictionResult';
import { getRecords, getSummary, getTransfers, formatDate, formatNumber, formatDays, downloadJSON, generateRunFilename, copyToClipboard } from '../lib/utils';
import { useDebounce } from '../hooks/useUtils';
import type { ResourceRecord } from '../types';
import gsap from 'gsap';

import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart } from 'echarts/charts';
import { GridComponent, TooltipComponent } from 'echarts/components';
import VChart from 'vue-echarts';

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent]);

const RISK_COLORS: Record<string, string> = { LOW: '#10b981', MEDIUM: '#f59e0b', HIGH: '#f97316', CRITICAL: '#ef4444' };

const router = useRouter();
const route = useRoute();
const activeTab = computed({
  get: () => route.query.tab as string ?? 'analytics',
  set: (val) => router.replace({ query: { ...route.query, tab: val } })
});

const { data: result, isLoading } = usePredictionResult();
const drawerRecord = ref<ResourceRecord | null>(null);
const globalFilter = ref('');
const riskFilter = ref('ALL');
const sortKey = ref('');
const sortDir = ref<'asc' | 'desc'>('asc');
const page = ref(0);
const PAGE_SIZE = 10;

const debouncedFilter = useDebounce(globalFilter, 300);

const summary = computed(() => getSummary(result.value as any));
const rawRecords = computed(() => getRecords(result.value as any) as ResourceRecord[]);
const transfers = computed(() => getTransfers(result.value as any));

const records = computed(() => {
  let filtered = [...rawRecords.value];
  if (riskFilter.value !== 'ALL') {
    filtered = filtered.filter((r) => String(r.risk_level ?? '').toUpperCase() === riskFilter.value);
  }
  if (debouncedFilter.value.trim()) {
    const q = debouncedFilter.value.toLowerCase();
    filtered = filtered.filter((r) =>
      String(r.phc_id ?? r.phc ?? '').toLowerCase().includes(q) ||
      String(r.medicine ?? '').toLowerCase().includes(q) ||
      String(r.district ?? '').toLowerCase().includes(q) ||
      String(r.state ?? '').toLowerCase().includes(q) ||
      String(r.country ?? '').toLowerCase().includes(q)
    );
  }
  if (sortKey.value) {
    filtered.sort((a, b) => {
      const av = (a as any)[sortKey.value] ?? '';
      const bv = (b as any)[sortKey.value] ?? '';
      const cmp = av < bv ? -1 : av > bv ? 1 : 0;
      return sortDir.value === 'asc' ? cmp : -cmp;
    });
  }
  return filtered;
});

const totalPages = computed(() => Math.ceil(records.value.length / PAGE_SIZE));
const pageRecords = computed(() => records.value.slice(page.value * PAGE_SIZE, (page.value + 1) * PAGE_SIZE));

const handleSort = (key: string) => {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey.value = key;
    sortDir.value = 'asc';
  }
  page.value = 0;
};

watch([debouncedFilter, riskFilter], () => {
  page.value = 0;
});

const riskDistOptions = computed(() => {
  const counts: Record<string, number> = { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 };
  rawRecords.value.forEach((r) => {
    const k = String(r.risk_level ?? '').toUpperCase();
    if (k in counts) counts[k]++;
  });
  const data = Object.entries(counts).filter(([, v]) => v > 0).map(([name, value]) => ({
    name, value, itemStyle: { color: RISK_COLORS[name], borderRadius: [5, 5, 0, 0] }
  }));
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow', shadowStyle: { color: 'rgba(241, 245, 249, 0.6)' } } },
    grid: { top: 10, right: 10, bottom: 20, left: 30 },
    xAxis: { type: 'category', data: data.map(d => d.name), axisLine: { lineStyle: { color: '#e2e8f0' } }, axisTick: { show: false }, axisLabel: { color: '#64748b', fontWeight: 600, fontSize: 11 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } }, axisLabel: { color: '#64748b', fontSize: 11 } },
    series: [{ type: 'bar', data, cursor: 'pointer' }]
  };
});

const stockoutDaysOptions = computed(() => {
  const data = rawRecords.value.slice(0, 8).map(r => ({
    name: String(r.phc_id ?? r.phc ?? '').slice(-6),
    value: r.stockout_days ?? 0,
    itemStyle: { color: '#0d9488', borderRadius: [5, 5, 0, 0] }
  }));
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 10, right: 10, bottom: 20, left: 30 },
    xAxis: { type: 'category', data: data.map(d => d.name), axisLine: { lineStyle: { color: '#e2e8f0' } }, axisTick: { show: false }, axisLabel: { color: '#94a3b8', fontSize: 10 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } }, axisLabel: { color: '#64748b', fontSize: 11 } },
    series: [{ type: 'bar', data }]
  };
});

const stockVsDemandOptions = computed(() => {
  const data = rawRecords.value.slice(0, 8);
  const categories = data.map(r => String(r.phc_id ?? r.phc ?? '').slice(-6));
  const stockData = data.map(r => ({ value: r.current_stock ?? 0, itemStyle: { color: '#0d9488', borderRadius: [5, 5, 0, 0] } }));
  const demandData = data.map(r => ({ value: r.daily_demand ?? r.forecast_demand ?? 0, itemStyle: { color: '#f59e0b', borderRadius: [5, 5, 0, 0] } }));
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 10, right: 10, bottom: 20, left: 30 },
    xAxis: { type: 'category', data: categories, axisLine: { lineStyle: { color: '#e2e8f0' } }, axisTick: { show: false }, axisLabel: { color: '#94a3b8', fontSize: 10 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } }, axisLabel: { color: '#64748b', fontSize: 11 } },
    series: [
      { name: 'Stock', type: 'bar', data: stockData },
      { name: 'Demand', type: 'bar', data: demandData }
    ]
  };
});

const onRiskBarClick = (params: any) => {
  if (params.name) {
    riskFilter.value = params.name;
    activeTab.value = 'data';
  }
};

const columns = [
  { key: 'phc_id', label: 'PHC ID' },
  { key: 'medicine', label: 'Medicine' },
  { key: 'district', label: 'Location' },
  { key: 'current_stock', label: 'Stock' },
  { key: 'stockout_days', label: 'Stockout' },
  { key: 'risk_level', label: 'Risk' },
  { key: 'stock_status', label: 'Status' },
  { key: 'anomaly', label: 'Anomaly' }
];

const TABS = [
  { id: 'analytics', label: 'Resilience Analytics', icon: BarChart3 },
  { id: 'data', label: `Resource Records (${records.value.length})`, icon: TableIcon },
  { id: 'transfers', label: `Redistribution Logistics (${transfers.value.length})`, icon: ArrowRightLeft },
  { id: 'raw', label: 'Telemetry JSON', icon: FileJson }
];

const copied = ref(false);
const searchJson = ref('');
const handleCopy = async () => {
  await copyToClipboard(JSON.stringify(result.value, null, 2));
  copied.value = true;
  setTimeout(() => copied.value = false, 2000);
};

const displayLines = computed(() => {
  if (!result.value) return [];
  const lines = JSON.stringify(result.value, null, 2).split('\n');
  if (searchJson.value.trim()) {
    const q = searchJson.value.toLowerCase();
    return lines.filter(l => l.toLowerCase().includes(q));
  }
  return lines;
});

// Animations
const vSlideInRight = {
  mounted: (el: Element) => {
    gsap.fromTo(el, { x: '100%' }, { x: 0, duration: 0.4, ease: "power3.out" });
  },
  unmounted: (el: Element, binding: any, vnode: any) => {
    gsap.to(el, { x: '100%', duration: 0.3, ease: "power3.in" });
  }
};
const onEnterDrawer = (el: Element, done: () => void) => {
  gsap.fromTo(el, { x: '100%' }, { x: 0, duration: 0.4, ease: "power3.out", onComplete: done });
};
const onLeaveDrawer = (el: Element, done: () => void) => {
  gsap.to(el, { x: '100%', duration: 0.3, ease: "power3.in", onComplete: done });
};
const onEnterFade = (el: Element, done: () => void) => {
  gsap.fromTo(el, { opacity: 0 }, { opacity: 1, duration: 0.2, onComplete: done });
};
const onLeaveFade = (el: Element, done: () => void) => {
  gsap.to(el, { opacity: 0, duration: 0.2, onComplete: done });
};
const vFadeInUp = {
  mounted: (el: Element, binding: any) => {
    gsap.fromTo(el, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.4, delay: binding.value ?? 0, ease: 'power2.out' });
  }
};
</script>

<template>
  <div class="page-container py-6 space-y-6 relative">
    <PageHeader
      title="Prediction Analytics & Exploration"
      :subtitle="result?.timestamp ? `Telemetry run logged at ${formatDate(result.timestamp as string)}` : 'No result available'"
      :icon="BarChart3"
    >
      <template #actions>
        <button
          v-if="result"
          @click="downloadJSON(result, generateRunFilename())"
          class="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors shadow-xs"
        >
          <Download :size="13" /> Export Results JSON
        </button>
      </template>
    </PageHeader>

    <div v-if="summary" v-fade-in-up class="bg-white border border-slate-200/80 rounded-xl p-5 shadow-card">
      <div class="flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <NetworkStatusDisplay :status="summary.status as string" />
        <div class="flex flex-wrap gap-4 text-xs text-slate-500 sm:ml-auto">
          <span><strong class="text-slate-800">{{ formatNumber(summary.total_phcs as number) }}</strong> PHCs Monitored</span>
          <span><strong class="text-emerald-700">{{ formatNumber(summary.controlled_phcs as number) }}</strong> Controlled</span>
          <span><strong class="text-blue-700">{{ formatNumber(summary.transfers_completed as number) }}</strong> Transfers</span>
          <span><strong class="text-slate-800">{{ rawRecords.length }}</strong> Drug Lines</span>
        </div>
      </div>
    </div>

    <div v-if="summary" class="grid grid-cols-2 md:grid-cols-4 gap-3.5">
      <MetricCard label="Total PHCs" :value="summary.total_phcs as number" variant="default" :index="0" :loading="isLoading" />
      <MetricCard label="Controlled" :value="summary.controlled_phcs as number" variant="success" :index="1" :loading="isLoading" />
      <MetricCard label="At Risk" :value="summary.at_risk_phcs as number" variant="warning" :index="2" :loading="isLoading" />
      <MetricCard label="Shortages" :value="summary.remaining_shortages as number" variant="danger" :index="3" :loading="isLoading" />
    </div>

    <div class="flex gap-2 border-b border-slate-200 pb-0.5 overflow-x-auto relative">
      <button
        v-for="tab in TABS"
        :key="tab.id"
        @click="activeTab = tab.id"
        class="relative flex items-center gap-2 px-4 py-2.5 text-xs font-bold transition-colors whitespace-nowrap cursor-pointer"
        :class="activeTab === tab.id ? 'text-teal-700' : 'text-slate-500 hover:text-slate-800'"
      >
        <component :is="tab.icon" :size="14" :class="activeTab === tab.id ? 'text-teal-600' : 'text-slate-400'" />
        <span>{{ tab.label }}</span>
        <div v-if="activeTab === tab.id" class="absolute bottom-0 left-0 right-0 h-0.5 bg-teal-600 rounded-full"></div>
      </button>
    </div>

    <!-- Analytics -->
    <div v-show="activeTab === 'analytics'">
      <EmptyState
        v-if="rawRecords.length === 0 && !isLoading"
        :icon="BarChart3"
        title="No analytics available"
        description="Run a prediction to generate analytics."
      >
        <template #action>
          <button @click="router.push('/prediction')" class="px-4 py-2 text-xs font-semibold bg-teal-600 text-white rounded-lg hover:bg-teal-700">
            Run Prediction
          </button>
        </template>
      </EmptyState>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div v-fade-in-up="0" class="bg-white border border-slate-200/80 rounded-xl p-5 shadow-card">
          <SectionHeader title="Risk Level Distribution" subtitle="Click any bar to filter records table" />
          <div class="mt-3 h-[210px]">
            <v-chart class="w-full h-full" :option="riskDistOptions" autoresize @click="onRiskBarClick" />
          </div>
        </div>

        <div v-if="rawRecords.some((r) => r.stockout_days !== undefined)" v-fade-in-up="0.1" class="bg-white border border-slate-200/80 rounded-xl p-5 shadow-card">
          <SectionHeader title="Stockout Days Buffer" subtitle="Days of remaining supply before complete stockout" />
          <div class="mt-3 h-[210px]">
            <v-chart class="w-full h-full" :option="stockoutDaysOptions" autoresize />
          </div>
        </div>

        <div v-if="rawRecords.some((r) => r.current_stock !== undefined)" v-fade-in-up="0.15" class="bg-white border border-slate-200/80 rounded-xl p-5 shadow-card md:col-span-2">
          <SectionHeader title="Stock vs Daily Demand Ratio" subtitle="Comparative analysis across sample clusters" />
          <div class="mt-3 h-[210px]">
            <v-chart class="w-full h-full" :option="stockVsDemandOptions" autoresize />
          </div>
        </div>
      </div>
    </div>

    <!-- Data -->
    <div v-show="activeTab === 'data'" class="space-y-4">
      <div class="flex flex-wrap items-center gap-2.5">
        <div class="flex items-center gap-2 border border-slate-200 rounded-lg px-3 py-2 flex-1 max-w-sm bg-white shadow-2xs">
          <Search :size="14" class="text-slate-400" />
          <input v-model="globalFilter" placeholder="Search PHC, medicine, district..." class="text-xs outline-none w-full bg-transparent text-slate-700 placeholder:text-slate-400" />
        </div>
        <select v-model="riskFilter" class="text-xs border border-slate-200 rounded-lg px-3 py-2 text-slate-700 bg-white outline-none cursor-pointer shadow-2xs font-semibold">
          <option value="ALL">All Risk Levels</option>
          <option value="LOW">Low Risk</option>
          <option value="MEDIUM">Medium Risk</option>
          <option value="HIGH">High Risk</option>
          <option value="CRITICAL">Critical Risk</option>
        </select>
        <button v-if="globalFilter || riskFilter !== 'ALL'" @click="globalFilter = ''; riskFilter = 'ALL';" class="text-xs font-semibold text-slate-500 hover:text-slate-800 flex items-center gap-1 px-2.5 py-1.5 rounded hover:bg-slate-100">
          <X :size="12" /> Clear Filters
        </button>
      </div>

      <div class="bg-white border border-slate-200/80 rounded-xl shadow-card overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50/80 border-b border-slate-200/80">
              <tr>
                <th v-for="col in columns" :key="col.key" @click="handleSort(col.key)" class="table-header-cell text-left cursor-pointer hover:bg-slate-100 select-none py-3">
                  <span class="flex items-center gap-1 font-bold text-slate-600">
                    {{ col.label }}
                    <ChevronDown :size="12" class="transition-transform" :class="[sortKey === col.key && sortDir === 'desc' ? 'rotate-180' : '', sortKey === col.key ? 'text-teal-600' : 'text-slate-300']" />
                  </span>
                </th>
                <th class="table-header-cell text-right py-3">Diagnostics</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <TableSkeleton v-if="isLoading" :rows="6" :cols="9" />
              <tr v-else-if="pageRecords.length === 0">
                <td colspan="9" class="py-12 text-center text-xs text-slate-400">No records match current search criteria.</td>
              </tr>
              <tr v-else v-for="(r, i) in pageRecords" :key="i" class="hover:bg-slate-50/80 transition-colors">
                <td class="table-cell font-mono text-xs font-bold text-slate-800">{{ r.phc_id ?? r.phc ?? '—' }}</td>
                <td class="table-cell font-medium text-slate-800">{{ r.medicine ?? '—' }}</td>
                <td class="table-cell text-xs text-slate-500">{{ [r.district, r.state].filter(Boolean).join(', ') || '—' }}</td>
                <td class="table-cell text-right numeric font-bold text-slate-800">{{ formatNumber(r.current_stock) }}</td>
                <td class="table-cell text-right numeric font-bold text-slate-700">{{ formatDays(r.stockout_days) }}</td>
                <td class="table-cell"><StatusBadge type="risk" :value="r.risk_level" /></td>
                <td class="table-cell"><StatusBadge type="status" :value="r.stock_status" /></td>
                <td class="table-cell">
                  <StatusBadge v-if="(r.anomaly ?? r.anomaly_detected) !== undefined" type="anomaly" :value="r.anomaly ?? r.anomaly_detected" />
                  <span v-else class="text-slate-300 text-xs">—</span>
                </td>
                <td class="table-cell text-right">
                  <button @click="drawerRecord = r" class="text-xs font-bold text-teal-600 hover:text-teal-700 hover:underline px-2 py-1 rounded bg-teal-50">Inspect</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="flex items-center justify-between px-4 py-3 border-t border-slate-100 bg-slate-50 text-xs text-slate-500">
          <span>{{ records.length }} total entries · Page {{ page + 1 }} of {{ Math.max(1, totalPages) }}</span>
          <div class="flex gap-1.5">
            <button @click="page = Math.max(0, page - 1)" :disabled="page === 0" class="px-3 py-1 font-semibold border border-slate-200 rounded-lg text-slate-700 hover:bg-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors">Previous</button>
            <button @click="page = Math.min(totalPages - 1, page + 1)" :disabled="page >= totalPages - 1" class="px-3 py-1 font-semibold border border-slate-200 rounded-lg text-slate-700 hover:bg-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors">Next</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Transfers -->
    <div v-show="activeTab === 'transfers'" class="space-y-6">
      <EmptyState v-if="transfers.length === 0" :icon="ArrowRightLeft" title="No transfer routes active" description="All primary health centers possess adequate inventory buffers." />
      <template v-else>
        <div class="space-y-3">
          <SectionHeader title="Dynamic Redistribution Telemetry" subtitle="Active transit corridors moving critical supplies from surplus nodes to deficit points" />
          <RedistributionFlow :transfers="transfers" :limit="10" />
        </div>
        <div class="bg-white border border-slate-200/80 rounded-xl shadow-card overflow-hidden">
          <div class="px-4 py-3 bg-slate-50/80 border-b border-slate-200">
            <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wider">Redistribution Manifest</h4>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-slate-50 border-b border-slate-100">
                <tr>
                  <th v-for="h in ['Manifest ID', 'Surplus Source', 'Deficit Destination', 'Resource', 'Quantity', 'Status']" :key="h" class="table-header-cell text-left py-2.5">{{ h }}</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr v-for="(t, i) in (transfers as any[])" :key="i" class="hover:bg-slate-50">
                  <td class="table-cell font-mono text-xs font-bold text-slate-500">{{ t.transfer_id ?? `TRF-00${i + 1}` }}</td>
                  <td class="table-cell font-mono text-xs font-bold text-emerald-800">{{ t.source_phc ?? '—' }}</td>
                  <td class="table-cell font-mono text-xs font-bold text-amber-800">{{ t.destination_phc ?? '—' }}</td>
                  <td class="table-cell font-semibold text-slate-800">{{ t.medicine ?? '—' }}</td>
                  <td class="table-cell text-right numeric font-bold text-slate-800">{{ t.quantity !== undefined ? formatNumber(Number(t.quantity)) : '—' }}</td>
                  <td class="table-cell"><StatusBadge type="transfer" :value="String(t.status ?? 'IN_TRANSIT')" /></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>
    </div>

    <!-- Raw -->
    <div v-show="activeTab === 'raw'">
      <div v-if="result" class="bg-white border border-slate-200 rounded-xl shadow-card overflow-hidden">
        <div class="flex items-center gap-2 px-4 py-3 border-b border-slate-100 bg-slate-50">
          <FileJson :size="15" class="text-slate-500" />
          <span class="text-xs font-bold text-slate-700 flex-1">Raw Prediction Telemetry JSON</span>
          <div class="flex items-center gap-1.5 border border-slate-200 rounded-lg px-2.5 overflow-hidden bg-white">
            <Search :size="12" class="text-slate-400" />
            <input v-model="searchJson" placeholder="Filter JSON..." class="text-xs py-1.5 pr-2 bg-transparent outline-none text-slate-700 w-28 placeholder:text-slate-400" />
          </div>
          <button @click="handleCopy" class="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold border border-slate-200 rounded-lg hover:bg-slate-100 transition-colors text-slate-700 bg-white">
            <Check v-if="copied" :size="12" class="text-emerald-600" />
            <Copy v-else :size="12" />
            {{ copied ? 'Copied' : 'Copy' }}
          </button>
          <button @click="downloadJSON(result, generateRunFilename('brics-raw-output'))" class="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors shadow-2xs">
            <Download :size="12" /> Download
          </button>
        </div>
        <div class="overflow-auto max-h-[600px] p-2 bg-slate-950 font-mono text-xs">
          <table class="w-full text-xs font-mono">
            <tbody>
              <tr v-for="(line, i) in displayLines" :key="i" class="hover:bg-slate-900">
                <td class="select-none text-right pr-3 pl-2 py-0.5 text-slate-600 border-r border-slate-800 w-12 numeric">{{ searchJson.trim() ? '·' : i + 1 }}</td>
                <td class="pl-3 py-0.5 whitespace-pre text-emerald-400">{{ line }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <EmptyState v-else :icon="FileJson" title="No telemetry data" description="Execute an AI prediction to view raw payload output." />
    </div>

    <transition @enter="onEnterFade" @leave="onLeaveFade" :css="false">
      <div v-if="drawerRecord" class="fixed inset-0 z-30 bg-slate-950/40 backdrop-blur-2xs" @click="drawerRecord = null"></div>
    </transition>
    <transition @enter="onEnterDrawer" @leave="onLeaveDrawer" :css="false">
      <div v-if="drawerRecord" class="fixed right-0 top-0 h-full w-88 bg-white border-l border-slate-200 shadow-2xl z-40 flex flex-col overflow-y-auto">
        <div class="flex items-center justify-between px-5 py-4 border-b border-slate-100 sticky top-0 bg-white/95 backdrop-blur-sm z-10">
          <div>
            <span class="text-sm font-bold text-slate-800">Primary Health Center</span>
            <p class="text-2xs text-slate-400 font-mono mt-0.5">{{ drawerRecord.phc_id ?? drawerRecord.phc }}</p>
          </div>
          <button @click="drawerRecord = null" class="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors">
            <X :size="16" />
          </button>
        </div>
        <div class="p-5 space-y-5">
          <div>
            <p class="text-2xs font-semibold uppercase tracking-wider text-slate-400 mb-1">Location Details</p>
            <p class="text-sm font-semibold text-slate-800">{{ [drawerRecord.district, drawerRecord.state, drawerRecord.country].filter(Boolean).join(', ') || 'Unspecified' }}</p>
          </div>
          <div v-if="drawerRecord.medicine">
            <p class="text-2xs font-semibold uppercase tracking-wider text-slate-400 mb-1">Monitored Medicine</p>
            <p class="text-sm font-bold text-teal-800 bg-teal-50 px-3 py-1.5 rounded-lg border border-teal-200/60 inline-block">{{ drawerRecord.medicine }}</p>
          </div>
          <div class="flex flex-wrap gap-2">
            <StatusBadge v-if="drawerRecord.risk_level" type="risk" :value="drawerRecord.risk_level" />
            <StatusBadge v-if="drawerRecord.stock_status" type="status" :value="drawerRecord.stock_status" />
            <StatusBadge v-if="(drawerRecord.anomaly ?? drawerRecord.anomaly_detected) !== undefined" type="anomaly" :value="drawerRecord.anomaly ?? drawerRecord.anomaly_detected" />
          </div>
          <div class="space-y-3 pt-2 border-t border-slate-100">
            <SectionHeader title="Inventory & Demand Metrics" />
            <div class="flex justify-between items-center text-xs"><span class="text-slate-500 font-medium">Current Stock</span><span class="font-bold text-slate-800 numeric">{{ formatNumber(drawerRecord.current_stock) }} units</span></div>
            <div class="flex justify-between items-center text-xs"><span class="text-slate-500 font-medium">Daily Demand</span><span class="font-bold text-slate-800 numeric">{{ formatNumber(drawerRecord.daily_demand ?? drawerRecord.forecast_demand) }} units/day</span></div>
            <div class="flex justify-between items-center text-xs"><span class="text-slate-500 font-medium">Estimated Stockout</span><span class="font-bold text-slate-800 numeric">{{ formatDays(drawerRecord.stockout_days) }}</span></div>
            <div class="flex justify-between items-center text-xs"><span class="text-slate-500 font-medium">Safety Stock Buffer</span><span class="font-bold text-slate-800 numeric">{{ formatNumber(drawerRecord.safety_stock) }} units</span></div>
            <div class="flex justify-between items-center text-xs"><span class="text-slate-500 font-medium">Procurement Lead Time</span><span class="font-bold text-slate-800 numeric">{{ drawerRecord.lead_time ? String(drawerRecord.lead_time) : '—' }}</span></div>
          </div>
          <div v-if="drawerRecord.received_units !== undefined || drawerRecord.sent_units !== undefined" class="space-y-2.5 pt-3 border-t border-slate-100">
            <SectionHeader title="Redistribution Allocation" />
            <div v-if="drawerRecord.received_units !== undefined" class="flex justify-between text-xs"><span class="text-slate-500">Units Received</span><span class="font-bold text-emerald-700">{{ formatNumber(drawerRecord.received_units) }} units</span></div>
            <div v-if="drawerRecord.transfer_source" class="flex justify-between text-xs"><span class="text-slate-500">From Node</span><span class="font-mono text-slate-700">{{ drawerRecord.transfer_source }}</span></div>
            <div v-if="drawerRecord.sent_units !== undefined" class="flex justify-between text-xs"><span class="text-slate-500">Units Dispatched</span><span class="font-bold text-blue-700">{{ formatNumber(drawerRecord.sent_units) }} units</span></div>
            <div v-if="drawerRecord.transfer_destination" class="flex justify-between text-xs"><span class="text-slate-500">To Node</span><span class="font-mono text-slate-700">{{ drawerRecord.transfer_destination }}</span></div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>
