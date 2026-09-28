<script setup lang="ts">
import { Settings as SettingsIcon } from 'lucide-vue-next';
import PageHeader from '../components/shared/PageHeader.vue';

const apiUrl = import.meta.env.VITE_API_BASE_URL ?? 'Not set';
const mockMode = import.meta.env.VITE_MOCK_MODE === 'true';
</script>

<template>
  <div class="page-container py-6 max-w-xl">
    <PageHeader title="Settings" subtitle="System configuration" :icon="SettingsIcon" />

    <div class="bg-white border border-slate-100 rounded-lg shadow-card p-5 space-y-4">
      <h3 class="text-sm font-semibold text-slate-700">API Configuration</h3>
      <div class="space-y-3 text-sm">
        <div class="flex justify-between items-center py-2 border-b border-slate-50">
          <span class="text-slate-500">Backend URL</span>
          <code class="text-xs bg-slate-50 border border-slate-100 rounded px-2 py-1 text-teal-700">{{ apiUrl }}</code>
        </div>
        <div class="flex justify-between items-center py-2 border-b border-slate-50">
          <span class="text-slate-500">Mock Mode</span>
          <span
            class="text-xs font-semibold px-2 py-0.5 rounded border"
            :class="mockMode ? 'bg-amber-50 text-amber-700 border-amber-200' : 'bg-green-50 text-green-700 border-green-200'"
          >
            {{ mockMode ? 'ENABLED' : 'DISABLED' }}
          </span>
        </div>
      </div>
      <p class="text-xs text-slate-400">
        Configure these values via <code class="text-xs bg-slate-50 px-1 rounded">.env</code> file using
        <code class="text-xs bg-slate-50 px-1 rounded ml-1">VITE_API_BASE_URL</code> and
        <code class="text-xs bg-slate-50 px-1 rounded ml-1">VITE_MOCK_MODE</code>.
      </p>
    </div>
  </div>
</template>
