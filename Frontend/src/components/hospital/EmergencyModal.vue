<script setup lang="ts">
import { computed } from 'vue';
import { AlertTriangle, Bed, Phone, Eye, Ambulance, CheckCheck, X } from 'lucide-vue-next';
import { useHospitalStore } from '../../stores/hospitalStore';

const store = useHospitalStore();
const popup = computed(() => store.activeEmergencyPopup);

const acknowledge = () => {
  if (popup.value) {
    store.acknowledgeAlert('ALT-001');
    store.dismissEmergencyPopup();
  }
};
</script>

<template>
  <Transition
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="popup?.visible"
      class="fixed inset-0 z-[9999] flex items-center justify-center p-4"
      style="background: rgba(0,0,0,0.7); backdrop-filter: blur(6px);"
    >
      <Transition
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="opacity-0 scale-90 translate-y-4"
        enter-to-class="opacity-100 scale-100 translate-y-0"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div
          v-if="popup?.visible"
          class="relative w-full max-w-md rounded-2xl overflow-hidden shadow-emergency"
          style="background: #0F172A; border: 1px solid rgba(220,38,38,0.4);"
        >
          <!-- Red glow top bar -->
          <div class="h-1 w-full" style="background: linear-gradient(90deg, #dc2626, #ef4444, #dc2626);"></div>

          <!-- Close -->
          <button
            @click="store.dismissEmergencyPopup()"
            class="absolute top-3 right-3 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors z-10"
          >
            <X :size="16" />
          </button>

          <!-- Header -->
          <div class="px-6 pt-5 pb-4">
            <div class="flex items-center gap-3 mb-4">
              <div class="relative emergency-ring">
                <div class="w-12 h-12 rounded-full flex items-center justify-center"
                  style="background: rgb(220 38 38 / 0.2); border: 2px solid rgb(220 38 38 / 0.5);">
                  <AlertTriangle :size="22" class="text-red-500" :stroke-width="2.5" />
                </div>
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <span class="text-2xs font-bold uppercase tracking-widest text-red-500 animate-pulse">🚨 Emergency Alert</span>
                </div>
                <h3 class="text-lg font-bold text-white mt-0.5">Critical Patient Arrived</h3>
              </div>
            </div>

            <!-- Details Grid -->
            <div class="grid grid-cols-2 gap-3">
              <div class="rounded-xl p-3" style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08);">
                <p class="text-2xs text-slate-500 font-semibold uppercase tracking-wider mb-1">Patient</p>
                <p class="text-sm font-semibold text-white">{{ popup?.patient || 'Unknown Patient' }}</p>
              </div>
              <div class="rounded-xl p-3" style="background: rgba(220,38,38,0.12); border: 1px solid rgba(220,38,38,0.25);">
                <p class="text-2xs text-slate-500 font-semibold uppercase tracking-wider mb-1">Priority</p>
                <p class="text-sm font-bold text-red-400">{{ popup?.priority }}</p>
              </div>
              <div class="rounded-xl p-3" style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08);">
                <p class="text-2xs text-slate-500 font-semibold uppercase tracking-wider mb-1">Department</p>
                <p class="text-sm font-semibold text-white">{{ popup?.department }}</p>
              </div>
              <div class="rounded-xl p-3" style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08);">
                <p class="text-2xs text-slate-500 font-semibold uppercase tracking-wider mb-1">Required</p>
                <p class="text-sm font-semibold text-amber-400">{{ popup?.required }}</p>
              </div>
              <div class="rounded-xl p-3" style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08);">
                <p class="text-2xs text-slate-500 font-semibold uppercase tracking-wider mb-1">Doctor</p>
                <p class="text-sm font-semibold text-white">{{ popup?.doctor }}</p>
              </div>
              <div class="rounded-xl p-3" style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08);">
                <p class="text-2xs text-slate-500 font-semibold uppercase tracking-wider mb-1">Arrival</p>
                <p class="text-sm font-semibold text-teal-400">{{ popup?.arrival }}</p>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="px-6 pb-5 grid grid-cols-2 gap-2.5">
            <button class="flex items-center justify-center gap-2 py-2.5 rounded-xl text-xs font-semibold text-white transition-all hover:scale-105"
              style="background: rgba(37,99,235,0.3); border: 1px solid rgba(37,99,235,0.4);">
              <Eye :size="14" /> View Patient
            </button>
            <button class="flex items-center justify-center gap-2 py-2.5 rounded-xl text-xs font-semibold text-white transition-all hover:scale-105"
              style="background: rgba(124,58,237,0.3); border: 1px solid rgba(124,58,237,0.4);">
              <Bed :size="14" /> Assign Bed
            </button>
            <button class="flex items-center justify-center gap-2 py-2.5 rounded-xl text-xs font-semibold text-white transition-all hover:scale-105"
              style="background: rgba(22,163,74,0.3); border: 1px solid rgba(22,163,74,0.4);">
              <Phone :size="14" /> Call Doctor
            </button>
            <button class="flex items-center justify-center gap-2 py-2.5 rounded-xl text-xs font-semibold text-white transition-all hover:scale-105"
              style="background: rgba(245,158,11,0.3); border: 1px solid rgba(245,158,11,0.4);">
              <Ambulance :size="14" /> Dispatch Ambulance
            </button>
            <button
              @click="acknowledge"
              class="col-span-2 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-bold text-white transition-all hover:scale-105"
              style="background: linear-gradient(135deg, #dc2626, #b91c1c); box-shadow: 0 4px 20px rgba(220,38,38,0.4);"
            >
              <CheckCheck :size="16" /> Acknowledge Emergency
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>
