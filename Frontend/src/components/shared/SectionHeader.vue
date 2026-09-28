<script setup lang="ts">
defineProps<{
  title: string;
  subtitle?: string;
}>();
</script>

<template>
  <div class="flex items-center justify-between mb-3">
    <div>
      <h2 class="text-sm font-semibold text-slate-700">{{ title }}</h2>
      <p v-if="subtitle" class="text-xs text-slate-400 mt-0.5">{{ subtitle }}</p>
    </div>
    <div v-if="$slots.actions" class="flex items-center gap-2">
      <slot name="actions"></slot>
    </div>
  </div>
</template>
