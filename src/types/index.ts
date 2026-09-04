export type UserRole = 'landing' | 'patient' | 'doctor' | 'caregiver' | 'admin';

export type TriageStatus = 'stable' | 'attention' | 'doctor_review' | 'critical';

export interface VitalMetric {
  name: string;
  value: string | number;
  unit: string;
  status: 'normal' | 'warning' | 'critical';
  trend: 'up' | 'down' | 'stable';
  idealRange: string;
  iconName: string;
}

export interface Medication {
  id: string;
  name: string;
  dosage: string;
  scheduledTime: string;
  timing: 'Before food' | 'After food' | 'With food';
  durationDays: number;
  startDate: string;
  endDate: string;
  instructions: string;
  status: 'taken' | 'pending' | 'missed';
  prescribedBy: string;
}

export interface CameraEvent {
  id: string;
  time: string;
  activity: 'Walking' | 'Sitting' | 'Standing' | 'Bed Exit' | 'Possible Fall' | 'Confirmed Fall' | 'Prolonged Inactivity';
  confidence?: number;
  severity: 'info' | 'warning' | 'critical';
  details?: string;
}

export interface AlertItem {
  id: string;
  patientId: string;
  patientName: string;
  title: string;
  message: string;
  time: string;
  timestamp: string;
  severity: TriageStatus;
  acknowledged: boolean;
  acknowledgedBy?: string;
  type: 'fall' | 'vitals' | 'medication' | 'pain' | 'checkup';
  eventType?: string;
  riskLevel?: string;
  screenshotUrl?: string;
  ntfyStatus?: string;
  caregiverStatus?: string;
  caregiverPhone?: string;
}

export interface CheckupSubmission {
  id: string;
  date: string;
  temperature: number;
  systolicBp: number;
  diastolicBp: number;
  heartRate: number;
  spO2: number;
  painLevel: number;
  mobility: string;
  symptoms: string[];
  notes: string;
  resultStatus: TriageStatus;
  triageReasoning: string;
}

export interface PatientProfile {
  id: string;
  name: string;
  age: number;
  gender: string;
  surgeryType: string;
  surgeryDate: string;
  dischargeDate: string;
  recoveryDay: number;
  targetRecoveryDays: number;
  roomNumber: string;
  doctorName: string;
  caregiverName: string;
  status: TriageStatus;
  medicationAdherence: number; // percentage
  vitals: {
    temperature: number;
    bpSystolic: number;
    bpDiastolic: number;
    heartRate: number;
    spO2: number;
    painLevel: number;
    mobility: string;
  };
  lastActivity: string;
  lastUpdate: string;
  allergies: string[];
  emergencyContact: {
    name: string;
    relation: string;
    phone: string;
  };
}

export interface ClinicalNote {
  id: string;
  patientId: string;
  doctorName: string;
  date: string;
  time: string;
  note: string;
  category: 'Observation' | 'Prescription Change' | 'Discharge Plan' | 'General';
}

export interface PhysioExerciseState {
  exercise: string;
  exercise_name: string;
  target_joint: string;
  side: string;
  is_tracking: boolean;
  current_angle: number;
  start_angle: number;
  target_angle: number;
  rep_count: number;
  target_reps: number;
  state: string;
  feedback: string;
  progress_pct: number;
  disclaimer: string;
}

export interface Appointment {
  id: string;
  patientId: string;
  patientName: string;
  doctorId: string;
  doctorName: string;
  specialty: string;
  hospital: string;
  distanceKm?: number;
  date: string;
  time: string;
  status: 'confirmed' | 'rescheduled' | 'cancelled' | 'completed';
  type: 'in_person' | 'video_consultation';
  reason: string;
  createdAt?: string;
}

export interface AssistantMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  language: 'en' | 'hi';
  isEmergency?: boolean;
  timestamp: string;
  actionType?: 'slots_list' | 'doctor_list' | 'appointment_card' | 'confirm_booking' | 'confirm_cancel' | 'upcoming_list';
  actionData?: any;
  quickReplies?: string[];
}

declare global {
  interface Window {
    google?: any;
  }
}


