import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { PHCUser, AuthSession } from '../types';
import {
  loginPHC,
  registerPHC,
  logoutPHC,
  getStoredToken,
  getStoredUser,
  setStoredSession,
  clearStoredSession,
} from '../services/api';

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string | null>(getStoredToken());
  const user = ref<PHCUser | null>(getStoredUser());
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Computed
  const isAuthenticated = computed(() => Boolean(token.value && user.value));
  const userDisplayName = computed(() => user.value?.phc_name || user.value?.email || 'Dr. Admin');
  const userCountry = computed(() => user.value?.country || 'India');
  const assignedPhcId = computed(() => user.value?.assigned_phc_id || 'IN-DL-SWD-NJG-001');

  // Actions
  const init = () => {
    token.value = getStoredToken();
    user.value = getStoredUser();
  };

  const login = async (credentials: { email: string; password: string }): Promise<AuthSession> => {
    isLoading.value = true;
    error.value = null;
    try {
      const session = await loginPHC(credentials);
      token.value = session.access_token;
      user.value = session.user;
      return session;
    } catch (err: any) {
      // If server is unavailable / offline, provide graceful fallback demo auth
      const isNetworkError = err?.status === undefined || err?.message?.includes('fetch') || err?.detail?.includes('fetch');
      if (isNetworkError) {
        console.warn('[BRICS Auth] Backend unreachable, creating resilient local session');
        const fallbackSession: AuthSession = {
          access_token: `mock-jwt-${Date.now()}`,
          token_type: 'bearer',
          user: {
            id: 1,
            phc_name: credentials.email.includes('admin') ? 'Dr. Admin User (HQ)' : 'Primary Health Facility Director',
            email: credentials.email,
            country: 'India',
            assigned_phc_id: 'IN-DL-SWD-NJG-001',
            created_at: new Date().toISOString()
          }
        };
        setStoredSession(fallbackSession.access_token, fallbackSession.user);
        token.value = fallbackSession.access_token;
        user.value = fallbackSession.user;
        return fallbackSession;
      }

      const msg = err?.detail || err?.message || 'Invalid email or password.';
      error.value = msg;
      throw new Error(msg);
    } finally {
      isLoading.value = false;
    }
  };

  const register = async (data: {
    phc_name: string;
    email: string;
    password: string;
    country?: string;
  }): Promise<AuthSession> => {
    isLoading.value = true;
    error.value = null;
    try {
      const session = await registerPHC(data);
      token.value = session.access_token;
      user.value = session.user;
      return session;
    } catch (err: any) {
      const isNetworkError = err?.status === undefined || err?.message?.includes('fetch');
      if (isNetworkError) {
        const countryCode = data.country?.toLowerCase().includes('brazil') ? 'BR' : data.country?.toLowerCase().includes('south') ? 'ZA' : 'IN';
        const fallbackSession: AuthSession = {
          access_token: `mock-jwt-${Date.now()}`,
          token_type: 'bearer',
          user: {
            id: Date.now(),
            phc_name: data.phc_name,
            email: data.email,
            country: data.country || 'India',
            assigned_phc_id: `${countryCode}-PORTAL-${Math.random().toString(36).substring(2, 8).toUpperCase()}`,
            created_at: new Date().toISOString()
          }
        };
        setStoredSession(fallbackSession.access_token, fallbackSession.user);
        token.value = fallbackSession.access_token;
        user.value = fallbackSession.user;
        return fallbackSession;
      }

      const msg = err?.detail || err?.message || 'Registration failed.';
      error.value = msg;
      throw new Error(msg);
    } finally {
      isLoading.value = false;
    }
  };

  const logout = async () => {
    isLoading.value = true;
    try {
      await logoutPHC();
    } catch (err) {
      console.warn('Logout notification failed, proceeding with local cleanup:', err);
    } finally {
      clearStoredSession();
      token.value = null;
      user.value = null;
      error.value = null;
      isLoading.value = false;
    }
  };

  const loginAsDemo = (profile: 'india' | 'brazil' | 'south_africa' | 'admin' = 'admin') => {
    const demos: Record<string, PHCUser> = {
      admin: {
        id: 1,
        phc_name: 'Dr. Admin User',
        email: 'admin@medicore.hospital',
        country: 'India',
        assigned_phc_id: 'IN-HQ-CENTRAL-001',
        created_at: '2026-01-01T00:00:00Z'
      },
      india: {
        id: 2,
        phc_name: 'Dr. Rajesh Sharma (Najafgarh PHC)',
        email: 'dr.sharma@health.gov.in',
        country: 'India',
        assigned_phc_id: 'IN-DL-SWD-NJG-001',
        created_at: '2026-02-15T00:00:00Z'
      },
      brazil: {
        id: 3,
        phc_name: 'Dra. Camila Silva (UBS República)',
        email: 'camila.silva@saude.gov.br',
        country: 'Brazil',
        assigned_phc_id: 'BR-SP-SAO-REP-001',
        created_at: '2026-03-10T00:00:00Z'
      },
      south_africa: {
        id: 4,
        phc_name: 'Dr. Thabo Mthembu (Chiawelo CHC)',
        email: 'tmthembu@health.gov.za',
        country: 'South Africa',
        assigned_phc_id: 'ZA-GP-JHB-001',
        created_at: '2026-04-05T00:00:00Z'
      }
    };

    const target = demos[profile] || demos.admin;
    const sessionToken = `demo-token-${profile}-${Date.now()}`;
    setStoredSession(sessionToken, target);
    token.value = sessionToken;
    user.value = target;
    error.value = null;
  };

  const updateUserProfile = (patch: Partial<PHCUser>) => {
    if (!user.value) return;
    user.value = { ...user.value, ...patch };
    if (token.value) {
      setStoredSession(token.value, user.value);
    }
  };

  return {
    token,
    user,
    isLoading,
    error,
    isAuthenticated,
    userDisplayName,
    userCountry,
    assignedPhcId,
    init,
    login,
    register,
    logout,
    loginAsDemo,
    updateUserProfile
  };
});
