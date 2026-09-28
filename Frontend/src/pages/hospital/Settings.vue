<script setup lang="ts">
import { ref, computed } from 'vue';
import { useHospitalStore } from '../../stores/hospitalStore';
import { useAuthStore } from '../../stores/authStore';
import {
  Moon, Sun, Bell, Shield, Database, Globe, User, ChevronRight,
  Check, X, Key, Smartphone, FileText, Users, Copy, CheckCircle2, AlertCircle
} from 'lucide-vue-next';

const store = useHospitalStore();
const authStore = useAuthStore();
const dark = computed(() => store.darkMode);

// Modals
const showEditHospitalModal = ref(false);
const showPasswordModal = ref(false);
const show2FAModal = ref(false);
const showApiTokenModal = ref(false);
const showAuditLogModal = ref(false);
const showRoleModal = ref(false);

// Edit Hospital Form
const editHosp = ref({
  name: store.hospitalInfo.name,
  code: store.hospitalInfo.code,
  location: store.hospitalInfo.location,
  accreditation: store.hospitalInfo.accreditation,
  emergencyContact: store.hospitalInfo.emergencyContact,
});
const hospSuccess = ref(false);

const openEditHospital = () => {
  editHosp.value = { ...store.hospitalInfo };
  showEditHospitalModal.value = true;
};

const saveHospitalInfo = () => {
  store.updateHospitalInfo(editHosp.value);
  showEditHospitalModal.value = false;
  hospSuccess.value = true;
  setTimeout(() => { hospSuccess.value = false; }, 3000);
};

// Password Form
const pwdForm = ref({ current: '', newPwd: '', confirm: '' });
const pwdError = ref('');
const pwdSuccess = ref(false);

const handlePasswordChange = () => {
  pwdError.value = '';
  if (!pwdForm.value.current) {
    pwdError.value = 'Please enter your current password.';
    return;
  }
  if (!pwdForm.value.newPwd || pwdForm.value.newPwd.length < 6) {
    pwdError.value = 'New password must be at least 6 characters.';
    return;
  }
  if (pwdForm.value.newPwd !== pwdForm.value.confirm) {
    pwdError.value = 'Passwords do not match.';
    return;
  }
  pwdSuccess.value = true;
  setTimeout(() => {
    pwdSuccess.value = false;
    showPasswordModal.value = false;
    pwdForm.value = { current: '', newPwd: '', confirm: '' };
  }, 1500);
};

// 2FA state
const twoFactorEnabled = ref(true);

// API Token state
const copiedToken = ref(false);
const apiToken = ref('brics_live_sec_99a8b77f43e210cd4e5f');

const copyToken = () => {
  navigator.clipboard?.writeText(apiToken.value);
  copiedToken.value = true;
  setTimeout(() => { copiedToken.value = false; }, 2000);
};

const generateNewToken = () => {
  apiToken.value = `brics_live_sec_${Math.random().toString(36).substring(2, 12)}${Math.random().toString(36).substring(2, 10)}`;
  copiedToken.value = false;
};

// Audit logs
const auditLogs = ref([
  { id: 'LOG-1092', action: 'Daily ML Pipeline Executed', user: 'System Worker', time: '10 mins ago', ip: '127.0.0.1', status: 'SUCCESS' },
  { id: 'LOG-1091', action: 'Emergency Alert Triggered', user: 'Dr. Admin User', time: '42 mins ago', ip: '192.168.1.104', status: 'WARNING' },
  { id: 'LOG-1090', action: 'PHC Portal Login', user: 'admin@medicore.hospital', time: '2 hours ago', ip: '192.168.1.104', status: 'SUCCESS' },
  { id: 'LOG-1089', action: 'Medicine Stock Redistribution', user: 'Automation Agent', time: '5 hours ago', ip: '127.0.0.1', status: 'SUCCESS' },
  { id: 'LOG-1088', action: 'Security Policy Updated', user: 'Dr. Admin User', time: '1 day ago', ip: '192.168.1.104', status: 'SUCCESS' },
]);
</script>

<template>
  <div class="page-container py-6 space-y-5" :class="store.compactMode ? 'p-3 space-y-3' : 'p-6 space-y-5'">
    <div class="stage-0 flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold" :class="dark ? 'text-white' : 'text-slate-900'">Settings & System Configuration</h2>
        <p class="text-sm mt-0.5" :class="dark ? 'text-slate-400' : 'text-slate-500'">Manage application parameters, alerts, security, and facility profile</p>
      </div>
      <div v-if="hospSuccess" class="px-3 py-1.5 rounded-xl bg-teal-500/10 border border-teal-500/20 text-teal-600 dark:text-teal-400 text-xs font-semibold flex items-center gap-1.5">
        <Check :size="14" /> Settings updated
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <!-- Appearance -->
      <div class="h-card rounded-xl overflow-hidden stage-1" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <div class="flex items-center gap-2.5 px-5 py-4 border-b"
          :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
          <div class="w-8 h-8 rounded-lg flex items-center justify-center"
            :class="dark ? 'bg-[#1E293B] text-slate-400' : 'bg-slate-100 text-slate-600'">
            <Sun :size="15" />
          </div>
          <h3 class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">Appearance & Interface</h3>
        </div>
        <div class="p-5 space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-semibold" :class="dark ? 'text-slate-200' : 'text-slate-700'">Dark Theme (Control Room Mode)</p>
              <p class="text-2xs mt-0.5" :class="dark ? 'text-slate-500' : 'text-slate-400'">Optimized high-contrast visual display for surveillance and night ops</p>
            </div>
            <button
              @click="store.toggleDarkMode()"
              class="relative w-11 h-6 rounded-full transition-colors duration-300 flex-shrink-0"
              :class="store.darkMode ? 'bg-teal-600' : 'bg-slate-200'"
              aria-label="Toggle dark mode"
            >
              <span
                class="absolute top-0.5 w-5 h-5 rounded-full bg-white shadow-sm transition-transform duration-300"
                :class="store.darkMode ? 'translate-x-5' : 'translate-x-0.5'"
              ></span>
            </button>
          </div>
          <div class="flex items-center justify-between py-3 border-t" :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
            <div>
              <p class="text-sm font-semibold" :class="dark ? 'text-slate-200' : 'text-slate-700'">Compact Density Mode</p>
              <p class="text-2xs mt-0.5" :class="dark ? 'text-slate-500' : 'text-slate-400'">Tighter spacing for multi-monitor operations control centers</p>
            </div>
            <button
              @click="store.toggleCompactMode()"
              class="relative w-11 h-6 rounded-full transition-colors duration-300 flex-shrink-0"
              :class="store.compactMode ? 'bg-teal-600' : 'bg-slate-200'"
              aria-label="Toggle compact mode"
            >
              <span
                class="absolute top-0.5 w-5 h-5 rounded-full bg-white shadow-sm transition-transform duration-300"
                :class="store.compactMode ? 'translate-x-5' : 'translate-x-0.5'"
              ></span>
            </button>
          </div>
        </div>
      </div>

      <!-- Notifications -->
      <div class="h-card rounded-xl overflow-hidden stage-2" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <div class="flex items-center gap-2.5 px-5 py-4 border-b"
          :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
          <div class="w-8 h-8 rounded-lg flex items-center justify-center"
            :class="dark ? 'bg-[#1E293B] text-slate-400' : 'bg-slate-100 text-slate-600'">
            <Bell :size="15" />
          </div>
          <h3 class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">Alert & Notification Triggers</h3>
        </div>
        <div class="p-5 space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-semibold" :class="dark ? 'text-slate-200' : 'text-slate-700'">Emergency Outbreak Alerts</p>
              <p class="text-2xs mt-0.5" :class="dark ? 'text-slate-500' : 'text-slate-400'">Real-time ML spike detection and disease alerts</p>
            </div>
            <button
              @click="store.updateNotificationPref('emergencyAlerts', !store.notificationPreferences.emergencyAlerts)"
              class="relative w-11 h-6 rounded-full transition-colors flex-shrink-0"
              :class="store.notificationPreferences.emergencyAlerts ? 'bg-teal-600' : 'bg-slate-200'"
            >
              <span class="absolute top-0.5 w-5 h-5 rounded-full bg-white shadow-sm transition-transform"
                :class="store.notificationPreferences.emergencyAlerts ? 'translate-x-5' : 'translate-x-0.5'"></span>
            </button>
          </div>

          <div class="flex items-center justify-between pt-3 border-t" :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
            <div>
              <p class="text-sm font-semibold" :class="dark ? 'text-slate-200' : 'text-slate-700'">Medicine Stockout Risk</p>
              <p class="text-2xs mt-0.5" :class="dark ? 'text-slate-500' : 'text-slate-400'">Warn when facility projected stockout is under 5 days</p>
            </div>
            <button
              @click="store.updateNotificationPref('stockAlerts', !store.notificationPreferences.stockAlerts)"
              class="relative w-11 h-6 rounded-full transition-colors flex-shrink-0"
              :class="store.notificationPreferences.stockAlerts ? 'bg-teal-600' : 'bg-slate-200'"
            >
              <span class="absolute top-0.5 w-5 h-5 rounded-full bg-white shadow-sm transition-transform"
                :class="store.notificationPreferences.stockAlerts ? 'translate-x-5' : 'translate-x-0.5'"></span>
            </button>
          </div>

          <div class="flex items-center justify-between pt-3 border-t" :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
            <div>
              <p class="text-sm font-semibold" :class="dark ? 'text-slate-200' : 'text-slate-700'">Bed Availability Updates</p>
              <p class="text-2xs mt-0.5" :class="dark ? 'text-slate-500' : 'text-slate-400'">Real-time ICU and emergency bed allocation status</p>
            </div>
            <button
              @click="store.updateNotificationPref('bedAvailability', !store.notificationPreferences.bedAvailability)"
              class="relative w-11 h-6 rounded-full transition-colors flex-shrink-0"
              :class="store.notificationPreferences.bedAvailability ? 'bg-teal-600' : 'bg-slate-200'"
            >
              <span class="absolute top-0.5 w-5 h-5 rounded-full bg-white shadow-sm transition-transform"
                :class="store.notificationPreferences.bedAvailability ? 'translate-x-5' : 'translate-x-0.5'"></span>
            </button>
          </div>

          <div class="flex items-center justify-between pt-3 border-t" :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
            <div>
              <p class="text-sm font-semibold" :class="dark ? 'text-slate-200' : 'text-slate-700'">Redistribution Sync Reminders</p>
              <p class="text-2xs mt-0.5" :class="dark ? 'text-slate-500' : 'text-slate-400'">Daily pipeline execution and dispatch confirmations</p>
            </div>
            <button
              @click="store.updateNotificationPref('appointmentReminders', !store.notificationPreferences.appointmentReminders)"
              class="relative w-11 h-6 rounded-full transition-colors flex-shrink-0"
              :class="store.notificationPreferences.appointmentReminders ? 'bg-teal-600' : 'bg-slate-200'"
            >
              <span class="absolute top-0.5 w-5 h-5 rounded-full bg-white shadow-sm transition-transform"
                :class="store.notificationPreferences.appointmentReminders ? 'translate-x-5' : 'translate-x-0.5'"></span>
            </button>
          </div>
        </div>
      </div>

      <!-- Hospital Info -->
      <div class="h-card rounded-xl overflow-hidden stage-3" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <div class="flex items-center gap-2.5 px-5 py-4 border-b"
          :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
          <div class="w-8 h-8 rounded-lg flex items-center justify-center"
            :class="dark ? 'bg-[#1E293B] text-slate-400' : 'bg-slate-100 text-slate-600'">
            <Database :size="15" />
          </div>
          <h3 class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">Facility Master Record</h3>
        </div>
        <div class="p-5 space-y-3">
          <div class="flex items-center justify-between text-sm pb-3 border-b" :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
            <span class="text-xs font-semibold" :class="dark ? 'text-slate-500' : 'text-slate-400'">Facility Name</span>
            <span class="text-xs font-bold" :class="dark ? 'text-slate-200' : 'text-slate-800'">{{ store.hospitalInfo.name }}</span>
          </div>
          <div class="flex items-center justify-between text-sm pb-3 border-b" :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
            <span class="text-xs font-semibold" :class="dark ? 'text-slate-500' : 'text-slate-400'">Facility Code</span>
            <span class="text-xs font-mono" :class="dark ? 'text-teal-400' : 'text-teal-700'">{{ store.hospitalInfo.code }}</span>
          </div>
          <div class="flex items-center justify-between text-sm pb-3 border-b" :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
            <span class="text-xs font-semibold" :class="dark ? 'text-slate-500' : 'text-slate-400'">Location / Jurisdiction</span>
            <span class="text-xs" :class="dark ? 'text-slate-300' : 'text-slate-700'">{{ store.hospitalInfo.location }}</span>
          </div>
          <div class="flex items-center justify-between text-sm pb-3 border-b" :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
            <span class="text-xs font-semibold" :class="dark ? 'text-slate-500' : 'text-slate-400'">Accreditation Standard</span>
            <span class="text-xs font-semibold" :class="dark ? 'text-teal-400' : 'text-teal-600'">{{ store.hospitalInfo.accreditation }}</span>
          </div>
          <div class="flex items-center justify-between text-sm pb-3 border-b" :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
            <span class="text-xs font-semibold" :class="dark ? 'text-slate-500' : 'text-slate-400'">Emergency Hotline</span>
            <span class="text-xs" :class="dark ? 'text-slate-300' : 'text-slate-700'">{{ store.hospitalInfo.emergencyContact }}</span>
          </div>
          <button @click="openEditHospital" class="btn-secondary w-full justify-center py-2 text-xs mt-2">
            Edit Facility Information
          </button>
        </div>
      </div>

      <!-- Security -->
      <div class="h-card rounded-xl overflow-hidden stage-4" :class="dark ? 'bg-[#111827] border-[#1E293B]' : ''">
        <div class="flex items-center gap-2.5 px-5 py-4 border-b"
          :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
          <div class="w-8 h-8 rounded-lg flex items-center justify-center"
            :class="dark ? 'bg-[#1E293B] text-slate-400' : 'bg-slate-100 text-slate-600'">
            <Shield :size="15" />
          </div>
          <h3 class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">Security & Access Controls</h3>
        </div>
        <div class="p-5 space-y-2">
          <button
            @click="showPasswordModal = true"
            class="flex items-center justify-between w-full px-3 py-3 rounded-lg text-sm transition-colors"
            :class="dark ? 'text-slate-300 hover:bg-[#1E293B]' : 'text-slate-700 hover:bg-slate-50'"
          >
            <span class="flex items-center gap-2.5"><Key :size="15" class="text-teal-500" /> Change Security Password</span>
            <ChevronRight :size="15" :class="dark ? 'text-slate-600' : 'text-slate-300'" />
          </button>

          <button
            @click="show2FAModal = true"
            class="flex items-center justify-between w-full px-3 py-3 rounded-lg text-sm transition-colors"
            :class="dark ? 'text-slate-300 hover:bg-[#1E293B]' : 'text-slate-700 hover:bg-slate-50'"
          >
            <span class="flex items-center gap-2.5"><Smartphone :size="15" class="text-blue-500" /> Two-Factor Authentication (2FA)</span>
            <span class="text-2xs font-semibold px-2 py-0.5 rounded" :class="twoFactorEnabled ? 'bg-teal-500/10 text-teal-600' : 'bg-slate-100 text-slate-500'">
              {{ twoFactorEnabled ? 'Active' : 'Disabled' }}
            </span>
          </button>

          <button
            @click="showApiTokenModal = true"
            class="flex items-center justify-between w-full px-3 py-3 rounded-lg text-sm transition-colors"
            :class="dark ? 'text-slate-300 hover:bg-[#1E293B]' : 'text-slate-700 hover:bg-slate-50'"
          >
            <span class="flex items-center gap-2.5"><Globe :size="15" class="text-purple-500" /> API Access Keys & Tokens</span>
            <ChevronRight :size="15" :class="dark ? 'text-slate-600' : 'text-slate-300'" />
          </button>

          <button
            @click="showAuditLogModal = true"
            class="flex items-center justify-between w-full px-3 py-3 rounded-lg text-sm transition-colors"
            :class="dark ? 'text-slate-300 hover:bg-[#1E293B]' : 'text-slate-700 hover:bg-slate-50'"
          >
            <span class="flex items-center gap-2.5"><FileText :size="15" class="text-amber-500" /> Operational Audit Trail</span>
            <ChevronRight :size="15" :class="dark ? 'text-slate-600' : 'text-slate-300'" />
          </button>

          <button
            @click="showRoleModal = true"
            class="flex items-center justify-between w-full px-3 py-3 rounded-lg text-sm transition-colors"
            :class="dark ? 'text-slate-300 hover:bg-[#1E293B]' : 'text-slate-700 hover:bg-slate-50'"
          >
            <span class="flex items-center gap-2.5"><Users :size="15" class="text-rose-500" /> Role & Privilege Matrix</span>
            <ChevronRight :size="15" :class="dark ? 'text-slate-600' : 'text-slate-300'" />
          </button>
        </div>
      </div>
    </div>

    <!-- System Info Footer -->
    <div class="text-center py-4 stage-5">
      <p class="text-2xs" :class="dark ? 'text-slate-600' : 'text-slate-400'">
        BRICS Smart Health & Supply Chain Resilience System v2.6.0 · Multi-Horizon Predictive Analytics & Autonomous Redistribution
      </p>
    </div>

    <!-- Edit Hospital Modal -->
    <teleport to="body">
      <div v-if="showEditHospitalModal" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="w-full max-w-md rounded-2xl border shadow-2xl p-6 space-y-4" :class="dark ? 'bg-[#111827] border-[#1E293B]' : 'bg-white border-slate-200'">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">Edit Facility Information</h3>
            <button @click="showEditHospitalModal = false" class="p-1 rounded-lg text-slate-400 hover:text-slate-600"><X :size="16" /></button>
          </div>
          <div class="space-y-3">
            <div>
              <label class="text-2xs font-bold uppercase text-slate-400">Facility Name</label>
              <input v-model="editHosp.name" class="w-full mt-1 px-3 py-2 text-xs rounded-xl border outline-none" :class="dark ? 'bg-[#1E293B] border-[#334155] text-white' : 'bg-slate-50 border-slate-200 text-slate-800'" />
            </div>
            <div>
              <label class="text-2xs font-bold uppercase text-slate-400">Facility Code</label>
              <input v-model="editHosp.code" class="w-full mt-1 px-3 py-2 text-xs rounded-xl border outline-none font-mono" :class="dark ? 'bg-[#1E293B] border-[#334155] text-white' : 'bg-slate-50 border-slate-200 text-slate-800'" />
            </div>
            <div>
              <label class="text-2xs font-bold uppercase text-slate-400">Location</label>
              <input v-model="editHosp.location" class="w-full mt-1 px-3 py-2 text-xs rounded-xl border outline-none" :class="dark ? 'bg-[#1E293B] border-[#334155] text-white' : 'bg-slate-50 border-slate-200 text-slate-800'" />
            </div>
            <div>
              <label class="text-2xs font-bold uppercase text-slate-400">Accreditation</label>
              <input v-model="editHosp.accreditation" class="w-full mt-1 px-3 py-2 text-xs rounded-xl border outline-none" :class="dark ? 'bg-[#1E293B] border-[#334155] text-white' : 'bg-slate-50 border-slate-200 text-slate-800'" />
            </div>
            <div>
              <label class="text-2xs font-bold uppercase text-slate-400">Emergency Contact</label>
              <input v-model="editHosp.emergencyContact" class="w-full mt-1 px-3 py-2 text-xs rounded-xl border outline-none" :class="dark ? 'bg-[#1E293B] border-[#334155] text-white' : 'bg-slate-50 border-slate-200 text-slate-800'" />
            </div>
          </div>
          <div class="flex gap-2 pt-2">
            <button @click="saveHospitalInfo" class="flex-1 py-2.5 rounded-xl text-xs font-bold text-white bg-teal-600 hover:bg-teal-700">Save Changes</button>
            <button @click="showEditHospitalModal = false" class="px-4 py-2.5 rounded-xl text-xs font-semibold border" :class="dark ? 'border-[#334155] text-slate-300' : 'border-slate-200 text-slate-600'">Cancel</button>
          </div>
        </div>
      </div>

      <!-- Password Modal -->
      <div v-if="showPasswordModal" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="w-full max-w-md rounded-2xl border shadow-2xl p-6 space-y-4" :class="dark ? 'bg-[#111827] border-[#1E293B]' : 'bg-white border-slate-200'">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">Change Security Password</h3>
            <button @click="showPasswordModal = false" class="p-1 rounded-lg text-slate-400 hover:text-slate-600"><X :size="16" /></button>
          </div>
          <div v-if="pwdError" class="p-2.5 rounded-xl bg-red-500/10 border border-red-500/20 text-red-500 text-xs">{{ pwdError }}</div>
          <div v-if="pwdSuccess" class="p-2.5 rounded-xl bg-teal-500/10 border border-teal-500/20 text-teal-600 text-xs flex items-center gap-1.5"><Check :size="14" /> Password changed successfully!</div>
          <div class="space-y-3">
            <div>
              <label class="text-2xs font-bold uppercase text-slate-400">Current Password</label>
              <input v-model="pwdForm.current" type="password" class="w-full mt-1 px-3 py-2 text-xs rounded-xl border outline-none" :class="dark ? 'bg-[#1E293B] border-[#334155] text-white' : 'bg-slate-50 border-slate-200 text-slate-800'" />
            </div>
            <div>
              <label class="text-2xs font-bold uppercase text-slate-400">New Password</label>
              <input v-model="pwdForm.newPwd" type="password" class="w-full mt-1 px-3 py-2 text-xs rounded-xl border outline-none" :class="dark ? 'bg-[#1E293B] border-[#334155] text-white' : 'bg-slate-50 border-slate-200 text-slate-800'" />
            </div>
            <div>
              <label class="text-2xs font-bold uppercase text-slate-400">Confirm New Password</label>
              <input v-model="pwdForm.confirm" type="password" class="w-full mt-1 px-3 py-2 text-xs rounded-xl border outline-none" :class="dark ? 'bg-[#1E293B] border-[#334155] text-white' : 'bg-slate-50 border-slate-200 text-slate-800'" />
            </div>
          </div>
          <div class="flex gap-2 pt-2">
            <button @click="handlePasswordChange" class="flex-1 py-2.5 rounded-xl text-xs font-bold text-white bg-teal-600 hover:bg-teal-700">Update Password</button>
            <button @click="showPasswordModal = false" class="px-4 py-2.5 rounded-xl text-xs font-semibold border" :class="dark ? 'border-[#334155] text-slate-300' : 'border-slate-200 text-slate-600'">Cancel</button>
          </div>
        </div>
      </div>

      <!-- 2FA Modal -->
      <div v-if="show2FAModal" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="w-full max-w-md rounded-2xl border shadow-2xl p-6 space-y-4" :class="dark ? 'bg-[#111827] border-[#1E293B]' : 'bg-white border-slate-200'">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">Two-Factor Authentication</h3>
            <button @click="show2FAModal = false" class="p-1 rounded-lg text-slate-400 hover:text-slate-600"><X :size="16" /></button>
          </div>
          <p class="text-xs text-slate-400">Protect access to critical redistribution triggers with TOTP or SMS OTP verification.</p>
          <div class="p-4 rounded-xl border flex items-center justify-between" :class="dark ? 'border-[#1E293B] bg-[#1E293B]/40' : 'border-slate-100 bg-slate-50'">
            <div>
              <p class="text-xs font-bold" :class="dark ? 'text-white' : 'text-slate-800'">Authenticator App (TOTP)</p>
              <p class="text-2xs text-slate-400">Google Authenticator, Authy, or 1Password</p>
            </div>
            <button @click="twoFactorEnabled = !twoFactorEnabled" class="relative w-11 h-6 rounded-full transition-colors" :class="twoFactorEnabled ? 'bg-teal-600' : 'bg-slate-200'">
              <span class="absolute top-0.5 w-5 h-5 rounded-full bg-white shadow-sm transition-transform" :class="twoFactorEnabled ? 'translate-x-5' : 'translate-x-0.5'"></span>
            </button>
          </div>
          <div class="pt-2 text-right">
            <button @click="show2FAModal = false" class="px-4 py-2 rounded-xl text-xs font-semibold bg-teal-600 text-white">Done</button>
          </div>
        </div>
      </div>

      <!-- API Token Modal -->
      <div v-if="showApiTokenModal" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="w-full max-w-lg rounded-2xl border shadow-2xl p-6 space-y-4" :class="dark ? 'bg-[#111827] border-[#1E293B]' : 'bg-white border-slate-200'">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">API Access Tokens</h3>
            <button @click="showApiTokenModal = false" class="p-1 rounded-lg text-slate-400 hover:text-slate-600"><X :size="16" /></button>
          </div>
          <p class="text-xs text-slate-400">Use this token to authenticate telemetry feeds and automated dispatch integration.</p>
          <div class="p-3 rounded-xl border flex items-center justify-between gap-3 font-mono text-xs" :class="dark ? 'bg-[#1E293B] border-[#334155] text-teal-400' : 'bg-slate-50 border-slate-200 text-teal-700'">
            <span class="truncate">{{ apiToken }}</span>
            <button @click="copyToken" class="p-1.5 rounded-lg border text-slate-400 hover:text-slate-200 flex items-center gap-1 text-2xs flex-shrink-0">
              <Check v-if="copiedToken" :size="14" class="text-teal-500" />
              <Copy v-else :size="14" />
              <span>{{ copiedToken ? 'Copied' : 'Copy' }}</span>
            </button>
          </div>
          <div class="flex justify-between items-center pt-2">
            <button @click="generateNewToken" class="text-xs font-semibold text-teal-600 hover:underline">Regenerate Token</button>
            <button @click="showApiTokenModal = false" class="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-200 dark:bg-slate-700">Close</button>
          </div>
        </div>
      </div>

      <!-- Audit Log Modal -->
      <div v-if="showAuditLogModal" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="w-full max-w-2xl rounded-2xl border shadow-2xl p-6 space-y-4" :class="dark ? 'bg-[#111827] border-[#1E293B]' : 'bg-white border-slate-200'">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">System Audit Trail</h3>
            <button @click="showAuditLogModal = false" class="p-1 rounded-lg text-slate-400 hover:text-slate-600"><X :size="16" /></button>
          </div>
          <div class="overflow-x-auto max-h-72">
            <table class="w-full text-left text-xs">
              <thead class="text-2xs uppercase tracking-wider text-slate-400 border-b" :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
                <tr>
                  <th class="py-2 px-3">Event ID</th>
                  <th class="py-2 px-3">Action</th>
                  <th class="py-2 px-3">Actor</th>
                  <th class="py-2 px-3">Timestamp</th>
                  <th class="py-2 px-3">Status</th>
                </tr>
              </thead>
              <tbody class="divide-y" :class="dark ? 'divide-[#1E293B]' : 'divide-slate-50'">
                <tr v-for="log in auditLogs" :key="log.id">
                  <td class="py-2.5 px-3 font-mono text-slate-400 text-2xs">{{ log.id }}</td>
                  <td class="py-2.5 px-3 font-semibold" :class="dark ? 'text-white' : 'text-slate-800'">{{ log.action }}</td>
                  <td class="py-2.5 px-3 text-slate-400">{{ log.user }}</td>
                  <td class="py-2.5 px-3 text-slate-400">{{ log.time }}</td>
                  <td class="py-2.5 px-3">
                    <span class="px-2 py-0.5 rounded text-2xs font-bold" :class="log.status === 'SUCCESS' ? 'bg-teal-500/10 text-teal-600' : 'bg-amber-500/10 text-amber-600'">{{ log.status }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="text-right pt-2">
            <button @click="showAuditLogModal = false" class="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-200 dark:bg-slate-700">Close</button>
          </div>
        </div>
      </div>

      <!-- Role Matrix Modal -->
      <div v-if="showRoleModal" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="w-full max-w-xl rounded-2xl border shadow-2xl p-6 space-y-4" :class="dark ? 'bg-[#111827] border-[#1E293B]' : 'bg-white border-slate-200'">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">Role & Privilege Matrix</h3>
            <button @click="showRoleModal = false" class="p-1 rounded-lg text-slate-400 hover:text-slate-600"><X :size="16" /></button>
          </div>
          <div class="space-y-3">
            <div v-for="role in [
              { name: 'System Administrator (HQ)', desc: 'Global surveillance, model re-runs, and system orchestration', level: 'Level 1' },
              { name: 'PHC Facility Director', desc: 'Local inventory approvals, request submission, and transfer execution', level: 'Level 2' },
              { name: 'District Medical Officer', desc: 'Regional surveillance oversight and disease cluster verification', level: 'Level 3' },
              { name: 'Pharmacy Officer', desc: 'Physical stock counts and batch tracking update authority', level: 'Level 4' },
            ]" :key="role.name" class="p-3 rounded-xl border flex items-center justify-between" :class="dark ? 'border-[#1E293B] bg-[#1E293B]/30' : 'border-slate-100 bg-slate-50'">
              <div>
                <p class="text-xs font-bold" :class="dark ? 'text-white' : 'text-slate-800'">{{ role.name }}</p>
                <p class="text-2xs text-slate-400">{{ role.desc }}</p>
              </div>
              <span class="text-2xs font-semibold px-2 py-0.5 rounded bg-teal-500/10 text-teal-600 border border-teal-500/20">{{ role.level }}</span>
            </div>
          </div>
          <div class="text-right pt-2">
            <button @click="showRoleModal = false" class="px-4 py-2 rounded-xl text-xs font-semibold bg-teal-600 text-white">Done</button>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>
