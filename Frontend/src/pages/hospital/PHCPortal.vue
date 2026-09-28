<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import {
  Building2, Plus, Bell, Clock, CheckCircle2, XCircle,
  ArrowRight, ShieldCheck, HeartHandshake, User, Lock, Mail,
  LogOut, AlertCircle, RefreshCw, Send, Package
} from 'lucide-vue-next';
import {
  registerPHC,
  loginPHC,
  logoutPHC,
  getCurrentPHC,
  getStoredUser,
  getStoredToken,
  getMedicineCatalog,
  createMedicineRequest,
  getMyRequests,
  getAvailableRequests,
  approveRequest,
  cancelRequest,
  getRequestNotifications
} from '../../services/api';
import type {
  PHCUser,
  MedicineRequestItem,
  MedicineCatalogItem,
  NotificationItem
} from '../../types';
import { useAuthStore } from '../../stores/authStore';

const authStore = useAuthStore();

// Auth State
const currentUser = computed(() => authStore.user);
const isAuthModeRegister = ref(false);
const authEmail = ref('');
const authPassword = ref('');
const authPhcName = ref('');
const authCountry = ref('India');
const authError = ref<string | null>(null);
const authLoading = computed(() => authStore.isLoading);

// Portal Data
const activeTab = ref<'my' | 'community' | 'notifications'>('my');
const catalog = ref<MedicineCatalogItem[]>([]);
const myRequests = ref<MedicineRequestItem[]>([]);
const communityRequests = ref<MedicineRequestItem[]>([]);
const notifications = ref<NotificationItem[]>([]);
const loadingData = ref(false);

// Modals
const showRequestModal = ref(false);
const showApproveModal = ref(false);
const targetRequestToApprove = ref<MedicineRequestItem | null>(null);
const unitsToSupply = ref(0);
const supplyNotes = ref('');

// New Request Form
const reqMedicineId = ref('');
const reqQuantity = ref(100);
const reqUrgency = ref('HIGH');
const reqReason = ref('');
const reqError = ref<string | null>(null);
const reqSubmitting = ref(false);

// ─────────────────────────────────────────────
// Auth Methods
// ─────────────────────────────────────────────

const handleAuth = async () => {
  authError.value = null;
  try {
    if (isAuthModeRegister.value) {
      if (!authPhcName.value.trim() || !authEmail.value.trim() || !authPassword.value) {
        authError.value = 'Please provide PHC name, email, and password.';
        return;
      }
      await authStore.register({
        phc_name: authPhcName.value,
        email: authEmail.value,
        password: authPassword.value,
        country: authCountry.value
      });
    } else {
      if (!authEmail.value.trim() || !authPassword.value) {
        authError.value = 'Please provide email and password.';
        return;
      }
      await authStore.login({
        email: authEmail.value,
        password: authPassword.value
      });
    }

    await loadPortalData();
  } catch (err: any) {
    authError.value = err?.detail || err?.message || 'Authentication failed. Please verify credentials.';
  }
};

const handleLogout = async () => {
  await authStore.logout();
};

const handleQuickDemo = (profile: 'admin' | 'india' | 'brazil' | 'south_africa') => {
  authStore.loginAsDemo(profile);
  loadPortalData();
};

// ─────────────────────────────────────────────
// Data Methods
// ─────────────────────────────────────────────

const loadPortalData = async () => {
  loadingData.value = true;
  try {
    const [catData, myData, commData, notifData] = await Promise.all([
      getMedicineCatalog(),
      getMyRequests().catch(() => []),
      getAvailableRequests().catch(() => []),
      getRequestNotifications().catch(() => [])
    ]);
    catalog.value = catData;
    myRequests.value = myData;
    communityRequests.value = commData;
    notifications.value = notifData;
    if (catData.length > 0 && !reqMedicineId.value) {
      reqMedicineId.value = catData[0].medicine_id;
    }
  } catch (err) {
    console.error('Failed to load portal data:', err);
  } finally {
    loadingData.value = false;
  }
};

// ─────────────────────────────────────────────
// Submit New Request
// ─────────────────────────────────────────────

const submitRequest = async () => {
  reqError.value = null;
  if (reqQuantity.value <= 0) {
    reqError.value = 'Quantity must be greater than zero.';
    return;
  }
  if (!reqReason.value.trim()) {
    reqError.value = 'Please state the operational reason / justification.';
    return;
  }

  reqSubmitting.value = true;
  try {
    await createMedicineRequest({
      medicine_id: reqMedicineId.value,
      quantity: reqQuantity.value,
      urgency: reqUrgency.value,
      reason: reqReason.value,
      description: reqReason.value
    });
    showRequestModal.value = false;
    reqReason.value = '';
    await loadPortalData();
  } catch (err: any) {
    reqError.value = err?.detail || err?.message || 'Failed to submit request.';
  } finally {
    reqSubmitting.value = false;
  }
};

// ─────────────────────────────────────────────
// Approve & Supply Modal / Submission
// ─────────────────────────────────────────────

const openApproveModal = (req: MedicineRequestItem) => {
  targetRequestToApprove.value = req;
  unitsToSupply.value = req.quantity;
  supplyNotes.value = 'Approved from local reserve; dispatched via cold-chain courier.';
  showApproveModal.value = true;
};

const submitApproval = async () => {
  if (!targetRequestToApprove.value) return;
  try {
    await approveRequest(targetRequestToApprove.value.request_id, {
      units_to_send: unitsToSupply.value,
      notes: supplyNotes.value
    });
    showApproveModal.value = false;
    targetRequestToApprove.value = null;
    await loadPortalData();
  } catch (err: any) {
    alert(err?.detail || err?.message || 'Failed to approve request.');
  }
};

const handleCancelRequest = async (requestId: string) => {
  if (!confirm('Are you sure you want to cancel this request?')) return;
  try {
    await cancelRequest(requestId);
    await loadPortalData();
  } catch (err: any) {
    alert(err?.detail || err?.message || 'Failed to cancel request.');
  }
};

onMounted(async () => {
  if (getStoredToken()) {
    try {
      const u = await getCurrentPHC();
      authStore.updateUserProfile(u);
    } catch {
      // Keep existing stored user or session
    }
  }
  loadPortalData();
});
</script>

<template>
  <div class="p-6 max-w-7xl mx-auto space-y-6">
    <!-- Unauthenticated State: Clean Register / Login Card -->
    <div v-if="!currentUser" class="max-w-md mx-auto my-12 p-8 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xl space-y-6">
      <div class="text-center space-y-2">
        <div class="w-12 h-12 rounded-2xl bg-teal-500/10 text-teal-600 dark:text-teal-400 mx-auto flex items-center justify-center">
          <Building2 :size="24" />
        </div>
        <h2 class="text-xl font-bold text-slate-900 dark:text-white">
          {{ isAuthModeRegister ? 'Register PHC Account' : 'PHC Portal Sign In' }}
        </h2>
        <p class="text-xs text-slate-500 dark:text-slate-400">
          PostgreSQL-authenticated portal for inter-facility medicine coordination
        </p>
      </div>

      <!-- Auth Mode Toggle -->
      <div class="grid grid-cols-2 p-1 rounded-xl bg-slate-100 dark:bg-slate-800 text-xs font-semibold">
        <button
          @click="isAuthModeRegister = false; authError = null"
          class="py-2 rounded-lg transition"
          :class="!isAuthModeRegister ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm' : 'text-slate-500'"
        >
          Sign In
        </button>
        <button
          @click="isAuthModeRegister = true; authError = null"
          class="py-2 rounded-lg transition"
          :class="isAuthModeRegister ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm' : 'text-slate-500'"
        >
          Register
        </button>
      </div>

      <!-- Error message -->
      <div v-if="authError" class="p-3 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 text-red-600 dark:text-red-400 text-xs">
        {{ authError }}
      </div>

      <!-- Form -->
      <form @submit.prevent="handleAuth" class="space-y-4">
        <div v-if="isAuthModeRegister" class="space-y-1">
          <label class="text-2xs font-bold uppercase tracking-wider text-slate-500">PHC / Organization Name</label>
          <div class="relative">
            <Building2 :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              v-model="authPhcName"
              type="text"
              required
              placeholder="e.g. Southwest District Primary Health Centre"
              class="w-full pl-9 pr-4 py-2.5 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:ring-1 focus:ring-teal-500 focus:outline-none"
            />
          </div>
        </div>

        <div class="space-y-1">
          <label class="text-2xs font-bold uppercase tracking-wider text-slate-500">Institutional Email</label>
          <div class="relative">
            <Mail :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              v-model="authEmail"
              type="email"
              required
              placeholder="e.g. clinic@brics.health"
              class="w-full pl-9 pr-4 py-2.5 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:ring-1 focus:ring-teal-500 focus:outline-none"
            />
          </div>
        </div>

        <div class="space-y-1">
          <label class="text-2xs font-bold uppercase tracking-wider text-slate-500">Secure Password</label>
          <div class="relative">
            <Lock :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              v-model="authPassword"
              type="password"
              required
              placeholder="••••••••"
              class="w-full pl-9 pr-4 py-2.5 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:ring-1 focus:ring-teal-500 focus:outline-none"
            />
          </div>
        </div>

        <div v-if="isAuthModeRegister" class="space-y-1">
          <label class="text-2xs font-bold uppercase tracking-wider text-slate-500">Country of Operation</label>
          <select
            v-model="authCountry"
            class="w-full px-3 py-2.5 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:ring-1 focus:ring-teal-500 focus:outline-none"
          >
            <option value="India">India</option>
            <option value="Brazil">Brazil</option>
            <option value="South Africa">South Africa</option>
            <option value="China">China</option>
            <option value="Russia">Russia</option>
          </select>
        </div>

        <button
          type="submit"
          :disabled="authLoading"
          class="w-full py-3 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-bold text-xs shadow-md shadow-teal-500/20 transition active:scale-95 disabled:opacity-50"
        >
          <span v-if="authLoading">Authenticating...</span>
          <span v-else>{{ isAuthModeRegister ? 'Create PHC Account' : 'Sign In to Portal' }}</span>
        </button>
      </form>

      <!-- 1-Click Demo Accounts -->
      <div class="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800">
        <p class="text-2xs font-bold uppercase tracking-wider text-slate-400 mb-2">Instant Demo Session (1-Click):</p>
        <div class="grid grid-cols-2 gap-2">
          <button
            @click="handleQuickDemo('admin')"
            type="button"
            class="p-2 rounded-xl border border-slate-200 dark:border-slate-700 text-2xs font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 transition text-left flex items-center gap-1.5"
          >
            <span>🛡️</span>
            <span class="truncate">Dr. Admin (HQ)</span>
          </button>
          <button
            @click="handleQuickDemo('india')"
            type="button"
            class="p-2 rounded-xl border border-slate-200 dark:border-slate-700 text-2xs font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 transition text-left flex items-center gap-1.5"
          >
            <span>🇮🇳</span>
            <span class="truncate">India PHC Lead</span>
          </button>
          <button
            @click="handleQuickDemo('brazil')"
            type="button"
            class="p-2 rounded-xl border border-slate-200 dark:border-slate-700 text-2xs font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 transition text-left flex items-center gap-1.5"
          >
            <span>🇧🇷</span>
            <span class="truncate">Brazil UBS Lead</span>
          </button>
          <button
            @click="handleQuickDemo('south_africa')"
            type="button"
            class="p-2 rounded-xl border border-slate-200 dark:border-slate-700 text-2xs font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 transition text-left flex items-center gap-1.5"
          >
            <span>🇿🇦</span>
            <span class="truncate">SA CHC Lead</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Authenticated PHC Portal View -->
    <div v-else class="space-y-6">
      <!-- Portal Header Banner -->
      <div class="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-2xl bg-teal-500/10 text-teal-600 dark:text-teal-400 flex items-center justify-center font-bold">
            <Building2 :size="24" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-lg font-bold text-slate-900 dark:text-white">Welcome, {{ currentUser.phc_name }}</h2>
              <span class="px-2 py-0.5 rounded text-2xs font-extrabold uppercase bg-teal-50 dark:bg-teal-950 text-teal-700 dark:text-teal-300 border border-teal-200 dark:border-teal-800">
                {{ currentUser.country }}
              </span>
            </div>
            <p class="text-xs text-slate-500 font-mono mt-0.5">Assigned Facility ID: {{ currentUser.assigned_phc_id || `PHC-${currentUser.id}` }}</p>
          </div>
        </div>

        <div class="flex items-center gap-3 self-end sm:self-center">
          <button
            @click="showRequestModal = true"
            class="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-bold shadow-md shadow-teal-500/20 transition active:scale-95"
          >
            <Plus :size="15" />
            <span>Request Medicine</span>
          </button>

          <button
            @click="handleLogout"
            class="flex items-center gap-1.5 px-3 py-2 text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-red-600 dark:hover:text-red-400 transition"
          >
            <LogOut :size="15" />
            <span>Sign Out</span>
          </button>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2">
        <div class="flex items-center gap-2">
          <button
            @click="activeTab = 'my'"
            class="px-4 py-2 text-xs font-bold rounded-lg transition"
            :class="activeTab === 'my'
              ? 'bg-teal-50 dark:bg-teal-950 text-teal-700 dark:text-teal-300 border border-teal-200 dark:border-teal-800'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'"
          >
            My Requests ({{ myRequests.length }})
          </button>

          <button
            @click="activeTab = 'community'"
            class="flex items-center gap-2 px-4 py-2 text-xs font-bold rounded-lg transition"
            :class="activeTab === 'community'
              ? 'bg-teal-50 dark:bg-teal-950 text-teal-700 dark:text-teal-300 border border-teal-200 dark:border-teal-800'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'"
          >
            <span>Community Requests</span>
            <span v-if="communityRequests.length > 0" class="w-5 h-5 rounded-full bg-teal-600 text-white text-2xs flex items-center justify-center font-bold">
              {{ communityRequests.length }}
            </span>
          </button>

          <button
            @click="activeTab = 'notifications'"
            class="flex items-center gap-2 px-4 py-2 text-xs font-bold rounded-lg transition"
            :class="activeTab === 'notifications'
              ? 'bg-teal-50 dark:bg-teal-950 text-teal-700 dark:text-teal-300 border border-teal-200 dark:border-teal-800'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'"
          >
            <Bell :size="13" />
            <span>Notifications ({{ notifications.length }})</span>
          </button>
        </div>

        <button
          @click="loadPortalData"
          class="p-2 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition"
          title="Refresh portal"
        >
          <RefreshCw :size="15" :class="{ 'animate-spin': loadingData }" />
        </button>
      </div>

      <!-- TAB 1: My Requests -->
      <div v-if="activeTab === 'my'" class="space-y-4">
        <div v-if="myRequests.length === 0" class="p-12 text-center rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-3">
          <div class="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400 mx-auto flex items-center justify-center">
            <Package :size="20" />
          </div>
          <h3 class="text-sm font-bold text-slate-900 dark:text-white">No active requests</h3>
          <p class="text-xs text-slate-500 max-w-sm mx-auto">
            You have not submitted any replenishment requests yet. Click "Request Medicine" above to create one.
          </p>
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="r in myRequests"
            :key="r.request_id"
            class="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
          >
            <div class="space-y-1">
              <div class="flex items-center gap-2">
                <span class="font-mono text-2xs font-bold text-slate-500">{{ r.request_id }}</span>
                <span
                  class="px-2 py-0.5 rounded text-2xs font-extrabold uppercase border"
                  :class="{
                    'bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300 border-amber-200': r.status === 'PENDING',
                    'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-200': r.status === 'APPROVED' || r.status === 'COMPLETED',
                    'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 border-slate-300': r.status === 'CANCELLED',
                  }"
                >
                  {{ r.status }}
                </span>
                <span class="text-2xs text-slate-400">{{ new Date(r.created_at).toLocaleDateString() }}</span>
              </div>
              <h4 class="text-sm font-bold text-slate-900 dark:text-white">{{ r.medicine_name }}</h4>
              <p class="text-xs text-slate-500">{{ r.description || r.reason }}</p>
            </div>

            <div class="flex items-center gap-6 self-end md:self-center">
              <div class="text-right">
                <p class="text-2xs text-slate-400">Requested Volume</p>
                <p class="text-base font-extrabold text-slate-900 dark:text-white">{{ r.quantity }} units</p>
              </div>

              <div v-if="r.supplied_by_phc_name" class="text-right">
                <p class="text-2xs text-teal-600 dark:text-teal-400 font-semibold">Supplied by</p>
                <p class="text-xs font-bold text-slate-900 dark:text-white">{{ r.supplied_by_phc_name }}</p>
                <p class="text-2xs text-slate-500">({{ r.supplied_quantity || r.quantity }} units)</p>
              </div>

              <button
                v-if="r.status === 'PENDING'"
                @click="handleCancelRequest(r.request_id)"
                class="px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-50 dark:hover:bg-red-950/40 rounded-lg transition"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 2: Available Community Requests (Peer Supply) -->
      <div v-if="activeTab === 'community'" class="space-y-4">
        <div v-if="communityRequests.length === 0" class="p-12 text-center rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-2">
          <CheckCircle2 :size="24" class="text-emerald-500 mx-auto" />
          <h3 class="text-sm font-bold text-slate-900 dark:text-white">All peer requests fulfilled</h3>
          <p class="text-xs text-slate-500">No other PHCs currently have pending emergency shortages in your regional cluster.</p>
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="r in communityRequests"
            :key="r.request_id"
            class="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4 transition hover:border-teal-500/40"
          >
            <div class="space-y-1">
              <div class="flex items-center gap-2">
                <span class="px-2 py-0.5 rounded text-2xs font-extrabold uppercase bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300 border border-amber-200">
                  PENDING REQUEST
                </span>
                <span class="text-xs font-bold text-teal-600 dark:text-teal-400">From: {{ r.requesting_phc_name }}</span>
              </div>
              <h4 class="text-sm font-bold text-slate-900 dark:text-white">{{ r.medicine_name }}</h4>
              <p class="text-xs text-slate-500">{{ r.description || r.reason }}</p>
            </div>

            <div class="flex items-center gap-6 self-end md:self-center">
              <div class="text-right">
                <p class="text-2xs text-slate-400">Required Quantity</p>
                <p class="text-base font-extrabold text-slate-900 dark:text-white">{{ r.quantity }} units</p>
              </div>

              <button
                @click="openApproveModal(r)"
                class="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-bold shadow-md shadow-teal-500/20 transition active:scale-95"
              >
                <HeartHandshake :size="14" />
                <span>Approve & Supply</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 3: Notifications -->
      <div v-if="activeTab === 'notifications'" class="space-y-3">
        <div v-if="notifications.length === 0" class="p-8 text-center rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 text-slate-500 text-xs">
          No new notifications.
        </div>

        <div
          v-for="n in notifications"
          :key="n.id"
          class="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-start gap-3"
        >
          <div class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
            :class="n.type === 'success' ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-950/60' : 'bg-teal-50 text-teal-600 dark:bg-teal-950/60'">
            <CheckCircle2 v-if="n.type === 'success'" :size="16" />
            <Bell v-else :size="16" />
          </div>
          <div class="flex-1">
            <p class="text-xs font-bold text-slate-900 dark:text-white">{{ n.title }}</p>
            <p class="text-xs text-slate-600 dark:text-slate-300 mt-0.5">{{ n.message }}</p>
            <p class="text-2xs text-slate-400 mt-1">{{ new Date(n.timestamp).toLocaleString() }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal 1: Request Medicine -->
    <div v-if="showRequestModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm">
      <div class="relative w-full max-w-lg bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-2xl p-6 space-y-4">
        <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
          <h3 class="text-base font-bold text-slate-900 dark:text-white">Submit Medicine Replenishment Request</h3>
          <button @click="showRequestModal = false" class="text-slate-400 hover:text-slate-600">✕</button>
        </div>

        <div v-if="reqError" class="p-3 rounded-xl bg-red-50 text-red-600 text-xs">
          {{ reqError }}
        </div>

        <form @submit.prevent="submitRequest" class="space-y-4">
          <div class="space-y-1">
            <label class="text-2xs font-bold uppercase text-slate-500">Medicine / Resource</label>
            <select
              v-model="reqMedicineId"
              class="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white"
            >
              <option v-for="m in catalog" :key="m.medicine_id" :value="m.medicine_id">
                {{ m.name }} ({{ m.medicine_id }})
              </option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div class="space-y-1">
              <label class="text-2xs font-bold uppercase text-slate-500">Required Units</label>
              <input
                v-model.number="reqQuantity"
                type="number"
                min="1"
                required
                class="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white"
              />
            </div>
            <div class="space-y-1">
              <label class="text-2xs font-bold uppercase text-slate-500">Urgency Level</label>
              <select
                v-model="reqUrgency"
                class="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white"
              >
                <option value="LOW">Low (Buffer)</option>
                <option value="MEDIUM">Medium (Routine)</option>
                <option value="HIGH">High (Emerging Outbreak)</option>
                <option value="CRITICAL">Critical (Immediate Stockout)</option>
              </select>
            </div>
          </div>

          <div class="space-y-1">
            <label class="text-2xs font-bold uppercase text-slate-500">Reason / Clinical Description</label>
            <textarea
              v-model="reqReason"
              required
              rows="3"
              placeholder="e.g. Dengue-related patient surge has exhausted primary antipyretic reserves..."
              class="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white"
            ></textarea>
          </div>

          <div class="flex items-center justify-end gap-3 pt-3 border-t border-slate-100 dark:border-slate-800">
            <button
              type="button"
              @click="showRequestModal = false"
              class="px-4 py-2 text-xs font-semibold text-slate-600"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="reqSubmitting"
              class="px-5 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-bold text-xs shadow-md transition"
            >
              {{ reqSubmitting ? 'Submitting...' : 'Submit Request' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal 2: Approve & Supply Confirmation -->
    <div v-if="showApproveModal && targetRequestToApprove" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm">
      <div class="relative w-full max-w-lg bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-2xl p-6 space-y-4">
        <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
          <h3 class="text-base font-bold text-slate-900 dark:text-white">Approve & Supply Medicine Batch</h3>
          <button @click="showApproveModal = false" class="text-slate-400 hover:text-slate-600">✕</button>
        </div>

        <div class="p-3 rounded-xl bg-teal-50 dark:bg-teal-950/50 text-xs text-teal-800 dark:text-teal-200">
          Supplying <strong>{{ targetRequestToApprove.requesting_phc_name }}</strong> for <strong>{{ targetRequestToApprove.medicine_name }}</strong>.
        </div>

        <div class="space-y-4">
          <div class="space-y-1">
            <label class="text-2xs font-bold uppercase text-slate-500">Units to Send</label>
            <input
              v-model.number="unitsToSupply"
              type="number"
              min="1"
              required
              class="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white"
            />
          </div>

          <div class="space-y-1">
            <label class="text-2xs font-bold uppercase text-slate-500">Dispatched Batch Notes</label>
            <input
              v-model="supplyNotes"
              type="text"
              class="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white"
            />
          </div>

          <div class="flex items-center justify-end gap-3 pt-3 border-t border-slate-100 dark:border-slate-800">
            <button
              type="button"
              @click="showApproveModal = false"
              class="px-4 py-2 text-xs font-semibold text-slate-600"
            >
              Cancel
            </button>
            <button
              @click="submitApproval"
              class="px-5 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-bold text-xs shadow-md transition"
            >
              Approve & Send
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
