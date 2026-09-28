<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue';
import { MapPin, Search, X, Radio, Globe2 } from 'lucide-vue-next';
import { LMap, LTileLayer, LMarker, LPopup } from '@vue-leaflet/vue-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import PageHeader from '../components/shared/PageHeader.vue';
import SectionHeader from '../components/shared/SectionHeader.vue';
import StatusBadge from '../components/shared/StatusBadge.vue';
import EmptyState from '../components/shared/EmptyState.vue';
import { usePredictionResult } from '../hooks/usePredictionResult';
import { getPHCLatLng, getRecords, formatNumber, formatDays } from '../lib/utils';
import { mockPHCData } from '../data/mock/mockPHCData';
import { useDebounce } from '../hooks/useUtils';
import type { PHCRecord, ResourceRecord } from '../types';
import gsap from 'gsap';

// Fix default Leaflet marker icon
(L.Icon.Default.prototype as any)._getIconUrl = undefined;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const createStatusIcon = (status?: string): L.DivIcon => {
  const s = status?.toUpperCase();
  const dotColor = s === 'CONTROLLED' ? '#10b981' : s === 'ATTENTION' ? '#f59e0b' : s === 'CRITICAL' ? '#ef4444' : '#64748b';
  const isAlert = s === 'CRITICAL' || s === 'ATTENTION';

  return L.divIcon({
    className: '',
    html: `
      <div style="position:relative; width:26px; height:26px; display:flex; align-items:center; justify-content:center;">
        ${
          isAlert
            ? `<div style="
                position:absolute; inset:-4px; border-radius:50%;
                background:${dotColor}; opacity:0.35;
                animation: radar-pulse-fast 2s cubic-bezier(0, 0, 0.2, 1) infinite;
              "></div>`
            : ''
        }
        <div style="
          width:18px; height:18px; border-radius:50%;
          background:${dotColor};
          border:2.5px solid white;
          box-shadow:0 2px 6px rgba(0,0,0,0.3);
          cursor:pointer;
          position:relative; z-index:2;
        "></div>
      </div>
    `,
    iconSize: [26, 26],
    iconAnchor: [13, 13],
  });
};

const { data: prediction } = usePredictionResult();
const search = ref('');
const selectedPHC = ref<PHCRecord | null>(null);
const flyTo = ref<[number, number] | null>(null);
const countryFilter = ref('ALL');
const onlyCritical = ref(false);
const debouncedSearch = useDebounce(search, 200);

const mapRef = ref<any>(null);

watch(flyTo, (newVal) => {
  if (newVal && mapRef.value) {
    const map = mapRef.value.leafletObject;
    if (map) map.flyTo(newVal, 9, { duration: 1.2 });
  }
});

const allPHCs: PHCRecord[] = mockPHCData;
const resultRecords = computed(() => getRecords(prediction.value as any) as ResourceRecord[]);
const resultByPhcId = computed(() => {
  const map: Record<string, ResourceRecord> = {};
  resultRecords.value.forEach((r) => {
    const id = r.phc_id ?? r.phc;
    if (id) map[id] = r;
  });
  return map;
});

const countries = ['ALL', 'India', 'South Africa', 'Brazil', 'China', 'Russia'];

const filtered = computed(() => {
  let list = allPHCs;
  if (countryFilter.value !== 'ALL') list = list.filter((p) => p.country === countryFilter.value);
  if (onlyCritical.value) {
    list = list.filter((p) => {
      const res = resultByPhcId.value[p.phc_id!];
      const st = String(res?.stock_status ?? '').toUpperCase();
      return st === 'CRITICAL' || st === 'ATTENTION';
    });
  }
  if (debouncedSearch.value.trim()) {
    const q = debouncedSearch.value.toLowerCase();
    list = list.filter((p) =>
      p.phc_id?.toLowerCase().includes(q) ||
      p.name?.toLowerCase().includes(q) ||
      p.district?.toLowerCase().includes(q) ||
      p.state?.toLowerCase().includes(q) ||
      p.country?.toLowerCase().includes(q)
    );
  }
  return list;
});

const phcsWithCoords = computed(() => filtered.value.filter((p) => getPHCLatLng(p as any) !== null));

const handleSelectPHC = (phc: PHCRecord) => {
  selectedPHC.value = phc;
  const ll = getPHCLatLng(phc as any);
  if (ll) flyTo.value = ll;
};

// Mapbox Integration
const mapboxToken = (import.meta.env.VITE_MAPBOX_ACCESS_TOKEN || '').trim();
const mapboxActive = ref(Boolean(mapboxToken));
const tileUrl = computed(() => {
  if (mapboxToken && mapboxActive.value) {
    return `https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/256/{z}/{x}/{y}@2x?access_token=${mapboxToken}`;
  }
  return 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
});
const tileAttribution = computed(() => {
  if (mapboxToken && mapboxActive.value) {
    return '&copy; <a href="https://www.mapbox.com/about/maps/" target="_blank">Mapbox</a> &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>';
  }
  return '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>';
});
const onTileError = () => {
  if (mapboxActive.value) {
    console.warn('PHCNetwork Mapbox tile request failed. Falling back to OpenStreetMap.');
    mapboxActive.value = false;
  }
};

import { applyEnglishCountryLabels } from '../lib/mapboxUtils';
// Language setting applied specifically to country/region place labels across all zoom levels

// Panel Animation
const onEnterPanel = (el: Element, done: () => void) => {
  gsap.fromTo(el, { opacity: 0, y: 10, scale: 0.98 }, { opacity: 1, y: 0, scale: 1, duration: 0.25, onComplete: done });
};
const onLeavePanel = (el: Element, done: () => void) => {
  gsap.to(el, { opacity: 0, y: 10, scale: 0.98, duration: 0.2, onComplete: done });
};

</script>

<template>
  <div class="flex flex-col h-full">
    <div class="page-container py-4 flex-shrink-0">
      <PageHeader
        title="Federated PHC Network Map"
        subtitle="Real-time geographical telemetry and stockout risk radar across member nations"
        :icon="MapPin"
      >
        <template #actions>
          <div class="flex items-center gap-2">
            <button
              @click="onlyCritical = !onlyCritical"
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all border"
              :class="onlyCritical ? 'bg-red-500 text-white border-red-600 shadow-xs' : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'"
            >
              <Radio :size="13" :class="onlyCritical ? 'animate-pulse' : ''" />
              <span>Critical Nodes Only</span>
            </button>
          </div>
        </template>
      </PageHeader>

      <!-- Quick Country Filter Pills -->
      <div class="flex items-center gap-1.5 pt-2 overflow-x-auto pb-1">
        <Globe2 :size="13" class="text-slate-400 flex-shrink-0 mr-1" />
        <button
          v-for="c in countries"
          :key="c"
          @click="countryFilter = c"
          class="px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap transition-all cursor-pointer"
          :class="countryFilter === c ? 'bg-teal-600 text-white shadow-2xs' : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'"
        >
          {{ c === 'ALL' ? 'All Territories' : c }}
        </button>
      </div>
    </div>

    <div class="flex-1 flex flex-col lg:flex-row gap-4 min-h-0 overflow-hidden px-4 sm:px-6 lg:px-8 pb-6">
      <!-- Map Container -->
      <div class="flex-1 rounded-2xl overflow-hidden border border-slate-200 shadow-card relative min-h-[380px] z-0">
        <l-map ref="mapRef" :zoom="2" :center="[20, 30]" :useGlobalLeaflet="false">
          <l-tile-layer
            :url="tileUrl"
            :attribution="tileAttribution"
            @tileerror="onTileError"
          />
          <l-marker
            v-for="phc in phcsWithCoords"
            :key="phc.phc_id"
            :lat-lng="getPHCLatLng(phc as any)"
            :icon="(createStatusIcon(resultByPhcId[phc.phc_id!]?.stock_status) as any)"
            @click="handleSelectPHC(phc)"
          >
            <l-popup>
              <div style="font-family: Inter, sans-serif; font-size: 12px; min-width: 150px">
                <strong style="color: #0f172a">{{ phc.phc_id }}</strong>
                <div v-if="phc.name" style="font-weight: 600">{{ phc.name }}</div>
                <div v-if="phc.district" style="color: #64748b; font-size: 11px">
                  {{ phc.district }}, {{ phc.country }}
                </div>
                <div v-if="resultByPhcId[phc.phc_id!]?.risk_level" style="margin-top: 6px; font-weight: 700; color: #0d9488">
                  Risk: {{ resultByPhcId[phc.phc_id!]?.risk_level }}
                </div>
              </div>
            </l-popup>
          </l-marker>
        </l-map>

        <!-- Floating Map Legend -->
        <div class="absolute bottom-4 left-4 z-10 bg-white/95 backdrop-blur-md border border-slate-200/80 rounded-xl px-3.5 py-2.5 text-xs shadow-lg">
          <p class="font-bold text-slate-700 mb-2 uppercase text-3xs tracking-wider">Node Status</p>
          <div v-for="s in [
            { label: 'Controlled', color: '#10b981' },
            { label: 'Attention (Buffer Low)', color: '#f59e0b' },
            { label: 'Critical (Radar Pulse)', color: '#ef4444' },
            { label: 'Baseline / Unlinked', color: '#64748b' },
          ]" :key="s.label" class="flex items-center gap-2 mb-1.5">
            <span class="w-2.5 h-2.5 rounded-full border border-white shadow-2xs" :style="{ background: s.color }"></span>
            <span class="text-slate-600 font-medium text-2xs">{{ s.label }}</span>
          </div>
        </div>
      </div>

      <!-- Sidebar Panel -->
      <div class="w-full lg:w-80 flex flex-col gap-3.5 overflow-y-auto">
        <div class="bg-white border border-slate-200/80 rounded-xl shadow-card p-3.5 space-y-2">
          <SectionHeader title="PHC Node Registry" :subtitle="`${filtered.length} nodes match criteria`" />
          <div class="flex items-center gap-2 border border-slate-200 rounded-lg px-2.5 py-1.5 bg-slate-50/50">
            <Search :size="14" class="text-slate-400" />
            <input v-model="search" placeholder="Search by code, district, city..." class="flex-1 text-xs outline-none bg-transparent text-slate-700 placeholder:text-slate-400" />
            <button v-if="search" @click="search = ''"><X :size="13" class="text-slate-400" /></button>
          </div>
        </div>

        <div class="bg-white border border-slate-200/80 rounded-xl shadow-card flex-1 overflow-y-auto max-h-[350px] lg:max-h-none">
          <EmptyState v-if="filtered.length === 0" :icon="MapPin" title="No nodes found" description="Adjust search query or country filter." />
          <ul v-else class="divide-y divide-slate-100">
            <li v-for="phc in filtered" :key="phc.phc_id">
              <button
                @click="handleSelectPHC(phc)"
                class="w-full text-left px-3.5 py-3 transition-colors cursor-pointer"
                :class="selectedPHC?.phc_id === phc.phc_id ? 'bg-teal-50/80 border-l-4 border-teal-600' : 'hover:bg-slate-50'"
              >
                <div class="flex items-start justify-between gap-2">
                  <div class="min-w-0">
                    <p class="text-xs font-mono font-bold text-slate-800 truncate">{{ phc.phc_id }}</p>
                    <p class="text-2xs text-slate-500 font-medium truncate mt-0.5">{{ [phc.district, phc.country].filter(Boolean).join(', ') }}</p>
                  </div>
                  <StatusBadge v-if="resultByPhcId[phc.phc_id!]?.stock_status" type="status" :value="resultByPhcId[phc.phc_id!]?.stock_status" :showDot="true" />
                </div>
              </button>
            </li>
          </ul>
        </div>

        <transition @enter="onEnterPanel" @leave="onLeavePanel" :css="false">
          <div v-if="selectedPHC" class="bg-white border border-slate-200 rounded-xl shadow-card p-4.5 space-y-3">
            <div class="flex items-start justify-between">
              <div>
                <span class="text-2xs font-semibold text-teal-700 bg-teal-50 px-2 py-0.5 rounded uppercase font-mono">{{ selectedPHC.phc_id }}</span>
                <h4 class="text-sm font-bold text-slate-800 mt-1">{{ selectedPHC.name || 'Primary Health Center' }}</h4>
                <p class="text-2xs text-slate-500 mt-0.5">{{ [selectedPHC.district, selectedPHC.state, selectedPHC.country].filter(Boolean).join(', ') }}</p>
              </div>
              <button @click="selectedPHC = null" class="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-slate-100">
                <X :size="15" />
              </button>
            </div>
            
            <div v-if="resultByPhcId[selectedPHC.phc_id!]" class="space-y-3 pt-2 border-t border-slate-100">
              <div class="flex flex-wrap gap-1.5">
                <StatusBadge v-if="resultByPhcId[selectedPHC.phc_id!].risk_level" type="risk" :value="resultByPhcId[selectedPHC.phc_id!].risk_level" />
                <StatusBadge v-if="resultByPhcId[selectedPHC.phc_id!].stock_status" type="status" :value="resultByPhcId[selectedPHC.phc_id!].stock_status" />
                <StatusBadge v-if="(resultByPhcId[selectedPHC.phc_id!].anomaly ?? resultByPhcId[selectedPHC.phc_id!].anomaly_detected) !== undefined" type="anomaly" :value="resultByPhcId[selectedPHC.phc_id!].anomaly ?? resultByPhcId[selectedPHC.phc_id!].anomaly_detected" />
              </div>
              <div class="grid grid-cols-2 gap-2 text-xs bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                <div>
                  <p class="text-3xs text-slate-400 font-semibold uppercase">Current Stock</p>
                  <p class="font-bold text-slate-800 mt-0.5">{{ formatNumber(resultByPhcId[selectedPHC.phc_id!].current_stock) }} units</p>
                </div>
                <div>
                  <p class="text-3xs text-slate-400 font-semibold uppercase">Daily Demand</p>
                  <p class="font-bold text-slate-800 mt-0.5">{{ formatNumber(resultByPhcId[selectedPHC.phc_id!].daily_demand ?? resultByPhcId[selectedPHC.phc_id!].forecast_demand) }}/day</p>
                </div>
                <div>
                  <p class="text-3xs text-slate-400 font-semibold uppercase">Stockout Risk</p>
                  <p class="font-bold text-amber-700 mt-0.5">{{ formatDays(resultByPhcId[selectedPHC.phc_id!].stockout_days) }}</p>
                </div>
                <div>
                  <p class="text-3xs text-slate-400 font-semibold uppercase">Medicine</p>
                  <p class="font-bold text-slate-800 truncate mt-0.5">{{ resultByPhcId[selectedPHC.phc_id!].medicine ?? '—' }}</p>
                </div>
              </div>
            </div>
            <p v-else class="text-xs text-slate-400 italic">No real-time inventory telemetry linked.</p>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<style>
@keyframes radar-pulse-fast {
  0% { transform: scale(0.95); opacity: 0.6; }
  100% { transform: scale(2.2); opacity: 0; }
}
.leaflet-container {
  font-family: inherit;
}
</style>
