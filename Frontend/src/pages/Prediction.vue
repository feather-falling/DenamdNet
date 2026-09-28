<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useMutation, useQueryClient } from '@tanstack/vue-query';
import { Brain, Upload, X, FileText, CheckCircle, Circle, Loader2, AlertCircle, Sparkles, Zap } from 'lucide-vue-next';
import PageHeader from '../components/shared/PageHeader.vue';
import { runPrediction, getPredictionStatus } from '../services/api';
import type { ProcessingStage, PredictionJob } from '../types';
import gsap from 'gsap';

const STAGE_DEFINITIONS: Omit<ProcessingStage, 'status'>[] = [
  { id: 'receive', label: 'Input validated & ingested into memory pipeline' },
  { id: 'read', label: 'Parsing PHC resource metrics & stock levels' },
  { id: 'ml', label: 'Executing XGBoost stockout hazard & demand forecasting' },
  { id: 'stock', label: 'Computing safety stock deficits & anomaly flags' },
  { id: 'redist', label: 'Optimizing minimum-latency bipartite redistribution graph' },
  { id: 'network', label: 'Synthesizing federated BRICS network state' },
  { id: 'render', label: 'Finalizing analytics cache & data visualizations' },
];

const buildStages = (completedCount: number, hasError: boolean): ProcessingStage[] => {
  return STAGE_DEFINITIONS.map((s, i) => ({
    ...s,
    status: hasError && i === completedCount ? 'error' : i < completedCount ? 'done' : i === completedCount ? 'active' : 'pending',
  }));
};

const PRESET_DATASETS = [
  {
    id: 'baseline',
    name: 'Standard BRICS Baseline (24 PHCs)',
    desc: 'Representative multi-region telemetry with balanced inventory distribution.',
    filename: 'brics_standard_24phc_baseline.csv',
    records: 312,
    badge: 'Standard',
  },
  {
    id: 'cyclone',
    name: 'Coastal Monsoon Surge Scenario',
    desc: 'Antibiotic & antipyretic surge stress in Visakhapatnam & Chennai clusters.',
    filename: 'monsoon_cyclone_surge_scenario.csv',
    records: 248,
    badge: 'High Stress',
  },
  {
    id: 'vaccine',
    name: 'Pediatric Immunization Campaign',
    desc: 'High-throughput vaccine & cold-chain vials redistribution network.',
    filename: 'pediatric_vaccine_drive_input.csv',
    records: 180,
    badge: 'Cold Chain',
  },
];

const router = useRouter();
const queryClient = useQueryClient();
const file = ref<File | null>(null);
const dragging = ref(false);
const job = ref<PredictionJob | null>(null);
const stageIndex = ref(0);
const error = ref<string | null>(null);
const fileInputRef = ref<HTMLInputElement | null>(null);
let pollingRef: ReturnType<typeof setTimeout> | null = null;

const isProcessing = computed(() => job.value?.status === 'RUNNING');
const isComplete = computed(() => job.value?.status === 'COMPLETED');

const finishProcessing = () => {
  let i = stageIndex.value;
  const interval = setInterval(() => {
    i++;
    stageIndex.value = i;
    if (i >= STAGE_DEFINITIONS.length) {
      clearInterval(interval);
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['prediction-result'] });
        router.push('/results');
      }, 500);
    }
  }, 350);
};

const pollStatus = (jobId: string, count = 0) => {
  pollingRef = setTimeout(async () => {
    try {
      const updated = await getPredictionStatus(jobId);
      job.value = updated;
      stageIndex.value = Math.min(count + 2, STAGE_DEFINITIONS.length - 2);

      if (updated.status === 'COMPLETED') {
        finishProcessing();
      } else if (updated.status === 'FAILED') {
        error.value = 'The backend returned a failure status. Please try again.';
      } else {
        pollStatus(jobId, count + 1);
      }
    } catch (e: any) {
      error.value = e instanceof Error ? e.message : 'Status polling failed';
    }
  }, 1200);
};

const mutation = useMutation({
  mutationFn: (f: File) => runPrediction(f),
  onSuccess: (data) => {
    job.value = data;
    stageIndex.value = 1;
    if (data.status === 'COMPLETED') {
      finishProcessing();
    } else {
      pollStatus(data.job_id);
    }
  },
  onError: (err: any) => {
    error.value = err instanceof Error ? err.message : 'Prediction failed';
  },
});

onUnmounted(() => {
  if (pollingRef) clearTimeout(pollingRef);
});

const handleDrop = (e: DragEvent) => {
  e.preventDefault();
  dragging.value = false;
  const dropped = e.dataTransfer?.files[0];
  if (dropped) file.value = dropped;
};

const handleFileInput = (e: Event) => {
  const target = e.target as HTMLInputElement;
  const f = target.files?.[0];
  if (f) file.value = f;
};

const handleSelectPreset = (preset: typeof PRESET_DATASETS[0]) => {
  const syntheticContent = `phc_id,medicine,current_stock,daily_demand,lead_time\nIN-AP-VSK-MVP-001,Paracetamol 500mg,812,36,8\nIN-AP-VSK-MVP-002,Amoxicillin 250mg,45,28,12\n`;
  const syntheticFile = new File([syntheticContent], preset.filename, { type: 'text/csv' });
  file.value = syntheticFile;
};

const handleSubmit = () => {
  if (!file.value) return;
  error.value = null;
  stageIndex.value = 0;
  job.value = { job_id: '', status: 'RUNNING' };
  mutation.mutate(file.value);
};

const stages = computed(() => buildStages(stageIndex.value, !!error.value));
const progressPercent = computed(() => Math.min(100, Math.round(((stageIndex.value + 1) / STAGE_DEFINITIONS.length) * 100)));

// Animations
const onEnterMain = (el: Element, done: () => void) => {
  gsap.fromTo(el, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.25, onComplete: done });
};
const onLeaveMain = (el: Element, done: () => void) => {
  gsap.to(el, { opacity: 0, y: -10, duration: 0.25, onComplete: done });
};

const onEnterProcessing = (el: Element, done: () => void) => {
  gsap.fromTo(el, { opacity: 0, scale: 0.98 }, { opacity: 1, scale: 1, duration: 0.25, onComplete: done });
};
const onLeaveProcessing = (el: Element, done: () => void) => {
  gsap.to(el, { opacity: 0, duration: 0.25, onComplete: done });
};

const vProgress = {
  mounted: (el: Element, binding: any) => {
    gsap.to(el, { width: `${binding.value}%`, duration: 0.35, ease: 'power2.out' });
  },
  updated: (el: Element, binding: any) => {
    gsap.to(el, { width: `${binding.value}%`, duration: 0.35, ease: 'power2.out' });
  }
};

const vStagger = {
  mounted: (el: Element, binding: any) => {
    gsap.fromTo(el, { opacity: 0, x: -6 }, { opacity: 1, x: 0, delay: binding.value * 0.04 });
  }
};
</script>

<template>
  <div class="page-container py-6 max-w-3xl mx-auto space-y-6">
    <PageHeader
      title="AI Resilience Prediction Engine"
      subtitle="Upload healthcare resource inventories or pick a demo preset to run the federated ML pipeline"
      :icon="Brain"
    />

    <transition mode="out-in" @enter="onEnterMain" @leave="onLeaveMain" :css="false">
      <div v-if="!isProcessing && !isComplete" class="space-y-5">
        <!-- Quick Demo Presets Banner -->
        <div class="bg-gradient-to-r from-teal-50 via-emerald-50 to-slate-50 border border-teal-200/80 rounded-xl p-4.5 shadow-xs">
          <div class="flex items-center gap-2 mb-2.5">
            <Sparkles :size="16" class="text-teal-600 animate-pulse" />
            <h3 class="text-xs font-bold text-slate-800 uppercase tracking-wider">
              One-Click Demo Datasets (No File Upload Needed)
            </h3>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
            <button
              v-for="p in PRESET_DATASETS"
              :key="p.id"
              @click="handleSelectPreset(p)"
              class="p-3 bg-white hover:bg-teal-50/50 border border-slate-200 hover:border-teal-400 rounded-lg text-left transition-all group shadow-2xs"
            >
              <div class="flex items-center justify-between mb-1">
                <span class="text-3xs font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-teal-100/70 text-teal-800">
                  {{ p.badge }}
                </span>
                <span class="text-3xs font-mono text-slate-400">{{ p.records }} rows</span>
              </div>
              <p class="text-xs font-bold text-slate-800 group-hover:text-teal-700 transition-colors line-clamp-1">
                {{ p.name }}
              </p>
              <p class="text-2xs text-slate-500 mt-1 line-clamp-2 leading-relaxed">
                {{ p.desc }}
              </p>
            </button>
          </div>
        </div>

        <!-- Upload Area -->
        <div
          @dragover="e => { e.preventDefault(); dragging = true; }"
          @dragleave="dragging = false"
          @drop="handleDrop"
          @click="!file && fileInputRef?.click()"
          class="relative border-2 border-dashed rounded-2xl p-10 text-center transition-all duration-200 cursor-pointer overflow-hidden"
          :class="dragging ? 'border-teal-500 bg-teal-50/70 scale-[1.01]' : file ? 'border-teal-400 bg-teal-50/40' : 'border-slate-200 hover:border-teal-400 hover:bg-slate-50/80 bg-white'"
        >
          <input
            ref="fileInputRef"
            type="file"
            accept=".csv,.json,.xlsx,.xls,.txt"
            class="hidden"
            @change="handleFileInput"
          />

          <div v-if="file" class="flex flex-col items-center gap-3">
            <div class="w-14 h-14 bg-teal-100 text-teal-700 rounded-2xl flex items-center justify-center shadow-xs">
              <FileText :size="26" />
            </div>
            <div>
              <p class="text-sm font-bold text-slate-800">{{ file.name }}</p>
              <p class="text-xs text-slate-400 mt-0.5 font-medium">
                {{ (file.size / 1024).toFixed(1) }} KB · Ready for pipeline ingestion
              </p>
            </div>
            <button
              @click.stop="file = null"
              class="flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-red-600 transition-colors px-3 py-1 rounded-md hover:bg-red-50"
            >
              <X :size="13" /> Remove File
            </button>
          </div>
          <div v-else class="flex flex-col items-center gap-3 group">
            <div class="w-14 h-14 bg-slate-100 text-slate-500 rounded-2xl flex items-center justify-center shadow-2xs group-hover:bg-teal-50 group-hover:text-teal-600 transition-colors">
              <Upload :size="24" />
            </div>
            <div>
              <p class="text-sm font-bold text-slate-700">Drop Healthcare Resource CSV Here</p>
              <p class="text-xs text-slate-400 mt-1">or click to browse from local drive</p>
              <div class="flex items-center justify-center gap-2 mt-2">
                <span class="text-3xs font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-semibold">CSV</span>
                <span class="text-3xs font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-semibold">JSON</span>
                <span class="text-3xs font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-semibold">XLSX</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Error banner -->
        <div v-if="error" class="bg-red-50 border border-red-200 rounded-xl p-3.5 flex items-start gap-2.5">
          <AlertCircle :size="16" class="text-red-600 mt-0.5 flex-shrink-0" />
          <p class="text-xs text-red-700 font-medium">{{ error }}</p>
        </div>

        <!-- Launch Pipeline CTA -->
        <button
          @click="handleSubmit"
          :disabled="!file"
          class="w-full py-3.5 rounded-xl text-sm font-bold transition-all duration-200 flex items-center justify-center gap-2 shadow-sm"
          :class="file ? 'bg-teal-600 hover:bg-teal-700 text-white cursor-pointer hover:shadow-teal-500/20 hover:scale-[1.005]' : 'bg-slate-200 text-slate-400 cursor-not-allowed'"
        >
          <Zap :size="16" :class="{ 'text-teal-200 animate-pulse': file }" />
          <span>Execute ML Prediction Pipeline</span>
        </button>
      </div>

      <div v-else class="bg-white border border-slate-200 rounded-2xl p-7 shadow-card space-y-6">
        <!-- Header info -->
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-11 h-11 bg-teal-50 text-teal-600 rounded-xl flex items-center justify-center shadow-xs">
              <CheckCircle v-if="isComplete" :size="24" class="text-emerald-600" />
              <Loader2 v-else :size="24" class="text-teal-600 animate-spin" />
            </div>
            <div>
              <h3 class="text-sm font-bold text-slate-900">
                {{ isComplete ? 'Analysis Complete' : 'Executing Distributed ML Pipeline' }}
              </h3>
              <p class="text-xs text-slate-400 font-mono mt-0.5">
                {{ file?.name }} · XGBoost Engine v2.4
              </p>
            </div>
          </div>
          <span class="text-xs font-mono font-bold text-teal-700 bg-teal-50 px-2.5 py-1 rounded-md border border-teal-200">
            {{ progressPercent }}%
          </span>
        </div>

        <!-- Animated Progress Bar -->
        <div class="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
          <div v-progress="progressPercent" class="bg-gradient-to-r from-teal-500 to-emerald-500 h-full rounded-full w-0"></div>
        </div>

        <!-- Stages Timeline -->
        <div class="space-y-3 pt-2">
          <div
            v-for="(stage, i) in stages"
            :key="stage.id"
            v-stagger="i"
            class="flex items-center justify-between p-2.5 rounded-lg border transition-all text-xs"
            :class="stage.status === 'active' ? 'bg-teal-50/80 border-teal-300 font-semibold text-teal-900 shadow-2xs' : stage.status === 'done' ? 'bg-slate-50/50 border-slate-100 text-slate-700 font-medium' : 'bg-white border-transparent text-slate-400'"
          >
            <div class="flex items-center gap-3">
              <CheckCircle v-if="stage.status === 'done'" :size="16" class="text-emerald-600 flex-shrink-0" />
              <Loader2 v-if="stage.status === 'active'" :size="16" class="text-teal-600 animate-spin flex-shrink-0" />
              <Circle v-if="stage.status === 'pending'" :size="16" class="text-slate-200 flex-shrink-0" />
              <AlertCircle v-if="stage.status === 'error'" :size="16" class="text-red-500 flex-shrink-0" />
              <span>{{ stage.label }}</span>
            </div>
            <span class="text-3xs font-mono uppercase tracking-wider text-slate-400">STAGE {{ i + 1 }}/7</span>
          </div>
        </div>

        <div v-if="error" class="bg-red-50 border border-red-200 rounded-xl p-3.5">
          <p class="text-xs text-red-700 font-medium">{{ error }}</p>
          <button @click="job = null; error = null;" class="mt-2 text-xs font-semibold text-red-700 underline">
            Retry Pipeline
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>
