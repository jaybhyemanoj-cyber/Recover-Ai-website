import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { HeartPulse, PhoneCall, ShieldAlert, Check, Eye, Users, AlertTriangle, Camera, X } from 'lucide-react';

export const CaregiverDashboard: React.FC = () => {
  const { patientsList, alerts, acknowledgeAlert, escalateAlert, setSelectedPatientId, setActiveTab } = useApp();
  const [selectedScreenshot, setSelectedScreenshot] = useState<string | null>(null);

  const assignedPatients = patientsList.slice(0, 3);
  const criticalAlerts = alerts.filter((a) => a.severity === 'critical' && !a.acknowledged);

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Screenshot Modal */}
      {selectedScreenshot && (
        <div
          className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-xs flex items-center justify-center p-4"
          onClick={() => setSelectedScreenshot(null)}
        >
          <div
            className="bg-slate-900 border border-slate-700 rounded-3xl p-6 max-w-2xl w-full shadow-2xl relative"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2 text-white font-bold text-sm">
                <Camera className="w-4 h-4 text-teal-400" />
                <span>Captured Event Evidence Frame</span>
              </div>
              <button
                onClick={() => setSelectedScreenshot(null)}
                className="p-1 rounded-xl bg-slate-800 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="mt-4 rounded-2xl overflow-hidden border border-slate-700 bg-black">
              <img
                src={selectedScreenshot}
                alt="Event Evidence"
                className="w-full h-auto max-h-[60vh] object-contain mx-auto"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="600" height="300" viewBox="0 0 600 300"><rect fill="%230f172a" width="600" height="300"/><text fill="%2338bdf8" x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="16">Event Evidence Frame Captured</text></svg>';
                }}
              />
            </div>
            <p className="text-[11px] text-slate-400 mt-3 text-center">
              Privacy Mandate: Keyframe snapshot attached to caregiver's ntfy phone notification.
            </p>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="bg-gradient-to-r from-purple-900 via-slate-900 to-purple-950 p-6 sm:p-8 rounded-3xl text-white shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-purple-300 text-xs font-bold uppercase tracking-wider mb-1">
            <HeartPulse className="w-4 h-4" />
            <span>Primary Caregiver Companion Desk</span>
          </div>
          <h1 className="text-3xl font-black">Caregiver Dashboard</h1>
          <p className="text-xs text-purple-100 mt-1">Monitoring assigned recovery patients & emergency escalations</p>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1.5 bg-purple-500/20 text-purple-200 border border-purple-400/30 text-xs font-bold rounded-full">
            3 Assigned Patients Active 🟢
          </span>
        </div>
      </div>

      {/* PROMINENT CRITICAL ALERT PANEL REQUIRED BY SPEC */}
      {criticalAlerts.length > 0 ? (
        <div className="bg-gradient-to-r from-rose-600 via-red-600 to-rose-700 text-white rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6 relative animate-pulse">
          <div className="flex items-center justify-between border-b border-white/20 pb-4">
            <div className="flex items-center gap-3">
              <ShieldAlert className="w-8 h-8 text-white" />
              <div>
                <span className="text-xs uppercase font-black tracking-widest text-rose-200 block">URGENT CAREGIVER DISPATCH</span>
                <h2 className="text-2xl font-black text-white">🔴 CRITICAL ALERT DETECTED</h2>
              </div>
            </div>
            <span className="px-3 py-1 bg-white text-rose-900 text-xs font-black rounded-full">
              NOT ACKNOWLEDGED
            </span>
          </div>

          <div className="bg-white/10 backdrop-blur-md p-5 rounded-2xl border border-white/20 space-y-2">
            <h3 className="text-xl font-black text-white">{criticalAlerts[0].title}</h3>
            <p className="text-sm text-rose-100 leading-relaxed">{criticalAlerts[0].message}</p>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs text-white pt-2 font-medium">
              <div>Patient: <strong className="text-white font-extrabold">{criticalAlerts[0].patientName} ({criticalAlerts[0].patientId})</strong></div>
              <div>Time: <strong className="text-white font-extrabold">{criticalAlerts[0].time}</strong></div>
              <div>Status: <strong className="text-amber-200 font-extrabold">{criticalAlerts[0].caregiverStatus?.toUpperCase() || 'PENDING'}</strong></div>
              <div>ntfy Push: <strong className="text-emerald-300 font-extrabold">{criticalAlerts[0].ntfyStatus || 'Dispatched 🟢'}</strong></div>
            </div>

            {criticalAlerts[0].screenshotUrl && (
              <div className="pt-2">
                <button
                  onClick={() => setSelectedScreenshot(criticalAlerts[0].screenshotUrl || null)}
                  className="px-3 py-1.5 bg-slate-900/60 hover:bg-slate-900 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 border border-white/20"
                >
                  <Camera className="w-3.5 h-3.5 text-teal-300" />
                  <span>View Screenshot Evidence Frame</span>
                </button>
              </div>
            )}
          </div>

          {/* Action Buttons: I'M CHECKING / ESCALATE / VIEW PATIENT / CALL PATIENT */}
          <div className="flex flex-wrap items-center gap-3 pt-2">
            <button
              onClick={() => acknowledgeAlert(criticalAlerts[0].id)}
              className="px-6 py-3 bg-white text-rose-950 hover:bg-slate-100 font-extrabold text-xs rounded-xl transition-all shadow-md flex items-center gap-2"
            >
              <Check className="w-4 h-4 text-emerald-600" />
              <span>I'M CHECKING</span>
            </button>

            <button
              onClick={() => escalateAlert(criticalAlerts[0].id, 'Caregiver requested emergency medical response')}
              className="px-6 py-3 bg-rose-950 hover:bg-rose-900 text-rose-200 border border-rose-400 font-extrabold text-xs rounded-xl transition-all shadow-md flex items-center gap-2"
            >
              <AlertTriangle className="w-4 h-4 text-rose-400" />
              <span>ESCALATE</span>
            </button>

            <button
              onClick={() => {
                setSelectedPatientId(criticalAlerts[0].patientId);
                setActiveTab('patient_detail');
              }}
              className="px-6 py-3 bg-slate-900 hover:bg-slate-800 text-white font-extrabold text-xs rounded-xl transition-all shadow-md flex items-center gap-2"
            >
              <Eye className="w-4 h-4 text-teal-400" />
              <span>VIEW PATIENT</span>
            </button>

            <a
              href="tel:+917498964628"
              className="px-6 py-3 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-xs rounded-xl transition-all shadow-md flex items-center gap-2"
            >
              <PhoneCall className="w-4 h-4" />
              <span>Call (+917498964628)</span>
            </a>
          </div>
        </div>
      ) : (
        <div className="bg-emerald-50 border border-emerald-200 rounded-3xl p-6 flex items-center justify-between text-emerald-900">
          <div className="flex items-center gap-3">
            <Check className="w-6 h-6 text-emerald-600" />
            <div>
              <h3 className="font-extrabold text-sm">All Critical Incident Alerts Resolved</h3>
              <p className="text-xs text-emerald-700">No unacknowledged fall or vital alerts for assigned patients.</p>
            </div>
          </div>
          <span className="px-3 py-1 bg-emerald-200 text-emerald-900 text-xs font-bold rounded-full">
            Status Normal 🟢
          </span>
        </div>
      )}

      {/* ASSIGNED PATIENTS GRID */}
      <div>
        <h2 className="text-lg font-bold text-slate-900 mb-3 flex items-center gap-2">
          <Users className="w-5 h-5 text-purple-600" />
          <span>Assigned Patients Overview</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {assignedPatients.map((patient) => (
            <div key={patient.id} className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-4">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-extrabold text-slate-900 text-base">{patient.name}</h3>
                  <p className="text-xs text-slate-500">{patient.surgeryType}</p>
                </div>
                <StatusBadge status={patient.status} size="sm" />
              </div>

              <div className="space-y-2 text-xs text-slate-600 bg-slate-50 p-3 rounded-2xl border border-slate-100">
                <div className="flex justify-between">
                  <span>Temp / BP:</span>
                  <strong className="text-slate-900">{patient.vitals.temperature}°F • {patient.vitals.bpSystolic}/{patient.vitals.bpDiastolic}</strong>
                </div>
                <div className="flex justify-between">
                  <span>Pain Score:</span>
                  <strong className="text-slate-900">{patient.vitals.painLevel}/10</strong>
                </div>
                <div className="flex justify-between">
                  <span>Adherence:</span>
                  <strong className="text-teal-700">{patient.medicationAdherence}%</strong>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setSelectedPatientId(patient.id);
                    setActiveTab('patient_detail');
                  }}
                  className="flex-1 py-2 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs rounded-xl transition-colors text-center"
                >
                  View Details
                </button>
                <button
                  onClick={() => alert(`Calling ${patient.name}...`)}
                  className="p-2 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 rounded-xl border border-emerald-200"
                >
                  <PhoneCall className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
