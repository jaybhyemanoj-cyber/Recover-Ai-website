import React from 'react';
import { Shield, Users, Stethoscope, HeartPulse, Camera, ShieldAlert, CheckCircle2, Activity, Cpu } from 'lucide-react';

export const AdminDashboard: React.FC = () => {
  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Header */}
      <div className="bg-gradient-to-r from-amber-900 via-slate-900 to-amber-950 p-6 sm:p-8 rounded-3xl text-white shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-amber-300 text-xs font-bold uppercase tracking-wider mb-1">
            <Shield className="w-4 h-4" />
            <span>Platform Operations Command</span>
          </div>
          <h1 className="text-3xl font-black">Admin Telemetry Control</h1>
          <p className="text-xs text-amber-100 mt-1">System infrastructure metrics, gateway SLA & active user provisioning</p>
        </div>

        <span className="px-3.5 py-1.5 bg-amber-500/20 text-amber-200 border border-amber-400/30 text-xs font-bold rounded-full">
          Gateway Node Cluster: ONLINE 🟢
        </span>
      </div>

      {/* SYSTEM METRICS GRID REQUIRED BY SPEC */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs">
          <div className="flex items-center gap-2 text-slate-500 text-xs font-bold uppercase mb-1">
            <Users className="w-4 h-4 text-teal-600" />
            <span>Total Patients</span>
          </div>
          <div className="text-2xl font-black text-slate-900">154</div>
          <span className="text-[10px] text-emerald-600 font-bold">+12 this week</span>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs">
          <div className="flex items-center gap-2 text-slate-500 text-xs font-bold uppercase mb-1">
            <Stethoscope className="w-4 h-4 text-blue-600" />
            <span>Doctors</span>
          </div>
          <div className="text-2xl font-black text-slate-900">18</div>
          <span className="text-[10px] text-blue-600 font-bold">100% Certified</span>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs">
          <div className="flex items-center gap-2 text-slate-500 text-xs font-bold uppercase mb-1">
            <HeartPulse className="w-4 h-4 text-purple-600" />
            <span>Caregivers</span>
          </div>
          <div className="text-2xl font-black text-slate-900">35</div>
          <span className="text-[10px] text-purple-600 font-bold">Active On Duty</span>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs">
          <div className="flex items-center gap-2 text-slate-500 text-xs font-bold uppercase mb-1">
            <Camera className="w-4 h-4 text-emerald-600" />
            <span>Active Monitoring</span>
          </div>
          <div className="text-2xl font-black text-slate-900">142</div>
          <span className="text-[10px] text-emerald-600 font-bold">Edge Privacy Nodes</span>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs">
          <div className="flex items-center gap-2 text-slate-500 text-xs font-bold uppercase mb-1">
            <ShieldAlert className="w-4 h-4 text-rose-600" />
            <span>Critical Incidents</span>
          </div>
          <div className="text-2xl font-black text-rose-600">3</div>
          <span className="text-[10px] text-rose-600 font-bold">Active Escalations</span>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs">
          <div className="flex items-center gap-2 text-slate-500 text-xs font-bold uppercase mb-1">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Resolved Incidents</span>
          </div>
          <div className="text-2xl font-black text-emerald-600">48</div>
          <span className="text-[10px] text-emerald-600 font-bold">99.4% SLA Compliance</span>
        </div>

      </div>

      {/* SYSTEM ACTIVITY LOG & HARDWARE GATEWAY HEALTH */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* System Activity Stream */}
        <div className="lg:col-span-7 bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-amber-600" />
              <h3 className="font-bold text-slate-900 text-base">Real-Time System Activity Log</h3>
            </div>
            <span className="text-xs text-slate-400 font-medium">Live Audit Stream</span>
          </div>

          <div className="space-y-3">
            {[
              { time: '10:42 AM', type: 'FALL_ALERT', msg: 'AI Edge Node #42 detected potential fall for Rahul Sharma. Escalated to Caregiver.' },
              { time: '10:30 AM', type: 'CHECKUP_SUBMITTED', msg: 'Patient Ananya Verma submitted Daily Health Check. Calculated Triage: Attention 🟡' },
              { time: '09:45 AM', type: 'GATEWAY_SYNC', msg: 'AI Camera Sensor Firmware v2.4 successfully synced across 142 active nodes.' },
              { time: '09:15 AM', type: 'MEDICATION_LOG', msg: 'Patient Suresh Patel marked Paracetamol 500mg as TAKEN.' },
              { time: '08:00 AM', type: 'DOCTOR_NOTE', msg: 'Dr. Vikramaditya Rao added clinical note for patient Kabir Mehta.' },
            ].map((log, idx) => (
              <div key={idx} className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 text-xs flex items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-extrabold text-slate-900">{log.type}</span>
                    <span className="text-[10px] text-slate-400 font-medium">{log.time}</span>
                  </div>
                  <p className="text-slate-600 mt-0.5 leading-relaxed">{log.msg}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* AI Hardware Gateway Health */}
        <div className="lg:col-span-5 bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <Cpu className="w-5 h-5 text-amber-600" />
              <h3 className="font-bold text-slate-900 text-base">Edge Hardware Gateway</h3>
            </div>
            <span className="text-xs text-emerald-600 font-bold">Optimal Health</span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="p-4 bg-slate-900 text-white rounded-2xl space-y-2">
              <div className="flex justify-between items-center text-slate-300">
                <span>AI Ingestion Gateway</span>
                <span className="text-emerald-400 font-bold">142 / 142 Connected</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div className="bg-emerald-500 h-full w-full" />
              </div>
            </div>

            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2">
              <div className="flex justify-between text-slate-700">
                <span>Avg Fall Detection SLA:</span>
                <strong className="text-slate-900">1.8 Seconds</strong>
              </div>
              <div className="flex justify-between text-slate-700">
                <span>Data Encryption:</span>
                <strong className="text-teal-700">AES-256 GCM</strong>
              </div>
              <div className="flex justify-between text-slate-700">
                <span>Database Backup Status:</span>
                <strong className="text-emerald-600">Synced to PostgreSQL (Mocked)</strong>
              </div>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};
