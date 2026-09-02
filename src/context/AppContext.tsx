import React, { createContext, useContext, useState } from 'react';
import type { UserRole, PatientProfile, Medication, AlertItem, CheckupSubmission, ClinicalNote, TriageStatus } from '../types';
import { mockPatients, mockMedications, mockAlerts, mockClinicalNotes, mockCheckupHistory } from '../data/mockData';

interface AppContextType {
  role: UserRole;
  setRole: (role: UserRole) => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  patientsList: PatientProfile[];
  selectedPatientId: string;
  setSelectedPatientId: (id: string) => void;
  currentPatient: PatientProfile;
  medications: Medication[];
  toggleMedicationStatus: (id: string, status: 'taken' | 'pending' | 'missed') => void;
  alerts: AlertItem[];
  acknowledgeAlert: (id: string) => void;
  escalateAlert: (id: string, reason?: string) => void;
  triggerSimulatedFall: () => void;
  emergencyModalOpen: boolean;
  setEmergencyModalOpen: (open: boolean) => void;
  assistantModalOpen: boolean;
  setAssistantModalOpen: (open: boolean) => void;
  checkupSubmissions: CheckupSubmission[];
  addCheckupSubmission: (sub: CheckupSubmission) => void;
  clinicalNotes: ClinicalNote[];
  addClinicalNote: (note: ClinicalNote) => void;
  unreadAlertCount: number;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [role, setRoleState] = useState<UserRole>('landing');
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [patientsList, setPatientsList] = useState<PatientProfile[]>(mockPatients);
  const [selectedPatientId, setSelectedPatientId] = useState<string>('P-101');
  const [medications, setMedications] = useState<Medication[]>(mockMedications);
  const [alerts, setAlerts] = useState<AlertItem[]>(mockAlerts);
  const [emergencyModalOpen, setEmergencyModalOpen] = useState<boolean>(false);
  const [assistantModalOpen, setAssistantModalOpen] = useState<boolean>(false);
  const [checkupSubmissions, setCheckupSubmissions] = useState<CheckupSubmission[]>(mockCheckupHistory);
  const [clinicalNotes, setClinicalNotes] = useState<ClinicalNote[]>(mockClinicalNotes);


  const currentPatient = patientsList.find((p) => p.id === selectedPatientId) || patientsList[0];

  const setRole = (newRole: UserRole) => {
    setRoleState(newRole);
    if (newRole === 'patient') setActiveTab('dashboard');
    else if (newRole === 'doctor') setActiveTab('doctor_dashboard');
    else if (newRole === 'caregiver') setActiveTab('caregiver_dashboard');
    else if (newRole === 'admin') setActiveTab('admin_dashboard');
    else if (newRole === 'landing') setActiveTab('home');
  };

  const toggleMedicationStatus = (id: string, status: 'taken' | 'pending' | 'missed') => {
    setMedications((prev) =>
      prev.map((m) => (m.id === id ? { ...m, status } : m))
    );
  };

  const acknowledgeAlert = (id: string) => {
    setAlerts((prev) =>
      prev.map((a) =>
        a.id === id
          ? {
              ...a,
              acknowledged: true,
              acknowledgedBy: role.toUpperCase(),
              caregiverStatus: 'checking',
            }
          : a
      )
    );

    // Call backend API if running
    fetch(`http://localhost:5000/api/alerts/${id}/acknowledge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'checking' }),
    }).catch(() => {});
  };

  const escalateAlert = (id: string, reason: string = 'Caregiver requested emergency medical response') => {
    setAlerts((prev) =>
      prev.map((a) =>
        a.id === id
          ? {
              ...a,
              caregiverStatus: 'escalated',
            }
          : a
      )
    );

    // Call backend API if running
    fetch(`http://localhost:5000/api/alerts/${id}/escalate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reason }),
    }).catch(() => {});
  };

  const triggerSimulatedFall = () => {
    const newFallAlert: AlertItem = {
      id: `ALT-${Date.now().toString().slice(-4)}`,
      patientId: currentPatient.id,
      patientName: currentPatient.name,
      title: 'CRITICAL INCIDENT - Confirmed Fall Detected',
      message: 'AI camera edge sensor confirmed sudden posture drop near bedroom doorway. Emergency dispatch initiated.',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      timestamp: new Date().toISOString(),
      severity: 'critical',
      acknowledged: false,
      caregiverStatus: 'pending',
      screenshotUrl: 'http://localhost:5000/static/screenshots/fall_P101_sample.jpg',
      ntfyStatus: 'delivered',
      type: 'fall',
    };
    setAlerts((prev) => [newFallAlert, ...prev]);

    setPatientsList((prev) =>
      prev.map((p) =>
        p.id === currentPatient.id
          ? {
              ...p,
              status: 'critical' as TriageStatus,
              lastActivity: 'Confirmed Fall Detected – Just now',
              lastUpdate: 'Just now',
            }
          : p
      )
    );

    // Trigger backend notification with screenshot if backend is running
    fetch('http://localhost:5000/api/camera/simulate-fall', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        patient_id: currentPatient.id,
        event_type: 'CONFIRMED_FALL',
        risk_level: 'critical',
      }),
    }).catch(() => {});
  };

  const addCheckupSubmission = (sub: CheckupSubmission) => {
    setCheckupSubmissions((prev) => [sub, ...prev]);
    setPatientsList((prev) =>
      prev.map((p) =>
        p.id === currentPatient.id
          ? {
              ...p,
              status: sub.resultStatus,
              lastUpdate: 'Just now',
              vitals: {
                ...p.vitals,
                temperature: sub.temperature,
                bpSystolic: sub.systolicBp,
                bpDiastolic: sub.diastolicBp,
                heartRate: sub.heartRate,
                spO2: sub.spO2,
                painLevel: sub.painLevel,
                mobility: sub.mobility,
              },
            }
          : p
      )
    );
  };

  const addClinicalNote = (note: ClinicalNote) => {
    setClinicalNotes((prev) => [note, ...prev]);
  };

  const unreadAlertCount = alerts.filter((a) => !a.acknowledged && a.severity === 'critical').length;

  return (
    <AppContext.Provider
      value={{
        role,
        setRole,
        activeTab,
        setActiveTab,
        patientsList,
        selectedPatientId,
        setSelectedPatientId,
        currentPatient,
        medications,
        toggleMedicationStatus,
        alerts,
        acknowledgeAlert,
        escalateAlert,
        triggerSimulatedFall,
        emergencyModalOpen,
        setEmergencyModalOpen,
        assistantModalOpen,
        setAssistantModalOpen,
        checkupSubmissions,
        addCheckupSubmission,
        clinicalNotes,
        addClinicalNote,
        unreadAlertCount,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
