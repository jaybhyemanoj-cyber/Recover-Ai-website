import React from 'react';
import { useApp } from '../../context/AppContext';
import {
  LayoutDashboard,
  HeartPulse,
  ClipboardCheck,
  FileText,
  Pill,
  Clock,
  Camera,
  BellRing,
  User,
  PhoneCall,
  UserCheck,
  ShieldAlert,
  ChevronRight,
  ShieldCheck,
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const { role, activeTab, setActiveTab, unreadAlertCount } = useApp();

  if (role === 'landing') return null;

  const patientNav = [
    { id: 'dashboard', label: 'Patient Dashboard', icon: LayoutDashboard },
    { id: 'recovery', label: 'My Recovery Plan', icon: HeartPulse },
    { id: 'checkup', label: 'Daily Health Check', icon: ClipboardCheck, highlight: true },
    { id: 'prescription', label: 'Prescription', icon: FileText },
    { id: 'medications', label: 'Medicines & Schedule', icon: Pill },
    { id: 'timeline', label: 'Recovery Timeline', icon: Clock },
    { id: 'camera', label: 'AI Camera Guard', icon: Camera },
    { id: 'alerts', label: 'Alert Center', icon: BellRing, badge: unreadAlertCount },
    { id: 'profile', label: 'My Profile', icon: User },
    { id: 'emergency', label: 'Emergency SOS', icon: PhoneCall, danger: true },
  ];

  const doctorNav = [
    { id: 'doctor_dashboard', label: 'Doctor Dashboard', icon: LayoutDashboard },
    { id: 'patient_detail', label: 'Patient Detail View', icon: UserCheck },
    { id: 'alerts', label: 'Clinical Incident Log', icon: ShieldAlert, badge: unreadAlertCount },
  ];

  const caregiverNav = [
    { id: 'caregiver_dashboard', label: 'Caregiver Overview', icon: HeartPulse },
    { id: 'patient_detail', label: 'Patient Vitals', icon: UserCheck },
    { id: 'alerts', label: 'Critical Alerts', icon: BellRing, badge: unreadAlertCount },
  ];

  const adminNav = [
    { id: 'admin_dashboard', label: 'Admin Metrics', icon: LayoutDashboard },
    { id: 'alerts', label: 'System Incident Logs', icon: ShieldCheck },
  ];

  let currentNav = patientNav;
  if (role === 'doctor') currentNav = doctorNav;
  else if (role === 'caregiver') currentNav = caregiverNav;
  else if (role === 'admin') currentNav = adminNav;

  return (
    <aside className="w-64 bg-white border-r border-slate-200 hidden lg:flex flex-col shrink-0 min-h-[calc(100vh-4rem)]">
      
      {/* Role Banner Header */}
      <div className="p-4 border-b border-slate-100 bg-slate-50/60">
        <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Navigation Menu</div>
        <div className="text-xs font-bold text-slate-900 capitalize mt-0.5 flex items-center justify-between">
          <span>{role} Portal</span>
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
        </div>
      </div>

      {/* Nav List */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {currentNav.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all group ${
                isActive
                  ? 'bg-teal-600 text-white shadow-md shadow-teal-600/20 font-bold'
                  : item.danger
                  ? 'text-rose-600 hover:bg-rose-50 font-bold'
                  : item.highlight
                  ? 'bg-emerald-50 text-emerald-800 hover:bg-emerald-100 border border-emerald-200'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon
                  className={`w-4 h-4 transition-transform group-hover:scale-110 ${
                    isActive ? 'text-white' : item.danger ? 'text-rose-600' : 'text-slate-500 group-hover:text-slate-900'
                  }`}
                />
                <span>{item.label}</span>
              </div>

              <div className="flex items-center gap-1">
                {item.badge !== undefined && item.badge > 0 && (
                  <span
                    className={`px-2 py-0.5 text-[10px] font-extrabold rounded-full ${
                      isActive ? 'bg-white text-teal-800' : 'bg-rose-500 text-white animate-pulse'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
                <ChevronRight className={`w-3.5 h-3.5 opacity-40 group-hover:opacity-100 ${isActive ? 'text-white' : ''}`} />
              </div>
            </button>
          );
        })}
      </nav>

      {/* Privacy Guard Notice Box */}
      <div className="p-3 m-3 bg-gradient-to-br from-teal-50 to-emerald-50 border border-teal-200 rounded-2xl">
        <div className="flex items-center gap-2 text-teal-900 font-bold text-xs">
          <ShieldCheck className="w-4 h-4 text-teal-600" />
          <span>AI Privacy Guard Active</span>
        </div>
        <p className="text-[10px] text-teal-700 mt-1 leading-relaxed">
          Zero raw video recorded. Pure edge event detection telemetry. HIPAA & GDPR ready.
        </p>
      </div>

      {/* User Info Footer */}
      <div className="p-4 border-t border-slate-100 bg-slate-50/50 flex items-center justify-between text-xs text-slate-500">
        <div>
          <div className="font-bold text-slate-800 text-xs">RecoverAI Platform</div>
          <div className="text-[10px] text-slate-400">v2.4 Production UI</div>
        </div>
        <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 text-[10px] font-bold rounded-md">LIVE</span>
      </div>
    </aside>
  );
};
