<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import gsap from 'gsap';
import Sidebar from './Sidebar.vue';
import Header from './Header.vue';
import CommandPalette from './CommandPalette.vue';
import SystemAlertTicker from '../shared/SystemAlertTicker.vue';
import ScenarioSimulatorModal from '../shared/ScenarioSimulatorModal.vue';
import TelemetryModal from '../shared/TelemetryModal.vue';

const route = useRoute();

const sidebarCollapsed = ref(false);
const mobileSidebarOpen = ref(false);

const cmdOpen = ref(false);
const simOpen = ref(false);
const telOpen = ref(false);

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value;
};

const closeMobileSidebar = () => {
  mobileSidebarOpen.value = false;
};

onMounted(() => {
  const handleKeydown = (e: KeyboardEvent) => {
    if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      cmdOpen.value = true;
    }
  };
  window.addEventListener('keydown', handleKeydown);
  onUnmounted(() => window.removeEventListener('keydown', handleKeydown));
});

const transitionEnter = (el: Element, done: () => void) => {
  gsap.fromTo(el, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.22, ease: "power2.out", onComplete: done });
};
const transitionLeave = (el: Element, done: () => void) => {
  gsap.to(el, { opacity: 0, y: -6, duration: 0.22, ease: "power2.in", onComplete: done });
};
</script>

<template>
  <div class="flex flex-col h-screen overflow-hidden bg-slate-50">
    <SystemAlertTicker />

    <div class="flex flex-1 min-h-0 overflow-hidden">
      <!-- Desktop sidebar -->
      <div class="hidden lg:flex flex-shrink-0">
        <Sidebar :collapsed="sidebarCollapsed" @toggle="toggleSidebar" />
      </div>

      <!-- Mobile sidebar overlay -->
      <div v-if="mobileSidebarOpen" class="lg:hidden fixed inset-0 z-40 flex">
        <div
          class="absolute inset-0 bg-slate-900/40 backdrop-blur-2xs"
          @click="closeMobileSidebar"
        ></div>
        <div class="relative z-10">
          <Sidebar :collapsed="false" @toggle="closeMobileSidebar" />
        </div>
      </div>

      <!-- Main content area -->
      <div class="flex flex-col flex-1 min-w-0 overflow-hidden">
        <Header
          @menuClick="mobileSidebarOpen = true"
          @commandPalette="cmdOpen = true"
          @simulatorClick="simOpen = true"
          @telemetryClick="telOpen = true"
        />
        <main class="flex-1 overflow-y-auto relative">
          <router-view v-slot="{ Component, route }">
            <transition
              mode="out-in"
              @enter="transitionEnter"
              @leave="transitionLeave"
              :css="false"
            >
              <component :is="Component" :key="route.path" class="min-h-full" />
            </transition>
          </router-view>
        </main>
      </div>
    </div>

    <!-- Modals -->
    <CommandPalette v-model:open="cmdOpen" />
    <ScenarioSimulatorModal v-model:open="simOpen" />
    <TelemetryModal v-model:open="telOpen" />
  </div>
</template>
