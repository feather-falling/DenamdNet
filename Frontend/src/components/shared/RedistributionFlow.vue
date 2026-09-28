<script setup lang="ts">
import { computed } from 'vue';
import { Truck, Clock, Package, CheckCircle2, Navigation } from 'lucide-vue-next';
import { formatNumber } from '../../lib/utils';
import gsap from 'gsap';

const props = withDefaults(defineProps<{
  transfers: any[];
  limit?: number;
}>(), {
  limit: 5
});

const displayTransfers = computed(() => {
  return props.transfers.slice(0, props.limit);
});

const vSlideIn = {
  mounted: (el: Element, binding: any) => {
    gsap.fromTo(el, 
      { opacity: 0, y: 10 },
      { 
        opacity: 1, 
        y: 0, 
        delay: (binding.value ?? 0) * 0.08,
        duration: 0.3, 
        ease: "power2.out" 
      }
    );
  }
};

const vAnimateTruck = {
  mounted: (el: Element, binding: any) => {
    if (!binding.value) { // if not completed
      gsap.to(el, {
        x: 20,
        duration: 1.75,
        ease: "power1.inOut",
        yoyo: true,
        repeat: -1
      });
      // Set initial x to -20
      gsap.set(el, { x: -20 });
    }
  }
};

const getSource = (item: any) => String(item.source_phc ?? item.source ?? 'PHC-SURPLUS-A');
const getDest = (item: any) => String(item.destination_phc ?? item.destination ?? 'PHC-DEFICIT-B');
const getMedicine = (item: any) => String(item.medicine ?? 'Essential Medical Resource');
const getQuantity = (item: any) => Number(item.quantity ?? 150);
const getStatus = (item: any) => String(item.status ?? 'IN_TRANSIT').toUpperCase();
const getEta = (item: any, index: number) => (item.eta as string) ?? `${(index + 1) * 2.5}h`;
const checkCompleted = (status: string) => status === 'COMPLETED';

</script>

<template>
  <div v-if="displayTransfers.length === 0" class="bg-white border border-slate-200/80 rounded-xl p-8 text-center">
    <Package :size="32" class="text-slate-300 mx-auto mb-2" />
    <p class="text-sm font-semibold text-slate-700">No Transfers Active</p>
    <p class="text-xs text-slate-400 mt-1">All network nodes are balanced or self-sufficient.</p>
  </div>

  <div v-else class="space-y-3">
    <div
      v-for="(item, index) in displayTransfers"
      :key="index"
      v-slide-in="index"
      class="bg-white border border-slate-200/80 hover:border-slate-300 rounded-xl p-4 shadow-xs hover:shadow-card transition-all relative overflow-hidden"
    >
      <!-- Top row: Medicine and Status -->
      <div class="flex items-center justify-between gap-2 mb-3">
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-teal-500"></span>
          <span class="text-xs font-bold text-slate-800">{{ getMedicine(item) }}</span>
          <span class="px-2 py-0.5 rounded-full bg-teal-50 text-teal-700 font-mono text-2xs font-bold border border-teal-200/60">
            {{ formatNumber(getQuantity(item)) }} UNITS
          </span>
        </div>
        <div class="flex items-center gap-2">
          <span
            class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-2xs font-semibold uppercase tracking-wider border"
            :class="checkCompleted(getStatus(item)) ? 'bg-green-50 text-green-700 border-green-200' : 'bg-blue-50 text-blue-700 border-blue-200'"
          >
            <CheckCircle2 v-if="checkCompleted(getStatus(item))" :size="11" />
            <Navigation v-else :size="11" class="animate-[spin_3s_linear_infinite]" />
            {{ getStatus(item) }}
          </span>
          <span class="text-2xs font-mono text-slate-400 flex items-center gap-1">
            <Clock :size="11" /> ETA {{ getEta(item, index) }}
          </span>
        </div>
      </div>

      <!-- Visual Node-to-Node Transfer Beam -->
      <div class="grid grid-cols-1 md:grid-cols-11 items-center gap-2 py-2 px-3 bg-slate-50/80 rounded-lg border border-slate-100">
        <!-- Source PHC -->
        <div class="md:col-span-4 flex items-center gap-2.5">
          <div class="w-7 h-7 rounded-md bg-emerald-100 text-emerald-700 flex items-center justify-center flex-shrink-0 font-bold text-2xs">
            SRC
          </div>
          <div class="min-w-0">
            <p class="text-2xs font-semibold text-emerald-800 uppercase tracking-wider">Surplus Origin</p>
            <p class="text-xs font-mono font-bold text-slate-800 truncate">{{ getSource(item) }}</p>
          </div>
        </div>

        <!-- Transit Pipeline Animation -->
        <div class="md:col-span-3 flex flex-col items-center justify-center py-1">
          <div class="w-full flex items-center justify-center relative">
            <!-- Dashed background track -->
            <div class="w-full h-0.5 border-t-2 border-dashed border-teal-300 relative"></div>

            <!-- Pulsing carrier icon -->
            <div
              v-animate-truck="checkCompleted(getStatus(item))"
              class="absolute bg-teal-600 text-white p-1 rounded-full shadow-xs"
            >
              <Truck :size="11" />
            </div>
          </div>
          <span class="text-3xs text-teal-700 font-semibold tracking-wider mt-1.5 uppercase">
            {{ checkCompleted(getStatus(item)) ? 'Transfer Delivered' : 'Cold-Chain En Route' }}
          </span>
        </div>

        <!-- Destination PHC -->
        <div class="md:col-span-4 flex items-center gap-2.5 md:justify-end">
          <div class="min-w-0 text-left md:text-right">
            <p class="text-2xs font-semibold text-amber-700 uppercase tracking-wider">Deficit Destination</p>
            <p class="text-xs font-mono font-bold text-slate-800 truncate">{{ getDest(item) }}</p>
          </div>
          <div class="w-7 h-7 rounded-md bg-amber-100 text-amber-700 flex items-center justify-center flex-shrink-0 font-bold text-2xs">
            DST
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
