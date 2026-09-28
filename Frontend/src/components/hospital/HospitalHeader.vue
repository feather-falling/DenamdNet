<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import {
  Search, Menu, Bell, Moon, Sun, ChevronDown, User,
  LogOut, Settings, AlertTriangle, Calendar
} from 'lucide-vue-next';
import { useHospitalStore } from '../../stores/hospitalStore';
import { useAuthStore } from '../../stores/authStore';

const emit = defineEmits<{
  (e: 'menuClick'): void;
  (e: 'searchClick'): void;
  (e: 'openProfile'): void;
  (e: 'openAuth'): void;
}>();

const store = useHospitalStore();
const authStore = useAuthStore();
const route = useRoute();

const PAGE_META: Record<string, { title: string; subtitle: string }> = {
  '/dashboard':     { title: 'Dashboard',           subtitle: 'Hospital overview & real-time metrics' },
  '/map':           { title: 'BRICS Operations Map', subtitle: 'Global PHC network, disease surveillance & geospatial intelligence' },
  '/results':       { title: 'Healthcare Analysis', subtitle: 'Sharma redistribution forecast & multi-horizon AI' },
  '/phc-portal':    { title: 'PHC Community Portal', subtitle: 'Decentralized mutual-aid & medicine replenishment' },
  '/emergency':     { title: 'Emergency Center',    subtitle: 'Active emergencies & critical response' },
  '/patients':      { title: 'Patients',            subtitle: 'Patient management & records' },
  '/doctors':       { title: 'Doctors',             subtitle: 'Medical staff & duty roster' },
  '/beds':          { title: 'Bed Management',      subtitle: 'Real-time bed occupancy & allocation' },
  '/departments':   { title: 'Departments',         subtitle: 'Department overview & performance' },
  '/pharmacy':      { title: 'Pharmacy',            subtitle: 'Medicine inventory & stock management' },
  '/inventory':     { title: 'Inventory',           subtitle: 'Hospital supplies & equipment' },
  '/ambulance':     { title: 'Ambulance',           subtitle: 'Fleet management & dispatch' },
  '/analytics':     { title: 'Analytics',           subtitle: 'Reports & performance analytics' },
  '/notifications': { title: 'Notifications',       subtitle: 'Alerts & system notifications' },
  '/settings':      { title: 'Settings',            subtitle: 'System configuration & preferences' },
};

const meta = computed(() => PAGE_META[route.path] ?? { title: 'MediCore', subtitle: '' });
const time = ref('');
const dateStr = ref('');
const profileOpen = ref(false);
const notifPanelOpen = ref(false);

onMounted(() => {
  const update = () => {
    const now = new Date();
    time.value = now.toLocaleTimeString('en-US', { hour12: true, hour: '2-digit', minute: '2-digit' });
    dateStr.value = now.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  };
  update();
  const interval = setInterval(update, 1000);
  onUnmounted(() => clearInterval(interval));

  // Close dropdowns on outside click
  const close = () => { profileOpen.value = false; notifPanelOpen.value = false; };
  document.addEventListener('click', close);
  onUnmounted(() => document.removeEventListener('click', close));
});

const recentNotifs = computed(() => store.notifications.filter(n => !n.read).slice(0, 5));
</script>

<template>
  <header
    class="h-16 flex items-center px-4 gap-3 sm:gap-4 flex-shrink-0 dark-transition"
    :class="store.darkMode
      ? 'bg-[#111827] border-b border-[#1E293B]'
      : 'bg-white border-b border-slate-100'"
  >
    <!-- Mobile menu -->
    <button
      @click="emit('menuClick')"
      class="lg:hidden p-2 rounded-lg transition-colors"
      :class="store.darkMode ? 'text-slate-400 hover:bg-[#1E293B]' : 'text-slate-500 hover:bg-slate-100'"
      aria-label="Open menu"
    >
      <Menu :size="19" />
    </button>

    <!-- Page Title -->
    <div class="flex-1 min-w-0">
      <h1 class="text-base font-bold truncate" :class="store.darkMode ? 'text-white' : 'text-slate-800'">
        {{ meta.title }}
      </h1>
      <p class="text-2xs font-medium truncate hidden sm:block" :class="store.darkMode ? 'text-slate-500' : 'text-slate-400'">
        {{ meta.subtitle }}
      </p>
    </div>

    <!-- Date & Time -->
    <div class="hidden xl:flex items-center gap-2 px-3 py-1.5 rounded-lg border text-2xs font-medium"
      :class="store.darkMode ? 'bg-[#1E293B] border-[#334155] text-slate-400' : 'bg-slate-50 border-slate-200 text-slate-500'">
      <Calendar :size="12" />
      <span>{{ dateStr }}</span>
      <span class="font-mono font-semibold" :class="store.darkMode ? 'text-teal-400' : 'text-teal-600'">{{ time }}</span>
    </div>

    <!-- Emergency Indicator -->
    <div
      v-if="store.unacknowledgedAlerts > 0"
      class="hidden sm:flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-red-200 bg-red-50 text-red-700 text-2xs font-bold"
    >
      <span class="pulse-dot-wrapper pulse-red">
        <span class="w-1.5 h-1.5 rounded-full bg-red-500 block"></span>
      </span>
      {{ store.unacknowledgedAlerts }} Emergency
    </div>

    <!-- Search -->
    <button
      @click="emit('searchClick')"
      class="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-2xs transition-colors hidden md:flex"
      :class="store.darkMode
        ? 'bg-[#1E293B] border-[#334155] text-slate-400 hover:border-[#475569]'
        : 'bg-slate-50 border-slate-200 text-slate-400 hover:bg-white hover:border-slate-300'"
      aria-label="Search"
    >
      <Search :size="13" />
      <span>Search...</span>
      <kbd class="ml-1 px-1.5 py-0.5 text-2xs font-mono rounded border"
        :class="store.darkMode ? 'bg-[#0B1220] border-[#334155] text-slate-500' : 'bg-white border-slate-200 text-slate-400'">
        Ctrl K
      </kbd>
    </button>

    <!-- Notification Bell -->
    <div class="relative">
      <button
        @click.stop="notifPanelOpen = !notifPanelOpen; profileOpen = false"
        class="relative p-2 rounded-lg transition-colors"
        :class="store.darkMode ? 'text-slate-400 hover:bg-[#1E293B]' : 'text-slate-500 hover:bg-slate-100'"
        aria-label="Notifications"
      >
        <Bell :size="19" />
        <span
          v-if="store.unreadNotifications > 0"
          class="absolute top-1 right-1 flex items-center justify-center w-4 h-4 text-2xs font-bold rounded-full bg-red-500 text-white"
        >
          {{ store.unreadNotifications > 9 ? '9+' : store.unreadNotifications }}
        </span>
      </button>

      <!-- Notification Dropdown -->
      <Transition
        enter-active-class="transition duration-150 ease-out"
        enter-from-class="opacity-0 scale-95 translate-y-1"
        enter-to-class="opacity-100 scale-100 translate-y-0"
        leave-active-class="transition duration-100 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div
          v-if="notifPanelOpen"
          class="absolute right-0 top-12 w-80 z-50 rounded-xl shadow-float border overflow-hidden"
          :class="store.darkMode ? 'bg-[#111827] border-[#1E293B]' : 'bg-white border-slate-200'"
        >
          <div class="flex items-center justify-between px-4 py-3 border-b"
            :class="store.darkMode ? 'border-[#1E293B]' : 'border-slate-100'">
            <p class="text-sm font-semibold" :class="store.darkMode ? 'text-white' : 'text-slate-800'">Notifications</p>
            <button @click="store.markAllNotificationsRead()" class="text-2xs text-teal-600 hover:text-teal-700 font-semibold">
              Mark all read
            </button>
          </div>
          <div class="max-h-72 overflow-y-auto">
            <div
              v-for="notif in recentNotifs"
              :key="notif.id"
              @click="store.markNotificationRead(notif.id)"
              class="flex items-start gap-3 px-4 py-3 cursor-pointer border-b transition-colors"
              :class="[
                store.darkMode ? 'border-[#1E293B] hover:bg-[#1E293B]' : 'border-slate-50 hover:bg-slate-50',
                !notif.read && (store.darkMode ? 'bg-[#1a2332]' : 'bg-blue-50/40')
              ]"
            >
              <span
                class="w-2 h-2 rounded-full mt-1.5 flex-shrink-0"
                :class="notif.severity === 'critical' ? 'bg-red-500' : notif.severity === 'high' ? 'bg-amber-500' : 'bg-blue-400'"
              ></span>
              <div class="min-w-0 flex-1">
                <p class="text-xs font-semibold" :class="store.darkMode ? 'text-slate-200' : 'text-slate-700'">{{ notif.title }}</p>
                <p class="text-2xs mt-0.5 line-clamp-2" :class="store.darkMode ? 'text-slate-500' : 'text-slate-400'">{{ notif.message }}</p>
                <p class="text-2xs mt-1 font-medium text-teal-600">{{ notif.time }}</p>
              </div>
            </div>
            <div v-if="recentNotifs.length === 0" class="px-4 py-6 text-center">
              <p class="text-sm" :class="store.darkMode ? 'text-slate-500' : 'text-slate-400'">All caught up! 🎉</p>
            </div>
          </div>
          <div class="px-4 py-2 border-t" :class="store.darkMode ? 'border-[#1E293B]' : 'border-slate-100'">
            <router-link to="/notifications" class="text-2xs text-teal-600 hover:text-teal-700 font-semibold">
              View all notifications →
            </router-link>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Dark Mode Toggle -->
    <button
      @click="store.toggleDarkMode()"
      class="p-2 rounded-lg transition-colors"
      :class="store.darkMode ? 'text-amber-400 hover:bg-[#1E293B]' : 'text-slate-500 hover:bg-slate-100'"
      :aria-label="store.darkMode ? 'Switch to light mode' : 'Switch to dark mode'"
    >
      <Sun v-if="store.darkMode" :size="19" />
      <Moon v-else :size="19" />
    </button>

    <!-- User Profile / Sign In -->
    <div class="relative">
      <!-- If Authenticated -->
      <button
        v-if="authStore.isAuthenticated"
        @click.stop="profileOpen = !profileOpen; notifPanelOpen = false"
        class="flex items-center gap-2.5 pl-1 pr-3 py-1.5 rounded-xl border transition-colors"
        :class="store.darkMode
          ? 'border-[#1E293B] hover:bg-[#1E293B]'
          : 'border-slate-200 hover:bg-slate-50'"
      >
        <div class="w-7 h-7 rounded-lg flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
          style="background: linear-gradient(135deg, #0d9488, #7c3aed);">
          {{ (authStore.user?.phc_name || 'DR').substring(0, 2).toUpperCase() }}
        </div>
        <div class="hidden sm:block text-left max-w-[130px]">
          <p class="text-xs font-semibold leading-none truncate" :class="store.darkMode ? 'text-slate-200' : 'text-slate-700'">
            {{ authStore.userDisplayName }}
          </p>
          <p class="text-2xs leading-none mt-0.5 font-medium text-teal-600 truncate">
            {{ authStore.assignedPhcId }}
          </p>
        </div>
        <ChevronDown :size="13" class="text-slate-400 hidden sm:block" />
      </button>

      <!-- If Not Authenticated -->
      <button
        v-else
        @click="emit('openAuth')"
        class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-white shadow-sm transition-all"
        style="background: linear-gradient(135deg, #0d9488, #0f766e);"
      >
        <User :size="14" />
        <span>Sign In</span>
      </button>

      <!-- Profile Dropdown -->
      <Transition
        enter-active-class="transition duration-150 ease-out"
        enter-from-class="opacity-0 scale-95 translate-y-1"
        enter-to-class="opacity-100 scale-100 translate-y-0"
        leave-active-class="transition duration-100 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div
          v-if="profileOpen && authStore.isAuthenticated"
          class="absolute right-0 top-12 w-56 z-50 rounded-xl shadow-float border"
          :class="store.darkMode ? 'bg-[#111827] border-[#1E293B]' : 'bg-white border-slate-200'"
        >
          <div class="px-4 py-3 border-b" :class="store.darkMode ? 'border-[#1E293B]' : 'border-slate-100'">
            <p class="text-sm font-semibold truncate" :class="store.darkMode ? 'text-white' : 'text-slate-800'">
              {{ authStore.userDisplayName }}
            </p>
            <p class="text-2xs truncate" :class="store.darkMode ? 'text-slate-500' : 'text-slate-400'">
              {{ authStore.user?.email || 'N/A' }}
            </p>
            <span class="inline-block mt-1 px-1.5 py-0.5 rounded text-3xs font-bold uppercase tracking-wider bg-teal-500/10 text-teal-600 border border-teal-500/20">
              {{ authStore.userCountry }}
            </span>
          </div>
          <div class="py-1">
            <button
              @click="profileOpen = false; emit('openProfile')"
              class="flex items-center gap-2.5 w-full px-4 py-2.5 text-sm transition-colors text-left"
              :class="store.darkMode ? 'text-slate-300 hover:bg-[#1E293B]' : 'text-slate-600 hover:bg-slate-50'"
            >
              <User :size="15" /> Profile Details
            </button>
            <router-link
              to="/settings"
              @click="profileOpen = false"
              class="flex items-center gap-2.5 w-full px-4 py-2.5 text-sm transition-colors"
              :class="store.darkMode ? 'text-slate-300 hover:bg-[#1E293B]' : 'text-slate-600 hover:bg-slate-50'"
            >
              <Settings :size="15" /> Settings
            </router-link>
            <div class="border-t mx-2 my-1" :class="store.darkMode ? 'border-[#1E293B]' : 'border-slate-100'"></div>
            <button
              @click="profileOpen = false; authStore.logout()"
              class="flex items-center gap-2.5 w-full px-4 py-2.5 text-sm text-red-500 transition-colors text-left"
              :class="store.darkMode ? 'hover:bg-[#1E293B]' : 'hover:bg-red-50'"
            >
              <LogOut :size="15" /> Sign out
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </header>
</template>
