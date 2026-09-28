import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import {
  mockPatients, mockBeds, mockMedicines, mockInventory,
  mockAmbulances, mockAlerts, mockNotifications, mockDepartments,
  dashboardStats,
  type Patient, type Bed, type Medicine, type InventoryItem,
  type Ambulance, type EmergencyAlert, type Notification,
} from '../data/mock/hospitalData';

export const useHospitalStore = defineStore('hospital', () => {
  // ─── State ───────────────────────────────────────────────────────────────
  const darkMode = ref(false);
  const sidebarCollapsed = ref(false);
  const mobileSidebarOpen = ref(false);

  const patients = ref<Patient[]>(mockPatients);
  const beds = ref<Bed[]>(mockBeds);
  const medicines = ref<Medicine[]>(mockMedicines);
  const inventory = ref<InventoryItem[]>(mockInventory);
  const ambulances = ref<Ambulance[]>(mockAmbulances);
  const alerts = ref<EmergencyAlert[]>(mockAlerts);
  const notifications = ref<Notification[]>(mockNotifications);
  const departments = ref(mockDepartments);
  const stats = ref(dashboardStats);

  // Emergency popup
  const activeEmergencyPopup = ref<{
    patient: string; priority: string; department: string;
    required: string; doctor: string; arrival: string; visible: boolean;
  } | null>(null);

  // ─── Computed ────────────────────────────────────────────────────────────
  const unreadNotifications = computed(() => notifications.value.filter(n => !n.read).length);
  const unacknowledgedAlerts = computed(() => alerts.value.filter(a => !a.acknowledged).length);
  const criticalPatients = computed(() => patients.value.filter(p => p.priority === 'CRITICAL'));
  const availableBeds = computed(() => beds.value.filter(b => b.status === 'Available').length);
  const availableAmbulances = computed(() => ambulances.value.filter(a => a.status === 'Available').length);

  // ─── Extended Settings & UI State ─────────────────────────────────────────
  const compactMode = ref(localStorage.getItem('brics_compact_mode') === 'true');
  const commandPaletteOpen = ref(false);
  const authModalOpen = ref(false);
  const profileModalOpen = ref(false);

  const notificationPreferences = ref({
    emergencyAlerts: true,
    stockAlerts: true,
    bedAvailability: true,
    appointmentReminders: false,
  });

  const hospitalInfo = ref({
    name: 'City General Hospital',
    code: 'CGH-MH-001',
    location: 'Mumbai, Maharashtra',
    accreditation: 'NABH Certified',
    emergencyContact: '+91-22-12345678',
  });

  // ─── Actions ─────────────────────────────────────────────────────────────
  const toggleDarkMode = () => { darkMode.value = !darkMode.value; };
  const toggleSidebar = () => { sidebarCollapsed.value = !sidebarCollapsed.value; };
  const setMobileSidebar = (v: boolean) => { mobileSidebarOpen.value = v; };

  const toggleCompactMode = () => {
    compactMode.value = !compactMode.value;
    localStorage.setItem('brics_compact_mode', String(compactMode.value));
  };

  const updateNotificationPref = (key: keyof typeof notificationPreferences.value, val: boolean) => {
    notificationPreferences.value[key] = val;
  };

  const updateHospitalInfo = (info: Partial<typeof hospitalInfo.value>) => {
    hospitalInfo.value = { ...hospitalInfo.value, ...info };
  };

  const acknowledgeAlert = (id: string) => {
    const alert = alerts.value.find(a => a.id === id);
    if (alert) alert.acknowledged = true;
  };

  const markNotificationRead = (id: string) => {
    const notif = notifications.value.find(n => n.id === id);
    if (notif) notif.read = true;
  };

  const markAllNotificationsRead = () => {
    notifications.value.forEach(n => n.read = true);
  };

  const updateBedStatus = (bedId: string, status: Bed['status']) => {
    const bed = beds.value.find(b => b.id === bedId);
    if (bed) bed.status = status;
  };

  const addPatient = (patient: Patient) => {
    patients.value.unshift(patient);
    stats.value.totalPatients++;
  };

  const triggerEmergency = (data: {
    patient: string; priority: string; department: string;
    required: string; doctor: string;
  }) => {
    const arrival = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    activeEmergencyPopup.value = { ...data, arrival, visible: true };

    // Add alert
    alerts.value.unshift({
      id: `ALT-${Date.now()}`,
      type: 'Critical Patient',
      severity: 'critical',
      time: arrival,
      description: `Emergency triggered: ${data.patient} — ${data.department}`,
      location: data.department,
      acknowledged: false,
    });

    // Add notification
    notifications.value.unshift({
      id: `NTF-${Date.now()}`,
      category: 'Emergency',
      title: '🚨 Emergency Triggered',
      message: `${data.patient} requires immediate ${data.required} in ${data.department}`,
      time: arrival,
      read: false,
      severity: 'critical',
    });
  };

  const dismissEmergencyPopup = () => {
    if (activeEmergencyPopup.value) activeEmergencyPopup.value.visible = false;
    setTimeout(() => { activeEmergencyPopup.value = null; }, 400);
  };

  return {
    darkMode, sidebarCollapsed, mobileSidebarOpen, compactMode,
    commandPaletteOpen, authModalOpen, profileModalOpen,
    notificationPreferences, hospitalInfo,
    patients, beds, medicines, inventory, ambulances, alerts, notifications, departments, stats,
    activeEmergencyPopup,
    unreadNotifications, unacknowledgedAlerts, criticalPatients, availableBeds, availableAmbulances,
    toggleDarkMode, toggleSidebar, setMobileSidebar, toggleCompactMode,
    updateNotificationPref, updateHospitalInfo,
    acknowledgeAlert, markNotificationRead, markAllNotificationsRead,
    updateBedStatus, addPatient, triggerEmergency, dismissEmergencyPopup,
  };
});

