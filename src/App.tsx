import React from 'react';
import { AppProvider, useApp } from './context/AppContext';
import { Layout } from './components/layout/Layout';

// Public Pages
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';

// Patient Pages
import { PatientDashboard } from './pages/patient/PatientDashboard';
import { MyRecoveryPage } from './pages/patient/MyRecoveryPage';
import { DailyHealthCheckPage } from './pages/patient/DailyHealthCheckPage';
import { PrescriptionPage } from './pages/patient/PrescriptionPage';
import { MedicationPage } from './pages/patient/MedicationPage';
import { RecoveryTimelinePage } from './pages/patient/RecoveryTimelinePage';
import { CameraMonitoringPage } from './pages/patient/CameraMonitoringPage';
import { AlertsPage } from './pages/patient/AlertsPage';
import { ProfilePage } from './pages/patient/ProfilePage';
import { EmergencyHelpPage } from './pages/patient/EmergencyHelpPage';

// Doctor Pages
import { DoctorDashboard } from './pages/doctor/DoctorDashboard';
import { PatientDetailPage } from './pages/doctor/PatientDetailPage';

// Caregiver Pages
import { CaregiverDashboard } from './pages/caregiver/CaregiverDashboard';

// Admin Pages
import { AdminDashboard } from './pages/admin/AdminDashboard';

const MainContent: React.FC = () => {
  const { role, activeTab } = useApp();

  if (role === 'landing') {
    if (activeTab === 'login') return <LoginPage />;
    if (activeTab === 'register') return <RegisterPage />;
    return <LandingPage />;
  }

  // Patient Views
  if (role === 'patient') {
    switch (activeTab) {
      case 'dashboard':
        return <PatientDashboard />;
      case 'recovery':
        return <MyRecoveryPage />;
      case 'checkup':
        return <DailyHealthCheckPage />;
      case 'prescription':
        return <PrescriptionPage />;
      case 'medications':
        return <MedicationPage />;
      case 'timeline':
        return <RecoveryTimelinePage />;
      case 'camera':
        return <CameraMonitoringPage />;
      case 'alerts':
        return <AlertsPage />;
      case 'profile':
        return <ProfilePage />;
      case 'emergency':
        return <EmergencyHelpPage />;
      default:
        return <PatientDashboard />;
    }
  }

  // Doctor Views
  if (role === 'doctor') {
    switch (activeTab) {
      case 'doctor_dashboard':
        return <DoctorDashboard />;
      case 'patient_detail':
        return <PatientDetailPage />;
      case 'alerts':
        return <AlertsPage />;
      default:
        return <DoctorDashboard />;
    }
  }

  // Caregiver Views
  if (role === 'caregiver') {
    switch (activeTab) {
      case 'caregiver_dashboard':
        return <CaregiverDashboard />;
      case 'patient_detail':
        return <PatientDetailPage />;
      case 'alerts':
        return <AlertsPage />;
      default:
        return <CaregiverDashboard />;
    }
  }

  // Admin Views
  if (role === 'admin') {
    switch (activeTab) {
      case 'admin_dashboard':
        return <AdminDashboard />;
      case 'alerts':
        return <AlertsPage />;
      default:
        return <AdminDashboard />;
    }
  }

  return <LandingPage />;
};

export function App() {
  return (
    <AppProvider>
      <Layout>
        <MainContent />
      </Layout>
    </AppProvider>
  );
}

export default App;
