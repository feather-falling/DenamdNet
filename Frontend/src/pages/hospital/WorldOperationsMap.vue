<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import {
  Globe, Search, Filter, AlertTriangle, ShieldCheck, Activity,
  Layers, MapPin, Building2, Pill, Users, Bed, ChevronRight,
  TrendingUp, RefreshCw, X, Eye, ExternalLink, Flame, Sparkles, Check
} from 'lucide-vue-next';
import { useHospitalStore } from '../../stores/hospitalStore';
import {
  fetchAllMapData,
  type EnrichedPHC,
  type MapSummaryMetrics,
  type OperationalCondition,
  type AlertDetail,
  type MedicinePredictionDetail
} from '../../services/mapDataService';

const store = useHospitalStore();
const router = useRouter();
const dark = computed(() => store.darkMode);

// Map instance & DOM refs
const mapContainer = ref<HTMLDivElement | null>(null);
let map: L.Map | null = null;
let markersLayer: L.LayerGroup | null = null;
const phcMarkersMap = new Map<string, L.Marker>();
let currentTileLayer: L.TileLayer | null = null;
let currentReferenceLayer: L.TileLayer | null = null;
let resizeObserver: ResizeObserver | null = null;

// Support existing 'mapbox' key name as primary, with fallback to standard environment variables
const rawMapboxToken = (
  (typeof window !== 'undefined' && ((window as any).mapbox || localStorage.getItem('mapbox') || sessionStorage.getItem('mapbox'))) ||
  import.meta.env.VITE_MAPBOX_ACCESS_TOKEN ||
  (import.meta.env as any).VITE_MAPBOX_TOKEN ||
  (import.meta.env as any).VITE_MAPBOX ||
  (import.meta.env as any).mapbox ||
  (import.meta.env as any).MAPBOX ||
  ''
).trim();

// Treat missing or dummy placeholder tokens (e.g. 'pk.xxxxxxxxxxxxxxxxx') as unconfigured
const isDummyToken = !rawMapboxToken || /^pk\.x+$/i.test(rawMapboxToken) || rawMapboxToken.includes('xxxxxxxx');
const mapboxToken = isDummyToken ? '' : rawMapboxToken;

// Basemap Provider State:
// When a valid Mapbox token is present, initialize with Mapbox as primary.
// Otherwise, start directly with the Esri World Basemap (English) fallback without throwing 401 errors.
const tileProvider = ref<'mapbox' | 'esri' | 'satellite'>(mapboxToken ? 'mapbox' : 'esri');
const mapboxActive = ref(Boolean(mapboxToken));
const mapboxError = ref<string | null>(null);
const mapTilesLoading = ref(false);

// State
const loading = ref(true);
const error = ref<string | null>(null);
const allPHCs = ref<EnrichedPHC[]>([]);
const metrics = ref<MapSummaryMetrics | null>(null);
const medicinesList = ref<string[]>([]);
const districtsList = ref<string[]>([]);

// Dynamic counts derived directly from canonical PHC master records
const indiaCount = computed(() => allPHCs.value.filter(p => p.country === 'India').length);
const brazilCount = computed(() => allPHCs.value.filter(p => p.country === 'Brazil').length);
const saCount = computed(() => allPHCs.value.filter(p => p.country === 'South Africa').length);
const chinaCount = computed(() => allPHCs.value.filter(p => p.country === 'China').length);
const russiaCount = computed(() => allPHCs.value.filter(p => p.country === 'Russia').length);

// Selected PHC Inspection Drawer
const selectedPHC = ref<EnrichedPHC | null>(null);
const showInspectionDrawer = ref(false);
const activeDrawerTab = ref<'overview' | 'medicines' | 'alerts' | 'capacity'>('overview');

// Filters
const filterSearch = ref('');
const filterCountry = ref<'ALL' | 'India' | 'Brazil' | 'South Africa' | 'China' | 'Russia'>('ALL');
const filterCondition = ref<'ALL' | OperationalCondition>('ALL');
const filterMedicine = ref('ALL');
const filterDistrict = ref('ALL');

// Basemap Tile Providers:
// Primary: Mapbox (Streets/Dark/Satellite) - defaults to global English country/region place labels
// Fallback: Esri World Basemap with English labels (No Carto watermark, no API key required)
const TILES = {
  mapboxDark: (token: string) =>
    `https://api.mapbox.com/styles/v1/mapbox/dark-v11/tiles/256/{z}/{x}/{y}@2x?access_token=${token}`,
  mapboxLight: (token: string) =>
    `https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/256/{z}/{x}/{y}@2x?access_token=${token}`,
  mapboxSatellite: (token: string) =>
    `https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v12/tiles/256/{z}/{x}/{y}@2x?access_token=${token}`,
  // Esri World Basemap raster tiles with crisp English labels (No Carto watermark, no API key required)
  esriLight: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
  esriDarkBase: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
  esriDarkRef: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}',
  satellite: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
  mapboxAttribution:
    '&copy; <a href="https://www.mapbox.com/about/maps/" target="_blank" rel="noopener noreferrer">Mapbox</a> &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> <strong><a href="https://www.mapbox.com/map-feedback/" target="_blank" rel="noopener noreferrer">Improve this map</a></strong>',
  esriAttribution:
    'Tiles &copy; <a href="https://www.esri.com" target="_blank" rel="noopener noreferrer">Esri</a> &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, METI, TomTom',
  satelliteAttribution:
    'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
};

// Filtered Facilities derived from PHC Master Dataset
const filteredPHCs = computed(() => {
  return allPHCs.value.filter(phc => {
    // 1. Strict Country Filter matching PHC master record
    if (filterCountry.value === 'India' && phc.country !== 'India') return false;
    if (filterCountry.value === 'Brazil' && phc.country !== 'Brazil') return false;
    if (filterCountry.value === 'South Africa' && phc.country !== 'South Africa') return false;
    if (filterCountry.value === 'China' && phc.country !== 'China') return false;
    if (filterCountry.value === 'Russia' && phc.country !== 'Russia') return false;

    // 2. Operational Condition (secondary operational filter)
    if (filterCondition.value !== 'ALL' && phc.operational_status !== filterCondition.value) return false;

    // 3. District Filter
    if (filterDistrict.value !== 'ALL' && phc.district !== filterDistrict.value) return false;

    // 4. Medicine Filter
    if (filterMedicine.value !== 'ALL') {
      const hasMed = phc.medicines.some(m => m.medicine_name === filterMedicine.value);
      if (!hasMed) return false;
    }

    // 5. Search Query matching PHC name, phc_id, district, state, locality, city
    if (filterSearch.value.trim()) {
      const q = filterSearch.value.toLowerCase().trim();
      const matchName = phc.name.toLowerCase().includes(q);
      const matchId = phc.phc_id.toLowerCase().includes(q);
      const matchDist = phc.district.toLowerCase().includes(q);
      const matchState = phc.state.toLowerCase().includes(q);
      const matchCity = (phc.city || '').toLowerCase().includes(q);
      const matchLocality = (phc.locality || '').toLowerCase().includes(q);
      if (!matchName && !matchId && !matchDist && !matchState && !matchCity && !matchLocality) return false;
    }

    return true;
  });
});

// Search suggestions for direct selection
const searchSuggestions = computed(() => {
  const q = filterSearch.value.trim().toLowerCase();
  if (!q) return [];
  return allPHCs.value
    .filter(phc => {
      return phc.name.toLowerCase().includes(q) ||
        phc.phc_id.toLowerCase().includes(q) ||
        phc.district.toLowerCase().includes(q) ||
        phc.state.toLowerCase().includes(q) ||
        (phc.city || '').toLowerCase().includes(q);
    })
    .slice(0, 6);
});

// Districts filtered by current country selection
const availableDistricts = computed(() => {
  if (filterCountry.value === 'ALL') return districtsList.value;
  const list = allPHCs.value
    .filter(p => p.country === filterCountry.value)
    .map(p => p.district);
  return Array.from(new Set(list)).sort();
});

// ─────────────────────────────────────────────────────────────────────────────
// Map Initialization & Basemap Tile Setup
// ─────────────────────────────────────────────────────────────────────────────

const getActiveTileConfig = () => {
  const useMapbox = Boolean(mapboxToken && mapboxActive.value);

  // 1. Satellite Basemap
  if (tileProvider.value === 'satellite') {
    if (useMapbox) {
      return {
        url: TILES.mapboxSatellite(mapboxToken),
        referenceUrl: undefined,
        attribution: TILES.mapboxAttribution,
        maxZoom: 19,
        subdomains: 'abc',
        isMapbox: true
      };
    }
    return {
      url: TILES.satellite,
      referenceUrl: undefined,
      attribution: TILES.satelliteAttribution,
      maxZoom: 19,
      subdomains: 'abc',
      isMapbox: false
    };
  }

  // 2. Esri World Basemap (Direct or Graceful Fallback) with English Labels
  if (tileProvider.value === 'esri' || (!useMapbox && tileProvider.value === 'mapbox')) {
    return {
      url: dark.value ? TILES.esriDarkBase : TILES.esriLight,
      referenceUrl: dark.value ? TILES.esriDarkRef : undefined,
      attribution: TILES.esriAttribution,
      maxZoom: 19,
      subdomains: 'abc',
      isMapbox: false
    };
  }

  // 3. Mapbox Streets / Dark Mode Basemap
  return {
    url: dark.value ? TILES.mapboxDark(mapboxToken) : TILES.mapboxLight(mapboxToken),
    referenceUrl: undefined,
    attribution: TILES.mapboxAttribution,
    maxZoom: 19,
    subdomains: 'abc',
    isMapbox: true
  };
};

const applyTileLayer = () => {
  if (!map) return;
  if (currentTileLayer) {
    map.removeLayer(currentTileLayer);
    currentTileLayer = null;
  }
  if (currentReferenceLayer) {
    map.removeLayer(currentReferenceLayer);
    currentReferenceLayer = null;
  }

  const config = getActiveTileConfig();
  mapTilesLoading.value = true;

  currentTileLayer = L.tileLayer(config.url, {
    attribution: config.attribution,
    maxZoom: config.maxZoom,
    subdomains: config.subdomains || 'abc',
    tileSize: 256
  }).addTo(map);

  if (config.referenceUrl) {
    currentReferenceLayer = L.tileLayer(config.referenceUrl, {
      maxZoom: config.maxZoom,
      subdomains: config.subdomains || 'abc',
      tileSize: 256,
      pane: 'tilePane'
    }).addTo(map);
  }

  currentTileLayer.on('load', () => {
    mapTilesLoading.value = false;
  });

  // Graceful fallback: If Mapbox tile request fails (e.g. 401 unauthorized / invalid token)
  currentTileLayer.on('tileerror', (event) => {
    mapTilesLoading.value = false;
    if (config.isMapbox && mapboxActive.value) {
      console.warn('Mapbox tile load failure (unauthorized token or network). Gracefully switching to Esri World Basemap (English) fallback.', event);
      mapboxActive.value = false;
      mapboxError.value = 'Mapbox token invalid or unauthorized. Using Esri World Basemap (English) fallback.';
      applyTileLayer();
    }
  });

  // Safety timeout to clear tile loading state
  setTimeout(() => {
    mapTilesLoading.value = false;
  }, 1800);
};

const cycleTileProvider = () => {
  if (tileProvider.value === 'mapbox') {
    tileProvider.value = 'esri';
  } else if (tileProvider.value === 'esri') {
    tileProvider.value = 'satellite';
  } else {
    tileProvider.value = mapboxToken ? 'mapbox' : 'esri';
    if (mapboxToken) {
      mapboxActive.value = true;
    }
  }
  applyTileLayer();
};

// Re-apply tile layer when dark mode is toggled
watch(dark, () => {
  applyTileLayer();
  updateMarkerSizes();
});

// ─────────────────────────────────────────────────────────────────────────────
// PHC Marker Design & Zoom-Dependent Scaling
// ─────────────────────────────────────────────────────────────────────────────

const getMarkerDimensions = (zoom: number, isSelected: boolean) => {
  let size = 8;
  if (zoom <= 3) {
    size = 8;
  } else if (zoom <= 5) {
    size = 12;
  } else if (zoom <= 7) {
    size = 16;
  } else if (zoom <= 9) {
    size = 20;
  } else {
    size = 24;
  }

  if (isSelected) {
    size = Math.max(size + 6, 20);
  }

  return size;
};

const createPhcMarkerIcon = (phc: EnrichedPHC, zoom: number, isSelected: boolean) => {
  const size = getMarkerDimensions(zoom, isSelected);
  const halfSize = Math.round(size / 2);

  // Facility Color Theme (Medical Teal / Cyan)
  const baseColor = isSelected ? '#0284c7' : '#0d9488';
  const borderStyle = isSelected
    ? 'border: 3px solid #38bdf8; box-shadow: 0 0 16px rgba(56, 189, 248, 0.9), 0 3px 12px rgba(0,0,0,0.5);'
    : 'border: 1.5px solid #ffffff; box-shadow: 0 1.5px 6px rgba(0,0,0,0.35);';

  // Sizing tiers:
  // zoom <= 3 (8px): sleek compact facility node
  // zoom 4-5 (12px): medium facility dot with center white dot
  // zoom >= 6 (16px+): healthcare badge with crisp white medical cross
  let innerHtml = '';
  if (size >= 16) {
    const iconSize = Math.max(8, Math.round(size * 0.52));
    innerHtml = `
      <svg width="${iconSize}" height="${iconSize}" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3.5" stroke-linecap="round">
        <path d="M12 5v14M5 12h14"/>
      </svg>
    `;
  } else if (size >= 12) {
    innerHtml = `<span style="width: 3px; height: 3px; border-radius: 50%; background: white;"></span>`;
  }

  const html = `
    <div class="phc-facility-marker-pin ${isSelected ? 'is-selected' : ''}" style="
      position: relative;
      width: ${size}px;
      height: ${size}px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transform: translate3d(0,0,0);
    ">
      <div style="
        width: ${size}px;
        height: ${size}px;
        border-radius: 50%;
        background: ${baseColor};
        display: flex;
        align-items: center;
        justify-content: center;
        ${borderStyle}
        transition: transform 0.15s ease, background 0.15s ease;
      ">
        ${innerHtml}
      </div>
    </div>
  `;

  return L.divIcon({
    html,
    className: 'phc-facility-div-icon',
    iconSize: [size, size],
    iconAnchor: [halfSize, halfSize],
    popupAnchor: [0, -halfSize - 6]
  });
};

const updateMarkers = () => {
  if (!map || !markersLayer) return;

  markersLayer.clearLayers();
  phcMarkersMap.clear();

  const facilities = filteredPHCs.value;
  const currentZoom = map.getZoom();

  for (const phc of facilities) {
    if (!phc.hasCoordinates) continue;

    const isSelected = selectedPHC.value?.phc_id === phc.phc_id;
    const icon = createPhcMarkerIcon(phc, currentZoom, isSelected);
    const marker = L.marker([phc.latitude, phc.longitude], {
      icon,
      zIndexOffset: isSelected ? 1000 : 0
    });

    // Clean PHC Facility Popup
    const popupContent = `
      <div style="font-family: system-ui, -apple-system, sans-serif; min-width: 220px; padding: 4px;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
          <span style="font-size: 10px; font-weight: 800; color: #0d9488; text-transform: uppercase; letter-spacing: 0.5px;">${phc.country} · ${phc.phc_id}</span>
          <span style="background: #0f766e; color: white; font-size: 9px; font-weight: 700; padding: 1px 6px; border-radius: 4px;">PHC</span>
        </div>
        <h4 style="margin: 0 0 6px 0; font-size: 13px; font-weight: 700; color: #0f172a; line-height: 1.2;">${phc.name}</h4>
        <div style="font-size: 11px; margin-bottom: 8px; background: #f8fafc; padding: 6px; border-radius: 6px; border: 1px solid #e2e8f0; color: #334155;">
          <div><span style="color: #64748b; font-size: 10px;">District:</span> <b>${phc.district}</b> (${phc.state})</div>
          <div><span style="color: #64748b; font-size: 10px;">Coordinates:</span> <b>${phc.latitude.toFixed(4)}°, ${phc.longitude.toFixed(4)}°</b></div>
          <div style="display: flex; gap: 8px; margin-top: 3px;">
            <span>Beds: <b>${phc.capacity.beds}</b></span>
            <span>OPD/day: <b>${phc.capacity.opd_capacity_per_day}</b></span>
          </div>
        </div>
        <button id="btn-inspect-${phc.phc_id}" style="width: 100%; background: #0d9488; color: white; border: none; padding: 6px 0; border-radius: 6px; font-size: 11px; font-weight: 700; cursor: pointer;">
          Inspect Facility Details →
        </button>
      </div>
    `;

    marker.bindPopup(popupContent, {
      className: 'phc-control-room-popup',
      closeButton: false,
      offset: [0, -6]
    });

    marker.on('popupopen', () => {
      const btn = document.getElementById(`btn-inspect-${phc.phc_id}`);
      if (btn) {
        btn.onclick = () => {
          selectPHC(phc);
        };
      }
    });

    marker.on('click', () => {
      selectPHC(phc);
    });

    marker.addTo(markersLayer);
    phcMarkersMap.set(phc.phc_id, marker);
  }
};

// Smooth zoom-dependent marker scaling: updates icons instantly when zoom level changes
const updateMarkerSizes = () => {
  if (!map) return;
  const currentZoom = map.getZoom();

  for (const [phcId, marker] of phcMarkersMap.entries()) {
    const phc = allPHCs.value.find(p => p.phc_id === phcId);
    if (!phc) continue;
    const isSelected = selectedPHC.value?.phc_id === phcId;
    marker.setIcon(createPhcMarkerIcon(phc, currentZoom, isSelected));
    marker.setZIndexOffset(isSelected ? 1000 : 0);
  }
};

// Select PHC by canonical ID
const selectPHC = (phc: EnrichedPHC) => {
  selectedPHC.value = phc;
  showInspectionDrawer.value = true;
  activeDrawerTab.value = 'overview';

  updateMarkerSizes();

  if (map && phc.hasCoordinates) {
    const targetZoom = Math.max(map.getZoom(), 8);
    map.flyTo([phc.latitude, phc.longitude], targetZoom, {
      duration: 1.2
    });

    const marker = phcMarkersMap.get(phc.phc_id);
    if (marker) {
      setTimeout(() => {
        marker.openPopup();
      }, 400);
    }
  }
};

// Country focal switcher and bounds fitting based on actual PHC coordinates
const setCountryFilter = (country: 'ALL' | 'India' | 'Brazil' | 'South Africa' | 'China' | 'Russia') => {
  filterCountry.value = country;
  if (!map) return;

  if (country === 'ALL') {
    fitToAllFacilities();
  } else {
    fitToCountryFacilities(country);
  }
};

const fitToCountryFacilities = (countryName: string) => {
  if (!map) return;
  const phcsInCountry = allPHCs.value.filter(p => p.hasCoordinates && p.country === countryName);
  if (phcsInCountry.length > 0) {
    const latLngs = phcsInCountry.map(p => [p.latitude, p.longitude] as [number, number]);
    const bounds = L.latLngBounds(latLngs);
    map.fitBounds(bounds, { padding: [50, 50], maxZoom: 8 });
  }
};

const fitToAllFacilities = () => {
  if (!map) return;
  const validPhcs = allPHCs.value.filter(p => p.hasCoordinates);
  if (validPhcs.length > 0) {
    const latLngs = validPhcs.map(p => [p.latitude, p.longitude] as [number, number]);
    const bounds = L.latLngBounds(latLngs);
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 4 });
  }
};

const fitToFilteredFacilities = () => {
  if (!map || filteredPHCs.value.length === 0) return;
  const coords = filteredPHCs.value
    .filter(p => p.hasCoordinates)
    .map(p => [p.latitude, p.longitude] as [number, number]);

  if (coords.length > 0) {
    const bounds = L.latLngBounds(coords);
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 10 });
  }
};

const onSearchEnter = () => {
  if (searchSuggestions.value.length > 0) {
    selectPHC(searchSuggestions.value[0]);
  }
};

// ─────────────────────────────────────────────────────────────────────────────
// Map Lifecycle
// ─────────────────────────────────────────────────────────────────────────────

const initMap = () => {
  if (!mapContainer.value) return;
  if (map) {
    map.invalidateSize();
    return;
  }

  try {
    map = L.map(mapContainer.value, {
      center: [10, 15],
      zoom: 3,
      minZoom: 2,
      maxZoom: 18,
      zoomControl: false,
      attributionControl: true
    });

    L.control.zoom({ position: 'topright' }).addTo(map);

    applyTileLayer();

    markersLayer = L.layerGroup().addTo(map);

    updateMarkers();

    // Smoothly scale marker icons when zoom changes
    map.on('zoomend', () => {
      updateMarkerSizes();
    });

    if (mapContainer.value && 'ResizeObserver' in window) {
      if (resizeObserver) resizeObserver.disconnect();
      resizeObserver = new ResizeObserver(() => {
        if (map) map.invalidateSize();
      });
      resizeObserver.observe(mapContainer.value);
    }

    [50, 150, 300, 600].forEach(delay => {
      setTimeout(() => { map?.invalidateSize(); }, delay);
    });
  } catch (err) {
    console.error('Leaflet initialization error:', err);
  }
};

const loadData = async () => {
  loading.value = true;
  error.value = null;
  try {
    const data = await fetchAllMapData();
    allPHCs.value = data.phcs;
    metrics.value = data.metrics;
    medicinesList.value = data.medicinesList;
    districtsList.value = data.districtsList;

    nextTick(() => {
      initMap();
    });
  } catch (err: any) {
    console.error('Failed to load map data:', err);
    error.value = 'Failed to load PHC facility network. Please check backend connection.';
  } finally {
    loading.value = false;
  }
};

const handleResize = () => {
  map?.invalidateSize();
};

onMounted(async () => {
  await loadData();
  nextTick(() => {
    initMap();
    window.addEventListener('resize', handleResize);
  });
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (resizeObserver) {
    resizeObserver.disconnect();
    resizeObserver = null;
  }
  if (currentReferenceLayer && map) {
    map.removeLayer(currentReferenceLayer);
    currentReferenceLayer = null;
  }
  if (currentTileLayer && map) {
    map.removeLayer(currentTileLayer);
    currentTileLayer = null;
  }
  if (map) {
    map.remove();
    map = null;
  }
});

// Watch filters to redraw markers
watch(
  [filteredPHCs],
  () => {
    updateMarkers();
  },
  { deep: true }
);
</script>

<template>
  <div
    class="flex flex-col w-full flex-1 overflow-hidden"
    style="min-height: calc(100vh - 4rem); height: 100%;"
    :class="dark ? 'bg-[#0B1220] text-slate-100' : 'bg-[#F8FAFC] text-slate-800'"
  >
    <!-- Top Operations Control-Room KPI Bar -->
    <header class="border-b px-4 py-3 flex-shrink-0 flex flex-wrap items-center justify-between gap-3 shadow-xs"
      :class="dark ? 'bg-[#111827] border-[#1E293B]' : 'bg-white border-slate-200'">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl flex items-center justify-center text-white shadow-sm"
          style="background: linear-gradient(135deg, #0d9488, #0284c7);">
          <Globe :size="20" />
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h2 class="text-sm font-bold tracking-tight" :class="dark ? 'text-white' : 'text-slate-900'">
              BRICS Primary Health Centre Network Map
            </h2>
            <span class="pulse-dot-wrapper pulse-green">
              <span class="w-2 h-2 rounded-full bg-emerald-500 block"></span>
            </span>
            <span class="text-3xs font-bold uppercase tracking-wider text-emerald-500">Facility Network</span>
          </div>
          <p class="text-2xs" :class="dark ? 'text-slate-400' : 'text-slate-500'">
            Canonical healthcare facility locations for {{ metrics?.total_phcs || allPHCs.length }} PHCs across India ({{ indiaCount }}), Brazil ({{ brazilCount }}), South Africa ({{ saCount }}), China ({{ chinaCount }}), and Russia ({{ russiaCount }})
          </p>
        </div>
      </div>

      <!-- Quick Metrics Counter Badges -->
      <div v-if="metrics" class="flex items-center gap-2 flex-wrap">
        <div class="px-2.5 py-1.5 rounded-lg border text-xs flex items-center gap-1.5"
          :class="dark ? 'bg-[#1E293B] border-[#334155]' : 'bg-slate-50 border-slate-200'">
          <span class="text-slate-400 text-2xs">Total PHCs:</span>
          <b class="text-teal-500 font-mono">{{ metrics.total_phcs }}</b>
        </div>

        <div class="px-2.5 py-1.5 rounded-lg border text-xs flex items-center gap-1.5"
          :class="dark ? 'bg-[#1E293B] border-[#334155]' : 'bg-slate-50 border-slate-200'">
          <span class="text-slate-400 text-2xs">🇮🇳 India:</span>
          <b class="text-sky-400 font-mono">{{ indiaCount }}</b>
        </div>

        <div class="px-2.5 py-1.5 rounded-lg border text-xs flex items-center gap-1.5"
          :class="dark ? 'bg-[#1E293B] border-[#334155]' : 'bg-slate-50 border-slate-200'">
          <span class="text-slate-400 text-2xs">🇧🇷 Brazil:</span>
          <b class="text-green-400 font-mono">{{ brazilCount }}</b>
        </div>

        <div class="px-2.5 py-1.5 rounded-lg border text-xs flex items-center gap-1.5"
          :class="dark ? 'bg-[#1E293B] border-[#334155]' : 'bg-slate-50 border-slate-200'">
          <span class="text-slate-400 text-2xs">🇿🇦 SA:</span>
          <b class="text-amber-400 font-mono">{{ saCount }}</b>
        </div>

        <div class="px-2.5 py-1.5 rounded-lg border text-xs flex items-center gap-1.5"
          :class="dark ? 'bg-[#1E293B] border-[#334155]' : 'bg-slate-50 border-slate-200'">
          <span class="text-slate-400 text-2xs">🇨🇳 China:</span>
          <b class="text-red-400 font-mono">{{ chinaCount }}</b>
        </div>

        <div class="px-2.5 py-1.5 rounded-lg border text-xs flex items-center gap-1.5"
          :class="dark ? 'bg-[#1E293B] border-[#334155]' : 'bg-slate-50 border-slate-200'">
          <span class="text-slate-400 text-2xs">🇷🇺 Russia:</span>
          <b class="text-indigo-400 font-mono">{{ russiaCount }}</b>
        </div>

        <div class="px-2.5 py-1.5 rounded-lg border text-xs flex items-center gap-1.5 hidden 2xl:flex"
          :class="dark ? 'bg-[#1E293B] border-[#334155]' : 'bg-slate-50 border-slate-200'">
          <span class="text-slate-400 text-2xs">Total Beds:</span>
          <b class="text-blue-400 font-mono">{{ metrics.total_beds.toLocaleString() }}</b>
        </div>

        <!-- Reload Button -->
        <button
          @click="loadData"
          :disabled="loading"
          class="p-2 rounded-lg border text-slate-400 hover:text-teal-500 transition-colors"
          :class="dark ? 'border-[#334155] hover:bg-[#1E293B]' : 'border-slate-200 hover:bg-slate-50'"
          title="Refresh Operations Data"
        >
          <RefreshCw :size="14" :class="loading ? 'animate-spin' : ''" />
        </button>
      </div>
    </header>

    <!-- Main Map Workspace Area -->
    <div class="flex-1 relative flex overflow-hidden">
      <!-- Left Filter Floating Panel -->
      <aside
        class="w-80 flex-shrink-0 border-r flex flex-col z-20 transition-all dark-transition"
        :class="dark ? 'bg-[#111827] border-[#1E293B]' : 'bg-white border-slate-200'"
      >
        <!-- Search input & Auto-suggestion -->
        <div class="p-3 border-b" :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
          <div class="relative">
            <Search :size="14" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              v-model="filterSearch"
              @keydown.enter="onSearchEnter"
              type="text"
              placeholder="Search PHC name, ID, district..."
              class="w-full pl-8 pr-3 py-2 text-xs rounded-xl border outline-none transition-all"
              :class="dark ? 'bg-[#1E293B] border-[#334155] text-white focus:border-teal-500' : 'bg-slate-50 border-slate-200 text-slate-800 focus:border-teal-500'"
            />
            <button v-if="filterSearch" @click="filterSearch = ''" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
              <X :size="13" />
            </button>
          </div>

          <!-- Matching search quick-select results -->
          <div v-if="filterSearch.trim() && searchSuggestions.length > 0" class="mt-2 space-y-1">
            <p class="text-3xs uppercase tracking-wider font-bold text-slate-400">Matching Facilities:</p>
            <div class="max-h-48 overflow-y-auto space-y-1 pr-1">
              <button
                v-for="phc in searchSuggestions"
                :key="phc.phc_id"
                @click="selectPHC(phc)"
                class="w-full text-left p-2 rounded-lg border text-2xs transition-colors flex flex-col gap-0.5"
                :class="selectedPHC?.phc_id === phc.phc_id
                  ? 'bg-teal-500/10 border-teal-500/40 text-teal-400'
                  : (dark ? 'bg-[#1E293B]/60 border-[#334155] hover:bg-[#1E293B] text-slate-300' : 'bg-slate-50 border-slate-200 hover:bg-slate-100 text-slate-700')"
              >
                <div class="flex items-center justify-between">
                  <span class="font-bold truncate">{{ phc.name }}</span>
                  <span class="font-mono text-3xs text-teal-500 flex-shrink-0">{{ phc.phc_id }}</span>
                </div>
                <span class="text-3xs text-slate-400">{{ phc.district }}, {{ phc.country }}</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Country Quick Jurisdiction Switcher (All / India / Brazil / SA / China / Russia) -->
        <div class="p-3 border-b space-y-1.5" :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
          <label class="text-3xs font-bold uppercase tracking-wider text-slate-400">Jurisdiction Filter</label>
          <div class="grid grid-cols-3 gap-1.5">
            <button
              @click="setCountryFilter('ALL')"
              class="py-1.5 px-2 rounded-lg text-2xs font-semibold border transition-all text-center"
              :class="filterCountry === 'ALL'
                ? 'bg-teal-600 text-white border-teal-600 shadow-xs'
                : (dark ? 'border-[#334155] text-slate-300 hover:bg-[#1E293B]' : 'border-slate-200 text-slate-700 hover:bg-slate-50')"
            >
              🌐 All ({{ allPHCs.length }})
            </button>
            <button
              @click="setCountryFilter('India')"
              class="py-1.5 px-2 rounded-lg text-2xs font-semibold border transition-all text-center"
              :class="filterCountry === 'India'
                ? 'bg-teal-600 text-white border-teal-600 shadow-xs'
                : (dark ? 'border-[#334155] text-slate-300 hover:bg-[#1E293B]' : 'border-slate-200 text-slate-700 hover:bg-slate-50')"
            >
              🇮🇳 India ({{ indiaCount }})
            </button>
            <button
              @click="setCountryFilter('Brazil')"
              class="py-1.5 px-2 rounded-lg text-2xs font-semibold border transition-all text-center"
              :class="filterCountry === 'Brazil'
                ? 'bg-teal-600 text-white border-teal-600 shadow-xs'
                : (dark ? 'border-[#334155] text-slate-300 hover:bg-[#1E293B]' : 'border-slate-200 text-slate-700 hover:bg-slate-50')"
            >
              🇧🇷 Brazil ({{ brazilCount }})
            </button>
            <button
              @click="setCountryFilter('South Africa')"
              class="py-1.5 px-2 rounded-lg text-2xs font-semibold border transition-all text-center"
              :class="filterCountry === 'South Africa'
                ? 'bg-teal-600 text-white border-teal-600 shadow-xs'
                : (dark ? 'border-[#334155] text-slate-300 hover:bg-[#1E293B]' : 'border-slate-200 text-slate-700 hover:bg-slate-50')"
            >
              🇿🇦 SA ({{ saCount }})
            </button>
            <button
              @click="setCountryFilter('China')"
              class="py-1.5 px-2 rounded-lg text-2xs font-semibold border transition-all text-center"
              :class="filterCountry === 'China'
                ? 'bg-teal-600 text-white border-teal-600 shadow-xs'
                : (dark ? 'border-[#334155] text-slate-300 hover:bg-[#1E293B]' : 'border-slate-200 text-slate-700 hover:bg-slate-50')"
            >
              🇨🇳 China ({{ chinaCount }})
            </button>
            <button
              @click="setCountryFilter('Russia')"
              class="py-1.5 px-2 rounded-lg text-2xs font-semibold border transition-all text-center"
              :class="filterCountry === 'Russia'
                ? 'bg-teal-600 text-white border-teal-600 shadow-xs'
                : (dark ? 'border-[#334155] text-slate-300 hover:bg-[#1E293B]' : 'border-slate-200 text-slate-700 hover:bg-slate-50')"
            >
              🇷🇺 Russia ({{ russiaCount }})
            </button>
          </div>
        </div>

        <!-- Filter Controls scroll area -->
        <div class="flex-1 overflow-y-auto p-3 space-y-4">
          <!-- District Filter -->
          <div class="space-y-1.5">
            <label class="text-3xs font-bold uppercase tracking-wider text-slate-400">District / Region</label>
            <select
              v-model="filterDistrict"
              class="w-full px-2.5 py-1.5 text-xs rounded-xl border outline-none"
              :class="dark ? 'bg-[#1E293B] border-[#334155] text-white' : 'bg-slate-50 border-slate-200 text-slate-800'"
            >
              <option value="ALL">All Districts ({{ availableDistricts.length }})</option>
              <option v-for="dist in availableDistricts" :key="dist" :value="dist">{{ dist }}</option>
            </select>
          </div>

          <!-- Essential Medicine Filter -->
          <div class="space-y-1.5">
            <label class="text-3xs font-bold uppercase tracking-wider text-slate-400">Essential Medicine Filter</label>
            <select
              v-model="filterMedicine"
              class="w-full px-2.5 py-1.5 text-xs rounded-xl border outline-none"
              :class="dark ? 'bg-[#1E293B] border-[#334155] text-white' : 'bg-slate-50 border-slate-200 text-slate-800'"
            >
              <option value="ALL">All Medicines</option>
              <option v-for="med in medicinesList" :key="med" :value="med">{{ med }}</option>
            </select>
          </div>

          <!-- Secondary Condition Filter -->
          <div class="space-y-1.5">
            <label class="text-3xs font-bold uppercase tracking-wider text-slate-400">Operational Condition</label>
            <select
              v-model="filterCondition"
              class="w-full px-2.5 py-1.5 text-xs rounded-xl border outline-none"
              :class="dark ? 'bg-[#1E293B] border-[#334155] text-white' : 'bg-slate-50 border-slate-200 text-slate-800'"
            >
              <option value="ALL">All Facilities ({{ allPHCs.length }})</option>
              <option value="CRITICAL">🚨 Critical Facility</option>
              <option value="OUTBREAK">☣ Disease Outbreak Alert</option>
              <option value="HIGH_RISK">▲ High Risk</option>
              <option value="ATTENTION">■ Attention / Warning</option>
              <option value="NORMAL">✓ Normal Operational</option>
            </select>
          </div>

          <!-- Matching Results Counter & Reset -->
          <div class="p-2.5 rounded-xl border flex items-center justify-between text-2xs"
            :class="dark ? 'bg-[#1E293B]/40 border-[#334155]' : 'bg-slate-50 border-slate-200'">
            <span class="text-slate-400">Showing <b>{{ filteredPHCs.length }}</b> of {{ allPHCs.length }} PHCs</span>
            <button
              @click="fitToFilteredFacilities"
              class="text-teal-600 hover:text-teal-500 font-bold"
            >
              Fit to Screen
            </button>
          </div>
        </div>

        <!-- Mini Legend Footer -->
        <div class="p-3 border-t text-3xs space-y-1.5" :class="dark ? 'border-[#1E293B] bg-[#0B1220]' : 'border-slate-100 bg-slate-50/50'">
          <p class="font-bold uppercase tracking-wider text-slate-400">Map Legend</p>
          <div class="space-y-1 text-slate-300">
            <div class="flex items-center gap-2">
              <span class="w-3 h-3 rounded-full bg-teal-600 border border-white flex-shrink-0"></span>
              <span>PHC Facility Node (Zoom-adaptive size)</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="w-3.5 h-3.5 rounded-full bg-sky-600 border-2 border-sky-400 shadow-sm flex-shrink-0"></span>
              <span>Selected PHC (Highlighted)</span>
            </div>
          </div>
        </div>
      </aside>

      <!-- Center Map Viewport -->
      <main class="flex-1 relative w-full h-full overflow-hidden" style="min-height: 520px;">
        <!-- Leaflet Map Container -->
        <div
          ref="mapContainer"
          class="w-full h-full z-0 outline-none"
          style="width: 100%; height: 100%; min-height: 520px; position: relative;"
        ></div>

        <!-- Floating Map Overlay Controls (Top Left) -->
        <div class="absolute top-4 left-4 z-10 flex flex-wrap gap-2">
          <button
            @click="fitToFilteredFacilities"
            class="px-3 py-1.5 rounded-xl shadow-lg border text-xs font-semibold backdrop-blur-md transition-all flex items-center gap-1.5"
            :class="dark ? 'bg-[#111827]/90 border-[#334155] text-slate-200 hover:bg-[#1E293B]' : 'bg-white/90 border-slate-200 text-slate-700 hover:bg-white'"
          >
            <Layers :size="13" /> Reset View
          </button>
          <button
            @click="cycleTileProvider"
            class="px-3 py-1.5 rounded-xl shadow-lg border text-xs font-semibold backdrop-blur-md transition-all flex items-center gap-1.5"
            :class="dark ? 'bg-[#111827]/90 border-[#334155] text-teal-400 hover:bg-[#1E293B]' : 'bg-white/90 border-slate-200 text-teal-700 hover:bg-white'"
            title="Switch map basemap: Mapbox, Esri (English), Satellite"
          >
            <Globe :size="13" />
            <span>Map: {{
              tileProvider === 'mapbox' && mapboxActive
                ? (dark ? 'Mapbox Dark' : 'Mapbox Streets')
                : tileProvider === 'satellite'
                  ? 'Satellite (Esri)'
                  : (tileProvider === 'mapbox' && !mapboxActive
                    ? 'Esri (English Fallback)'
                    : (dark ? 'Esri Dark Canvas (English)' : 'Esri World Street (English)'))
            }}</span>
          </button>
          <button
            @click="store.toggleDarkMode()"
            class="px-3 py-1.5 rounded-xl shadow-lg border text-xs font-semibold backdrop-blur-md transition-all flex items-center gap-1.5"
            :class="dark ? 'bg-[#111827]/90 border-[#334155] text-amber-400 hover:bg-[#1E293B]' : 'bg-white/90 border-slate-200 text-slate-600 hover:bg-white'"
          >
            {{ dark ? '☀️ Light' : '🌙 Dark' }}
          </button>
        </div>

        <!-- Empty State Alert when zero facilities match filter -->
        <div
          v-if="filteredPHCs.length === 0 && !loading"
          class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-10 p-6 rounded-2xl border shadow-xl text-center max-w-sm"
          :class="dark ? 'bg-[#111827] border-[#1E293B]' : 'bg-white border-slate-200'"
        >
          <AlertTriangle :size="32" class="text-amber-500 mx-auto mb-2" />
          <h4 class="text-sm font-bold" :class="dark ? 'text-white' : 'text-slate-800'">No Facilities Match Current Filters</h4>
          <p class="text-xs text-slate-400 mt-1 mb-3">Try clearing search terms or selecting 'All Jurisdictions'.</p>
          <button
            @click="filterCountry = 'ALL'; filterCondition = 'ALL'; filterSearch = ''; filterMedicine = 'ALL'; filterDistrict = 'ALL';"
            class="px-4 py-2 rounded-xl text-xs font-bold text-white bg-teal-600 hover:bg-teal-500"
          >
            Reset All Filters
          </button>
        </div>

        <!-- Graceful Mapbox Warning/Notification Banner -->
        <Transition
          enter-active-class="transition duration-300 ease-out"
          enter-from-class="opacity-0 translate-y-2"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition duration-200 ease-in"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 translate-y-2"
        >
          <div
            v-if="mapboxError"
            class="absolute bottom-6 left-4 z-20 max-w-md p-3 rounded-xl border shadow-xl backdrop-blur-md flex items-center justify-between gap-3 text-xs transition-all"
            :class="dark ? 'bg-[#1e293b]/95 border-amber-500/30 text-amber-200' : 'bg-amber-50/95 border-amber-200 text-amber-900'"
          >
            <div class="flex items-center gap-2">
              <AlertTriangle :size="16" class="text-amber-500 flex-shrink-0" />
              <div>
                <p class="font-bold">Mapbox Notice</p>
                <p class="text-2xs opacity-90">{{ mapboxError }}</p>
              </div>
            </div>
            <button
              @click="mapboxError = null"
              class="p-1 rounded-lg hover:bg-black/10 dark:hover:bg-white/10 text-slate-400 hover:text-slate-200 flex-shrink-0"
              title="Dismiss"
            >
              <X :size="14" />
            </button>
          </div>
        </Transition>

        <!-- Loading Spinner Overlay -->
        <div
          v-if="loading"
          class="absolute inset-0 z-30 flex items-center justify-center backdrop-blur-xs"
          :class="dark ? 'bg-[#0B1220]/70 text-teal-400' : 'bg-white/70 text-teal-600'"
        >
          <div class="text-center space-y-2">
            <RefreshCw :size="32" class="animate-spin mx-auto text-teal-500" />
            <p class="text-xs font-bold uppercase tracking-wider">Loading PHC Facilities...</p>
          </div>
        </div>
      </main>

      <!-- Right Slide-Over Inspection Drawer -->
      <Transition
        enter-active-class="transition duration-300 ease-out transform"
        enter-from-class="translate-x-full"
        enter-to-class="translate-x-0"
        leave-active-class="transition duration-200 ease-in transform"
        leave-from-class="translate-x-0"
        leave-to-class="translate-x-full"
      >
        <section
          v-if="showInspectionDrawer && selectedPHC"
          class="w-96 flex-shrink-0 border-l z-20 flex flex-col shadow-2xl h-full dark-transition"
          :class="dark ? 'bg-[#111827] border-[#1E293B]' : 'bg-white border-slate-200'"
        >
          <!-- Drawer Header -->
          <div class="p-4 border-b flex items-start justify-between" :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
            <div class="min-w-0 flex-1 pr-2">
              <div class="flex items-center gap-1.5 text-2xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                <span>{{ selectedPHC.country }}</span>
                <span>·</span>
                <span class="font-mono text-teal-500">{{ selectedPHC.phc_id }}</span>
              </div>
              <h3 class="text-sm font-bold truncate leading-tight" :class="dark ? 'text-white' : 'text-slate-800'">
                {{ selectedPHC.name }}
              </h3>
              <p class="text-2xs text-slate-400 truncate mt-0.5">
                {{ selectedPHC.facility_type }} · {{ selectedPHC.district }}
              </p>
            </div>
            <button @click="showInspectionDrawer = false" class="p-1 rounded-lg text-slate-400 hover:text-slate-600">
              <X :size="16" />
            </button>
          </div>

          <!-- Facility Status Banner inside Drawer -->
          <div
            class="px-4 py-2.5 flex items-center justify-between text-xs font-bold border-b"
            :class="selectedPHC.operational_status === 'CRITICAL' ? 'bg-red-500/10 text-red-500 border-red-500/20' :
                    selectedPHC.operational_status === 'OUTBREAK' ? 'bg-purple-500/10 text-purple-400 border-purple-500/20' :
                    selectedPHC.operational_status === 'HIGH_RISK' ? 'bg-orange-500/10 text-orange-500 border-orange-500/20' :
                    selectedPHC.operational_status === 'ATTENTION' ? 'bg-amber-500/10 text-amber-500 border-amber-500/20' :
                    'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'"
          >
            <span class="flex items-center gap-1.5">
              <Activity :size="14" />
              STATUS: {{ selectedPHC.operational_status.replace('_', ' ') }}
            </span>
            <span class="text-2xs font-mono">Risk Score: {{ selectedPHC.max_risk_score }}</span>
          </div>

          <!-- Drawer Navigation Tabs -->
          <div class="flex border-b text-2xs font-bold" :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
            <button
              @click="activeDrawerTab = 'overview'"
              class="flex-1 py-2.5 text-center border-b-2 transition-colors"
              :class="activeDrawerTab === 'overview' ? 'border-teal-500 text-teal-600 dark:text-teal-400' : 'border-transparent text-slate-400'"
            >
              Overview
            </button>
            <button
              @click="activeDrawerTab = 'medicines'"
              class="flex-1 py-2.5 text-center border-b-2 transition-colors relative"
              :class="activeDrawerTab === 'medicines' ? 'border-teal-500 text-teal-600 dark:text-teal-400' : 'border-transparent text-slate-400'"
            >
              Medicines ({{ selectedPHC.medicines.length }})
            </button>
            <button
              @click="activeDrawerTab = 'alerts'"
              class="flex-1 py-2.5 text-center border-b-2 transition-colors relative"
              :class="activeDrawerTab === 'alerts' ? 'border-teal-500 text-teal-600 dark:text-teal-400' : 'border-transparent text-slate-400'"
            >
              Alerts ({{ selectedPHC.alerts.length }})
            </button>
            <button
              @click="activeDrawerTab = 'capacity'"
              class="flex-1 py-2.5 text-center border-b-2 transition-colors"
              :class="activeDrawerTab === 'capacity' ? 'border-teal-500 text-teal-600 dark:text-teal-400' : 'border-transparent text-slate-400'"
            >
              Capacity
            </button>
          </div>

          <!-- Drawer Tab Contents -->
          <div class="flex-1 overflow-y-auto p-4 space-y-4">
            <!-- TAB: OVERVIEW -->
            <div v-if="activeDrawerTab === 'overview'" class="space-y-4">
              <!-- Geographical Coordinates directly from PHC Master Record -->
              <div class="p-3 rounded-xl border space-y-2 text-xs" :class="dark ? 'bg-[#1E293B]/30 border-[#334155]' : 'bg-slate-50 border-slate-200'">
                <div class="flex items-center justify-between">
                  <span class="text-slate-400 text-2xs flex items-center gap-1"><MapPin :size="12" /> Coordinates</span>
                  <span class="font-mono text-2xs font-bold" :class="dark ? 'text-teal-400' : 'text-teal-700'">
                    {{ selectedPHC.latitude.toFixed(4) }}°, {{ selectedPHC.longitude.toFixed(4) }}°
                  </span>
                </div>
                <div class="flex items-center justify-between border-t pt-1.5" :class="dark ? 'border-[#334155]' : 'border-slate-200'">
                  <span class="text-slate-400 text-2xs">Region / State</span>
                  <span class="text-2xs font-semibold">{{ selectedPHC.state || 'N/A' }}</span>
                </div>
                <div class="flex items-center justify-between border-t pt-1.5" :class="dark ? 'border-[#334155]' : 'border-slate-200'">
                  <span class="text-slate-400 text-2xs">Locality / City</span>
                  <span class="text-2xs font-semibold">{{ selectedPHC.locality || selectedPHC.city || 'N/A' }}</span>
                </div>
              </div>

              <!-- Key Operations Cards -->
              <div class="grid grid-cols-2 gap-2">
                <div class="p-2.5 rounded-xl border text-left" :class="dark ? 'bg-[#1E293B]/40 border-[#334155]' : 'bg-slate-50 border-slate-200'">
                  <p class="text-3xs font-bold text-slate-400 uppercase">Total Beds</p>
                  <p class="text-base font-extrabold mt-0.5 text-teal-500">
                    {{ selectedPHC.capacity.beds }} <span class="text-2xs font-normal">beds</span>
                  </p>
                </div>

                <div class="p-2.5 rounded-xl border text-left" :class="dark ? 'bg-[#1E293B]/40 border-[#334155]' : 'bg-slate-50 border-slate-200'">
                  <p class="text-3xs font-bold text-slate-400 uppercase">Daily OPD Capacity</p>
                  <p class="text-base font-extrabold mt-0.5 text-blue-500">
                    {{ selectedPHC.capacity.opd_capacity_per_day.toLocaleString() }} <span class="text-2xs font-normal">pts/day</span>
                  </p>
                </div>

                <div class="p-2.5 rounded-xl border text-left" :class="dark ? 'bg-[#1E293B]/40 border-[#334155]' : 'bg-slate-50 border-slate-200'">
                  <p class="text-3xs font-bold text-slate-400 uppercase">Emergency Beds</p>
                  <p class="text-base font-extrabold mt-0.5 text-red-400">
                    {{ selectedPHC.capacity.emergency_beds }} <span class="text-2xs font-normal">beds</span>
                  </p>
                </div>

                <div class="p-2.5 rounded-xl border text-left" :class="dark ? 'bg-[#1E293B]/40 border-[#334155]' : 'bg-slate-50 border-slate-200'">
                  <p class="text-3xs font-bold text-slate-400 uppercase">Catchment Pop.</p>
                  <p class="text-base font-extrabold mt-0.5 text-slate-300">
                    {{ selectedPHC.catchment_population.toLocaleString() }}
                  </p>
                </div>
              </div>

              <!-- Secondary Telemetry Overview -->
              <div class="p-3 rounded-xl border space-y-2 text-xs" :class="dark ? 'bg-[#1E293B]/30 border-[#334155]' : 'bg-slate-50 border-slate-200'">
                <p class="text-3xs font-bold text-slate-400 uppercase">Operational Inventory & Demand</p>
                <div class="flex items-center justify-between text-2xs">
                  <span class="text-slate-400">Total Stock Available:</span>
                  <span class="font-bold text-emerald-400">{{ selectedPHC.total_current_stock.toLocaleString() }} units</span>
                </div>
                <div class="flex items-center justify-between text-2xs">
                  <span class="text-slate-400">7-Day Demand Forecast:</span>
                  <span class="font-bold text-blue-400">{{ selectedPHC.total_forecast_demand.toLocaleString() }} units</span>
                </div>
                <div class="flex items-center justify-between text-2xs">
                  <span class="text-slate-400">Estimated Stockout Horizon:</span>
                  <span class="font-bold" :class="selectedPHC.min_stockout_days <= 3 ? 'text-red-400' : 'text-slate-200'">
                    {{ selectedPHC.min_stockout_days }} days
                  </span>
                </div>
              </div>
            </div>

            <!-- TAB: MEDICINES -->
            <div v-if="activeDrawerTab === 'medicines'" class="space-y-2">
              <div v-if="selectedPHC.medicines.length === 0" class="text-center py-8 text-xs text-slate-400">
                No active medicine telemetry reported for this facility.
              </div>
              <div
                v-for="med in selectedPHC.medicines"
                :key="med.medicine_id"
                class="p-2.5 rounded-xl border text-xs space-y-1.5 transition-colors"
                :class="dark ? 'bg-[#1E293B]/40 border-[#334155]' : 'bg-slate-50 border-slate-200'"
              >
                <div class="flex items-center justify-between">
                  <span class="font-bold truncate pr-2" :class="dark ? 'text-white' : 'text-slate-800'">
                    {{ med.medicine_name }}
                  </span>
                  <span
                    class="px-1.5 py-0.5 rounded text-3xs font-bold uppercase"
                    :class="med.risk_level === 'CRITICAL' ? 'bg-red-500 text-white' :
                            med.risk_level === 'HIGH' ? 'bg-orange-500 text-white' :
                            med.risk_level === 'MEDIUM' ? 'bg-amber-500 text-white' : 'bg-emerald-500/20 text-emerald-400'"
                  >
                    {{ med.risk_level }}
                  </span>
                </div>

                <div class="grid grid-cols-3 gap-2 text-2xs text-slate-400 pt-1">
                  <div>Stock: <b class="text-slate-200 font-mono">{{ med.current_stock }}</b></div>
                  <div>7d Demand: <b class="text-blue-400 font-mono">{{ med.forecast_7d }}</b></div>
                  <div>Days Left: <b :class="med.stockout_days <= 3 ? 'text-red-400 font-bold' : 'text-slate-200'" class="font-mono">{{ med.stockout_days }}d</b></div>
                </div>
              </div>
            </div>

            <!-- TAB: ALERTS -->
            <div v-if="activeDrawerTab === 'alerts'" class="space-y-3">
              <div v-if="selectedPHC.alerts.length === 0" class="text-center py-8 text-xs text-slate-400">
                No active disease alerts recorded for this facility.
              </div>
              <div
                v-for="alt in selectedPHC.alerts"
                :key="alt.alert_id"
                class="p-3 rounded-xl border space-y-2 text-xs"
                :class="alt.severity === 'EMERGENCY' ? 'bg-red-500/10 border-red-500/30' : 'bg-purple-500/10 border-purple-500/30'"
              >
                <div class="flex items-center justify-between">
                  <span class="font-bold flex items-center gap-1.5" :class="alt.severity === 'EMERGENCY' ? 'text-red-400' : 'text-purple-400'">
                    <Flame :size="14" /> {{ alt.pattern_type }}
                  </span>
                  <span class="text-3xs font-extrabold px-1.5 py-0.5 rounded uppercase"
                    :class="alt.severity === 'EMERGENCY' ? 'bg-red-600 text-white' : 'bg-purple-600 text-white'">
                    {{ alt.severity }}
                  </span>
                </div>
                <p class="text-2xs text-slate-300">Driver Resource: <b>{{ alt.primary_driver }}</b></p>
                <div class="text-2xs text-slate-400 space-y-1">
                  <p class="font-semibold text-slate-300">Action Protocols:</p>
                  <ul class="list-disc pl-4 space-y-0.5">
                    <li v-for="act in alt.recommended_actions" :key="act">{{ act }}</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- TAB: CAPACITY -->
            <div v-if="activeDrawerTab === 'capacity'" class="space-y-3 text-xs">
              <div class="p-3 rounded-xl border space-y-2.5" :class="dark ? 'bg-[#1E293B]/40 border-[#334155]' : 'bg-slate-50 border-slate-200'">
                <p class="text-2xs font-bold uppercase tracking-wider text-slate-400">Facility Bed Capacities</p>
                <div class="grid grid-cols-3 gap-2 text-center">
                  <div class="p-2 rounded-lg bg-slate-900/30">
                    <p class="text-3xs text-slate-400">Total Beds</p>
                    <p class="text-sm font-bold text-teal-400">{{ selectedPHC.capacity.beds }}</p>
                  </div>
                  <div class="p-2 rounded-lg bg-slate-900/30">
                    <p class="text-3xs text-slate-400">Emergency</p>
                    <p class="text-sm font-bold text-red-400">{{ selectedPHC.capacity.emergency_beds }}</p>
                  </div>
                  <div class="p-2 rounded-lg bg-slate-900/30">
                    <p class="text-3xs text-slate-400">Daily OPD</p>
                    <p class="text-sm font-bold text-blue-400">{{ selectedPHC.capacity.opd_capacity_per_day }}</p>
                  </div>
                </div>
              </div>

              <div class="p-3 rounded-xl border space-y-2.5" :class="dark ? 'bg-[#1E293B]/40 border-[#334155]' : 'bg-slate-50 border-slate-200'">
                <p class="text-2xs font-bold uppercase tracking-wider text-slate-400">Medical Staffing Baseline</p>
                <div class="grid grid-cols-2 gap-2 text-2xs">
                  <div>Doctors: <b>{{ selectedPHC.staffing.doctors }}</b></div>
                  <div>Nurses: <b>{{ selectedPHC.staffing.nurses }}</b></div>
                  <div>Pharmacists: <b>{{ selectedPHC.staffing.pharmacists }}</b></div>
                  <div>Lab Technicians: <b>{{ selectedPHC.staffing.lab_technicians }}</b></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Drawer Action Footer -->
          <div class="p-4 border-t space-y-2" :class="dark ? 'border-[#1E293B]' : 'border-slate-100'">
            <button
              @click="router.push('/phc-portal')"
              class="w-full py-2.5 rounded-xl text-xs font-bold text-white shadow-sm flex items-center justify-center gap-1.5 transition active:scale-95"
              style="background: linear-gradient(135deg, #0d9488, #0f766e);"
            >
              <ExternalLink :size="14" />
              Open in PHC Redistribution Portal
            </button>
            <button
              @click="showInspectionDrawer = false"
              class="w-full py-2 rounded-xl text-xs font-semibold border"
              :class="dark ? 'border-[#334155] text-slate-400 hover:text-white' : 'border-slate-200 text-slate-600 hover:text-slate-900'"
            >
              Dismiss
            </button>
          </div>
        </section>
      </Transition>
    </div>
  </div>
</template>

<style>
/* Leaflet map container full dimensions */
.leaflet-container {
  width: 100% !important;
  height: 100% !important;
  min-height: 520px !important;
  background-color: #0b1220 !important;
  z-index: 1;
}

/* PHC facility markers */
.phc-facility-div-icon {
  background: transparent !important;
  border: none !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.phc-facility-marker-pin:hover > div {
  transform: scale(1.22);
}

.phc-facility-marker-pin.is-selected > div {
  transform: scale(1.15);
}

/* Dark mode and control room popups */
.phc-control-room-popup .leaflet-popup-content-wrapper {
  background: rgba(17, 24, 39, 0.95);
  color: #f8fafc;
  border-radius: 12px;
  border: 1px solid #334155;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(8px);
}

.phc-control-room-popup .leaflet-popup-tip {
  background: rgba(17, 24, 39, 0.95);
  border: 1px solid #334155;
}

/* Crisp Dark & Light Attribution Control */
.leaflet-control-attribution {
  background: rgba(15, 23, 42, 0.8) !important;
  color: #94a3b8 !important;
  font-size: 10px !important;
  border-radius: 6px !important;
  padding: 2px 6px !important;
  margin: 0 4px 4px 0 !important;
  backdrop-filter: blur(4px);
}
.leaflet-control-attribution a {
  color: #38bdf8 !important;
  text-decoration: none !important;
}
.leaflet-control-attribution a:hover {
  text-decoration: underline !important;
}
</style>
