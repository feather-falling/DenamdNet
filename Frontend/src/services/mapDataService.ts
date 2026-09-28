// ─────────────────────────────────────────────────────────────────────────────
// Map Data Service — BRICS Healthcare Intelligence & PHC Operations
// ─────────────────────────────────────────────────────────────────────────────
// Provides defensive, unified data loading, normalization, and operational
// risk classification for all 163 PHC facilities across India, Brazil, and
// South Africa. Consumes backend /api/phcs, /api/predictions, /api/alerts
// with seamless fallback to project static datasets.
// ─────────────────────────────────────────────────────────────────────────────

import staticFacilities from '../data/static/facilities.json';
import staticAlerts from '../data/static/alerts.json';
import staticPredictions from '../data/static/predictions.json';

export interface AlertDetail {
  alert_id: string;
  timestamp: string;
  country_code: string;
  phc_id: string;
  district: string;
  pattern_type: string;
  confidence_score: number;
  severity: 'EMERGENCY' | 'WARNING' | 'WATCH' | string;
  correlated_resources: string[];
  primary_driver: string;
  recommended_actions: string[];
}

export interface MedicinePredictionDetail {
  medicine_id: string;
  medicine_name: string;
  unit: string;
  current_stock: number;
  forecast_daily: number;
  forecast_7d: number;
  stockout_days: number;
  stockout_date?: string;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  anomaly_detected: boolean;
  anomaly_score: number;
  safety_stock: number;
  lead_time_hours: number;
}

export type OperationalCondition =
  | 'NORMAL'
  | 'ATTENTION'
  | 'HIGH_RISK'
  | 'CRITICAL'
  | 'OUTBREAK';

export interface EnrichedPHC {
  phc_id: string;
  name: string;
  official_name?: string;
  country: string;
  country_code: string;
  state: string;
  district: string;
  city?: string;
  locality?: string;
  facility_type: string;
  urban_rural?: string;
  latitude: number;
  longitude: number;
  hasCoordinates: boolean;
  capacity: {
    beds: number;
    opd_capacity_per_day: number;
    emergency_beds: number;
  };
  staffing: {
    doctors: number;
    nurses: number;
    pharmacists: number;
    lab_technicians: number;
    other_staff: number;
  };
  catchment_population: number;
  services: string[];
  operational_status: OperationalCondition;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  max_risk_score: number;
  min_stockout_days: number;
  stockout_risk: boolean;
  active_anomaly: boolean;
  has_outbreak_alert: boolean;
  outbreak_severity?: string;
  primary_outbreak?: AlertDetail;
  alerts: AlertDetail[];
  medicines: MedicinePredictionDetail[];
  total_current_stock: number;
  total_forecast_demand: number;
}

export interface MapSummaryMetrics {
  total_phcs: number;
  india_count: number;
  brazil_count: number;
  south_africa_count: number;
  china_count: number;
  russia_count: number;
  critical_count: number;
  high_risk_count: number;
  outbreak_count: number;
  attention_count: number;
  normal_count: number;
  total_beds: number;
  total_daily_opd: number;
  severe_stockout_count: number;
}

// Country code normalizer
export function normalizeCountryCode(codeOrName: string | undefined): string {
  if (!codeOrName) return 'UNKNOWN';
  const lower = codeOrName.toLowerCase().trim();
  if (lower === 'in' || lower.includes('india')) return 'IN';
  if (lower === 'br' || lower.includes('brazil') || lower.includes('brasil')) return 'BR';
  if (lower === 'za' || lower.includes('south africa') || lower.includes('africa')) return 'ZA';
  if (lower === 'cn' || lower.includes('china')) return 'CN';
  if (lower === 'ru' || lower.includes('russia')) return 'RU';
  return codeOrName.toUpperCase();
}

export function getCountryDisplayName(countryCode: string): string {
  switch (countryCode) {
    case 'IN': return 'India';
    case 'BR': return 'Brazil';
    case 'ZA': return 'South Africa';
    case 'CN': return 'China';
    case 'RU': return 'Russia';
    default: return countryCode;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Raw data normalization
// ─────────────────────────────────────────────────────────────────────────────

function extractPHCList(): any[] {
  const list: any[] = [];

  const rawIndia = (staticFacilities as any).india;
  if (Array.isArray(rawIndia)) {
    list.push(...rawIndia);
  } else if (rawIndia && Array.isArray(rawIndia.phcs)) {
    list.push(...rawIndia.phcs);
  }

  const rawBrazil = (staticFacilities as any).brazil;
  if (Array.isArray(rawBrazil)) {
    list.push(...rawBrazil);
  } else if (rawBrazil && Array.isArray(rawBrazil.phcs)) {
    list.push(...rawBrazil.phcs);
  }

  const rawSA = (staticFacilities as any).south_africa;
  if (Array.isArray(rawSA)) {
    list.push(...rawSA);
  } else if (rawSA && Array.isArray(rawSA.phcs)) {
    list.push(...rawSA.phcs);
  }

  const rawChina = (staticFacilities as any).china;
  if (Array.isArray(rawChina)) {
    list.push(...rawChina);
  } else if (rawChina && Array.isArray(rawChina.phcs)) {
    list.push(...rawChina.phcs);
  }

  const rawRussia = (staticFacilities as any).russia;
  if (Array.isArray(rawRussia)) {
    list.push(...rawRussia);
  } else if (rawRussia && Array.isArray(rawRussia.phcs)) {
    list.push(...rawRussia.phcs);
  }

  return list;
}

export async function fetchAllMapData(): Promise<{
  phcs: EnrichedPHC[];
  metrics: MapSummaryMetrics;
  medicinesList: string[];
  districtsList: string[];
}> {
  // 1. Immediately initialize with bundled static data for instant 0ms rendering
  let rawPhcList: any[] = extractPHCList();
  let rawAlerts: any[] = Array.isArray(staticAlerts) ? staticAlerts : [];
  let rawPredictions: any[] = Array.isArray(staticPredictions) ? staticPredictions : [];

  const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

  // Fast health check: only fetch backend if online (300ms timeout)
  try {
    const healthRes = await fetch(`${BASE_URL}/health`, { signal: AbortSignal.timeout(300) });
    if (healthRes.ok) {
      const [phcRes, alertRes, predRes] = await Promise.all([
        fetch(`${BASE_URL}/api/phcs`).catch(() => null),
        fetch(`${BASE_URL}/api/alerts`).catch(() => null),
        fetch(`${BASE_URL}/api/predictions`).catch(() => null)
      ]);

      if (phcRes && phcRes.ok) {
        const json = await phcRes.json();
        if (Array.isArray(json) && json.length > 0) rawPhcList = json;
      }
      if (alertRes && alertRes.ok) {
        const json = await alertRes.json();
        if (json && Array.isArray(json.alerts)) rawAlerts = json.alerts;
      }
      if (predRes && predRes.ok) {
        const json = await predRes.json();
        if (json && Array.isArray(json.records)) rawPredictions = json.records;
      }
    }
  } catch {
    // Backend offline -> instantly continues with loaded static data
  }

  // 2. Index alerts by phc_id
  const alertsByPhc = new Map<string, AlertDetail[]>();
  for (const a of rawAlerts) {
    const pid = a.phc_id;
    if (!pid) continue;
    if (!alertsByPhc.has(pid)) {
      alertsByPhc.set(pid, []);
    }
    alertsByPhc.get(pid)!.push({
      alert_id: a.alert_id || `ALT-${Math.random()}`,
      timestamp: a.timestamp || '',
      country_code: normalizeCountryCode(a.country_code),
      phc_id: pid,
      district: a.district || '',
      pattern_type: a.pattern_type || 'UNKNOWN',
      confidence_score: Number(a.confidence_score ?? 0.8),
      severity: a.severity || 'WARNING',
      correlated_resources: Array.isArray(a.correlated_resources) ? a.correlated_resources : [],
      primary_driver: a.primary_driver || '',
      recommended_actions: Array.isArray(a.recommended_actions) ? a.recommended_actions : []
    });
  }

  // 3. Index predictions by phc_id
  const predsByPhc = new Map<string, MedicinePredictionDetail[]>();
  const allMedicineNames = new Set<string>();

  for (const p of rawPredictions) {
    const pid = p.phc_id;
    if (!pid) continue;
    if (!predsByPhc.has(pid)) {
      predsByPhc.set(pid, []);
    }

    const medName = p.medicine_name || p.medicine_id || 'Unknown Medicine';
    allMedicineNames.add(medName);

    const fDaily = Number(p.forecast_demand?.daily ?? p.daily_demand ?? 0);
    const f7d = Number(p.forecast_demand?.total ?? fDaily * 7);
    const sDays = Number(p.stockout?.estimated_days ?? p.stockout_days ?? 999);
    const rScore = Number(p.risk?.score ?? p.risk_score ?? 0);
    const rLevel = (p.risk?.level ?? p.risk_level ?? 'LOW').toUpperCase() as any;
    const aDetected = Boolean(p.anomaly?.detected ?? p.anomaly_detected ?? false);
    const aScore = Number(p.anomaly?.score ?? p.anomaly_score ?? 0);
    const currStock = Number(p.current_stock ?? 0);
    const safeStock = Number(p.inventory_protection?.safety_stock ?? p.safety_stock ?? 10);
    const leadTime = Number(p.inventory_protection?.lead_time_hours ?? p.lead_time ?? 12);

    predsByPhc.get(pid)!.push({
      medicine_id: p.medicine_id || '',
      medicine_name: medName,
      unit: p.unit || 'units',
      current_stock: currStock,
      forecast_daily: fDaily,
      forecast_7d: f7d,
      stockout_days: Math.round(sDays * 10) / 10,
      stockout_date: p.stockout?.estimated_date,
      risk_score: Math.round(rScore * 100) / 100,
      risk_level: rLevel,
      anomaly_detected: aDetected,
      anomaly_score: Math.round(aScore * 100) / 100,
      safety_stock: safeStock,
      lead_time_hours: leadTime
    });
  }

  // 4. Enrich and assemble all PHCs
  const enrichedList: EnrichedPHC[] = [];
  const districtsSet = new Set<string>();

  for (const raw of rawPhcList) {
    const pid = raw.phc_id || raw.id;
    if (!pid) continue;

    // Geography parsing directly from canonical PHC master record
    const lat = Number(raw.geography?.latitude ?? raw.latitude);
    const lon = Number(raw.geography?.longitude ?? raw.longitude);
    const hasCoords = !isNaN(lat) && !isNaN(lon) && lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180;

    const rawCountry = raw.country || '';
    const countryCode = normalizeCountryCode(rawCountry || raw.country_code || pid.split('-')[0]);
    const countryName = rawCountry || getCountryDisplayName(countryCode);
    const districtName = raw.district || raw.city || 'District Unknown';
    if (districtName) districtsSet.add(districtName);

    const facilityAlerts = alertsByPhc.get(pid) || [];
    const facilityPreds = predsByPhc.get(pid) || [];

    // Calculate aggregated metrics
    let maxRiskScore = 0;
    let minStockoutDays = 999;
    let criticalMeds = 0;
    let activeAnomaly = false;
    let totalStock = 0;
    let totalDemand = 0;
    let hasHighRiskMed = false;

    for (const m of facilityPreds) {
      if (m.risk_score > maxRiskScore) maxRiskScore = m.risk_score;
      if (m.stockout_days < minStockoutDays) minStockoutDays = m.stockout_days;
      if (m.stockout_days <= 3 || m.risk_level === 'HIGH' || m.risk_level === 'CRITICAL') {
        criticalMeds++;
      }
      if (m.risk_level === 'HIGH' || m.risk_level === 'CRITICAL') {
        hasHighRiskMed = true;
      }
      if (m.anomaly_detected) {
        activeAnomaly = true;
      }
      totalStock += m.current_stock;
      totalDemand += m.forecast_7d;
    }

    const hasOutbreak = facilityAlerts.length > 0;
    const hasEmergencyAlert = facilityAlerts.some(a => a.severity === 'EMERGENCY');
    const primaryAlert = facilityAlerts[0];

    // Determine operational condition
    let operationalStatus: OperationalCondition = 'NORMAL';
    let riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' = 'LOW';

    if (hasEmergencyAlert || minStockoutDays <= 2 || maxRiskScore >= 0.75) {
      operationalStatus = 'CRITICAL';
      riskLevel = 'CRITICAL';
    } else if (hasOutbreak) {
      operationalStatus = 'OUTBREAK';
      riskLevel = 'HIGH';
    } else if (hasHighRiskMed || minStockoutDays <= 5 || maxRiskScore >= 0.5) {
      operationalStatus = 'HIGH_RISK';
      riskLevel = 'HIGH';
    } else if (activeAnomaly || minStockoutDays <= 10 || maxRiskScore >= 0.3) {
      operationalStatus = 'ATTENTION';
      riskLevel = 'MEDIUM';
    } else {
      operationalStatus = 'NORMAL';
      riskLevel = 'LOW';
    }

    const stockoutRisk = minStockoutDays <= 5;

    enrichedList.push({
      phc_id: pid,
      name: raw.name || raw.phc_name || pid,
      official_name: raw.official_name,
      country: countryName,
      country_code: countryCode,
      state: raw.state || raw.state_region || '',
      district: districtName,
      city: raw.city,
      locality: raw.locality,
      facility_type: raw.facility_type || 'Primary Health Centre',
      urban_rural: raw.urban_rural,
      latitude: hasCoords ? lat : 0,
      longitude: hasCoords ? lon : 0,
      hasCoordinates: hasCoords,
      capacity: {
        beds: Number(raw.capacity?.beds ?? 10),
        opd_capacity_per_day: Number(raw.capacity?.opd_capacity_per_day ?? 150),
        emergency_beds: Number(raw.capacity?.emergency_beds ?? 2)
      },
      staffing: {
        doctors: Number(raw.staffing_baseline?.doctors ?? 2),
        nurses: Number(raw.staffing_baseline?.nurses ?? 5),
        pharmacists: Number(raw.staffing_baseline?.pharmacists ?? 1),
        lab_technicians: Number(raw.staffing_baseline?.lab_technicians ?? 1),
        other_staff: Number(raw.staffing_baseline?.other_staff ?? 4)
      },
      catchment_population: Number(raw.catchment?.population ?? 25000),
      services: Array.isArray(raw.services) ? raw.services : ['general_medicine', 'pharmacy', 'emergency_first_aid'],
      operational_status: operationalStatus,
      risk_level: riskLevel,
      max_risk_score: Math.round(maxRiskScore * 100) / 100,
      min_stockout_days: minStockoutDays === 999 ? 30 : minStockoutDays,
      stockout_risk: stockoutRisk,
      active_anomaly: activeAnomaly,
      has_outbreak_alert: hasOutbreak,
      outbreak_severity: primaryAlert?.severity,
      primary_outbreak: primaryAlert,
      alerts: facilityAlerts,
      medicines: facilityPreds,
      total_current_stock: totalStock,
      total_forecast_demand: totalDemand
    });
  }

  // 5. Aggregate summary metrics
  const metrics: MapSummaryMetrics = {
    total_phcs: enrichedList.length,
    india_count: enrichedList.filter(p => p.country === 'India' || p.country_code === 'IN').length,
    brazil_count: enrichedList.filter(p => p.country === 'Brazil' || p.country_code === 'BR').length,
    south_africa_count: enrichedList.filter(p => p.country === 'South Africa' || p.country_code === 'ZA').length,
    china_count: enrichedList.filter(p => p.country === 'China' || p.country_code === 'CN').length,
    russia_count: enrichedList.filter(p => p.country === 'Russia' || p.country_code === 'RU').length,
    critical_count: enrichedList.filter(p => p.operational_status === 'CRITICAL').length,
    high_risk_count: enrichedList.filter(p => p.operational_status === 'HIGH_RISK').length,
    outbreak_count: enrichedList.filter(p => p.operational_status === 'OUTBREAK' || p.has_outbreak_alert).length,
    attention_count: enrichedList.filter(p => p.operational_status === 'ATTENTION').length,
    normal_count: enrichedList.filter(p => p.operational_status === 'NORMAL').length,
    total_beds: enrichedList.reduce((acc, p) => acc + p.capacity.beds, 0),
    total_daily_opd: enrichedList.reduce((acc, p) => acc + p.capacity.opd_capacity_per_day, 0),
    severe_stockout_count: enrichedList.filter(p => p.min_stockout_days <= 3).length
  };

  return {
    phcs: enrichedList,
    metrics,
    medicinesList: Array.from(allMedicineNames).sort(),
    districtsList: Array.from(districtsSet).sort()
  };
}
