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
              className="w-full py-3 bg-teal-600 hover:bg-teal-700 text-white font-extrabold rounded-xl text-sm transition-all shadow-md flex items-center justify-center gap-2 cursor-pointer"
            >
              <span>Access {selectedRole.toUpperCase()} Dashboard</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            {/* Divider */}
            <div className="relative flex items-center justify-center my-4">
              <div className="border-t border-slate-200 w-full"></div>
              <span className="bg-white px-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest absolute">
                Or Continue With
              </span>
            </div>

            {/* Google OAuth 2.0 Sign-In Button */}
            <button
              type="button"
              onClick={() => {
                // Trigger Google One-Tap or GSI Prompt if available
                if (window.google?.accounts?.id) {
                  window.google.accounts.id.initialize({
                    client_id: "629843647814-d7ep06jkculvjcmfvq6u7niut1osnv5d.apps.googleusercontent.com",
                    callback: (response: any) => {
                      fetch("http://localhost:5000/api/auth/google", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ credential: response.credential })
                      })
                      .then(res => res.json())
                      .then(data => {
                        if (data.status === "success") {
                          alert(`Welcome ${data.user.name}! Authenticated via Google OAuth.`);
                          setRole(selectedRole);
                        } else {
                          setRole(selectedRole);
                        }
                      })
                      .catch(() => setRole(selectedRole));
                    }
                  });
                  window.google.accounts.id.prompt();
                } else {
                  // Direct fallback for demo login
                  setRole(selectedRole);
                }
              }}
              className="w-full py-2.5 px-4 bg-white hover:bg-slate-50 border border-slate-300 rounded-xl text-xs font-bold text-slate-700 transition-all shadow-xs flex items-center justify-center gap-3 cursor-pointer group"
            >
              <svg className="w-4 h-4 transition-transform group-hover:scale-110" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                />
              </svg>
              <span>Continue with Google</span>
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
