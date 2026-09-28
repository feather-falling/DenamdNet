<script setup lang="ts">
defineProps<{
  title: string;
  subtitle?: string;
  icon?: any;
}>();
</script>

<template>
  <div class="flex items-start justify-between gap-4 mb-6">
    <div class="flex items-center gap-3 min-w-0">
      <div v-if="icon" class="w-9 h-9 bg-teal-50 border border-teal-100 rounded-lg flex items-center justify-center flex-shrink-0">
        <component :is="icon" :size="18" class="text-teal-700" :stroke-width="2" />
      </div>
      <div class="min-w-0">
        <h1 class="text-xl font-bold text-slate-800 tracking-tight">{{ title }}</h1>
        <p v-if="subtitle" class="text-sm text-slate-500 mt-0.5 truncate">{{ subtitle }}</p>
      </div>
    </div>
    <div v-if="$slots.actions" class="flex items-center gap-2 flex-shrink-0">
      <slot name="actions"></slot>
    </div>
  </div>
</template>
