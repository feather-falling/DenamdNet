<script setup lang="ts">
const heights = [60, 80, 45, 90, 70, 55, 85];
</script>

<template>
  <div class="bg-white border border-slate-100 rounded-lg p-4 shadow-card">
    <div class="skeleton h-3 w-32 rounded mb-4"></div>
    <div class="flex items-end gap-2 h-32">
      <div
        v-for="(h, i) in heights"
        :key="i"
        class="skeleton flex-1 rounded-sm"
        :style="{ height: `${h}%` }"
      ></div>
    </div>
  </div>
</template>
