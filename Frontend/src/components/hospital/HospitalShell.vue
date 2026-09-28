<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue';
import gsap from 'gsap';
import HospitalSidebar from './HospitalSidebar.vue';
import HospitalHeader from './HospitalHeader.vue';
import EmergencyModal from './EmergencyModal.vue';
import EmergencyTriggerModal from './EmergencyTriggerModal.vue';
import CommandPalette from '../layout/CommandPalette.vue';
import AuthModal from '../auth/AuthModal.vue';
import UserProfileModal from '../auth/UserProfileModal.vue';
import { useHospitalStore } from '../../stores/hospitalStore';

const store = useHospitalStore();

const transitionEnter = (el: Element, done: () => void) => {
  gsap.fromTo(el, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.22, ease: 'power2.out', onComplete: done });
};
const transitionLeave = (el: Element, done: () => void) => {
  gsap.to(el, { opacity: 0, y: -6, duration: 0.18, ease: 'power2.in', onComplete: done });
};

// Global Ctrl+K / Cmd+K listener
const handleGlobalKeyDown = (e: KeyboardEvent) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault();
    store.commandPaletteOpen = !store.commandPaletteOpen;
  }
};

onMounted(() => {
  window.addEventListener('keydown', handleGlobalKeyDown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeyDown);
});

// Apply dark class to body
watch(() => store.darkMode, (dark) => {
  document.body.classList.toggle('dark', dark);
}, { immediate: true });
</script>

<template>
  <div
    class="flex h-screen overflow-hidden dark-transition"
    :class="store.darkMode ? 'bg-[#0B1220]' : 'bg-[#F8FAFC]'"
  >
    <!-- Desktop Sidebar -->
    <div class="hidden lg:flex flex-shrink-0">
      <HospitalSidebar
        :collapsed="store.sidebarCollapsed"
        @toggle="store.toggleSidebar()"
        @close="store.setMobileSidebar(false)"
      />
    </div>

    <!-- Mobile Sidebar Overlay -->
    <Transition
      enter-active-class="transition duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="store.mobileSidebarOpen"
        class="lg:hidden fixed inset-0 z-40 flex"
      >
        <div
          class="absolute inset-0 emergency-overlay"
          @click="store.setMobileSidebar(false)"
        ></div>
        <div class="relative z-10 flex-shrink-0">
          <HospitalSidebar
            :collapsed="false"
            @toggle="store.setMobileSidebar(false)"
            @close="store.setMobileSidebar(false)"
          />
        </div>
      </div>
    </Transition>

    <!-- Main Content -->
    <div class="flex flex-col flex-1 min-w-0 overflow-hidden" :class="store.compactMode ? 'compact-density' : ''">
      <HospitalHeader
        @menuClick="store.setMobileSidebar(true)"
        @searchClick="store.commandPaletteOpen = true"
        @openAuth="store.authModalOpen = true"
        @openProfile="store.profileModalOpen = true"
      />
      <main class="flex-1 overflow-y-auto relative flex flex-col min-h-0">
        <router-view v-slot="{ Component, route }">
          <transition
            mode="out-in"
            @enter="transitionEnter"
            @leave="transitionLeave"
            :css="false"
          >
            <component :is="Component" :key="route.path" class="flex-1 flex flex-col min-h-full" />
          </transition>
        </router-view>
      </main>
    </div>

    <!-- Emergency Modal (popup) -->
    <EmergencyModal />

    <!-- Emergency Trigger Modal -->
    <EmergencyTriggerModal />

    <!-- Global Command Palette -->
    <CommandPalette v-model:open="store.commandPaletteOpen" />

    <!-- Authentication Modal -->
    <AuthModal v-model:open="store.authModalOpen" />

    <!-- User Profile Details Modal -->
    <UserProfileModal v-model:open="store.profileModalOpen" />
  </div>
</template>
