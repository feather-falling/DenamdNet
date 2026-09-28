<script setup lang="ts">
import { computed, ref, onMounted } from 'vue';
import {
  Users, Bed, UserCog, Heart, Ambulance, Pill, AlertTriangle,
  Activity, TrendingUp, ClipboardList, Calendar, Package,
  ArrowRight, Plus, Bell, Zap, BarChart3, Sparkles, Upload, FileJson, Globe
} from 'lucide-vue-next';
import { useHospitalStore } from '../../stores/hospitalStore';
import StatCard from '../../components/hospital/StatCard.vue';
import DailyPipelineModal from '../../components/orchestration/DailyPipelineModal.vue';


// ECharts
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart, BarChart, PieChart } from 'echarts/charts';
import {
  GridComponent, TooltipComponent, LegendComponent,
  DataZoomComponent, MarkLineComponent
} from 'echarts/components';
import * as echarts from 'echarts/core';
import VChart from 'vue-echarts';

use([CanvasRenderer, LineChart, BarChart, PieChart, GridComponent, TooltipComponent, LegendComponent, DataZoomComponent, MarkLineComponent]);

const store = useHospitalStore();
const showAnalysisModal = ref(false);

// Quick actions
const quickActions = [
  { label: 'Operations Map', icon: Globe, color: 'teal', path: '/map' },
  { label: 'Run Analysis', icon: Sparkles, color: 'teal', path: '/results' },
  { label: 'PHC Portal', icon: Package, color: 'blue', path: '/phc-portal' },
  { label: 'Add Patient', icon: Plus, color: 'green', path: '/patients' },
  { label: 'Assign Bed', icon: Bed, color: 'blue', path: '/beds' },
  { label: 'Pharmacy', icon: Pill, color: 'purple', path: '/pharmacy' },
  { label: 'Analytics', icon: BarChart3, color: 'amber', path: '/analytics' },
];


const quickActionColors: Record<string, string> = {
  teal:   'bg-teal-50 text-teal-700 border-teal-100 hover:bg-teal-100',
  blue:   'bg-blue-50 text-blue-700 border-blue-100 hover:bg-blue-100',
  purple: 'bg-purple-50 text-purple-700 border-purple-100 hover:bg-purple-100',
  amber:  'bg-amber-50 text-amber-700 border-amber-100 hover:bg-amber-100',
  green:  'bg-green-50 text-green-700 border-green-100 hover:bg-green-100',
  red:    'bg-red-50 text-red-700 border-red-100 hover:bg-red-100',
};
const quickActionColorsDark: Record<string, string> = {
  teal:   'bg-teal-900/20 text-teal-400 border-teal-900/40 hover:bg-teal-900/30',
  blue:   'bg-blue-900/20 text-blue-400 border-blue-900/40 hover:bg-blue-900/30',
  purple: 'bg-purple-900/20 text-purple-400 border-purple-900/40 hover:bg-purple-900/30',
  amber:  'bg-amber-900/20 text-amber-400 border-amber-900/40 hover:bg-amber-900/30',
  green:  'bg-green-900/20 text-green-400 border-green-900/40 hover:bg-green-900/30',
  red:    'bg-red-900/20 text-red-400 border-red-900/40 hover:bg-red-900/30',
};

const dark = computed(() => store.darkMode);

// Patient Admissions Chart
const admissionsChartOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    backgroundColor: dark.value ? '#1E293B' : '#fff',
    borderColor: dark.value ? '#334155' : '#E2E8F0',
    textStyle: { color: dark.value ? '#CBD5E1' : '#334155', fontSize: 12 },
  },
  legend: {
    bottom: 0,
    icon: 'circle',
    itemWidth: 8,
    textStyle: { color: dark.value ? '#94A3B8' : '#64748B', fontSize: 11 },
  },
  grid: { top: 10, right: 10, bottom: 40, left: 36 },
  xAxis: {
    type: 'category',
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
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
      name: 'Admissions',
      type: 'line',
      data: [42, 55, 38, 61, 48, 35, 28],
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { color: '#0d9488', width: 2.5 },
      itemStyle: { color: '#0d9488', borderWidth: 2, borderColor: '#fff' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(13,148,136,0.2)' },
          { offset: 1, color: 'rgba(13,148,136,0.0)' },
        ]),
      },
    },
    {
      name: 'Discharges',
      type: 'line',
      data: [35, 48, 41, 52, 44, 30, 22],
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { color: '#2563EB', width: 2.5 },
      itemStyle: { color: '#2563EB', borderWidth: 2, borderColor: '#fff' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(37,99,235,0.12)' },
          { offset: 1, color: 'rgba(37,99,235,0.0)' },
        ]),
      },
    },
    {
      name: 'Emergency',
      type: 'line',
      data: [12, 18, 9, 22, 15, 8, 11],
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { color: '#DC2626', width: 2, type: 'dashed' },
      itemStyle: { color: '#DC2626', borderWidth: 2, borderColor: '#fff' },
    },
  ],
}));

// Bed occupancy donut
const bedChartOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'item',
    backgroundColor: dark.value ? '#1E293B' : '#fff',
    borderColor: dark.value ? '#334155' : '#E2E8F0',
    textStyle: { color: dark.value ? '#CBD5E1' : '#334155', fontSize: 12 },
  },
  series: [{
    type: 'pie',
    radius: ['55%', '80%'],
    center: ['50%', '48%'],
    itemStyle: { borderColor: dark.value ? '#111827' : '#fff', borderWidth: 3 },
    label: { show: false },
    data: [
      { name: 'Occupied', value: 72,  itemStyle: { color: '#DC2626' } },
      { name: 'Available', value: 48, itemStyle: { color: '#16A34A' } },
      { name: 'Reserved', value: 10, itemStyle: { color: '#F59E0B' } },
    ],
    animationDuration: 1000,
  }],
}));

// Department bar chart
const deptChartOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    backgroundColor: dark.value ? '#1E293B' : '#fff',
    borderColor: dark.value ? '#334155' : '#E2E8F0',
    textStyle: { color: dark.value ? '#CBD5E1' : '#334155', fontSize: 12 },
    formatter: '{b}: {c}% load',
  },
  grid: { top: 8, right: 10, bottom: 30, left: 80 },
  xAxis: {
    type: 'value',
    max: 100,
    axisLabel: { color: dark.value ? '#64748B' : '#94A3B8', fontSize: 10, formatter: '{value}%' },
    splitLine: { lineStyle: { type: 'dashed', color: dark.value ? '#1E293B' : '#F1F5F9' } },
  },
  yAxis: {
    type: 'category',
    data: ['Surgery', 'Pediatrics', 'Neurology', 'Cardiology', 'ICU', 'Emergency'],
    axisLabel: { color: dark.value ? '#64748B' : '#94A3B8', fontSize: 11 },
    axisLine: { show: false },
    axisTick: { show: false },
  },
  series: [{
    type: 'bar',
    data: [58, 68, 65, 72, 83, 90],
    barMaxWidth: 16,
    itemStyle: {
      color: (params: any) => {
        const v = params.value;
        if (v >= 85) return new echarts.graphic.LinearGradient(1, 0, 0, 0, [{ offset: 0, color: '#DC2626' }, { offset: 1, color: '#ef4444' }]);
        if (v >= 70) return new echarts.graphic.LinearGradient(1, 0, 0, 0, [{ offset: 0, color: '#F59E0B' }, { offset: 1, color: '#fbbf24' }]);
        return new echarts.graphic.LinearGradient(1, 0, 0, 0, [{ offset: 0, color: '#0d9488' }, { offset: 1, color: '#14b8a6' }]);
      },
      borderRadius: [0, 8, 8, 0],
    },
    animationDuration: 1200,
  }],
}));

const recentPatients = computed(() => store.patients.slice(0, 5));
const unacknowledgedAlerts = computed(() => store.alerts.filter(a => !a.acknowledged).slice(0, 4));

const bedPct = computed(() => Math.round((store.stats.occupiedBeds / store.stats.totalBeds) * 100));
const icuPct = computed(() => Math.round((store.stats.icuOccupied / store.stats.icuBeds) * 100));
</script>

<template>
  <div class="page-container py-6 space-y-6">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 stage-0">
      <div>
        <h2 class="text-2xl font-bold" :class="dark ? 'text-white' : 'text-slate-900'">
          Good {{ new Date().getHours() < 12 ? 'Morning' : new Date().getHours() < 17 ? 'Afternoon' : 'Evening' }}, Dr. Admin 👋
        </h2>
        <p class="text-sm mt-0.5" :class="dark ? 'text-slate-400' : 'text-slate-500'">
          Here's what's happening at City General Hospital today.
        </p>
      </div>
      <div class="flex items-center gap-2">
        <button
          @click="store.triggerEmergency({ patient: 'John Doe', priority: 'CRITICAL', department: 'Emergency', required: 'ICU Bed', doctor: 'Dr. Sharma' })"
          class="btn-emergency px-4 py-2.5 text-xs"
        >
          <AlertTriangle :size="14" /> 🚨 Emergency
        </button>
      </div>
    </div>

    <!-- ─── Dual Command Banners: Analysis Pipeline & Operations Map ─── -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- Run Analysis Card -->
      <div class="relative overflow-hidden rounded-2xl bg-gradient-to-r from-teal-900 via-teal-800 to-slate-900 p-5 text-white shadow-lg border border-teal-500/30 flex flex-col justify-between gap-4">
        <div class="space-y-1.5">
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-0.5 rounded-full text-2xs font-bold uppercase tracking-wider bg-teal-500/20 text-teal-300 border border-teal-500/30">
              Operational Orchestration
            </span>
          </div>
          <h3 class="text-base sm:text-lg font-extrabold tracking-tight">Run Today's Healthcare Analysis</h3>
          <p class="text-xs text-teal-100/80 leading-relaxed">
            Upload daily telemetry (<code class="bg-black/30 px-1 py-0.5 rounded font-mono">input_today.json</code>) to trigger ML forecasting, anomaly detection, and bipartite supply redistribution.
          </p>
        </div>

        <div class="flex flex-wrap items-center gap-2.5 pt-1">
          <button
            @click="showAnalysisModal = true"
            class="flex items-center gap-2 px-4 py-2 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs shadow-md shadow-teal-500/20 transition active:scale-95 cursor-pointer"
          >
            <Upload :size="13" />
            <span>Upload JSON</span>
          </button>
          <router-link
            to="/results"
            class="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold text-xs border border-white/10 transition"
          >
            <span>View Results</span>
            <ArrowRight :size="13" />
          </router-link>
        </div>
      </div>

      <!-- BRICS PHC Operations Map Card -->
      <div class="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 p-5 text-white shadow-lg border border-indigo-500/30 flex flex-col justify-between gap-4">
        <div class="space-y-1.5">
          <div class="flex items-center justify-between gap-2">
            <span class="px-2.5 py-0.5 rounded-full text-2xs font-bold uppercase tracking-wider bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              Live Geospatial Telemetry
            </span>
            <span class="text-3xs font-mono text-indigo-300 bg-white/5 px-2 py-0.5 rounded">271 Facilities · 5 Countries</span>
          </div>
          <h3 class="text-base sm:text-lg font-extrabold tracking-tight flex items-center gap-2">
            <span>BRICS PHC Operations Map</span>
            <span class="text-xs font-normal text-slate-400">🇮🇳 🇧🇷 🇿🇦 🇨🇳 🇷🇺</span>
          </h3>
          <p class="text-xs text-indigo-100/80 leading-relaxed">
            Real-time interactive surveillance across India, Brazil, South Africa, China & Russia. Live disease outbreak zones, stockout depletion warnings & supply telemetry.
          </p>
        </div>

        <div class="flex flex-wrap items-center gap-2.5 pt-1">
          <router-link
            to="/map"
            class="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-teal-500 to-indigo-600 hover:from-teal-400 hover:to-indigo-500 text-white font-bold text-xs shadow-md shadow-indigo-500/20 transition active:scale-95"
          >
            <Globe :size="13" />
            <span>Launch Operations Map →</span>
          </router-link>
          <router-link
            to="/phc-portal"
            class="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold text-xs border border-white/10 transition"
          >
            <span>PHC Portal</span>
          </router-link>
        </div>
      </div>
    </div>

    <!-- ─── Quick Actions ─────────────────────────────── -->
    <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2.5 stage-1">
      <router-link
        v-for="qa in quickActions"
        :key="qa.label"
        :to="qa.path"
        class="flex flex-col items-center gap-2 p-3 rounded-xl border text-center transition-all hover:scale-105"
        :class="dark ? quickActionColorsDark[qa.color] : quickActionColors[qa.color]"
      >
        <component :is="qa.icon" :size="20" :stroke-width="2" />
        <span class="text-2xs font-semibold leading-tight">{{ qa.label }}</span>
      </router-link>
    </div>

    <!-- ─── KPI Cards ────────────────────────────────── -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3.5">
      <StatCard label="Total Patients" :value="store.stats.totalPatients" :icon="Users" variant="teal" :trend="12.4" trendLabel="vs last month" :index="0" />
      <StatCard label="Emergency Patients" :value="store.stats.emergencyPatients" :icon="AlertTriangle" variant="red" sublabel="Requires immediate attention" :index="1" />
      <StatCard label="Available Beds" :value="store.stats.availableBeds" :icon="Bed" variant="green" :sublabel="`${store.stats.occupiedBeds}/${store.stats.totalBeds} occupied`" :index="2" />
      <StatCard label="Doctors On Duty" :value="store.stats.doctorsOnDuty" :icon="UserCog" variant="blue" trendLabel="Across all departments" :index="3" />
      <StatCard label="Nurses On Duty" :value="store.stats.nursesOnDuty" :icon="Heart" variant="purple" :index="4" />
      <StatCard label="Pending Appointments" :value="store.stats.pendingAppointments" :icon="ClipboardList" variant="amber" :index="5" />
      <StatCard label="Ambulances Available" :value="store.stats.ambulancesAvailable" :icon="Ambulance" variant="cyan" :sublabel="`${store.stats.ambulancesOnMission} on mission`" :index="6" />
      <StatCard label="Medicine Alerts" :value="store.stats.medicineAlerts" :icon="Pill" variant="red" sublabel="Low stock / expiring" :index="7" />
    </div>

    <!-- ─── Charts Row 1 ─────────────────────────────── -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5 stage-2">
      <!-- Patient Trends -->
      <div class="lg:col-span-2 h-card p-5 rounded-xl"
        :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">Patient Admissions</h3>
            <p class="text-2xs" :class="dark ? 'text-slate-500' : 'text-slate-400'">Weekly admissions, discharges & emergencies</p>
          </div>
          <div class="flex items-center gap-1 text-2xs font-medium text-teal-600 bg-teal-50 px-2.5 py-1 rounded-full"
            :class="dark ? 'bg-teal-900/20 text-teal-400' : ''">
            <Activity :size="11" /> Live
          </div>
        </div>
        <div class="h-52">
          <v-chart class="w-full h-full" :option="admissionsChartOption" autoresize />
        </div>
      </div>

      <!-- Bed Occupancy -->
      <div class="h-card p-5 rounded-xl" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <h3 class="text-sm font-bold mb-0.5" :class="dark ? 'text-white' : 'text-slate-800'">Bed Occupancy</h3>
        <p class="text-2xs mb-3" :class="dark ? 'text-slate-500' : 'text-slate-400'">Total 120 beds</p>
        <div class="h-36">
          <v-chart class="w-full h-full" :option="bedChartOption" autoresize />
        </div>
        <div class="space-y-2 mt-2">
          <div v-for="item in [
            { label: 'Occupied', value: 72, color: 'bg-red-500' },
            { label: 'Available', value: 48, color: 'bg-green-500' },
            { label: 'Reserved', value: 10, color: 'bg-amber-500' },
          ]" :key="item.label" class="flex items-center justify-between text-xs">
            <div class="flex items-center gap-2">
              <span class="w-2 h-2 rounded-full" :class="item.color"></span>
              <span :class="dark ? 'text-slate-400' : 'text-slate-500'">{{ item.label }}</span>
            </div>
            <span class="font-semibold" :class="dark ? 'text-slate-300' : 'text-slate-700'">{{ item.value }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ─── Row 2: Alerts + Department + Recent Patients ── -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5 stage-3">
      <!-- Active Alerts -->
      <div class="h-card rounded-xl overflow-hidden" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <div class="flex items-center justify-between px-5 py-4 border-b"
          :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
          <h3 class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">Active Alerts</h3>
          <span class="badge badge-critical">{{ store.unacknowledgedAlerts }} Active</span>
        </div>
        <div class="divide-y" :class="dark ? 'divide-[#1E293B]' : 'divide-slate-50'">
          <div
            v-for="alert in unacknowledgedAlerts"
            :key="alert.id"
            class="flex items-start gap-3 px-5 py-3.5 cursor-pointer transition-colors"
            :class="dark ? 'hover:bg-[#1E293B]' : 'hover:bg-slate-50'"
            @click="store.acknowledgeAlert(alert.id)"
          >
            <span
              class="mt-0.5 w-2 h-2 rounded-full flex-shrink-0"
              :class="alert.severity === 'critical' ? 'bg-red-500 animate-pulse' : alert.severity === 'high' ? 'bg-amber-500' : 'bg-blue-400'"
            ></span>
            <div class="min-w-0 flex-1">
              <p class="text-xs font-semibold" :class="dark ? 'text-slate-200' : 'text-slate-700'">{{ alert.type }}</p>
              <p class="text-2xs mt-0.5 line-clamp-2" :class="dark ? 'text-slate-500' : 'text-slate-400'">{{ alert.description }}</p>
              <div class="flex items-center gap-2 mt-1">
                <span class="text-2xs font-medium text-teal-600">{{ alert.time }}</span>
                <span class="text-2xs" :class="dark ? 'text-slate-600' : 'text-slate-300'">·</span>
                <span class="text-2xs" :class="dark ? 'text-slate-600' : 'text-slate-400'">{{ alert.location }}</span>
              </div>
            </div>
          </div>
          <div v-if="unacknowledgedAlerts.length === 0" class="px-5 py-8 text-center">
            <p class="text-sm" :class="dark ? 'text-slate-500' : 'text-slate-400'">No active alerts ✅</p>
          </div>
        </div>
        <div class="px-5 py-3 border-t" :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
          <router-link to="/emergency" class="text-2xs text-teal-600 hover:text-teal-700 font-semibold">
            View Emergency Center →
          </router-link>
        </div>
      </div>

      <!-- Department Load -->
      <div class="h-card p-5 rounded-xl" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <h3 class="text-sm font-bold mb-0.5" :class="dark ? 'text-white' : 'text-slate-800'">Department Load</h3>
        <p class="text-2xs mb-3" :class="dark ? 'text-slate-500' : 'text-slate-400'">Current patient load by department</p>
        <div class="h-52">
          <v-chart class="w-full h-full" :option="deptChartOption" autoresize />
        </div>
      </div>

      <!-- Recent Patients -->
      <div class="h-card rounded-xl overflow-hidden" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <div class="flex items-center justify-between px-5 py-4 border-b"
          :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
          <h3 class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">Recent Patients</h3>
          <router-link to="/patients" class="text-2xs text-teal-600 hover:text-teal-700 font-semibold">View all →</router-link>
        </div>
        <div class="divide-y" :class="dark ? 'divide-[#1E293B]' : 'divide-slate-50'">
          <div
            v-for="patient in recentPatients"
            :key="patient.id"
            class="flex items-center gap-3 px-5 py-3 cursor-pointer transition-colors"
            :class="dark ? 'hover:bg-[#1E293B]' : 'hover:bg-slate-50'"
          >
            <div class="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
              :style="`background: linear-gradient(135deg, hsl(${(patient.name.charCodeAt(0) * 40) % 360},60%,45%), hsl(${(patient.name.charCodeAt(0) * 40 + 40) % 360},60%,38%))`">
              {{ patient.name.split(' ').map((n: string) => n[0]).join('').slice(0,2) }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs font-semibold truncate" :class="dark ? 'text-slate-200' : 'text-slate-700'">{{ patient.name }}</p>
              <p class="text-2xs" :class="dark ? 'text-slate-500' : 'text-slate-400'">{{ patient.department }} · {{ patient.doctor }}</p>
            </div>
            <span
              class="badge text-2xs flex-shrink-0"
              :class="patient.priority === 'CRITICAL' ? 'badge-critical' : patient.priority === 'HIGH' ? 'badge-high' : 'badge-normal'"
            >{{ patient.priority }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ─── Row 3: Bed & ICU Occupancy ─────────────────── -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-5 stage-4">
      <!-- Overall Bed Status -->
      <div class="h-card p-5 rounded-xl" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">Bed Status Overview</h3>
          <router-link to="/beds" class="text-2xs text-teal-600 hover:text-teal-700 font-semibold">Manage →</router-link>
        </div>
        <div class="space-y-3">
          <div v-for="row in [
            { label: 'General Beds', occ: 45, total: 60, color: 'bg-teal-500' },
            { label: 'ICU Beds', occ: store.stats.icuOccupied, total: store.stats.icuBeds, color: 'bg-red-500' },
            { label: 'Emergency Beds', occ: store.stats.emergencyOccupied, total: store.stats.emergencyBeds, color: 'bg-orange-500' },
            { label: 'Ventilator Beds', occ: store.stats.ventilatorOccupied, total: store.stats.ventilatorBeds, color: 'bg-purple-500' },
          ]" :key="row.label">
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs font-medium" :class="dark ? 'text-slate-400' : 'text-slate-600'">{{ row.label }}</span>
              <span class="text-xs font-semibold numeric" :class="dark ? 'text-slate-300' : 'text-slate-700'">
                {{ row.occ }}/{{ row.total }}
                <span class="text-2xs font-normal" :class="dark ? 'text-slate-500' : 'text-slate-400'">
                  ({{ Math.round((row.occ/row.total)*100) }}%)
                </span>
              </span>
            </div>
            <div class="progress-bar">
              <div
                class="progress-fill"
                :class="row.color"
                :style="`width: ${Math.round((row.occ/row.total)*100)}%`"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Medicine Alerts -->
      <div class="h-card p-5 rounded-xl" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">Medicine Alerts</h3>
          <router-link to="/pharmacy" class="text-2xs text-teal-600 hover:text-teal-700 font-semibold">Pharmacy →</router-link>
        </div>
        <div class="grid grid-cols-2 gap-3 mb-4">
          <div class="rounded-xl p-3.5 border" :class="dark ? 'bg-amber-900/10 border-amber-900/20' : 'bg-amber-50 border-amber-100'">
            <p class="text-2xs font-semibold text-amber-700 mb-1">⚠ Low Stock</p>
            <p class="text-2xl font-bold text-amber-600 numeric">{{ store.stats.lowStock }}</p>
            <p class="text-2xs text-amber-600/70">medicines</p>
          </div>
          <div class="rounded-xl p-3.5 border" :class="dark ? 'bg-red-900/10 border-red-900/20' : 'bg-red-50 border-red-100'">
            <p class="text-2xs font-semibold text-red-700 mb-1">🚨 Out of Stock</p>
            <p class="text-2xl font-bold text-red-600 numeric">{{ store.stats.outOfStock }}</p>
            <p class="text-2xs text-red-600/70">medicines</p>
          </div>
          <div class="rounded-xl p-3.5 border" :class="dark ? 'bg-orange-900/10 border-orange-900/20' : 'bg-orange-50 border-orange-100'">
            <p class="text-2xs font-semibold text-orange-700 mb-1">⏰ Expiring Soon</p>
            <p class="text-2xl font-bold text-orange-600 numeric">{{ store.stats.expiringSoon }}</p>
            <p class="text-2xs text-orange-600/70">medicines</p>
          </div>
          <div class="rounded-xl p-3.5 border" :class="dark ? 'bg-teal-900/10 border-teal-900/20' : 'bg-teal-50 border-teal-100'">
            <p class="text-2xs font-semibold text-teal-700 mb-1">✅ Total Medicines</p>
            <p class="text-2xl font-bold text-teal-600 numeric">{{ (store.stats.totalMedicines / 1000).toFixed(1) }}k</p>
            <p class="text-2xs text-teal-600/70">in stock</p>
          </div>
        </div>
        <div class="space-y-2">
          <div v-for="med in store.medicines.filter(m => m.status !== 'IN STOCK').slice(0,3)" :key="med.id"
            class="flex items-center gap-2 py-2 border-t"
            :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
            <span class="w-2 h-2 rounded-full flex-shrink-0"
              :class="med.status === 'OUT OF STOCK' ? 'bg-red-500' : med.status === 'LOW STOCK' ? 'bg-amber-500' : 'bg-orange-500'"></span>
            <span class="text-xs flex-1 truncate" :class="dark ? 'text-slate-300' : 'text-slate-700'">{{ med.name }}</span>
            <span class="text-2xs font-semibold"
              :class="med.status === 'OUT OF STOCK' ? 'text-red-600' : med.status === 'LOW STOCK' ? 'text-amber-600' : 'text-orange-600'">
              {{ med.status.replace(' ', '\u00A0') }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Pipeline Orchestration Modal -->
    <DailyPipelineModal
      :show="showAnalysisModal"
      @close="showAnalysisModal = false"
      @completed="() => {}"
    />
  </div>
</template>

