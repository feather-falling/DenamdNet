<script setup lang="ts">
import { ref, computed } from 'vue';
import {
  AlertTriangle, Activity, Bed, Ambulance, UserCog, Heart,
  CheckCheck, Clock, MapPin, Phone, Eye, Shield, Zap
} from 'lucide-vue-next';
import { useHospitalStore } from '../../stores/hospitalStore';

const store = useHospitalStore();
const dark = computed(() => store.darkMode);

const severityConfig: Record<string, { color: string; bg: string; border: string; label: string }> = {
  critical: { color: 'text-red-600',   bg: 'bg-red-50',   border: 'border-red-200',   label: 'CRITICAL' },
  high:     { color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200', label: 'HIGH' },
  medium:   { color: 'text-blue-600',  bg: 'bg-blue-50',  border: 'border-blue-200',  label: 'MEDIUM' },
  low:      { color: 'text-green-600', bg: 'bg-green-50', border: 'border-green-200', label: 'LOW' },
};
const severityConfigDark: Record<string, { color: string; bg: string; border: string }> = {
  critical: { color: 'text-red-400',   bg: 'bg-red-900/20',   border: 'border-red-900/30' },
  high:     { color: 'text-amber-400', bg: 'bg-amber-900/20', border: 'border-amber-900/30' },
  medium:   { color: 'text-blue-400',  bg: 'bg-blue-900/20',  border: 'border-blue-900/30' },
  low:      { color: 'text-green-400', bg: 'bg-green-900/20', border: 'border-green-900/30' },
};

const alertTypeIcon: Record<string, string> = {
  'Critical Patient':   '🚨',
  'Code Blue':          '💙',
  'Ambulance Arrival':  '🚑',
  'ICU Bed Shortage':   '🛏️',
  'Low Medicine Stock': '💊',
  'Blood Bank Alert':   '🩸',
  'Equipment Failure':  '⚙️',
  'Doctor Required':    '👨‍⚕️',
};

const getSev = (sev: string) => dark.value ? severityConfigDark[sev] : { color: severityConfig[sev]?.color, bg: severityConfig[sev]?.bg, border: severityConfig[sev]?.border };

const activeAlerts = computed(() => store.alerts.filter(a => !a.acknowledged));
const acknowledgedAlerts = computed(() => store.alerts.filter(a => a.acknowledged));

const emergencyStats = [
  { label: 'Active Emergencies', value: 3, icon: AlertTriangle, color: 'red' },
  { label: 'Critical Patients', value: 5, icon: Activity, color: 'red' },
  { label: 'Emergency Beds', value: '2/8', icon: Bed, color: 'amber' },
  { label: 'Ambulances Ready', value: 6, icon: Ambulance, color: 'green' },
  { label: 'ICU Available', value: '2/12', icon: Shield, color: 'amber' },
  { label: 'Doctors on ER Duty', value: 6, icon: UserCog, color: 'blue' },
];

const colorMap: Record<string, string> = {
  red:   dark.value ? 'bg-red-900/20 text-red-400 border-red-900/30' : 'bg-red-50 text-red-700 border-red-200',
  amber: dark.value ? 'bg-amber-900/20 text-amber-400 border-amber-900/30' : 'bg-amber-50 text-amber-700 border-amber-200',
  green: dark.value ? 'bg-green-900/20 text-green-400 border-green-900/30' : 'bg-green-50 text-green-700 border-green-200',
  blue:  dark.value ? 'bg-blue-900/20 text-blue-400 border-blue-900/30' : 'bg-blue-50 text-blue-700 border-blue-200',
};

const triggerEmergency = () => {
  store.triggerEmergency({
    patient: 'John Doe',
    priority: 'CRITICAL',
    department: 'Emergency',
    required: 'ICU Bed',
    doctor: 'Dr. Sharma',
  });
};
</script>

<template>
  <div class="page-container py-6 space-y-6">
    <!-- Header with emergency visual -->
    <div class="relative overflow-hidden rounded-2xl p-6 stage-0"
      style="background: linear-gradient(135deg, #0F172A 0%, #1a0a0a 50%, #0F172A 100%); border: 1px solid rgba(220,38,38,0.3);">
      <div class="absolute top-0 left-0 right-0 h-0.5" style="background: linear-gradient(90deg, transparent, #dc2626, #ef4444, #dc2626, transparent);"></div>
      <div class="absolute inset-0 opacity-30"
        style="background: radial-gradient(ellipse at 20% 50%, rgba(220,38,38,0.2) 0%, transparent 60%), radial-gradient(ellipse at 80% 50%, rgba(220,38,38,0.1) 0%, transparent 50%);"></div>
      <div class="relative z-10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div class="flex items-center gap-4">
          <div class="relative emergency-ring">
            <div class="w-14 h-14 rounded-2xl flex items-center justify-center"
              style="background: rgba(220,38,38,0.2); border: 2px solid rgba(220,38,38,0.5);">
              <AlertTriangle :size="26" class="text-red-400" :stroke-width="2.5" />
            </div>
          </div>
          <div>
            <div class="flex items-center gap-2 mb-1">
              <span class="text-2xs font-bold uppercase tracking-widest text-red-400 animate-pulse">🔴 Live</span>
              <span class="text-2xs text-slate-500">Emergency Control Center</span>
            </div>
            <h2 class="text-2xl font-bold text-white">Emergency Center</h2>
            <p class="text-sm text-slate-400">Real-time emergency monitoring & response</p>
          </div>
        </div>
        <button
          @click="triggerEmergency"
          class="flex-shrink-0 flex items-center gap-2 px-5 py-3 rounded-xl font-bold text-sm text-white transition-all hover:scale-105"
          style="background: linear-gradient(135deg, #dc2626, #b91c1c); box-shadow: 0 4px 20px rgba(220,38,38,0.4);"
        >
          <Zap :size="16" /> Trigger Emergency
        </button>
      </div>
    </div>

    <!-- Emergency Stats Grid -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 stage-1">
      <div
        v-for="stat in emergencyStats"
        :key="stat.label"
        class="h-card p-4 rounded-xl text-center"
        :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''"
      >
        <div class="w-9 h-9 rounded-lg flex items-center justify-center mx-auto mb-2 border"
          :class="colorMap[stat.color]">
          <component :is="stat.icon" :size="16" :stroke-width="2" />
        </div>
        <p class="text-xl font-bold numeric" :class="dark ? 'text-white' : 'text-slate-800'">{{ stat.value }}</p>
        <p class="text-2xs font-medium mt-0.5" :class="dark ? 'text-slate-500' : 'text-slate-500'">{{ stat.label }}</p>
      </div>
    </div>

    <!-- Active & Acknowledged Alerts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 stage-2">
      <!-- Active Emergencies -->
      <div class="h-card rounded-xl overflow-hidden" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <div class="flex items-center justify-between px-5 py-4 border-b"
          :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
          <div class="flex items-center gap-2">
            <h3 class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">Active Emergencies</h3>
            <span v-if="activeAlerts.length" class="badge badge-critical animate-pulse">{{ activeAlerts.length }}</span>
          </div>
        </div>
        <div class="divide-y max-h-96 overflow-y-auto" :class="dark ? 'divide-[#1E293B]' : 'divide-slate-50'">
          <div
            v-for="alert in activeAlerts"
            :key="alert.id"
            class="p-5 emergency-glow transition-all"
            :class="dark ? 'border-l-4 border-l-red-600/60' : 'border-l-4 border-l-red-500'"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="flex items-start gap-3 flex-1 min-w-0">
                <span class="text-2xl flex-shrink-0">{{ alertTypeIcon[alert.type] || '⚠️' }}</span>
                <div class="min-w-0 flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <span
                      class="badge text-2xs"
                      :class="alert.severity === 'critical' ? 'badge-critical' : alert.severity === 'high' ? 'badge-high' : 'badge-info'"
                    >{{ alert.severity.toUpperCase() }}</span>
                    <span class="text-xs font-bold" :class="dark ? 'text-white' : 'text-slate-800'">{{ alert.type }}</span>
                  </div>
                  <p class="text-xs" :class="dark ? 'text-slate-400' : 'text-slate-600'">{{ alert.description }}</p>
                  <div class="flex items-center gap-3 mt-2">
                    <div class="flex items-center gap-1 text-2xs" :class="dark ? 'text-slate-500' : 'text-slate-400'">
                      <Clock :size="11" /> {{ alert.time }}
                    </div>
                    <div class="flex items-center gap-1 text-2xs" :class="dark ? 'text-slate-500' : 'text-slate-400'">
                      <MapPin :size="11" /> {{ alert.location }}
                    </div>
                  </div>
                </div>
              </div>
              <button
                @click="store.acknowledgeAlert(alert.id)"
                class="flex-shrink-0 flex items-center gap-1 px-3 py-1.5 rounded-lg text-2xs font-semibold transition-colors"
                :class="dark ? 'bg-teal-900/20 text-teal-400 hover:bg-teal-900/30' : 'bg-teal-50 text-teal-700 hover:bg-teal-100'"
              >
                <CheckCheck :size="12" /> ACK
              </button>
            </div>
          </div>
          <div v-if="activeAlerts.length === 0" class="py-12 text-center">
            <div class="w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3"
              :class="dark ? 'bg-green-900/20' : 'bg-green-50'">
              <CheckCheck :size="20" class="text-green-500" />
            </div>
            <p class="text-sm font-medium" :class="dark ? 'text-slate-400' : 'text-slate-600'">All clear! No active emergencies</p>
          </div>
        </div>
      </div>

      <!-- Acknowledged / Recent -->
      <div class="h-card rounded-xl overflow-hidden" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <div class="flex items-center justify-between px-5 py-4 border-b"
          :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
          <h3 class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">Acknowledged Alerts</h3>
          <span class="badge badge-normal">{{ acknowledgedAlerts.length }} Resolved</span>
        </div>
        <div class="divide-y max-h-96 overflow-y-auto" :class="dark ? 'divide-[#1E293B]' : 'divide-slate-50'">
          <div
            v-for="alert in acknowledgedAlerts"
            :key="alert.id"
            class="flex items-start gap-3 p-5 opacity-60"
          >
            <span class="text-xl flex-shrink-0">{{ alertTypeIcon[alert.type] || '⚠️' }}</span>
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-2 mb-0.5">
                <span class="badge badge-normal text-2xs">Acknowledged</span>
                <span class="text-xs font-semibold" :class="dark ? 'text-slate-300' : 'text-slate-700'">{{ alert.type }}</span>
              </div>
              <p class="text-2xs" :class="dark ? 'text-slate-500' : 'text-slate-400'">{{ alert.description }}</p>
              <div class="flex items-center gap-2 mt-1.5">
                <Clock :size="11" :class="dark ? 'text-slate-600' : 'text-slate-300'" />
                <span class="text-2xs" :class="dark ? 'text-slate-600' : 'text-slate-400'">{{ alert.time }} · {{ alert.location }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Critical Patients Section -->
    <div class="h-card rounded-xl overflow-hidden stage-3" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
      <div class="flex items-center justify-between px-5 py-4 border-b"
        :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
        <h3 class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">Critical Patients</h3>
        <router-link to="/patients" class="text-2xs text-teal-600 font-semibold">View all →</router-link>
      </div>
      <div class="overflow-x-auto overflow-table-scroll">
        <table class="w-full">
          <thead>
            <tr :class="dark ? 'bg-[#1E293B]/50' : 'bg-slate-50'">
              <th class="table-header-cell text-left">Patient</th>
              <th class="table-header-cell text-left">Department</th>
              <th class="table-header-cell text-left">Doctor</th>
              <th class="table-header-cell text-left">Room</th>
              <th class="table-header-cell text-left">Vitals</th>
              <th class="table-header-cell text-left">Status</th>
              <th class="table-header-cell text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="p in store.criticalPatients"
              :key="p.id"
              class="table-row-hover border-t"
              :class="dark ? 'border-[#1E293B]' : 'border-slate-100'"
            >
              <td class="table-cell">
                <div class="flex items-center gap-2.5">
                  <div class="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold"
                    :style="`background: linear-gradient(135deg, #dc2626, #b91c1c)`">
                    {{ p.name.split(' ').map((n: string) => n[0]).join('').slice(0, 2) }}
                  </div>
                  <div>
                    <p class="font-semibold text-xs" :class="dark ? 'text-slate-200' : 'text-slate-700'">{{ p.name }}</p>
                    <p class="text-2xs" :class="dark ? 'text-slate-500' : 'text-slate-400'">{{ p.id }} · {{ p.age }}y {{ p.gender }}</p>
                  </div>
                </div>
              </td>
              <td class="table-cell">
                <span class="text-xs" :class="dark ? 'text-slate-300' : 'text-slate-700'">{{ p.department }}</span>
              </td>
              <td class="table-cell">
                <span class="text-xs" :class="dark ? 'text-slate-300' : 'text-slate-700'">{{ p.doctor }}</span>
              </td>
              <td class="table-cell">
                <span class="text-xs font-mono" :class="dark ? 'text-slate-300' : 'text-slate-600'">{{ p.room }}</span>
              </td>
              <td class="table-cell">
                <div class="text-2xs space-y-0.5" :class="dark ? 'text-slate-400' : 'text-slate-500'">
                  <div>BP: <span class="font-semibold text-red-500">{{ p.vitals.bp }}</span></div>
                  <div>SpO₂: <span :class="p.vitals.spo2 < 92 ? 'font-semibold text-red-500' : 'text-slate-500'">{{ p.vitals.spo2 }}%</span></div>
                </div>
              </td>
              <td class="table-cell">
                <span class="badge badge-critical">{{ p.status }}</span>
              </td>
              <td class="table-cell">
                <div class="flex items-center gap-2">
                  <button class="flex items-center gap-1 px-2 py-1 rounded-md text-2xs font-semibold transition-colors"
                    :class="dark ? 'bg-blue-900/20 text-blue-400 hover:bg-blue-900/30' : 'bg-blue-50 text-blue-600 hover:bg-blue-100'">
                    <Eye :size="11" /> View
                  </button>
                  <button class="flex items-center gap-1 px-2 py-1 rounded-md text-2xs font-semibold transition-colors"
                    :class="dark ? 'bg-green-900/20 text-green-400 hover:bg-green-900/30' : 'bg-green-50 text-green-600 hover:bg-green-100'">
                    <Phone :size="11" /> Call
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
