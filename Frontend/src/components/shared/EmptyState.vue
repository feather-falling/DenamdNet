<script setup lang="ts">
defineProps<{
  title: string;
  description?: string;
  icon?: any;
}>();
</script>

<template>
  <div class="flex flex-col items-center justify-center py-16 px-8 text-center">
    <div v-if="icon" class="w-12 h-12 bg-slate-50 border border-slate-100 rounded-xl flex items-center justify-center mb-4">
      <component :is="icon" :size="22" class="text-slate-300" :stroke-width="1.5" />
    </div>
    <h3 class="text-sm font-semibold text-slate-600 mb-1">{{ title }}</h3>
    <p v-if="description" class="text-xs text-slate-400 max-w-xs">{{ description }}</p>
    <div v-if="$slots.action" class="mt-4">
      <slot name="action"></slot>
    </div>
  </div>
</template>
