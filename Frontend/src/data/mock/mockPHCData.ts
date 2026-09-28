// Sample PHC reference dataset for BRICS countries
// This is a separate reference dataset — NOT the ML prediction input
import type { PHCRecord } from '../../types';

export const mockPHCData: PHCRecord[] = [
  { phc_id: 'IN-AP-VSK-MVP-001', name: 'MVP Colony PHC', district: 'Visakhapatnam', state: 'Andhra Pradesh', country: 'India', lat: 17.7041, lon: 83.2977 },
  { phc_id: 'IN-AP-VSK-MVP-002', name: 'Gajuwaka PHC', district: 'Visakhapatnam', state: 'Andhra Pradesh', country: 'India', lat: 17.6842, lon: 83.2099 },
  { phc_id: 'IN-AP-GUN-PHC-003', name: 'Brodipet PHC', district: 'Guntur', state: 'Andhra Pradesh', country: 'India', lat: 16.3008, lon: 80.4428 },
  { phc_id: 'IN-TN-CHE-PHC-004', name: 'Adyar PHC', district: 'Chennai', state: 'Tamil Nadu', country: 'India', lat: 13.0067, lon: 80.2565 },
  { phc_id: 'IN-TN-CHE-PHC-005', name: 'Tambaram PHC', district: 'Chennai', state: 'Tamil Nadu', country: 'India', lat: 12.9249, lon: 80.1000 },
  { phc_id: 'ZA-WC-CPT-PHC-006', name: 'Woodstock CHC', district: 'Cape Town', state: 'Western Cape', country: 'South Africa', lat: -33.9249, lon: 18.4241 },
  { phc_id: 'ZA-WC-CPT-PHC-007', name: 'Mitchells Plain CHC', district: 'Cape Town', state: 'Western Cape', country: 'South Africa', lat: -34.0475, lon: 18.6239 },
  { phc_id: 'BR-SP-SAO-PHC-008', name: 'UBS Vila Matilde', district: 'São Paulo', state: 'São Paulo', country: 'Brazil', lat: -23.5505, lon: -46.6333 },
  { phc_id: 'IN-TN-CHE-PHC-009', name: 'Perambur PHC', district: 'Chennai', state: 'Tamil Nadu', country: 'India', lat: 13.1186, lon: 80.2356 },
  { phc_id: 'IN-AP-VSK-MVP-010', name: 'Madhurawada PHC', district: 'Visakhapatnam', state: 'Andhra Pradesh', country: 'India', lat: 17.7867, lon: 83.3780 },
  { phc_id: 'RU-MOW-PHC-011', name: 'Khamovniki PHC', district: 'Moscow', state: 'Moscow Oblast', country: 'Russia', lat: 55.7558, lon: 37.6173 },
  { phc_id: 'CN-BJ-PHC-012', name: 'Chaoyang PHC', district: 'Beijing', state: 'Beijing', country: 'China', lat: 39.9042, lon: 116.4074 },
];
