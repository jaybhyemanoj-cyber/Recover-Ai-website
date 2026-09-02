import React from 'react';
import { useApp } from '../context/AppContext';
import {
  Activity,
  HeartPulse,
  Stethoscope,
  Users,
  ShieldAlert,
  ArrowRight,
  CheckCircle2,
  Lock,
  Clock,
  Sparkles,
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  const { setRole } = useApp();

  return (
    <div className="bg-slate-50 min-h-screen text-slate-900">
      
      {/* HERO SECTION */}
      <section className="relative overflow-hidden bg-gradient-to-b from-teal-900 via-slate-900 to-slate-950 text-white py-16 lg:py-24 px-4 sm:px-6 lg:px-8">
        <div className="absolute inset-0 bg-[radial-gradient(#14b8a6_1px,transparent_1px)] [background-size:24px_24px] opacity-15" />

        <div className="max-w-7xl mx-auto relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          
          <div className="lg:col-span-7 space-y-6 text-center lg:text-left">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-teal-500/10 border border-teal-400/30 text-teal-300 text-xs font-semibold">
              <Sparkles className="w-4 h-4 text-teal-400" />
              <span>AI-Powered Post-Operative Telemetry Platform</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-tight">
              Post-Operative Recovery <br className="hidden sm:inline" />
              <span className="bg-gradient-to-r from-teal-300 via-emerald-300 to-teal-100 bg-clip-text text-transparent">
                Monitored with Care & Precision
              </span>
            </h1>

            <p className="text-slate-300 text-base sm:text-lg max-w-2xl mx-auto lg:mx-0 leading-relaxed font-normal">
              RecoverAI seamlessly bridges hospital discharge with home recovery. Real-time vital telemetry, multi-step symptom triage, medication adherence tracking, and privacy-first AI incident detection.
            </p>

            <div className="flex flex-wrap items-center justify-center lg:justify-start gap-4 pt-2">
              <button
                onClick={() => setRole('patient')}
                className="px-6 py-3.5 bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-slate-950 font-extrabold rounded-2xl shadow-xl shadow-teal-500/25 transition-all flex items-center gap-2 hover:scale-105 active:scale-95"
              >
                <span>Launch Patient Portal</span>
                <ArrowRight className="w-5 h-5" />
              </button>

              <button
                onClick={() => setRole('doctor')}
                className="px-6 py-3.5 bg-white/10 hover:bg-white/20 text-white font-bold rounded-2xl border border-white/20 transition-all flex items-center gap-2 backdrop-blur-xs"
              >
                <Stethoscope className="w-5 h-5 text-teal-300" />
                <span>Doctor Workspace</span>
              </button>
            </div>

            {/* Quick Metrics Badge */}
            <div className="pt-8 border-t border-slate-800 grid grid-cols-3 gap-4 max-w-md mx-auto lg:mx-0 text-center lg:text-left">
              <div>
                <div className="text-2xl font-black text-white">99.8%</div>
                <div className="text-xs text-slate-400">Incident Alert Accuracy</div>
              </div>
              <div>
                <div className="text-2xl font-black text-teal-400">&lt; 2 sec</div>
                <div className="text-xs text-slate-400">Fall Escalation SLA</div>
              </div>
              <div>
                <div className="text-2xl font-black text-emerald-400">100%</div>
                <div className="text-xs text-slate-400">Privacy Compliant</div>
              </div>
            </div>
          </div>

          {/* Hero Card Preview */}
          <div className="lg:col-span-5">
            <div className="bg-slate-900/90 rounded-3xl p-6 border border-slate-800 shadow-2xl space-y-4 backdrop-blur-md">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-emerald-500 animate-ping" />
                  <div>
                    <h3 className="font-bold text-white text-sm">Live Monitoring Active</h3>
                    <p className="text-[11px] text-slate-400">Patient: Rahul Sharma (Knee Rehab Day 8)</p>
                  </div>
                </div>
                <span className="px-2.5 py-1 bg-emerald-500/20 text-emerald-300 text-xs font-bold rounded-full border border-emerald-500/30">
                  STABLE 🟢
                </span>
              </div>

              {/* Mini Vitals Grid */}
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-slate-800/60 p-3 rounded-2xl border border-slate-700/50">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Temperature</span>
                  <div className="text-lg font-black text-white mt-0.5">98.6 °F</div>
                  <span className="text-[10px] text-emerald-400">Normal range</span>
                </div>
                <div className="bg-slate-800/60 p-3 rounded-2xl border border-slate-700/50">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Heart Rate</span>
                  <div className="text-lg font-black text-white mt-0.5">72 bpm</div>
                  <span className="text-[10px] text-emerald-400">Rhythm regular</span>
                </div>
                <div className="bg-slate-800/60 p-3 rounded-2xl border border-slate-700/50">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Blood Pressure</span>
                  <div className="text-lg font-black text-white mt-0.5">120/80</div>
                  <span className="text-[10px] text-emerald-400">Optimal</span>
                </div>
                <div className="bg-slate-800/60 p-3 rounded-2xl border border-slate-700/50">
                  <span className="text-[10px] uppercase font-bold text-slate-400">SpO2 Oxygen</span>
                  <div className="text-lg font-black text-white mt-0.5">98 %</div>
                  <span className="text-[10px] text-emerald-400">Optimal</span>
                </div>
              </div>

              {/* Camera Activity Preview */}
              <div className="bg-slate-950 p-3.5 rounded-2xl border border-slate-800 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-teal-400 animate-pulse" />
                  <span className="text-slate-300 font-medium">Camera AI Event: <strong className="text-white">Walking detected</strong></span>
                </div>
                <span className="text-[10px] text-slate-500">10m ago</span>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* ROLE EXPLORER CARDS */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="text-center max-w-2xl mx-auto mb-12 space-y-2">
          <h2 className="text-3xl font-extrabold text-slate-900">Explore Role Dashboards</h2>
          <p className="text-slate-600 text-sm">
            Experience the custom-tailored interface designed for every healthcare stakeholder in the post-operative continuum.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          
          {/* Patient Card */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm hover:shadow-md transition-all flex flex-col justify-between space-y-4">
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
                <HeartPulse className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900">Patient Web App</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Daily health checkup wizard, pain scale, prescription viewer, medicine reminder, timeline tracker & camera monitoring privacy view.
              </p>
            </div>
            <button
              onClick={() => setRole('patient')}
              className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs transition-colors flex items-center justify-center gap-1.5"
            >
              <span>Enter Patient View</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Doctor Card */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm hover:shadow-md transition-all flex flex-col justify-between space-y-4">
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-2xl bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
                <Stethoscope className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900">Doctor Portal</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Centralized patient risk matrix, triage status sorting, recovery charts, clinical notes editor, prescription management.
              </p>
            </div>
            <button
              onClick={() => setRole('doctor')}
              className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl text-xs transition-colors flex items-center justify-center gap-1.5"
            >
              <span>Enter Doctor View</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Caregiver Card */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm hover:shadow-md transition-all flex flex-col justify-between space-y-4">
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-2xl bg-purple-100 text-purple-700 flex items-center justify-center font-bold">
                <Users className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900">Caregiver Dashboard</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Prominent critical incident popups (Fall/High Pain), one-touch patient calls, medication alerts, assigned patient activity feed.
              </p>
            </div>
            <button
              onClick={() => setRole('caregiver')}
              className="w-full py-2.5 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-xl text-xs transition-colors flex items-center justify-center gap-1.5"
            >
              <span>Enter Caregiver View</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Admin Card */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm hover:shadow-md transition-all flex flex-col justify-between space-y-4">
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-2xl bg-amber-100 text-amber-700 flex items-center justify-center font-bold">
                <ShieldAlert className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900">Admin Control</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                System telemetry, active camera node counts, critical incident resolution SLAs, user role provisioning.
              </p>
            </div>
            <button
              onClick={() => setRole('admin')}
              className="w-full py-2.5 bg-amber-600 hover:bg-amber-700 text-white font-bold rounded-xl text-xs transition-colors flex items-center justify-center gap-1.5"
            >
              <span>Enter Admin View</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

        </div>
      </section>

      {/* PLATFORM FEATURES & PRIVACY */}
      <section className="py-16 bg-white border-y border-slate-200 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
          
          <div className="flex gap-4 items-start">
            <div className="p-3 bg-teal-50 text-teal-600 rounded-2xl shrink-0">
              <Lock className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-bold text-slate-900 text-base mb-1">Privacy-First AI Detection</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                No continuous video streams are stored or viewed. AI edge models output encrypted metadata events (Walking, Sitting, Fall) ensuring absolute patient dignity.
              </p>
            </div>
          </div>

          <div className="flex gap-4 items-start">
            <div className="p-3 bg-teal-50 text-teal-600 rounded-2xl shrink-0">
              <Clock className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-bold text-slate-900 text-base mb-1">Automated Triage Engine</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Daily checkups calculate immediate triage status (Stable 🟢, Attention 🟡, Doctor Review 🟠, Critical 🔴) based on temperature, BP, SpO2 & pain scores.
              </p>
            </div>
          </div>

          <div className="flex gap-4 items-start">
            <div className="p-3 bg-teal-50 text-teal-600 rounded-2xl shrink-0">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-bold text-slate-900 text-base mb-1">Adherence & Prescriptions</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Strict read-only patient prescription enforcement with daily scheduled reminders, intake logging, and weekly adherence reporting.
              </p>
            </div>
          </div>

        </div>
      </section>

      {/* FOOTER */}
      <footer className="py-8 bg-slate-900 text-slate-400 text-xs text-center border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-teal-400" />
            <span className="font-bold text-white">RecoverAI Platform</span>
            <span>– Remote Recovery & Escalation System</span>
          </div>
          <p>© 2026 RecoverAI Health Technologies. Designed for Web & Desktop Browsers.</p>
        </div>
      </footer>

    </div>
  );
};
