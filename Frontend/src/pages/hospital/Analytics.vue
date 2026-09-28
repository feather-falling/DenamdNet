<script setup lang="ts">
import { computed } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart, BarChart, PieChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components';
import * as echarts from 'echarts/core';
import VChart from 'vue-echarts';
import { useHospitalStore } from '../../stores/hospitalStore';
import { weeklyPatientData, bedOccupancyData, departmentPerformanceData } from '../../data/mock/hospitalData';

use([CanvasRenderer, LineChart, BarChart, PieChart, GridComponent, TooltipComponent, LegendComponent]);

const store = useHospitalStore();
const dark = computed(() => store.darkMode);

const makeOption = (label: string, data: number[], color: string) => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    backgroundColor: dark.value ? '#1E293B' : '#fff',
    borderColor: dark.value ? '#334155' : '#E2E8F0',
    textStyle: { color: dark.value ? '#CBD5E1' : '#334155', fontSize: 12 },
  },
  grid: { top: 10, right: 10, bottom: 30, left: 36 },
  xAxis: {
    type: 'category',
    data: weeklyPatientData.labels,
    axisLine: { lineStyle: { color: dark.value ? '#1E293B' : '#E2E8F0' } },
    axisTick: { show: false },
    axisLabel: { color: dark.value ? '#64748B' : '#94A3B8', fontSize: 11 },
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { type: 'dashed', color: dark.value ? '#1E293B' : '#F1F5F9' } },
    axisLabel: { color: dark.value ? '#64748B' : '#94A3B8', fontSize: 11 },
  },
  series: [{
    type: 'bar',
    data,
    itemStyle: {
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color },
        { offset: 1, color: color + '60' },
      ]),
      borderRadius: [6, 6, 0, 0],
    },
    animationDuration: 1200,
  }],
});

const admissionsOpt = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    backgroundColor: dark.value ? '#1E293B' : '#fff',
    borderColor: dark.value ? '#334155' : '#E2E8F0',
    textStyle: { color: dark.value ? '#CBD5E1' : '#334155', fontSize: 12 },
  },
  legend: {
    bottom: 0, icon: 'circle', itemWidth: 8,
    textStyle: { color: dark.value ? '#94A3B8' : '#64748B', fontSize: 11 },
  },
  grid: { top: 10, right: 10, bottom: 40, left: 36 },
  xAxis: {
    type: 'category',
    data: weeklyPatientData.labels,
    axisLine: { lineStyle: { color: dark.value ? '#1E293B' : '#E2E8F0' } },
    axisTick: { show: false },
    axisLabel: { color: dark.value ? '#64748B' : '#94A3B8', fontSize: 11 },
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { type: 'dashed', color: dark.value ? '#1E293B' : '#F1F5F9' } },
    axisLabel: { color: dark.value ? '#64748B' : '#94A3B8', fontSize: 11 },
  },
  series: [
    {
      name: 'Admissions', type: 'line', data: weeklyPatientData.admissions,
      smooth: true, symbol: 'circle', symbolSize: 5,
      lineStyle: { color: '#0d9488', width: 2.5 },
      itemStyle: { color: '#0d9488' },
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(13,148,136,0.2)' }, { offset: 1, color: 'rgba(13,148,136,0)' }]) },
    },
    {
      name: 'Discharges', type: 'line', data: weeklyPatientData.discharges,
      smooth: true, symbol: 'circle', symbolSize: 5,
      lineStyle: { color: '#2563EB', width: 2.5 },
      itemStyle: { color: '#2563EB' },
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(37,99,235,0.12)' }, { offset: 1, color: 'rgba(37,99,235,0)' }]) },
    },
    {
      name: 'Emergency', type: 'line', data: weeklyPatientData.emergency,
      smooth: true, symbol: 'circle', symbolSize: 5,
      lineStyle: { color: '#DC2626', width: 2, type: 'dashed' },
      itemStyle: { color: '#DC2626' },
    },
  ],
}));

const bedOccOpt = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    backgroundColor: dark.value ? '#1E293B' : '#fff',
    borderColor: dark.value ? '#334155' : '#E2E8F0',
    textStyle: { color: dark.value ? '#CBD5E1' : '#334155', fontSize: 12 },
  },
  legend: {
    bottom: 0, icon: 'circle', itemWidth: 8,
    textStyle: { color: dark.value ? '#94A3B8' : '#64748B', fontSize: 11 },
  },
  grid: { top: 10, right: 10, bottom: 40, left: 36 },
  xAxis: {
    type: 'category', data: bedOccupancyData.labels,
    axisLine: { lineStyle: { color: dark.value ? '#1E293B' : '#E2E8F0' } },
    axisTick: { show: false },
    axisLabel: { color: dark.value ? '#64748B' : '#94A3B8', fontSize: 10 },
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { type: 'dashed', color: dark.value ? '#1E293B' : '#F1F5F9' } },
    axisLabel: { color: dark.value ? '#64748B' : '#94A3B8', fontSize: 11 },
  },
  series: [
    {
      name: 'Occupied', type: 'bar', data: bedOccupancyData.occupied,
      barMaxWidth: 20,
      itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#DC2626' }, { offset: 1, color: '#ef4444' }]), borderRadius: [4, 4, 0, 0] },
      stack: 'beds',
    },
    {
      name: 'Available', type: 'bar', data: bedOccupancyData.total.map((t, i) => t - bedOccupancyData.occupied[i]),
      barMaxWidth: 20,
      itemStyle: { color: dark.value ? '#1E293B' : '#E2E8F0', borderRadius: [4, 4, 0, 0] },
      stack: 'beds',
    },
  ],
}));

const emergencyOpt = computed(() => makeOption('Emergency', weeklyPatientData.emergency, '#DC2626'));
const deptLoadOpt = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    backgroundColor: dark.value ? '#1E293B' : '#fff',
    borderColor: dark.value ? '#334155' : '#E2E8F0',
    textStyle: { color: dark.value ? '#CBD5E1' : '#334155', fontSize: 12 },
    formatter: '{b}: {c}%',
  },
  grid: { top: 8, right: 10, bottom: 30, left: 90 },
  xAxis: {
    type: 'value', max: 100,
    axisLabel: { color: dark.value ? '#64748B' : '#94A3B8', fontSize: 10, formatter: '{value}%' },
    splitLine: { lineStyle: { type: 'dashed', color: dark.value ? '#1E293B' : '#F1F5F9' } },
  },
  yAxis: {
    type: 'category', data: departmentPerformanceData.labels,
    axisLabel: { color: dark.value ? '#64748B' : '#94A3B8', fontSize: 11 },
    axisLine: { show: false }, axisTick: { show: false },
  },
  series: [{
    type: 'bar', data: departmentPerformanceData.patientLoad, barMaxWidth: 14,
    itemStyle: {
      color: (params: any) => {
        const v = params.value;
        if (v >= 85) return new echarts.graphic.LinearGradient(1, 0, 0, 0, [{ offset: 0, color: '#DC2626' }, { offset: 1, color: '#ef4444' }]);
        if (v >= 70) return new echarts.graphic.LinearGradient(1, 0, 0, 0, [{ offset: 0, color: '#F59E0B' }, { offset: 1, color: '#fbbf24' }]);
        return new echarts.graphic.LinearGradient(1, 0, 0, 0, [{ offset: 0, color: '#0d9488' }, { offset: 1, color: '#14b8a6' }]);
      },
      borderRadius: [0, 6, 6, 0],
    },
    animationDuration: 1200,
  }],
}));
</script>

<template>
  <div class="page-container py-6 space-y-5">
    <div class="stage-0">
      <h2 class="text-xl font-bold" :class="dark ? 'text-white' : 'text-slate-900'">Analytics & Reports</h2>
      <p class="text-sm mt-0.5" :class="dark ? 'text-slate-400' : 'text-slate-500'">Hospital performance metrics & data visualization</p>
    </div>

    <!-- Patient Flow Chart -->
    <div class="h-card p-5 rounded-xl stage-1" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
      <h3 class="text-sm font-bold mb-0.5" :class="dark ? 'text-white' : 'text-slate-800'">Weekly Patient Flow</h3>
      <p class="text-2xs mb-4" :class="dark ? 'text-slate-500' : 'text-slate-400'">Admissions, discharges & emergencies over the past week</p>
      <div class="h-64">
        <v-chart class="w-full h-full" :option="admissionsOpt" autoresize />
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 stage-2">
      <!-- Bed Occupancy by Type -->
      <div class="h-card p-5 rounded-xl" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <h3 class="text-sm font-bold mb-0.5" :class="dark ? 'text-white' : 'text-slate-800'">Bed Occupancy by Type</h3>
        <p class="text-2xs mb-4" :class="dark ? 'text-slate-500' : 'text-slate-400'">Occupied vs available beds per ward type</p>
        <div class="h-52">
          <v-chart class="w-full h-full" :option="bedOccOpt" autoresize />
        </div>
      </div>

      <!-- Department Load -->
      <div class="h-card p-5 rounded-xl" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <h3 class="text-sm font-bold mb-0.5" :class="dark ? 'text-white' : 'text-slate-800'">Department Load</h3>
        <p class="text-2xs mb-4" :class="dark ? 'text-slate-500' : 'text-slate-400'">Current patient load percentage by department</p>
        <div class="h-52">
          <v-chart class="w-full h-full" :option="deptLoadOpt" autoresize />
        </div>
      </div>
    </div>

    <!-- Emergency Trend -->
    <div class="h-card p-5 rounded-xl stage-3" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
      <h3 class="text-sm font-bold mb-0.5" :class="dark ? 'text-white' : 'text-slate-800'">Emergency Cases per Day</h3>
      <p class="text-2xs mb-4" :class="dark ? 'text-slate-500' : 'text-slate-400'">Daily emergency intake trend</p>
      <div class="h-44">
        <v-chart class="w-full h-full" :option="emergencyOpt" autoresize />
      </div>
    </div>

    <!-- Key Metrics Summary -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3.5 stage-4">
      <div v-for="item in [
        { label: 'Avg Daily Admissions', value: '44', unit: 'patients/day', color: 'teal' },
        { label: 'Avg Bed Occupancy', value: '74%', unit: 'this week', color: 'amber' },
        { label: 'Emergency Avg', value: '13.6', unit: 'cases/day', color: 'red' },
        { label: 'Discharge Rate', value: '89%', unit: 'success rate', color: 'green' },
      ]" :key="item.label"
        class="h-card p-5 rounded-xl"
        :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <p class="text-2xs font-semibold mb-2"
          :class="item.color === 'teal' ? 'text-teal-600' : item.color === 'amber' ? 'text-amber-600' : item.color === 'red' ? 'text-red-600' : 'text-green-600'">
          {{ item.label }}
        </p>
        <p class="text-2xl font-bold numeric" :class="dark ? 'text-white' : 'text-slate-800'">{{ item.value }}</p>
        <p class="text-2xs mt-0.5" :class="dark ? 'text-slate-500' : 'text-slate-400'">{{ item.unit }}</p>
      </div>
    </div>
  </div>
</template>
