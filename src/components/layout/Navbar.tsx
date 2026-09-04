import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { useAuth } from '../../context/AuthContext';
import type { UserRole } from '../../types';
import { Activity, Bell, PhoneCall, ChevronDown, UserCheck, Stethoscope, HeartPulse, Shield, Home, LogIn, Bot, LogOut } from 'lucide-react';
import { NotificationDrawer } from '../ui/NotificationDrawer';

export const Navbar: React.FC = () => {
  const { role, setRole, unreadAlertCount, setEmergencyModalOpen, setAssistantModalOpen, currentPatient, patientsList, setSelectedPatientId } = useApp();
  const { user, logout } = useAuth();

  const [roleDropdownOpen, setRoleDropdownOpen] = useState(false);
  const [patientDropdownOpen, setPatientDropdownOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);

  const roleLabels: Record<UserRole, { title: string; icon: React.FC<{ className?: string }>; color: string }> = {
    landing: { title: 'Public Portal', icon: Home, color: 'bg-slate-100 text-slate-700' },
    patient: { title: 'Patient View', icon: UserCheck, color: 'bg-emerald-100 text-emerald-800' },
    doctor: { title: 'Doctor View', icon: Stethoscope, color: 'bg-blue-100 text-blue-800' },
    caregiver: { title: 'Caregiver View', icon: HeartPulse, color: 'bg-purple-100 text-purple-800' },
    admin: { title: 'Admin View', icon: Shield, color: 'bg-amber-100 text-amber-800' },
  };

  const handleRoleChange = (newRole: UserRole) => {
    setRole(newRole);
    setRoleDropdownOpen(false);
  };

  const CurrentRoleIcon = roleLabels[role].icon;

  return (
    <>
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-2xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
          
          {/* Left: Branding */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => setRole('landing')}
              className="flex items-center gap-2.5 text-left group"
            >
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-teal-600 via-teal-500 to-emerald-400 p-2 text-white flex items-center justify-center shadow-md shadow-teal-500/20 group-hover:scale-105 transition-transform">
                <Activity className="w-6 h-6 animate-pulse" />
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="font-extrabold text-xl tracking-tight text-slate-900">
                    Recover<span className="text-teal-600">AI</span>
                  </span>
                  <span className="hidden sm:inline-block text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-teal-50 text-teal-700 border border-teal-200">
                    Post-Op Remote Care
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 hidden md:block">Remote Patient Recovery & AI Incident Escalation</p>
              </div>
            </button>
          </div>

          {/* Center: Patient Quick Switcher (Visible in Doctor/Caregiver view) */}
          {(role === 'doctor' || role === 'caregiver') && (
            <div className="relative hidden md:block">
              <button
                onClick={() => setPatientDropdownOpen(!patientDropdownOpen)}
                className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 hover:bg-slate-200/70 rounded-xl text-xs font-semibold text-slate-700 border border-slate-200 transition-colors"
              >
                <span className="text-slate-400">Monitoring Patient:</span>
                <span className="text-slate-900 font-bold">{currentPatient.name}</span>
                <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
              </button>

              {patientDropdownOpen && (
                <div className="absolute left-0 mt-2 w-64 bg-white rounded-2xl shadow-xl border border-slate-200 py-2 z-50 animate-fadeIn">
                  <div className="px-3 py-1.5 text-[11px] font-bold text-slate-400 uppercase tracking-wider">Select Patient</div>
                  {patientsList.map((p) => (
                    <button
                      key={p.id}
                      onClick={() => {
                        setSelectedPatientId(p.id);
                        setPatientDropdownOpen(false);
                      }}
                      className={`w-full text-left px-3 py-2 text-xs hover:bg-slate-50 flex items-center justify-between ${
                        p.id === currentPatient.id ? 'bg-teal-50 text-teal-800 font-bold' : 'text-slate-700'
                      }`}
                    >
                      <div>
                        <div>{p.name} ({p.gender}, {p.age})</div>
                        <div className="text-[10px] text-slate-400">{p.surgeryType}</div>
                      </div>
                      <span className={`w-2 h-2 rounded-full ${p.status === 'critical' ? 'bg-rose-500 animate-ping' : p.status === 'attention' ? 'bg-amber-500' : 'bg-emerald-500'}`} />
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Right Controls: Role Switcher, SOS Button, Notifications, Login */}
          <div className="flex items-center gap-2 sm:gap-3">
            
            {/* Global Role Switcher */}
            <div className="relative">
              <button
                onClick={() => setRoleDropdownOpen(!roleDropdownOpen)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs font-bold transition-all shadow-2xs ${roleLabels[role].color}`}
              >
                <CurrentRoleIcon className="w-4 h-4" />
                <span className="hidden xs:inline">{roleLabels[role].title}</span>
                <ChevronDown className="w-3.5 h-3.5 opacity-60" />
              </button>

              {roleDropdownOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-white rounded-2xl shadow-xl border border-slate-200 py-2 z-50 animate-fadeIn">
                  <div className="px-3 py-1.5 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                    Switch Role Demo
                  </div>
                  {(Object.keys(roleLabels) as UserRole[]).map((r) => {
                    const RoleIcon = roleLabels[r].icon;
                    return (
                      <button
                        key={r}
                        onClick={() => handleRoleChange(r)}
                        className={`w-full text-left px-3.5 py-2.5 text-xs font-medium flex items-center gap-2.5 hover:bg-slate-50 transition-colors ${
                          role === r ? 'bg-teal-50 text-teal-800 font-bold' : 'text-slate-700'
                        }`}
                      >
                        <RoleIcon className="w-4 h-4 text-slate-500" />
                        <span>{roleLabels[r].title}</span>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

            {/* AI Recovery Assistant Trigger */}
            <button
              onClick={() => setAssistantModalOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-700 hover:to-emerald-700 text-white text-xs font-bold rounded-xl transition-all shadow-md shadow-teal-500/20 active:scale-95"
              title="Open Bilingual Post-Op Recovery Assistant"
            >
              <Bot className="w-3.5 h-3.5 animate-bounce" />
              <span className="hidden sm:inline">AI Assistant</span>
              <span className="text-[10px] bg-white/20 px-1 py-0.2 rounded font-extrabold">हिंदी/EN</span>
            </button>

            {/* Notifications Bell */}
            <button
              onClick={() => setNotificationsOpen(!notificationsOpen)}
              className="relative p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-xl transition-colors"
              title="Notifications"
            >
              <Bell className="w-5 h-5" />
              {unreadAlertCount > 0 && (
                <span className="absolute top-1 right-1 w-4 h-4 bg-rose-500 text-white text-[10px] font-extrabold rounded-full flex items-center justify-center animate-bounce">
                  {unreadAlertCount}
                </span>
              )}
            </button>

            {/* Emergency SOS Button */}
            <button
              onClick={() => setEmergencyModalOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-700 hover:to-red-700 text-white text-xs font-black uppercase tracking-wider rounded-xl transition-all shadow-md shadow-rose-500/20 active:scale-95"
            >
              <PhoneCall className="w-3.5 h-3.5 animate-pulse" />
              <span>SOS Emergency</span>
            </button>

            {/* Login / Auth direct trigger */}
            {role === 'landing' && (
              <button
                onClick={() => setRole('patient')}
                className="hidden sm:flex items-center gap-1.5 px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold rounded-xl transition-colors shadow-xs"
              >
                <LogIn className="w-3.5 h-3.5" />
                <span>Portal Login</span>
              </button>
            )}

            {/* Firebase Logout */}
            {user && (
              <button
                onClick={logout}
                className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 text-slate-600 hover:text-rose-600 hover:bg-rose-50 text-xs font-bold rounded-xl transition-colors cursor-pointer"
                title={`Signed in as ${user.email}`}
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Sign Out</span>
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Notification Drawer Component */}
      <NotificationDrawer isOpen={notificationsOpen} onClose={() => setNotificationsOpen(false)} />
    </>
  );
};
