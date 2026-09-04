
import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import type { UserRole } from '../types';
import { Activity, User, Mail, Building, ArrowRight } from 'lucide-react';

export const RegisterPage: React.FC = () => {
  const { setRole } = useApp();
  const [selectedRole, setSelectedRole] = useState<UserRole>('patient');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [hospitalId, setHospitalId] = useState('');

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault();
    setRole(selectedRole);
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4 sm:p-6 lg:p-8">
      <div className="w-full max-w-lg bg-white rounded-3xl shadow-2xl overflow-hidden border border-slate-200">
        
        <div className="bg-gradient-to-r from-teal-700 to-emerald-700 p-6 text-white text-center space-y-2">
          <div className="w-10 h-10 bg-white/20 rounded-2xl mx-auto flex items-center justify-center backdrop-blur-xs">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-2xl font-extrabold">Create RecoverAI Account</h2>
          <p className="text-xs text-teal-100">Register post-operative patient or healthcare staff</p>
        </div>

        <form onSubmit={handleRegister} className="p-6 space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Select Registration Role
            </label>
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value as UserRole)}
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-900"
            >
              <option value="patient">Patient (Post-Op Care)</option>
              <option value="doctor">Doctor / Surgeon</option>
              <option value="caregiver">Primary Caregiver</option>
              <option value="admin">Hospital Administrator</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Full Name
            </label>
            <div className="relative">
              <User className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Rahul Sharma"
                className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="rahul.sharma@example.com"
                className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Hospital Discharge MRN / Staff ID
            </label>
            <div className="relative">
              <Building className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="text"
                value={hospitalId}
                onChange={(e) => setHospitalId(e.target.value)}
                placeholder="MRN-2026-8890"
                className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full py-3 bg-teal-600 hover:bg-teal-700 text-white font-extrabold rounded-xl text-xs transition-all shadow-md flex items-center justify-center gap-2 mt-4 cursor-pointer"
          >
            <span>Complete Registration</span>
            <ArrowRight className="w-4 h-4" />
          </button>

          {/* Divider */}
          <div className="relative flex items-center justify-center my-3">
            <div className="border-t border-slate-200 w-full"></div>
            <span className="bg-white px-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest absolute">
              Or Sign Up With
            </span>
          </div>

          {/* Google OAuth Button */}
          <button
            type="button"
            onClick={() => {
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
                        alert(`Registration Verified for ${data.user.name}!`);
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
    </div>
  );
};
