<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { LayoutDashboard, Building2, ShieldCheck, AlertTriangle, AlertCircle, Package, ArrowRightLeft, Minus, TrendingUp, Brain, BarChart3, Download, Sparkles, Zap } from 'lucide-vue-next';
import PageHeader from '../components/shared/PageHeader.vue';
import SectionHeader from '../components/shared/SectionHeader.vue';
import MetricCard from '../components/shared/MetricCard.vue';
import NetworkStatusDisplay from '../components/shared/NetworkStatusDisplay.vue';
import EmptyState from '../components/shared/EmptyState.vue';
import ChartSkeleton from '../components/shared/ChartSkeleton.vue';
import RedistributionFlow from '../components/shared/RedistributionFlow.vue';
import ScenarioSimulatorModal from '../components/shared/ScenarioSimulatorModal.vue';
import { usePredictionResult } from '../hooks/usePredictionResult';
import { getRecords, getSummary, getTransfers, formatDate, downloadJSON, generateRunFilename } from '../lib/utils';
import gsap from 'gsap';

// ECharts
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart, PieChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components';
import * as echarts from 'echarts/core';
import VChart from 'vue-echarts';

use([CanvasRenderer, BarChart, PieChart, GridComponent, TooltipComponent, LegendComponent]);

const router = useRouter();
const { data: result, isLoading } = usePredictionResult();
const simulatorOpen = ref(false);

const summary = computed(() => getSummary(result.value as any));
const records = computed(() => getRecords(result.value as any));
const transfers = computed(() => getTransfers(result.value as any));

// Risk distribution chart data
const riskOptions = computed(() => {
  if (!records.value.length) return null;
  const counts: Record<string, number> = { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 };
  records.value.forEach((r: any) => {
    const risk = String(r.risk_level ?? 'UNKNOWN').toUpperCase();
    if (risk in counts) counts[risk]++;
  });

  const categories = Object.keys(counts).filter(k => counts[k] > 0);
  const data = categories.map(k => {
    let color: any;
    if (k === 'LOW') color = new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: '#10b981'}, {offset: 1, color: '#059669'}]);
    else if (k === 'MEDIUM') color = new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: '#f59e0b'}, {offset: 1, color: '#d97706'}]);
    else if (k === 'HIGH') color = new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: '#f97316'}, {offset: 1, color: '#ea580c'}]);
    else color = new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: '#ef4444'}, {offset: 1, color: '#dc2626'}]);
    return { name: k, value: counts[k], itemStyle: { color, borderRadius: [6, 6, 0, 0] } };
  });

  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow', shadowStyle: { color: 'rgba(241, 245, 249, 0.6)' } } },
    grid: { top: 10, right: 10, bottom: 20, left: 30 },
    xAxis: { type: 'category', data: categories, axisLine: { lineStyle: { color: '#e2e8f0' } }, axisTick: { show: false }, axisLabel: { color: '#64748b', fontWeight: 600, fontSize: 11 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } }, axisLabel: { color: '#64748b', fontSize: 11 } },
    series: [{ type: 'bar', data, animationDuration: 1200 }]
  };
});

// Status distribution chart data
const statusOptions = computed(() => {
  if (!records.value.length) return null;
  const counts: Record<string, number> = { CONTROLLED: 0, ATTENTION: 0, CRITICAL: 0 };
  records.value.forEach((r: any) => {
    const s = String(r.stock_status ?? 'UNKNOWN').toUpperCase();
    if (s in counts) counts[s]++;
  });

  const data = Object.entries(counts).filter(([, v]) => v > 0).map(([k, v]) => {
    let color;
    if (k === 'CONTROLLED') color = '#10b981';
    else if (k === 'ATTENTION') color = '#f59e0b';
    else color = '#ef4444';
    return { name: k, value: v, itemStyle: { color } };
  });

  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item' },
    legend: { bottom: 0, icon: 'circle', itemWidth: 9, textStyle: { color: '#64748b', fontWeight: 500, fontSize: 12 } },
    series: [{
      type: 'pie',
      radius: ['60%', '85%'],
      center: ['50%', '45%'],
      itemStyle: { borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      data,
      animationDuration: 1200
    }]
  };
});

const onEnter = (el: Element, done: () => void) => {
  gsap.fromTo(el, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.3, ease: 'power2.out', onComplete: done });
};
const vFadeIn = {
  mounted: (el: Element, binding: any) => {
    gsap.fromTo(el, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.4, delay: binding.value ?? 0, ease: 'power2.out' });
  }
};
</script>

<template>
  <div class="page-container py-6 space-y-6">
    <PageHeader
      title="Network Resilience Overview"
      :subtitle="result?.timestamp ? `Active Telemetry · Last synchronized ${formatDate(result.timestamp as string)}` : 'Operational monitoring ready'"
      :icon="LayoutDashboard"
    >
      <template #actions>
        <button
          @click="simulatorOpen = true"
          class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-gradient-to-r from-teal-50 to-emerald-50 hover:from-teal-100 hover:to-emerald-100 text-teal-800 border border-teal-300/80 rounded-lg shadow-2xs hover:shadow-xs transition-all"
        >
          <Sparkles :size="13" class="text-teal-600 animate-pulse" />
          <span>Simulate Scenario</span>
        </button>
        <button
          v-if="result"
          @click="downloadJSON(result, generateRunFilename())"
          class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
        >
          <Download :size="13" /> JSON
        </button>
        <button
          @click="router.push('/prediction')"
          class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-all shadow-xs"
        >
          <Brain :size="13" /> Run AI Prediction
        </button>
      </template>
    </PageHeader>

    <transition @enter="onEnter" :css="false">
      <div v-if="summary || isLoading">
        <NetworkStatusDisplay v-if="summary" :status="(summary.status as string)" />
        <div v-else class="skeleton w-44 h-12 rounded-xl"></div>
      </div>
    </transition>

    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-4 gap-3.5">
      <MetricCard label="Total PHCs" :value="summary?.total_phcs as number" :icon="Building2" variant="default" :loading="isLoading" :index="0" />
      <MetricCard label="Controlled PHCs" :value="summary?.controlled_phcs as number" :icon="ShieldCheck" variant="success" :loading="isLoading" :index="1" />
      <MetricCard label="At-Risk PHCs" :value="summary?.at_risk_phcs as number" :icon="AlertTriangle" variant="warning" :loading="isLoading" :index="2" />
      <MetricCard label="Critical PHCs" :value="summary?.critical_phcs as number" :icon="AlertCircle" variant="danger" :loading="isLoading" :index="3" />
      <MetricCard label="Total Resources" :value="summary?.total_resources as number" :icon="Package" variant="default" :loading="isLoading" :index="4" />
      <MetricCard label="Transfers Dispatched" :value="summary?.transfers_completed as number" :icon="ArrowRightLeft" variant="info" :loading="isLoading" :index="5" />
      <MetricCard label="Shortage Deficits" :value="summary?.remaining_shortages as number" :icon="Minus" variant="warning" :loading="isLoading" :index="6" />
      <MetricCard label="Avg Risk Index" :value="summary?.average_risk as number" :icon="TrendingUp" variant="default" format="percent" :loading="isLoading" :index="7" />
    </div>

    <div
      v-fade-in="0.15"
      class="relative overflow-hidden rounded-xl bg-gradient-to-r from-teal-900 via-slate-900 to-slate-950 p-5 text-white shadow-lg border border-teal-500/20"
    >
      <div class="absolute right-0 top-0 bottom-0 w-1/3 bg-radial from-teal-500/10 to-transparent pointer-events-none"></div>
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 relative z-10">
        <div class="space-y-1">
          <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-teal-500/20 text-teal-300 text-2xs font-semibold tracking-wider uppercase border border-teal-500/30">
            <Zap :size="11" class="text-teal-400" /> Executive What-If Mode
          </div>
          <h3 class="text-base font-bold text-white tracking-tight">Test Network Resilience Under Sudden Shock Scenarios</h3>
          <p class="text-xs text-slate-300 max-w-xl">Simulate high-impact crises like coastal cyclone outbreaks, global sea-freight delays, or mass vaccine drives to test AI auto-redistribution.</p>
        </div>
        <button
          @click="simulatorOpen = true"
          class="flex-shrink-0 flex items-center gap-2 px-4 py-2 bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs rounded-lg transition-all shadow-md hover:shadow-teal-500/20"
        >
          <Sparkles :size="14" /> Launch Stress Test
        </button>
      </div>
    </div>

    <template v-if="!isLoading && records.length === 0">
      <EmptyState
        :icon="BarChart3"
        title="No prediction results yet"
        description="Run a prediction or trigger a stress test scenario to generate network analytics."
      >
        <template #action>
          <button @click="router.push('/prediction')" class="px-4 py-2 text-xs font-semibold bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors shadow-xs">
            Run Prediction
          </button>
        </template>
      </EmptyState>
    </template>
    
    <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <!-- Risk Distribution -->
      <ChartSkeleton v-if="isLoading" />
      <div v-else v-fade-in="0.2" class="bg-white border border-slate-200/80 rounded-xl p-5 shadow-card hover:shadow-card-hover transition-shadow">
        <SectionHeader title="Risk Level Distribution" subtitle="Hazard breakdown across all monitored medicine records" />
        <div class="mt-3 h-[230px]">
          <v-chart class="w-full h-full" :option="riskOptions" autoresize />
        </div>
      </div>

      <!-- Status Distribution -->
      <ChartSkeleton v-if="isLoading" />
      <div v-else v-fade-in="0.25" class="bg-white border border-slate-200/80 rounded-xl p-5 shadow-card hover:shadow-card-hover transition-shadow">
        <SectionHeader title="PHC Inventory Status" subtitle="Stock health stability proportion across all clusters" />
        <div class="mt-3 h-[230px]">
          <v-chart class="w-full h-full" :option="statusOptions" autoresize />
        </div>
      </div>

      <!-- Redistribution -->
      <div v-fade-in="0.3" class="lg:col-span-2 bg-white border border-slate-200/80 rounded-xl p-5 shadow-card">
        <div class="flex items-center justify-between mb-4">
          <SectionHeader title="Active Dynamic Redistribution" subtitle="Automated inventory rebalancing from surplus clusters to critical deficit nodes" />
          <button @click="router.push('/results?tab=transfers')" class="text-xs font-semibold text-teal-600 hover:text-teal-700 hover:underline flex items-center gap-1">
            View Full Logistics Log ➔
          </button>
        </div>
        <RedistributionFlow :transfers="transfers" :limit="4" />
      </div>
    </div>

    <!-- Modals -->
    <ScenarioSimulatorModal v-model:open="simulatorOpen" />
  </div>
</template>
