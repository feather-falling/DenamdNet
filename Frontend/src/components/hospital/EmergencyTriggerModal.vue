<script setup lang="ts">
import { ref } from 'vue';
import { AlertTriangle, X } from 'lucide-vue-next';
import { useHospitalStore } from '../../stores/hospitalStore';

const store = useHospitalStore();

const isOpen = ref(false);
const form = ref({
  patient: '',
  priority: 'CRITICAL',
  department: 'Emergency',
  required: 'ICU Bed',
  doctor: 'Dr. On-Call',
  ambulanceRequired: false,
});

const open = () => { isOpen.value = true; };
const close = () => { isOpen.value = false; };

const submit = () => {
  store.triggerEmergency({
    patient: form.value.patient || 'Unknown Patient',
    priority: form.value.priority,
    department: form.value.department,
    required: form.value.required,
    doctor: form.value.doctor,
  });
  close();
};

// Expose open for external use via provide/inject or event bus if needed
defineExpose({ open });
</script>

<template>
  <!-- This is an internal emergency trigger — opened via store -->
  <!-- Empty component - emergency trigger is done directly via store -->
</template>
