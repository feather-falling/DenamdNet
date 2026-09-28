<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import gsap from 'gsap';

const props = defineProps<{
  value: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  duration?: number;
}>();

const display = ref('0');
const count = { val: 0 };

const animateTo = (newVal: number) => {
  gsap.to(count, {
    val: newVal,
    duration: props.duration ?? 1.2,
    ease: "power2.out",
    onUpdate: () => {
      display.value = new Intl.NumberFormat('en-IN', {
        minimumFractionDigits: props.decimals ?? 0,
        maximumFractionDigits: props.decimals ?? 0,
      }).format(count.val);
    }
  });
};

onMounted(() => {
  animateTo(props.value);
});

watch(() => props.value, (newVal) => {
  animateTo(newVal);
});
</script>

<template>
  <span>{{ prefix }}{{ display }}{{ suffix }}</span>
</template>
