<script setup lang="ts">
import { Toaster } from 'vue-sonner';
</script>

<template>
  <router-view />
  <Toaster
    position="bottom-right"
    :toastOptions="{
      style: { fontSize: '13px', border: '1px solid #e2e8f0' }
    }"
  />
</template>
