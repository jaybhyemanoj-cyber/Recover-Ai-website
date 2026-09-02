import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import type { UserRole } from '../types';
import { Activity, Lock, Mail, UserCheck, Stethoscope, HeartPulse, Shield, ArrowRight } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const { setRole } = useApp();
  const [selectedRole, setSelectedRole] = useState<UserRole>('patient');
  const [email, setEmail] = useState('rahul.sharma@example.com');
  const [password, setPassword] = useState('••••••••••••');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setRole(selectedRole);
  };

  const demoAccounts: Record<UserRole, { name: string; email: string }> = {
    patient: { name: 'Rahul Sharma (Patient)', email: 'rahul.sharma@recoverai.health' },
    doctor: { name: 'Dr. Vikramaditya Rao (Orthopedic Surgeon)', email: 'dr.rao@apollo.health' },
    caregiver: { name: 'Priya Sharma (Primary Caregiver)', email: 'priya.sharma@recoverai.health' },
    admin: { name: 'Admin Command Desk', email: 'admin@recoverai.health' },
    landing: { name: 'Public Guest', email: 'guest@recoverai.health' },
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-950 to-teal-950 flex items-center justify-center p-4 sm:p-6 lg:p-8">
      <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl overflow-hidden border border-slate-200">
        
        {/* Header */}
        <div className="bg-slate-900 p-6 text-white text-center space-y-2 relative">
          <div className="w-12 h-12 bg-teal-500 rounded-2xl mx-auto flex items-center justify-center text-slate-950 font-black shadow-lg shadow-teal-500/30">
            <Activity className="w-7 h-7" />
          </div>
          <h2 className="text-2xl font-black tracking-tight">Portal Login</h2>
          <p className="text-xs text-slate-400">Select role and access your RecoverAI dashboard</p>
        </div>

        <div className="p-6 space-y-6">
          
          {/* Role Selector Tabs */}
          <div className="grid grid-cols-4 gap-1.5 p-1 bg-slate-100 rounded-2xl text-xs font-bold text-slate-600">
            <button
              onClick={() => {
                setSelectedRole('patient');
                setEmail(demoAccounts.patient.email);
              }}
              className={`py-2 rounded-xl flex flex-col items-center gap-1 transition-all ${
                selectedRole === 'patient' ? 'bg-white text-emerald-700 shadow-xs' : 'hover:text-slate-900'
              }`}
            >
              <UserCheck className="w-4 h-4" />
              <span className="text-[10px]">Patient</span>
            </button>

            <button
              onClick={() => {
                setSelectedRole('doctor');
                setEmail(demoAccounts.doctor.email);
              }}
              className={`py-2 rounded-xl flex flex-col items-center gap-1 transition-all ${
                selectedRole === 'doctor' ? 'bg-white text-blue-700 shadow-xs' : 'hover:text-slate-900'
              }`}
            >
              <Stethoscope className="w-4 h-4" />
              <span className="text-[10px]">Doctor</span>
            </button>

            <button
              onClick={() => {
                setSelectedRole('caregiver');
                setEmail(demoAccounts.caregiver.email);
              }}
              className={`py-2 rounded-xl flex flex-col items-center gap-1 transition-all ${
                selectedRole === 'caregiver' ? 'bg-white text-purple-700 shadow-xs' : 'hover:text-slate-900'
              }`}
            >
              <HeartPulse className="w-4 h-4" />
              <span className="text-[10px]">Caregiver</span>
            </button>

            <button
              onClick={() => {
                setSelectedRole('admin');
                setEmail(demoAccounts.admin.email);
              }}
              className={`py-2 rounded-xl flex flex-col items-center gap-1 transition-all ${
                selectedRole === 'admin' ? 'bg-white text-amber-700 shadow-xs' : 'hover:text-slate-900'
              }`}
            >
              <Shield className="w-4 h-4" />
              <span className="text-[10px]">Admin</span>
            </button>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Account Email
              </label>
              <div className="relative">
                <Mail className="w-5 h-5 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-900 focus:outline-hidden focus:ring-2 focus:ring-teal-500"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="w-5 h-5 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-900 focus:outline-hidden focus:ring-2 focus:ring-teal-500"
                  required
                />
              </div>
            </div>

            <div className="bg-teal-50 border border-teal-200 rounded-2xl p-3 text-xs text-teal-800 flex items-center justify-between">
              <div>
                <span className="font-bold text-[11px] block">Demo Mode Auto-Login</span>
                <span className="text-[10px] text-teal-600">Logging in as {demoAccounts[selectedRole].name}</span>
              </div>
              <span className="px-2 py-0.5 bg-teal-200 text-teal-900 font-extrabold rounded-md text-[10px]">READY</span>
            </div>

            <button
              type="submit"
              className="w-full py-3 bg-teal-600 hover:bg-teal-700 text-white font-extrabold rounded-xl text-sm transition-all shadow-md flex items-center justify-center gap-2"
            >
              <span>Access {selectedRole.toUpperCase()} Dashboard</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        </div>

        <div className="p-4 bg-slate-50 border-t border-slate-100 text-center text-xs text-slate-500">
          RecoverAI Secure Authentication Gateway • HIPAA Compliant
        </div>
      </div>
    </div>
  );
};
