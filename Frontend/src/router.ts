import { createRouter, createWebHistory } from 'vue-router';
import HospitalShell from './components/hospital/HospitalShell.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: HospitalShell,
      children: [
        { path: '', redirect: '/dashboard' },
        { path: 'dashboard', component: () => import('./pages/hospital/Dashboard.vue') },
        { path: 'emergency', component: () => import('./pages/hospital/Emergency.vue') },
        { path: 'patients', component: () => import('./pages/hospital/Patients.vue') },
        { path: 'doctors', component: () => import('./pages/hospital/Doctors.vue') },
        { path: 'beds', component: () => import('./pages/hospital/Beds.vue') },
        { path: 'pharmacy', component: () => import('./pages/hospital/Pharmacy.vue') },
        { path: 'inventory', component: () => import('./pages/hospital/Inventory.vue') },
        { path: 'ambulance', component: () => import('./pages/hospital/Ambulance.vue') },
        { path: 'departments', component: () => import('./pages/hospital/Departments.vue') },
        { path: 'analytics', component: () => import('./pages/hospital/Analytics.vue') },
        { path: 'notifications', component: () => import('./pages/hospital/Notifications.vue') },
        { path: 'settings', component: () => import('./pages/hospital/Settings.vue') },
        
        // BRICS Healthcare Intelligence & PHC Portal Routes
        { path: 'map', component: () => import('./pages/hospital/WorldOperationsMap.vue') },
        { path: 'results', component: () => import('./pages/hospital/BricsResultsDashboard.vue') },
        { path: 'brics-analysis', component: () => import('./pages/hospital/BricsResultsDashboard.vue') },
        { path: 'phc-portal', component: () => import('./pages/hospital/PHCPortal.vue') },
        { path: 'requests', redirect: '/phc-portal' },

        // Legacy compatibility routes
        { path: 'overview', redirect: '/dashboard' },
        { path: 'prediction', redirect: '/results' },
        { path: 'network', redirect: '/map' },
      ]
    }
  ]
});

export default router;
