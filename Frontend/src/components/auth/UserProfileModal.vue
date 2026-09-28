<script setup lang="ts">
import { ref } from 'vue';
import { X, User, Mail, ShieldCheck, MapPin, Building2, Calendar, LogOut, Check } from 'lucide-vue-next';
import { useAuthStore } from '../../stores/authStore';
import { useHospitalStore } from '../../stores/hospitalStore';

const props = defineProps<{ open: boolean }>();
const emit = defineEmits<{ (e: 'update:open', val: boolean): void }>();

const authStore = useAuthStore();
const hospitalStore = useHospitalStore();

const isEditing = ref(false);
const editName = ref('');
const editCountry = ref('');
const savedSuccess = ref(false);

const close = () => {
  emit('update:open', false);
  isEditing.value = false;
  savedSuccess.value = false;
};

const startEdit = () => {
  editName.value = authStore.user?.phc_name || '';
  editCountry.value = authStore.user?.country || 'India';
  isEditing.value = true;
  savedSuccess.value = false;
};

const saveProfile = () => {
  authStore.updateUserProfile({
    phc_name: editName.value.trim() || 'Health Officer',
    country: editCountry.value
  });
  isEditing.value = false;
  savedSuccess.value = true;
  setTimeout(() => { savedSuccess.value = false; }, 3000);
};

const handleLogout = async () => {
  await authStore.logout();
  close();
};
</script>

<template>
  <teleport to="body">
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="open" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="close">
        <div
          class="w-full max-w-md rounded-2xl border shadow-2xl overflow-hidden transition-all"
          :class="hospitalStore.darkMode ? 'bg-[#111827] border-[#1E293B]' : 'bg-white border-slate-200'"
        >
          <!-- Header -->
          <div class="p-6 pb-4 border-b flex items-start justify-between"
            :class="hospitalStore.darkMode ? 'border-[#1E293B]' : 'border-slate-100'">
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 rounded-2xl flex items-center justify-center text-white font-bold text-base shadow-sm"
                style="background: linear-gradient(135deg, #0d9488, #7c3aed);">
                {{ (authStore.user?.phc_name || 'DR').substring(0, 2).toUpperCase() }}
              </div>
              <div>
                <h3 class="text-base font-bold" :class="hospitalStore.darkMode ? 'text-white' : 'text-slate-800'">
                  {{ authStore.userDisplayName }}
                </h3>
                <p class="text-2xs font-semibold text-teal-600 dark:text-teal-400 flex items-center gap-1 mt-0.5">
                  <ShieldCheck :size="13" /> Verified Healthcare Authority
                </p>
              </div>
            </div>
            <button @click="close" class="p-1 rounded-lg text-slate-400 hover:text-slate-600 transition-colors">
              <X :size="18" />
            </button>
          </div>

          <!-- Body details -->
          <div class="p-6 space-y-4">
            <div v-if="savedSuccess" class="p-2.5 rounded-xl bg-teal-500/10 border border-teal-500/20 text-teal-600 dark:text-teal-400 text-xs flex items-center gap-2">
              <Check :size="15" /> Profile details saved successfully!
            </div>

            <!-- Profile Info Fields -->
            <div v-if="!isEditing" class="space-y-3">
              <div class="flex items-center justify-between py-2 border-b" :class="hospitalStore.darkMode ? 'border-[#1E293B]' : 'border-slate-100'">
                <span class="text-xs text-slate-400 flex items-center gap-1.5"><Mail :size="13" /> Email Address</span>
                <span class="text-xs font-medium" :class="hospitalStore.darkMode ? 'text-slate-200' : 'text-slate-700'">
                  {{ authStore.user?.email || 'N/A' }}
                </span>
              </div>

              <div class="flex items-center justify-between py-2 border-b" :class="hospitalStore.darkMode ? 'border-[#1E293B]' : 'border-slate-100'">
                <span class="text-xs text-slate-400 flex items-center gap-1.5"><Building2 :size="13" /> Facility Name</span>
                <span class="text-xs font-semibold" :class="hospitalStore.darkMode ? 'text-white' : 'text-slate-800'">
                  {{ authStore.user?.phc_name || 'Central Command' }}
                </span>
              </div>

              <div class="flex items-center justify-between py-2 border-b" :class="hospitalStore.darkMode ? 'border-[#1E293B]' : 'border-slate-100'">
                <span class="text-xs text-slate-400 flex items-center gap-1.5"><MapPin :size="13" /> Assigned Facility ID</span>
                <span class="text-xs font-mono px-2 py-0.5 rounded border"
                  :class="hospitalStore.darkMode ? 'bg-[#1E293B] border-[#334155] text-teal-400' : 'bg-slate-50 border-slate-200 text-teal-700'">
                  {{ authStore.assignedPhcId }}
                </span>
              </div>

              <div class="flex items-center justify-between py-2 border-b" :class="hospitalStore.darkMode ? 'border-[#1E293B]' : 'border-slate-100'">
                <span class="text-xs text-slate-400 flex items-center gap-1.5"><Calendar :size="13" /> Jurisdictional Country</span>
                <span class="text-xs font-medium" :class="hospitalStore.darkMode ? 'text-slate-200' : 'text-slate-700'">
                  {{ authStore.userCountry }}
                </span>
              </div>

              <div class="flex items-center justify-between py-2 border-b" :class="hospitalStore.darkMode ? 'border-[#1E293B]' : 'border-slate-100'">
                <span class="text-xs text-slate-400">Security Clearance</span>
                <span class="text-2xs font-bold px-2 py-0.5 rounded-full bg-teal-500/10 text-teal-600 border border-teal-500/20">
                  Level 3 · Full Operations & Redistribution
                </span>
              </div>
            </div>

            <!-- Editing Form -->
            <div v-else class="space-y-3">
              <div>
                <label class="text-2xs font-bold uppercase tracking-wider text-slate-400">Facility / Officer Name</label>
                <input
                  v-model="editName"
                  type="text"
                  class="w-full mt-1 px-3 py-2 text-xs rounded-xl border outline-none"
                  :class="hospitalStore.darkMode ? 'bg-[#1E293B] border-[#334155] text-white' : 'bg-slate-50 border-slate-200 text-slate-800'"
                />
              </div>

              <div>
                <label class="text-2xs font-bold uppercase tracking-wider text-slate-400">Country</label>
                <select
                  v-model="editCountry"
                  class="w-full mt-1 px-3 py-2 text-xs rounded-xl border outline-none"
                  :class="hospitalStore.darkMode ? 'bg-[#1E293B] border-[#334155] text-white' : 'bg-slate-50 border-slate-200 text-slate-800'"
                >
                  <option value="India">India</option>
                  <option value="Brazil">Brazil</option>
                  <option value="South Africa">South Africa</option>
                  <option value="China">China</option>
                  <option value="Russia">Russia</option>
                </select>
              </div>

              <div class="flex gap-2 pt-2">
                <button
                  @click="saveProfile"
                  class="flex-1 py-2 rounded-xl text-xs font-bold text-white shadow-sm"
                  style="background: linear-gradient(135deg, #0d9488, #0f766e);"
                >
                  Save Changes
                </button>
                <button
                  @click="isEditing = false"
                  class="px-4 py-2 rounded-xl text-xs font-semibold border"
                  :class="hospitalStore.darkMode ? 'border-[#334155] text-slate-300' : 'border-slate-200 text-slate-600'"
                >
                  Cancel
                </button>
              </div>
            </div>

            <!-- Action buttons -->
            <div v-if="!isEditing" class="flex gap-2 pt-2">
              <button
                @click="startEdit"
                class="flex-1 py-2 rounded-xl text-xs font-semibold border transition-colors"
                :class="hospitalStore.darkMode ? 'border-[#334155] text-slate-300 hover:bg-[#1E293B]' : 'border-slate-200 text-slate-700 hover:bg-slate-50'"
              >
                Edit Details
              </button>
              <button
                @click="handleLogout"
                class="flex items-center justify-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-red-50 hover:bg-red-100 text-red-600 dark:bg-red-950/40 dark:hover:bg-red-900/50 dark:text-red-400 transition-colors"
              >
                <LogOut :size="14" /> Sign Out
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>
