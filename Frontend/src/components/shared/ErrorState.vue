<script setup lang="ts">
import { ref } from 'vue';

const props = withDefaults(defineProps<{
  title?: string;
  description?: string;
  technical?: string;
}>(), {
  title: 'Something went wrong',
  description: 'The application could not complete this request.'
});

const showTechnical = ref(false);
</script>

<template>
  <div class="flex flex-col items-center justify-center py-12 px-8 text-center">
    <div class="w-12 h-12 bg-red-50 border border-red-100 rounded-xl flex items-center justify-center mb-4">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="text-red-400">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
    </div>
    <h3 class="text-sm font-semibold text-slate-700 mb-1">{{ title }}</h3>
    <p class="text-xs text-slate-400 max-w-sm mb-4">{{ description }}</p>
    <div v-if="$slots.action" class="mb-4">
      <slot name="action"></slot>
    </div>
    <div v-if="technical" class="mt-2">
      <button
        @click="showTechnical = !showTechnical"
        class="text-xs text-slate-400 hover:text-slate-600 underline underline-offset-2"
      >
        {{ showTechnical ? 'Hide' : 'Show' }} technical details
      </button>
      <pre
        v-if="showTechnical"
        class="mt-2 text-left text-2xs bg-slate-50 border border-slate-100 rounded-lg p-3 max-w-md overflow-auto text-slate-500 font-mono"
      >{{ technical }}</pre>
    </div>
  </div>
</template>
