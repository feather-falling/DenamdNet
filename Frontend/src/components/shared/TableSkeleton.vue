<script setup lang="ts">
withDefaults(defineProps<{
  rows?: number;
  cols?: number;
}>(), {
  rows: 5,
  cols: 6
});
</script>

<template>
  <tr v-for="i in rows" :key="i" class="border-b border-slate-50">
    <td v-for="j in cols" :key="j" class="px-3 py-3">
      <div class="skeleton h-4 rounded" :style="{ width: `${60 + ((j * 13) % 30)}%` }"></div>
    </td>
  </tr>
</template>
