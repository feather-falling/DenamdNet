<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import {
  Upload, Sparkles, CheckCircle2, Loader2, AlertCircle,
  ArrowRight, FileJson, RefreshCw, X, Play
} from 'lucide-vue-next';
import { uploadTodayJson, runDailyPipeline, getPipelineStatus } from '../../services/api';
import type { PipelineJobStatus } from '../../types';

const props = defineProps<{
  show: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'completed', jobId: string): void;
}>();

const router = useRouter();

const PIPELINE_STAGES = [
  { minProgress: 0,  label: 'Uploading input telemetry' },
  { minProgress: 17, label: 'Validating operational data' },
  { minProgress: 34, label: 'Running demand forecasting' },
  { minProgress: 52, label: 'Detecting healthcare anomalies' },
  { minProgress: 71, label: 'Evaluating stock requirements & finding redistribution sources' },
  { minProgress: 86, label: 'Generating next-day inventory' },
  { minProgress: 100, label: 'Preparing results dashboard' },
];

const selectedFile = ref<File | null>(null);
const country = ref('all');
const isRunning = ref(false);
const errorMsg = ref<string | null>(null);
const currentJob = ref<PipelineJobStatus | null>(null);
const fileInputRef = ref<HTMLInputElement | null>(null);
let pollTimer: ReturnType<typeof setTimeout> | null = null;

const progressPercent = computed(() => {
  if (!currentJob.value) return 0;
  return currentJob.value.progress;
});

const isComplete = computed(() => {
  return currentJob.value?.status === 'completed' || currentJob.value?.progress === 100;
});

const currentStageText = computed(() => {
  if (errorMsg.value) return errorMsg.value;
  if (!currentJob.value) return 'Ready to launch';
  return currentJob.value.stage || 'Processing...';
});

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    const f = target.files[0];
    if (!f.name.toLowerCase().endsWith('.json')) {
      errorMsg.value = 'Invalid file type. Please upload a .json file (input_today.json).';
      selectedFile.value = null;
      return;
    }
    selectedFile.value = f;
    errorMsg.value = null;
  }
};

const handleDrop = (event: DragEvent) => {
  event.preventDefault();
  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    const f = event.dataTransfer.files[0];
    if (!f.name.toLowerCase().endsWith('.json')) {
      errorMsg.value = 'Invalid file type. Please select a .json file.';
      return;
    }
    selectedFile.value = f;
    errorMsg.value = null;
  }
};

const pollJob = (jobId: string) => {
  pollTimer = setTimeout(async () => {
    try {
      const status = await getPipelineStatus(jobId);
      currentJob.value = status;

      if (status.status === 'completed') {
        isRunning.value = false;
        emit('completed', jobId);
      } else if (status.status === 'failed') {
        isRunning.value = false;
        errorMsg.value = status.error || 'Daily pipeline execution failed. Please check input telemetry format.';
      } else {
        pollJob(jobId);
      }
    } catch (err: any) {
      isRunning.value = false;
      errorMsg.value = err?.message || 'Failed to poll pipeline status from backend.';
    }
  }, 1200);
};

const startAnalysis = async () => {
  errorMsg.value = null;
  isRunning.value = true;
  currentJob.value = {
    job_id: 'init',
    status: 'running',
    progress: 5,
    stage: 'Uploading input telemetry...'
  };

  try {
    let result: { job_id: string; status: string; progress: number; stage: string };

    if (selectedFile.value) {
      result = await uploadTodayJson(selectedFile.value, country.value);
    } else {
      // Run with current input/input_today.json in backend
      result = await runDailyPipeline(country.value);
    }

    currentJob.value = {
      job_id: result.job_id,
      status: 'running',
      progress: result.progress || 17,
      stage: result.stage || 'Validating operational data'
    };

    pollJob(result.job_id);
  } catch (err: any) {
    isRunning.value = false;
    errorMsg.value = err?.detail || err?.message || 'Pipeline failed to initiate. Ensure backend is running.';
  }
};

const viewResults = () => {
  emit('close');
  router.push('/results');
};

const reset = () => {
  if (pollTimer) clearTimeout(pollTimer);
  isRunning.value = false;
  currentJob.value = null;
  errorMsg.value = null;
  selectedFile.value = null;
};

onUnmounted(() => {
  if (pollTimer) clearTimeout(pollTimer);
});
</script>

<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-in fade-in duration-200">
    <div class="relative w-full max-w-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-teal-500/10 dark:bg-teal-500/20 flex items-center justify-center text-teal-600 dark:text-teal-400">
            <Sparkles :size="20" />
          </div>
          <div>
            <h3 class="text-base font-bold text-slate-900 dark:text-white">Run Today's Healthcare Analysis</h3>
            <p class="text-xs text-slate-500 dark:text-slate-400">End-to-end ML demand forecasting & network redistribution</p>
          </div>
        </div>
        <button
          v-if="!isRunning"
          @click="emit('close')"
          class="p-2 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
        >
          <X :size="18" />
        </button>
      </div>

      <!-- Body -->
      <div class="p-6 space-y-6">
        <!-- Error Alert -->
        <div v-if="errorMsg" class="flex items-start gap-3 p-4 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900/50 text-red-700 dark:text-red-300 text-sm animate-in fade-in">
          <AlertCircle :size="18" class="mt-0.5 flex-shrink-0" />
          <div class="flex-1">
            <p class="font-semibold">Analysis Failed</p>
            <p class="text-xs mt-0.5 opacity-90">{{ errorMsg }}</p>
          </div>
          <button @click="reset" class="text-xs underline font-medium hover:opacity-80">Try Again</button>
        </div>

        <!-- Initial Upload / Configuration State (Not Running & Not Completed) -->
        <div v-if="!isRunning && !isComplete" class="space-y-4">
          <!-- File Drop Zone -->
          <div
            @dragover.prevent
            @drop="handleDrop"
            @click="fileInputRef?.click()"
            class="group cursor-pointer border-2 border-dashed rounded-xl p-6 text-center transition flex flex-col items-center justify-center gap-2"
            :class="selectedFile
              ? 'border-teal-500 bg-teal-50/30 dark:bg-teal-950/20'
              : 'border-slate-300 dark:border-slate-700 hover:border-teal-500 hover:bg-slate-50 dark:hover:bg-slate-800/40'"
          >
            <input
              ref="fileInputRef"
              type="file"
              accept=".json"
              class="hidden"
              @change="handleFileSelect"
            />
            <div class="w-12 h-12 rounded-full flex items-center justify-center transition"
              :class="selectedFile ? 'bg-teal-500 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-500 group-hover:bg-teal-50 dark:group-hover:bg-teal-900/40 group-hover:text-teal-600'">
              <FileJson v-if="selectedFile" :size="24" />
              <Upload v-else :size="24" />
            </div>

            <div v-if="selectedFile">
              <p class="text-sm font-semibold text-slate-900 dark:text-white">{{ selectedFile.name }}</p>
              <p class="text-xs text-teal-600 dark:text-teal-400 mt-0.5">Ready for upload ({{ (selectedFile.size / 1024).toFixed(1) }} KB)</p>
            </div>
            <div v-else>
              <p class="text-sm font-medium text-slate-700 dark:text-slate-300">
                <span class="text-teal-600 dark:text-teal-400 font-semibold">Upload today's JSON</span> or drag & drop
              </p>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Accepts <code class="font-mono bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded">input_today.json</code></p>
            </div>
          </div>

          <!-- Or use current input -->
          <div class="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
            <span class="flex-1 h-px bg-slate-200 dark:border-slate-800"></span>
            <span>OR RUN EXISTING INPUT</span>
            <span class="flex-1 h-px bg-slate-200 dark:border-slate-800"></span>
          </div>

          <!-- Country Selection -->
          <div class="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-800">
            <div>
              <p class="text-xs font-semibold text-slate-800 dark:text-slate-200">Federated Coverage</p>
              <p class="text-2xs text-slate-500">Target regional operational cluster</p>
            </div>
            <select
              v-model="country"
              class="text-xs font-medium rounded-lg bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 px-2.5 py-1.5 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-teal-500"
            >
              <option value="all">All BRICS (5 Countries: India, Brazil, SA, China, Russia)</option>
              <option value="india">India Network (54 PHCs)</option>
              <option value="brazil">Brazil Network (54 PHCs)</option>
              <option value="south_africa">South Africa Network (55 PHCs)</option>
              <option value="china">China Network (54 PHCs)</option>
              <option value="russia">Russia Network (54 PHCs)</option>
            </select>
          </div>
        </div>

        <!-- Real-Time Processing / Loading State -->
        <div v-if="isRunning || isComplete" class="space-y-6">
          <!-- Progress Bar & Percentage -->
          <div>
            <div class="flex items-center justify-between text-xs font-semibold mb-2">
              <span class="text-slate-700 dark:text-slate-300">{{ currentStageText }}</span>
              <span class="text-teal-600 dark:text-teal-400 font-mono text-sm">{{ progressPercent }}%</span>
            </div>
            <div class="w-full h-3 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden p-0.5">
              <div
                class="h-full bg-gradient-to-r from-teal-500 via-teal-400 to-emerald-500 rounded-full transition-all duration-500 ease-out"
                :style="{ width: `${progressPercent}%` }"
              ></div>
            </div>
          </div>

          <!-- Processing Stage Checklist -->
          <div class="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800 space-y-2.5">
            <div
              v-for="st in PIPELINE_STAGES"
              :key="st.minProgress"
              class="flex items-center justify-between text-xs transition-colors"
              :class="progressPercent >= st.minProgress ? 'text-slate-900 dark:text-white font-medium' : 'text-slate-400 dark:text-slate-600'"
            >
              <div class="flex items-center gap-2.5">
                <CheckCircle2
                  v-if="progressPercent > st.minProgress || (progressPercent === 100 && st.minProgress === 100)"
                  :size="16"
                  class="text-teal-500 flex-shrink-0"
                />
                <Loader2
                  v-else-if="progressPercent >= st.minProgress && isRunning"
                  :size="16"
                  class="animate-spin text-teal-600 dark:text-teal-400 flex-shrink-0"
                />
                <span v-else class="w-4 h-4 rounded-full border border-slate-300 dark:border-slate-700 flex-shrink-0 inline-block"></span>
                <span>{{ st.label }}</span>
              </div>
              <span v-if="progressPercent > st.minProgress || isComplete" class="text-teal-600 dark:text-teal-400 font-mono text-2xs font-semibold">✓</span>
              <span v-else-if="progressPercent >= st.minProgress && isRunning" class="text-teal-600 dark:text-teal-400 font-mono text-2xs animate-pulse">{{ progressPercent }}%</span>
              <span v-else class="text-slate-400 text-2xs">...</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer Actions -->
      <div class="flex items-center justify-end gap-3 px-6 py-4 border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
        <button
          v-if="!isRunning && !isComplete"
          @click="emit('close')"
          class="px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white"
        >
          Cancel
        </button>

        <button
          v-if="!isRunning && !isComplete"
          @click="startAnalysis"
          class="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold shadow-md shadow-teal-500/20 transition active:scale-95"
        >
          <Play :size="14" />
          <span>{{ selectedFile ? 'Upload & Run Pipeline' : "Run Today's Analysis" }}</span>
        </button>

        <button
          v-if="isRunning"
          disabled
          class="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-teal-600/70 text-white text-xs font-semibold cursor-not-allowed opacity-90"
        >
          <Loader2 :size="14" class="animate-spin" />
          <span>Processing Pipeline...</span>
        </button>

        <button
          v-if="isComplete"
          @click="viewResults"
          class="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md shadow-emerald-500/20 transition active:scale-95"
        >
          <span>View Results Dashboard</span>
          <ArrowRight :size="14" />
        </button>
      </div>
    </div>
  </div>
</template>
