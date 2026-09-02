import React from 'react';
import { useApp } from '../../context/AppContext';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { BellRing, ShieldAlert, PhoneCall, Check, UserCheck } from 'lucide-react';

export const AlertsPage: React.FC = () => {
  const { alerts, acknowledgeAlert, setEmergencyModalOpen, currentPatient } = useApp();

  const criticalAlerts = alerts.filter((a) => a.severity === 'critical' && !a.acknowledged);

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Header */}
      <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-xs flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-rose-50 text-rose-600 rounded-2xl border border-rose-100">
            <BellRing className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-900">Incident Alert Center</h1>
            <p className="text-xs text-slate-500">Real-time triage warnings, fall alerts & escalation workflows</p>
          </div>
        </div>

        <span className="px-3 py-1 bg-slate-100 text-slate-700 text-xs font-bold rounded-full">
          {alerts.length} Total Incident Logs
        </span>
      </div>

      {/* PROMINENT CRITICAL INCIDENT BANNER (IF ANY CRITICAL ALERT UNACKNOWLEDGED) */}
      {criticalAlerts.length > 0 && (
        <div className="bg-gradient-to-r from-rose-600 via-red-600 to-rose-700 text-white rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6 relative overflow-hidden animate-pulse">
          <div className="flex items-center justify-between border-b border-white/20 pb-4">
            <div className="flex items-center gap-3">
              <ShieldAlert className="w-8 h-8 text-white" />
              <div>
                <span className="text-xs uppercase font-extrabold tracking-widest text-rose-200 block">PRIORITY INCIDENT</span>
                <h2 className="text-2xl font-black text-white">CRITICAL INCIDENT DETECTED</h2>
              </div>
            </div>
            <span className="px-3 py-1 bg-white text-rose-700 text-xs font-black rounded-full">
              ACTION REQUIRED
            </span>
          </div>

          <div className="bg-white/10 backdrop-blur-md p-5 rounded-2xl border border-white/20 space-y-2">
            <h3 className="text-lg font-black text-white">{criticalAlerts[0].title}</h3>
            <p className="text-xs text-rose-100 leading-relaxed">{criticalAlerts[0].message}</p>
            <div className="flex items-center gap-4 text-xs text-white/90 pt-2">
              <span>Time: <strong>{criticalAlerts[0].time}</strong></span>
              <span>Status: <strong className="text-amber-200">Waiting for caregiver acknowledgement</strong></span>
            </div>
          </div>

          {/* Action Buttons required by spec */}
          <div className="flex flex-wrap items-center gap-3 pt-2">
            <button
              onClick={() => acknowledgeAlert(criticalAlerts[0].id)}
              className="px-6 py-3 bg-white text-rose-900 hover:bg-slate-100 font-extrabold text-xs rounded-xl transition-all shadow-md flex items-center gap-2"
            >
              <Check className="w-4 h-4 text-emerald-600" />
              <span>Acknowledge Alert</span>
            </button>

            <button
              onClick={() => alert(`Calling Caregiver ${currentPatient.emergencyContact.name} (${currentPatient.emergencyContact.phone})...`)}
              className="px-6 py-3 bg-slate-900 hover:bg-slate-800 text-white font-extrabold text-xs rounded-xl transition-all shadow-md flex items-center gap-2"
            >
              <UserCheck className="w-4 h-4 text-teal-400" />
              <span>Call Caregiver</span>
            </button>

            <button
              onClick={() => setEmergencyModalOpen(true)}
              className="px-6 py-3 bg-amber-400 hover:bg-amber-300 text-slate-950 font-black text-xs rounded-xl transition-all shadow-md flex items-center gap-2"
            >
              <PhoneCall className="w-4 h-4" />
              <span>Emergency Help (SOS)</span>
            </button>
          </div>
        </div>
      )}

      {/* FULL ALERT LOG LIST */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <h3 className="font-bold text-slate-900 text-base">Alert & Incident Log History</h3>
          <span className="text-xs text-slate-500 font-medium">Categorized by priority</span>
        </div>

        <div className="space-y-3">
          {alerts.map((alertItem) => (
            <div
              key={alertItem.id}
              className={`p-5 rounded-2xl border transition-all ${
                alertItem.acknowledged
                  ? 'bg-slate-50 border-slate-200 opacity-75'
                  : alertItem.severity === 'critical'
                  ? 'bg-rose-50/80 border-rose-300 shadow-xs'
                  : alertItem.severity === 'doctor_review'
                  ? 'bg-orange-50/80 border-orange-200'
                  : alertItem.severity === 'attention'
                  ? 'bg-amber-50/80 border-amber-200'
                  : 'bg-emerald-50/50 border-emerald-200'
              }`}
            >
              <div className="flex items-start justify-between gap-4 mb-2">
                <div className="flex items-center gap-2">
                  <StatusBadge status={alertItem.severity} size="sm" />
                  <span className="text-xs font-bold text-slate-400">ID: {alertItem.id}</span>
                </div>
                <span className="text-xs font-semibold text-slate-500">{alertItem.time}</span>
              </div>

              <h4 className="font-extrabold text-slate-900 text-base mb-1">{alertItem.title}</h4>
              <p className="text-xs text-slate-600 leading-relaxed mb-3">{alertItem.message}</p>

              <div className="flex items-center justify-between pt-3 border-t border-slate-200/60 text-xs">
                <span className="text-slate-500 font-medium">Patient: <strong className="text-slate-800">{alertItem.patientName}</strong></span>
                {alertItem.acknowledged ? (
                  <span className="text-emerald-700 font-bold flex items-center gap-1">
                    <Check className="w-4 h-4" /> Acknowledged by {alertItem.acknowledgedBy || 'Caregiver'}
                  </span>
                ) : (
                  <button
                    onClick={() => acknowledgeAlert(alertItem.id)}
                    className="px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs rounded-xl shadow-xs transition-colors"
                  >
                    Acknowledge
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
