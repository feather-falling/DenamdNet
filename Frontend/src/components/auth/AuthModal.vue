<script setup lang="ts">
import { ref } from 'vue';
import { X, Lock, Mail, Building2, Globe, Sparkles, CheckCircle2, AlertCircle } from 'lucide-vue-next';
import { useAuthStore } from '../../stores/authStore';
import { useHospitalStore } from '../../stores/hospitalStore';

const props = defineProps<{ open: boolean }>();
const emit = defineEmits<{ (e: 'update:open', val: boolean): void; (e: 'success'): void }>();

const authStore = useAuthStore();
const hospitalStore = useHospitalStore();

const isRegister = ref(false);
const email = ref('');
const password = ref('');
const phcName = ref('');
const country = ref('India');
const formError = ref<string | null>(null);

const close = () => {
  emit('update:open', false);
  formError.value = null;
};

const handleAuth = async () => {
  formError.value = null;

  if (!email.value || !email.value.includes('@')) {
    formError.value = 'Please provide a valid email address.';
    return;
  }
  if (!password.value || password.value.length < 4) {
    formError.value = 'Password must be at least 4 characters long.';
    return;
  }
  if (isRegister.value && !phcName.value.trim()) {
    formError.value = 'Please enter your Primary Health Facility name.';
    return;
  }

  try {
    if (isRegister.value) {
      await authStore.register({
        phc_name: phcName.value.trim(),
        email: email.value.trim(),
        password: password.value,
        country: country.value,
      });
    } else {
      await authStore.login({
        email: email.value.trim(),
        password: password.value,
      });
    }
    emit('success');
    close();
  } catch (err: any) {
    formError.value = err?.message || 'Authentication failed. Please verify credentials.';
  }
};

const handleDemoLogin = (profile: 'admin' | 'india' | 'brazil' | 'south_africa') => {
  authStore.loginAsDemo(profile);
  emit('success');
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
          class="w-full max-w-md rounded-2xl border shadow-2xl overflow-hidden transition-all transform scale-100"
          :class="hospitalStore.darkMode ? 'bg-[#111827] border-[#1E293B]' : 'bg-white border-slate-200'"
        >
          <!-- Header banner -->
          <div class="p-6 pb-4 border-b flex items-start justify-between"
            :class="hospitalStore.darkMode ? 'border-[#1E293B] bg-gradient-to-r from-teal-950/40 to-slate-900' : 'border-slate-100 bg-gradient-to-r from-teal-50 to-slate-50'">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl flex items-center justify-center shadow-sm text-white"
                style="background: linear-gradient(135deg, #0d9488, #0f766e);">
                <Lock :size="20" />
              </div>
              <div>
                <h3 class="text-base font-bold" :class="hospitalStore.darkMode ? 'text-white' : 'text-slate-800'">
                  {{ isRegister ? 'Register PHC Facility' : 'Sign In to BRICS Portal' }}
                </h3>
                <p class="text-2xs" :class="hospitalStore.darkMode ? 'text-slate-400' : 'text-slate-500'">
                  {{ isRegister ? 'Create an authorized facility node' : 'Access healthcare resilience & redistribution' }}
                </p>
              </div>
            </div>
            <button @click="close" class="p-1 rounded-lg text-slate-400 hover:text-slate-600 transition-colors">
              <X :size="18" />
            </button>
          </div>

          <!-- Mode switcher tabs -->
          <div class="flex border-b text-xs font-semibold" :class="hospitalStore.darkMode ? 'border-[#1E293B]' : 'border-slate-100'">
            <button
              @click="isRegister = false; formError = null"
              class="flex-1 py-3 text-center border-b-2 transition-colors"
              :class="!isRegister
                ? 'border-teal-500 text-teal-600 dark:text-teal-400 bg-teal-500/5'
                : (hospitalStore.darkMode ? 'border-transparent text-slate-400 hover:text-slate-200' : 'border-transparent text-slate-500 hover:text-slate-800')"
            >
              Sign In
            </button>
            <button
              @click="isRegister = true; formError = null"
              class="flex-1 py-3 text-center border-b-2 transition-colors"
              :class="isRegister
                ? 'border-teal-500 text-teal-600 dark:text-teal-400 bg-teal-500/5'
                : (hospitalStore.darkMode ? 'border-transparent text-slate-400 hover:text-slate-200' : 'border-transparent text-slate-500 hover:text-slate-800')"
            >
              Register Facility
            </button>
          </div>

          <!-- Form body -->
          <form @submit.prevent="handleAuth" class="p-6 space-y-4">
            <!-- Error Banner -->
            <div v-if="formError" class="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 text-xs flex items-center gap-2">
              <AlertCircle :size="16" class="flex-shrink-0" />
              <span>{{ formError }}</span>
            </div>

            <!-- PHC Name (Only on register) -->
            <div v-if="isRegister" class="space-y-1">
              <label class="text-2xs font-bold uppercase tracking-wider" :class="hospitalStore.darkMode ? 'text-slate-400' : 'text-slate-600'">
                Facility / PHC Name
              </label>
              <div class="relative">
                <Building2 :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  v-model="phcName"
                  type="text"
                  placeholder="e.g. Najafgarh PHC / UBS República"
                  class="w-full pl-9 pr-3 py-2 rounded-xl text-xs border outline-none transition-all"
                  :class="hospitalStore.darkMode ? 'bg-[#1E293B] border-[#334155] text-white focus:border-teal-500' : 'bg-slate-50 border-slate-200 text-slate-800 focus:border-teal-500'"
                />
              </div>
            </div>

            <!-- Email -->
            <div class="space-y-1">
              <label class="text-2xs font-bold uppercase tracking-wider" :class="hospitalStore.darkMode ? 'text-slate-400' : 'text-slate-600'">
                Email Address
              </label>
              <div class="relative">
                <Mail :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  v-model="email"
                  type="email"
                  placeholder="doctor@health.gov.in"
                  class="w-full pl-9 pr-3 py-2 rounded-xl text-xs border outline-none transition-all"
                  :class="hospitalStore.darkMode ? 'bg-[#1E293B] border-[#334155] text-white focus:border-teal-500' : 'bg-slate-50 border-slate-200 text-slate-800 focus:border-teal-500'"
                />
              </div>
            </div>

            <!-- Password -->
            <div class="space-y-1">
              <label class="text-2xs font-bold uppercase tracking-wider" :class="hospitalStore.darkMode ? 'text-slate-400' : 'text-slate-600'">
                Password
              </label>
              <div class="relative">
                <Lock :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  v-model="password"
                  type="password"
                  placeholder="••••••••"
                  class="w-full pl-9 pr-3 py-2 rounded-xl text-xs border outline-none transition-all"
                  :class="hospitalStore.darkMode ? 'bg-[#1E293B] border-[#334155] text-white focus:border-teal-500' : 'bg-slate-50 border-slate-200 text-slate-800 focus:border-teal-500'"
                />
              </div>
            </div>

            <!-- Country (Only on register) -->
            <div v-if="isRegister" class="space-y-1">
              <label class="text-2xs font-bold uppercase tracking-wider" :class="hospitalStore.darkMode ? 'text-slate-400' : 'text-slate-600'">
                Country Jurisdiction
              </label>
              <div class="relative">
                <Globe :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <select
                  v-model="country"
                  class="w-full pl-9 pr-3 py-2 rounded-xl text-xs border outline-none transition-all"
                  :class="hospitalStore.darkMode ? 'bg-[#1E293B] border-[#334155] text-white focus:border-teal-500' : 'bg-slate-50 border-slate-200 text-slate-800 focus:border-teal-500'"
                >
                  <option value="India">🇮🇳 India</option>
                  <option value="Brazil">🇧🇷 Brazil</option>
                  <option value="South Africa">🇿🇦 South Africa</option>
                  <option value="China">🇨🇳 China</option>
                  <option value="Russia">🇷🇺 Russia</option>
                </select>
              </div>
            </div>

            <!-- Submit button -->
            <button
              type="submit"
              :disabled="authStore.isLoading"
              class="w-full py-2.5 rounded-xl text-xs font-bold text-white shadow-md transition-all flex items-center justify-center gap-2"
              style="background: linear-gradient(135deg, #0d9488, #0f766e);"
            >
              <span v-if="authStore.isLoading">Authenticating...</span>
              <span v-else>{{ isRegister ? 'Complete Registration' : 'Sign In to Session' }}</span>
            </button>
          </form>

          <!-- Quick 1-Click Demo Profiles -->
          <div class="p-6 pt-3 border-t bg-slate-50/50 dark:bg-[#0B1220]/50"
            :class="hospitalStore.darkMode ? 'border-[#1E293B]' : 'border-slate-100'">
            <div class="flex items-center gap-1.5 text-2xs font-semibold text-slate-400 mb-2">
              <Sparkles :size="12" class="text-amber-500" />
              <span>Quick 1-Click Demo Accounts:</span>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <button
                @click="handleDemoLogin('admin')"
                class="px-2.5 py-1.5 rounded-lg border text-2xs font-medium text-left transition-colors flex items-center gap-1.5"
                :class="hospitalStore.darkMode ? 'border-[#334155] hover:bg-[#1E293B] text-slate-300' : 'border-slate-200 hover:bg-white text-slate-700'"
              >
                <span>🛡️</span>
                <span class="truncate">Dr. Admin (HQ)</span>
              </button>
              <button
                @click="handleDemoLogin('india')"
                class="px-2.5 py-1.5 rounded-lg border text-2xs font-medium text-left transition-colors flex items-center gap-1.5"
                :class="hospitalStore.darkMode ? 'border-[#334155] hover:bg-[#1E293B] text-slate-300' : 'border-slate-200 hover:bg-white text-slate-700'"
              >
                <span>🇮🇳</span>
                <span class="truncate">India PHC Lead</span>
              </button>
              <button
                @click="handleDemoLogin('brazil')"
                class="px-2.5 py-1.5 rounded-lg border text-2xs font-medium text-left transition-colors flex items-center gap-1.5"
                :class="hospitalStore.darkMode ? 'border-[#334155] hover:bg-[#1E293B] text-slate-300' : 'border-slate-200 hover:bg-white text-slate-700'"
              >
                <span>🇧🇷</span>
                <span class="truncate">Brazil UBS Lead</span>
              </button>
              <button
                @click="handleDemoLogin('south_africa')"
                class="px-2.5 py-1.5 rounded-lg border text-2xs font-medium text-left transition-colors flex items-center gap-1.5"
                :class="hospitalStore.darkMode ? 'border-[#334155] hover:bg-[#1E293B] text-slate-300' : 'border-slate-200 hover:bg-white text-slate-700'"
              >
                <span>🇿🇦</span>
                <span class="truncate">SA CHC Lead</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>
