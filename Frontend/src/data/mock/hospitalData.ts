// ─── Hospital Mock Data ────────────────────────────────────────────────────

export interface Patient {
  id: string;
  name: string;
  age: number;
  gender: 'Male' | 'Female' | 'Other';
  department: string;
  doctor: string;
  room: string;
  bed: string;
  priority: 'NORMAL' | 'HIGH' | 'CRITICAL';
  admissionDate: string;
  status: 'Admitted' | 'Discharged' | 'Critical' | 'Under Observation' | 'In Surgery';
  bloodGroup: string;
  contact: string;
  diagnosis: string;
  insurance: string;
  vitals: { bp: string; pulse: number; temp: number; spo2: number };
}

export interface Doctor {
  id: string;
  name: string;
  specialty: string;
  department: string;
  status: 'On Duty' | 'Off Duty' | 'In Surgery' | 'On Leave';
  patients: number;
  experience: string;
  contact: string;
  avatar: string;
}

export interface Bed {
  id: string;
  ward: string;
  room: string;
  type: 'General' | 'ICU' | 'Emergency' | 'Surgical' | 'Pediatric' | 'Maternity';
  status: 'Available' | 'Occupied' | 'Reserved' | 'Cleaning' | 'Maintenance' | 'Emergency';
  patient?: string;
  admittedDate?: string;
}

export interface Medicine {
  id: string;
  name: string;
  category: string;
  quantity: number;
  maxQuantity: number;
  unit: string;
  minStock: number;
  expiryDate: string;
  supplier: string;
  status: 'IN STOCK' | 'LOW STOCK' | 'OUT OF STOCK' | 'EXPIRING SOON';
  price: number;
}

export interface InventoryItem {
  id: string;
  name: string;
  category: string;
  quantity: number;
  minQuantity: number;
  status: 'In Stock' | 'Low Stock' | 'Critical Stock' | 'Out of Stock';
  location: string;
  lastUpdated: string;
}

export interface Ambulance {
  id: string;
  regNumber: string;
  status: 'Available' | 'On Mission' | 'Returning' | 'Maintenance';
  driver: string;
  contact: string;
  location: string;
  destination?: string;
  eta?: string;
  lastService: string;
}

export interface EmergencyAlert {
  id: string;
  type: 'Critical Patient' | 'Code Blue' | 'Ambulance Arrival' | 'ICU Bed Shortage' | 'Low Medicine Stock' | 'Blood Bank Alert' | 'Equipment Failure' | 'Doctor Required';
  severity: 'critical' | 'high' | 'medium' | 'low';
  time: string;
  description: string;
  location: string;
  acknowledged: boolean;
}

export interface Notification {
  id: string;
  category: 'Emergency' | 'Patients' | 'Beds' | 'Pharmacy' | 'Inventory' | 'Appointments' | 'Staff';
  title: string;
  message: string;
  time: string;
  read: boolean;
  severity: 'critical' | 'high' | 'medium' | 'low';
}

export interface Department {
  id: string;
  name: string;
  icon: string;
  patients: number;
  doctors: number;
  nurses: number;
  availableBeds: number;
  totalBeds: number;
  status: 'Normal' | 'Busy' | 'Critical' | 'Full';
  head: string;
  color: string;
}

// ─── Patients ───────────────────────────────────────────────────────────────
export const mockPatients: Patient[] = [
  { id: 'P-001', name: 'Rajesh Kumar', age: 58, gender: 'Male', department: 'Cardiology', doctor: 'Dr. Sharma', room: 'A-204', bed: 'A204-B', priority: 'CRITICAL', admissionDate: '2026-09-20', status: 'Critical', bloodGroup: 'B+', contact: '+91-9876543210', diagnosis: 'Acute Myocardial Infarction', insurance: 'CGHS', vitals: { bp: '160/100', pulse: 102, temp: 99.2, spo2: 94 } },
  { id: 'P-002', name: 'Priya Sharma', age: 32, gender: 'Female', department: 'Obstetrics', doctor: 'Dr. Mehta', room: 'B-101', bed: 'B101-A', priority: 'NORMAL', admissionDate: '2026-09-22', status: 'Admitted', bloodGroup: 'O+', contact: '+91-9988776655', diagnosis: 'Normal Delivery', insurance: 'Mediclaim', vitals: { bp: '120/80', pulse: 78, temp: 98.6, spo2: 99 } },
  { id: 'P-003', name: 'Amit Patel', age: 45, gender: 'Male', department: 'Neurology', doctor: 'Dr. Gupta', room: 'ICU-02', bed: 'ICU-02-A', priority: 'CRITICAL', admissionDate: '2026-09-23', status: 'In Surgery', bloodGroup: 'A-', contact: '+91-9123456789', diagnosis: 'Ischemic Stroke', insurance: 'None', vitals: { bp: '180/110', pulse: 95, temp: 100.4, spo2: 91 } },
  { id: 'P-004', name: 'Sunita Devi', age: 67, gender: 'Female', department: 'General Medicine', doctor: 'Dr. Verma', room: 'C-302', bed: 'C302-B', priority: 'HIGH', admissionDate: '2026-09-21', status: 'Under Observation', bloodGroup: 'AB+', contact: '+91-8765432109', diagnosis: 'Type 2 Diabetes Complications', insurance: 'PMJAY', vitals: { bp: '145/95', pulse: 88, temp: 99.8, spo2: 96 } },
  { id: 'P-005', name: 'Mohammed Ali', age: 24, gender: 'Male', department: 'Emergency', doctor: 'Dr. Khan', room: 'E-01', bed: 'E01-C', priority: 'CRITICAL', admissionDate: '2026-09-24', status: 'Critical', bloodGroup: 'O-', contact: '+91-7654321098', diagnosis: 'Polytrauma - RTA', insurance: 'None', vitals: { bp: '90/60', pulse: 120, temp: 97.8, spo2: 89 } },
  { id: 'P-006', name: 'Kavitha Nair', age: 38, gender: 'Female', department: 'Orthopedics', doctor: 'Dr. Pillai', room: 'D-201', bed: 'D201-A', priority: 'NORMAL', admissionDate: '2026-09-19', status: 'Admitted', bloodGroup: 'A+', contact: '+91-6543210987', diagnosis: 'Femur Fracture - Post Op', insurance: 'ESIC', vitals: { bp: '125/82', pulse: 76, temp: 98.4, spo2: 98 } },
  { id: 'P-007', name: 'Suresh Reddy', age: 52, gender: 'Male', department: 'Cardiology', doctor: 'Dr. Sharma', room: 'A-210', bed: 'A210-A', priority: 'HIGH', admissionDate: '2026-09-22', status: 'Under Observation', bloodGroup: 'B-', contact: '+91-5432109876', diagnosis: 'Unstable Angina', insurance: 'Mediclaim', vitals: { bp: '148/92', pulse: 96, temp: 98.9, spo2: 95 } },
  { id: 'P-008', name: 'Ananya Singh', age: 7, gender: 'Female', department: 'Pediatrics', doctor: 'Dr. Bose', room: 'P-105', bed: 'P105-B', priority: 'NORMAL', admissionDate: '2026-09-23', status: 'Admitted', bloodGroup: 'O+', contact: '+91-4321098765', diagnosis: 'Severe Pneumonia', insurance: 'PMJAY', vitals: { bp: '95/65', pulse: 110, temp: 102.2, spo2: 97 } },
  { id: 'P-009', name: 'Vikram Joshi', age: 71, gender: 'Male', department: 'Urology', doctor: 'Dr. Mehta', room: 'C-401', bed: 'C401-A', priority: 'NORMAL', admissionDate: '2026-09-20', status: 'Admitted', bloodGroup: 'AB-', contact: '+91-3210987654', diagnosis: 'Benign Prostatic Hyperplasia', insurance: 'Senior Citizen', vitals: { bp: '130/85', pulse: 74, temp: 98.2, spo2: 99 } },
  { id: 'P-010', name: 'Meena Krishnan', age: 29, gender: 'Female', department: 'Surgery', doctor: 'Dr. Rao', room: 'S-301', bed: 'S301-C', priority: 'HIGH', admissionDate: '2026-09-24', status: 'In Surgery', bloodGroup: 'B+', contact: '+91-2109876543', diagnosis: 'Acute Appendicitis', insurance: 'CGHS', vitals: { bp: '118/76', pulse: 98, temp: 101.0, spo2: 97 } },
  { id: 'P-011', name: 'Rajan Trivedi', age: 63, gender: 'Male', department: 'Pulmonology', doctor: 'Dr. Chandra', room: 'B-308', bed: 'B308-B', priority: 'HIGH', admissionDate: '2026-09-21', status: 'Under Observation', bloodGroup: 'A+', contact: '+91-9876512345', diagnosis: 'COPD Exacerbation', insurance: 'None', vitals: { bp: '138/88', pulse: 92, temp: 99.5, spo2: 91 } },
  { id: 'P-012', name: 'Fatima Begum', age: 44, gender: 'Female', department: 'Endocrinology', doctor: 'Dr. Shah', room: 'C-205', bed: 'C205-A', priority: 'NORMAL', admissionDate: '2026-09-22', status: 'Admitted', bloodGroup: 'O+', contact: '+91-8765123456', diagnosis: 'Thyroid Storm', insurance: 'ESIC', vitals: { bp: '126/80', pulse: 85, temp: 98.7, spo2: 98 } },
];

// ─── Beds ───────────────────────────────────────────────────────────────────
export const mockBeds: Bed[] = [
  // General Ward A
  { id: 'A101', ward: 'Ward A', room: 'A-101', type: 'General', status: 'Available' },
  { id: 'A102', ward: 'Ward A', room: 'A-102', type: 'General', status: 'Occupied', patient: 'John Smith', admittedDate: '2026-09-20' },
  { id: 'A103', ward: 'Ward A', room: 'A-103', type: 'General', status: 'Cleaning' },
  { id: 'A104', ward: 'Ward A', room: 'A-104', type: 'General', status: 'Available' },
  { id: 'A105', ward: 'Ward A', room: 'A-105', type: 'General', status: 'Occupied', patient: 'Mary Davis', admittedDate: '2026-09-22' },
  { id: 'A106', ward: 'Ward A', room: 'A-106', type: 'General', status: 'Reserved' },
  { id: 'A107', ward: 'Ward A', room: 'A-107', type: 'General', status: 'Maintenance' },
  { id: 'A108', ward: 'Ward A', room: 'A-108', type: 'General', status: 'Available' },
  // Ward B
  { id: 'B101', ward: 'Ward B', room: 'B-101', type: 'General', status: 'Occupied', patient: 'Priya Sharma', admittedDate: '2026-09-22' },
  { id: 'B102', ward: 'Ward B', room: 'B-102', type: 'General', status: 'Available' },
  { id: 'B103', ward: 'Ward B', room: 'B-103', type: 'General', status: 'Occupied', patient: 'Robert Wilson', admittedDate: '2026-09-21' },
  { id: 'B104', ward: 'Ward B', room: 'B-104', type: 'General', status: 'Cleaning' },
  { id: 'B105', ward: 'Ward B', room: 'B-105', type: 'General', status: 'Available' },
  { id: 'B106', ward: 'Ward B', room: 'B-106', type: 'General', status: 'Reserved' },
  // ICU
  { id: 'ICU01', ward: 'ICU', room: 'ICU-01', type: 'ICU', status: 'Occupied', patient: 'Rajesh Kumar', admittedDate: '2026-09-20' },
  { id: 'ICU02', ward: 'ICU', room: 'ICU-02', type: 'ICU', status: 'Occupied', patient: 'Amit Patel', admittedDate: '2026-09-23' },
  { id: 'ICU03', ward: 'ICU', room: 'ICU-03', type: 'ICU', status: 'Available' },
  { id: 'ICU04', ward: 'ICU', room: 'ICU-04', type: 'ICU', status: 'Available' },
  { id: 'ICU05', ward: 'ICU', room: 'ICU-05', type: 'ICU', status: 'Reserved' },
  // Emergency
  { id: 'E01', ward: 'Emergency', room: 'E-01', type: 'Emergency', status: 'Occupied', patient: 'Mohammed Ali', admittedDate: '2026-09-24' },
  { id: 'E02', ward: 'Emergency', room: 'E-02', type: 'Emergency', status: 'Emergency' },
  { id: 'E03', ward: 'Emergency', room: 'E-03', type: 'Emergency', status: 'Available' },
  { id: 'E04', ward: 'Emergency', room: 'E-04', type: 'Emergency', status: 'Occupied', patient: 'Sanjay Mehta', admittedDate: '2026-09-24' },
  // Surgical
  { id: 'S301', ward: 'Surgical', room: 'S-301', type: 'Surgical', status: 'Occupied', patient: 'Meena Krishnan', admittedDate: '2026-09-24' },
  { id: 'S302', ward: 'Surgical', room: 'S-302', type: 'Surgical', status: 'Available' },
  { id: 'S303', ward: 'Surgical', room: 'S-303', type: 'Surgical', status: 'Cleaning' },
  // Pediatric
  { id: 'P101', ward: 'Pediatric', room: 'P-101', type: 'Pediatric', status: 'Available' },
  { id: 'P102', ward: 'Pediatric', room: 'P-102', type: 'Pediatric', status: 'Occupied', patient: 'Ananya Singh', admittedDate: '2026-09-23' },
  { id: 'P103', ward: 'Pediatric', room: 'P-103', type: 'Pediatric', status: 'Available' },
];

// ─── Medicines ───────────────────────────────────────────────────────────────
export const mockMedicines: Medicine[] = [
  { id: 'MED-001', name: 'Paracetamol 500mg', category: 'Analgesics', quantity: 850, maxQuantity: 1000, unit: 'Tablets', minStock: 200, expiryDate: '2027-08-30', supplier: 'Sun Pharma', status: 'IN STOCK', price: 2.5 },
  { id: 'MED-002', name: 'Amoxicillin 500mg', category: 'Antibiotics', quantity: 12, maxQuantity: 500, unit: 'Capsules', minStock: 100, expiryDate: '2027-03-15', supplier: 'Cipla', status: 'LOW STOCK', price: 8.0 },
  { id: 'MED-003', name: 'Insulin Glargine', category: 'Endocrine', quantity: 0, maxQuantity: 200, unit: 'Vials', minStock: 50, expiryDate: '2026-12-01', supplier: 'Novo Nordisk', status: 'OUT OF STOCK', price: 450.0 },
  { id: 'MED-004', name: 'Ceftriaxone 1g', category: 'Antibiotics', quantity: 85, maxQuantity: 300, unit: 'Vials', minStock: 60, expiryDate: '2026-10-08', supplier: 'Pfizer', status: 'EXPIRING SOON', price: 120.0 },
  { id: 'MED-005', name: 'Metformin 500mg', category: 'Antidiabetics', quantity: 620, maxQuantity: 800, unit: 'Tablets', minStock: 150, expiryDate: '2027-06-20', supplier: 'Sun Pharma', status: 'IN STOCK', price: 3.0 },
  { id: 'MED-006', name: 'Atorvastatin 40mg', category: 'Cardiovascular', quantity: 45, maxQuantity: 400, unit: 'Tablets', minStock: 80, expiryDate: '2027-04-10', supplier: 'Ranbaxy', status: 'LOW STOCK', price: 12.0 },
  { id: 'MED-007', name: 'Omeprazole 20mg', category: 'Gastrointestinal', quantity: 730, maxQuantity: 900, unit: 'Capsules', minStock: 180, expiryDate: '2027-09-15', supplier: 'Cipla', status: 'IN STOCK', price: 4.5 },
  { id: 'MED-008', name: 'Amlodipine 5mg', category: 'Cardiovascular', quantity: 0, maxQuantity: 500, unit: 'Tablets', minStock: 100, expiryDate: '2027-05-22', supplier: 'Torrent', status: 'OUT OF STOCK', price: 6.0 },
  { id: 'MED-009', name: 'Dexamethasone 4mg', category: 'Corticosteroids', quantity: 220, maxQuantity: 400, unit: 'Ampoules', minStock: 80, expiryDate: '2026-10-20', supplier: 'Mylan', status: 'EXPIRING SOON', price: 35.0 },
  { id: 'MED-010', name: 'Heparin 5000IU', category: 'Anticoagulants', quantity: 160, maxQuantity: 250, unit: 'Vials', minStock: 50, expiryDate: '2027-02-14', supplier: 'Leo Pharma', status: 'IN STOCK', price: 280.0 },
  { id: 'MED-011', name: 'Morphine 10mg', category: 'Opioids', quantity: 22, maxQuantity: 100, unit: 'Ampoules', minStock: 30, expiryDate: '2027-01-30', supplier: 'Neon Labs', status: 'LOW STOCK', price: 95.0 },
  { id: 'MED-012', name: 'Salbutamol 100mcg', category: 'Bronchodilators', quantity: 380, maxQuantity: 500, unit: 'Inhalers', minStock: 100, expiryDate: '2027-07-12', supplier: 'GSK', status: 'IN STOCK', price: 68.0 },
  { id: 'MED-013', name: 'Vancomycin 500mg', category: 'Antibiotics', quantity: 8, maxQuantity: 150, unit: 'Vials', minStock: 30, expiryDate: '2027-04-18', supplier: 'Fresenius', status: 'LOW STOCK', price: 520.0 },
  { id: 'MED-014', name: 'Furosemide 40mg', category: 'Diuretics', quantity: 540, maxQuantity: 700, unit: 'Tablets', minStock: 140, expiryDate: '2027-08-05', supplier: 'Abbott', status: 'IN STOCK', price: 5.5 },
  { id: 'MED-015', name: 'Midazolam 5mg', category: 'Sedatives', quantity: 55, maxQuantity: 200, unit: 'Ampoules', minStock: 40, expiryDate: '2026-10-15', supplier: 'Roche', status: 'EXPIRING SOON', price: 180.0 },
];

// ─── Inventory ───────────────────────────────────────────────────────────────
export const mockInventory: InventoryItem[] = [
  { id: 'INV-001', name: 'Surgical Gloves (L)', category: 'PPE', quantity: 850, minQuantity: 500, status: 'In Stock', location: 'Store A', lastUpdated: '2026-09-22' },
  { id: 'INV-002', name: 'N95 Masks', category: 'PPE', quantity: 120, minQuantity: 300, status: 'Low Stock', location: 'Store A', lastUpdated: '2026-09-23' },
  { id: 'INV-003', name: 'Oxygen Cylinders (B)', category: 'Medical Gas', quantity: 18, minQuantity: 30, status: 'Low Stock', location: 'Gas Store', lastUpdated: '2026-09-24' },
  { id: 'INV-004', name: 'IV Cannula 18G', category: 'Surgical Equipment', quantity: 620, minQuantity: 200, status: 'In Stock', location: 'Store B', lastUpdated: '2026-09-21' },
  { id: 'INV-005', name: 'Ventilator Units', category: 'Equipment', quantity: 2, minQuantity: 5, status: 'Critical Stock', location: 'ICU Store', lastUpdated: '2026-09-24' },
  { id: 'INV-006', name: 'Wheelchair', category: 'Mobility', quantity: 15, minQuantity: 10, status: 'In Stock', location: 'Ward Store', lastUpdated: '2026-09-20' },
  { id: 'INV-007', name: 'Pulse Oximeter', category: 'Monitors', quantity: 28, minQuantity: 20, status: 'In Stock', location: 'Equipment Room', lastUpdated: '2026-09-22' },
  { id: 'INV-008', name: 'Blood Glucose Strips', category: 'Lab Supplies', quantity: 0, minQuantity: 200, status: 'Out of Stock', location: 'Lab Store', lastUpdated: '2026-09-24' },
  { id: 'INV-009', name: 'Sterile Drapes', category: 'Surgical Equipment', quantity: 340, minQuantity: 100, status: 'In Stock', location: 'OT Store', lastUpdated: '2026-09-21' },
  { id: 'INV-010', name: 'ECG Electrodes', category: 'Lab Supplies', quantity: 45, minQuantity: 100, status: 'Low Stock', location: 'Cardiology Store', lastUpdated: '2026-09-23' },
  { id: 'INV-011', name: 'Foley Catheter 16Fr', category: 'Surgical Equipment', quantity: 180, minQuantity: 80, status: 'In Stock', location: 'Store B', lastUpdated: '2026-09-20' },
  { id: 'INV-012', name: 'Disinfectant (5L)', category: 'Cleaning Supplies', quantity: 62, minQuantity: 40, status: 'In Stock', location: 'Housekeeping', lastUpdated: '2026-09-22' },
];

// ─── Ambulances ───────────────────────────────────────────────────────────────
export const mockAmbulances: Ambulance[] = [
  { id: 'AMB-001', regNumber: 'MH-01-1001', status: 'Available', driver: 'Ravi Kumar', contact: '+91-9876501234', location: 'Main Gate', lastService: '2026-09-10' },
  { id: 'AMB-002', regNumber: 'MH-01-1002', status: 'On Mission', driver: 'Sunil Das', contact: '+91-9876502345', location: 'Ring Road, Sector 5', destination: 'St. Mary Hospital', eta: '14 min', lastService: '2026-09-08' },
  { id: 'AMB-003', regNumber: 'MH-01-1003', status: 'Returning', driver: 'Arjun Yadav', contact: '+91-9876503456', location: 'Highway NH-8, KM 12', destination: 'City Hospital', eta: '22 min', lastService: '2026-09-12' },
  { id: 'AMB-004', regNumber: 'MH-01-1004', status: 'Available', driver: 'Mahesh Tiwari', contact: '+91-9876504567', location: 'Emergency Bay', lastService: '2026-09-15' },
  { id: 'AMB-005', regNumber: 'MH-01-1005', status: 'Available', driver: 'Dilip Sharma', contact: '+91-9876505678', location: 'Parking Area B', lastService: '2026-09-09' },
  { id: 'AMB-006', regNumber: 'MH-01-1006', status: 'Maintenance', driver: 'Sanjay Patil', contact: '+91-9876506789', location: 'Garage', lastService: '2026-09-01' },
  { id: 'AMB-007', regNumber: 'MH-01-1007', status: 'Available', driver: 'Vinod Nair', contact: '+91-9876507890', location: 'Main Gate', lastService: '2026-09-18' },
  { id: 'AMB-008', regNumber: 'MH-01-1008', status: 'On Mission', driver: 'Prakash Reddy', contact: '+91-9876508901', location: 'Airport Road', destination: 'Trauma Center', eta: '8 min', lastService: '2026-09-14' },
  { id: 'AMB-009', regNumber: 'MH-01-1009', status: 'Available', driver: 'Ganesh Pillai', contact: '+91-9876509012', location: 'Emergency Bay', lastService: '2026-09-20' },
  { id: 'AMB-010', regNumber: 'MH-01-1010', status: 'Available', driver: 'Rajiv Sinha', contact: '+91-9876510123', location: 'Main Gate', lastService: '2026-09-17' },
];

// ─── Emergency Alerts ───────────────────────────────────────────────────────
export const mockAlerts: EmergencyAlert[] = [
  { id: 'ALT-001', type: 'Critical Patient', severity: 'critical', time: '14:32', description: 'Patient John Doe arrived in critical condition — Polytrauma', location: 'Emergency Bay', acknowledged: false },
  { id: 'ALT-002', type: 'Code Blue', severity: 'critical', time: '14:15', description: 'Cardiac arrest reported in Ward A, Bed A-204', location: 'Ward A - Room 204', acknowledged: false },
  { id: 'ALT-003', type: 'ICU Bed Shortage', severity: 'high', time: '13:55', description: 'Only 2 ICU beds remaining. 4 patients waiting for ICU admission.', location: 'ICU Unit', acknowledged: false },
  { id: 'ALT-004', type: 'Low Medicine Stock', severity: 'high', time: '13:30', description: 'Amoxicillin critically low — only 12 units remaining (threshold: 100)', location: 'Pharmacy', acknowledged: true },
  { id: 'ALT-005', type: 'Ambulance Arrival', severity: 'medium', time: '14:28', description: 'AMB-003 returning with critical patient. ETA 22 minutes.', location: 'Main Entrance', acknowledged: true },
  { id: 'ALT-006', type: 'Blood Bank Alert', severity: 'high', time: '12:45', description: 'O-negative blood units critically low — only 3 units remaining', location: 'Blood Bank', acknowledged: false },
  { id: 'ALT-007', type: 'Equipment Failure', severity: 'high', time: '12:20', description: 'Ventilator Unit #3 in ICU has malfunctioned. Maintenance notified.', location: 'ICU - Bed ICU-03', acknowledged: true },
  { id: 'ALT-008', type: 'Doctor Required', severity: 'medium', time: '11:50', description: 'Cardiologist required for consultation in Emergency — Patient P-007', location: 'Emergency Room', acknowledged: false },
];

// ─── Notifications ───────────────────────────────────────────────────────────
export const mockNotifications: Notification[] = [
  { id: 'NTF-001', category: 'Emergency', title: 'Critical Patient Admitted', message: 'Mohammed Ali admitted with Polytrauma - RTA. Priority: CRITICAL.', time: '14:32', read: false, severity: 'critical' },
  { id: 'NTF-002', category: 'Emergency', title: 'Code Blue Alert', message: 'Code Blue in Ward A Room 204. Crash team dispatched.', time: '14:15', read: false, severity: 'critical' },
  { id: 'NTF-003', category: 'Beds', title: 'ICU Capacity Warning', message: 'ICU at 83% capacity. 2 beds remaining. Request bed management review.', time: '13:55', read: false, severity: 'high' },
  { id: 'NTF-004', category: 'Pharmacy', title: 'Low Stock: Amoxicillin', message: 'Amoxicillin stock below minimum threshold (12/100). Reorder required.', time: '13:30', read: false, severity: 'high' },
  { id: 'NTF-005', category: 'Pharmacy', title: 'Out of Stock: Insulin Glargine', message: 'Insulin Glargine is completely out of stock. Immediate procurement needed.', time: '12:50', read: true, severity: 'critical' },
  { id: 'NTF-006', category: 'Appointments', title: 'Appointment Reminder', message: '17 pending appointments scheduled for today. 3 are overdue.', time: '12:00', read: true, severity: 'medium' },
  { id: 'NTF-007', category: 'Staff', title: 'Doctor On-Call Report', message: 'Dr. Gupta (Neurology) reports for emergency duty at 14:00.', time: '11:45', read: true, severity: 'low' },
  { id: 'NTF-008', category: 'Inventory', title: 'PPE Stock Low', message: 'N95 Masks at 40% of minimum threshold (120/300 required).', time: '11:20', read: true, severity: 'high' },
  { id: 'NTF-009', category: 'Patients', title: 'Discharge Approved', message: 'Patient Kavitha Nair (P-006) cleared for discharge by Dr. Pillai.', time: '10:55', read: true, severity: 'low' },
  { id: 'NTF-010', category: 'Emergency', title: 'Blood Bank Alert', message: 'O-negative blood group critically low — 3 units available.', time: '12:45', read: false, severity: 'high' },
  { id: 'NTF-011', category: 'Beds', title: 'Bed Status Updated', message: 'Beds A103, B104 moved to "Cleaning" status after discharge.', time: '10:30', read: true, severity: 'low' },
  { id: 'NTF-012', category: 'Staff', title: 'Nurse Shift Change', message: 'Night shift nurses (42) have checked in. Morning shift handover complete.', time: '08:00', read: true, severity: 'low' },
];

// ─── Departments ───────────────────────────────────────────────────────────
export const mockDepartments: Department[] = [
  { id: 'DEPT-001', name: 'Emergency', icon: '🚨', patients: 12, doctors: 6, nurses: 18, availableBeds: 2, totalBeds: 8, status: 'Critical', head: 'Dr. Khan', color: 'red' },
  { id: 'DEPT-002', name: 'ICU', icon: '🏥', patients: 10, doctors: 4, nurses: 16, availableBeds: 2, totalBeds: 12, status: 'Busy', head: 'Dr. Verma', color: 'orange' },
  { id: 'DEPT-003', name: 'Cardiology', icon: '❤️', patients: 18, doctors: 5, nurses: 12, availableBeds: 8, totalBeds: 20, status: 'Normal', head: 'Dr. Sharma', color: 'pink' },
  { id: 'DEPT-004', name: 'Neurology', icon: '🧠', patients: 14, doctors: 4, nurses: 10, availableBeds: 6, totalBeds: 18, status: 'Normal', head: 'Dr. Gupta', color: 'purple' },
  { id: 'DEPT-005', name: 'Pediatrics', icon: '👶', patients: 22, doctors: 5, nurses: 14, availableBeds: 10, totalBeds: 25, status: 'Normal', head: 'Dr. Bose', color: 'blue' },
  { id: 'DEPT-006', name: 'Orthopedics', icon: '🦴', patients: 16, doctors: 4, nurses: 8, availableBeds: 12, totalBeds: 20, status: 'Normal', head: 'Dr. Pillai', color: 'amber' },
  { id: 'DEPT-007', name: 'General Medicine', icon: '💊', patients: 30, doctors: 8, nurses: 20, availableBeds: 5, totalBeds: 30, status: 'Busy', head: 'Dr. Mehta', color: 'teal' },
  { id: 'DEPT-008', name: 'Surgery', icon: '🔬', patients: 8, doctors: 6, nurses: 12, availableBeds: 4, totalBeds: 15, status: 'Normal', head: 'Dr. Rao', color: 'indigo' },
  { id: 'DEPT-009', name: 'Radiology', icon: '📷', patients: 0, doctors: 3, nurses: 4, availableBeds: 0, totalBeds: 0, status: 'Normal', head: 'Dr. Jain', color: 'cyan' },
  { id: 'DEPT-010', name: 'Laboratory', icon: '🧪', patients: 0, doctors: 2, nurses: 6, availableBeds: 0, totalBeds: 0, status: 'Normal', head: 'Dr. Singh', color: 'green' },
  { id: 'DEPT-011', name: 'Pharmacy', icon: '💉', patients: 0, doctors: 2, nurses: 4, availableBeds: 0, totalBeds: 0, status: 'Normal', head: 'Dr. Shah', color: 'violet' },
];

// ─── Dashboard Stats ───────────────────────────────────────────────────────
export const dashboardStats = {
  totalPatients: 1248,
  patientTrend: 12.4,
  emergencyPatients: 23,
  totalBeds: 120,
  occupiedBeds: 72,
  availableBeds: 48,
  reservedBeds: 10,
  icuBeds: 12,
  icuOccupied: 10,
  emergencyBeds: 8,
  emergencyOccupied: 6,
  ventilatorBeds: 5,
  ventilatorOccupied: 4,
  doctorsOnDuty: 36,
  nursesOnDuty: 84,
  pendingAppointments: 17,
  ambulancesAvailable: 6,
  ambulancesOnMission: 3,
  ambulancesMaintenance: 1,
  medicineAlerts: 12,
  totalMedicines: 1845,
  lowStock: 24,
  outOfStock: 7,
  expiringSoon: 18,
};

// ─── Chart Data ───────────────────────────────────────────────────────────
export const weeklyPatientData = {
  labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
  admissions: [42, 55, 38, 61, 48, 35, 28],
  discharges: [35, 48, 41, 52, 44, 30, 22],
  emergency: [12, 18, 9, 22, 15, 8, 11],
};

export const bedOccupancyData = {
  labels: ['General', 'ICU', 'Emergency', 'Surgical', 'Pediatric', 'Maternity'],
  occupied: [45, 10, 6, 8, 14, 6],
  total: [60, 12, 8, 12, 18, 10],
};

export const departmentPerformanceData = {
  labels: ['Emergency', 'ICU', 'Cardiology', 'Neurology', 'Pediatrics', 'Surgery'],
  patientLoad: [90, 83, 72, 65, 68, 58],
};
