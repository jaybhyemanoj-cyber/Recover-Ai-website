import React from 'react';
import { useApp } from '../../context/AppContext';
import { ShieldAlert, PhoneCall } from 'lucide-react';

export const EmergencyHelpPage: React.FC = () => {
  const { currentPatient, setEmergencyModalOpen } = useApp();

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fadeIn">
      
      {/* Red Alert Header */}
      <div className="bg-gradient-to-r from-rose-600 via-red-600 to-rose-700 text-white p-6 sm:p-8 rounded-3xl shadow-2xl space-y-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-white/20 rounded-2xl backdrop-blur-xs">
            <ShieldAlert className="w-10 h-10 text-white animate-bounce" />
          </div>
          <div>
            <span className="text-xs font-black uppercase tracking-widest text-rose-200">24/7 HOTLINE PROTOCOL</span>
            <h1 className="text-3xl font-black text-white">Emergency Assistance Hub</h1>
          </div>
        </div>

        <p className="text-xs text-rose-100 leading-relaxed max-w-xl">
          If you are experiencing severe chest pain, extreme breathlessness, uncontrolled incisional bleeding, or have suffered a fall, activate SOS immediately.
        </p>

        <button
          onClick={() => setEmergencyModalOpen(true)}
          className="w-full py-4 bg-white text-rose-900 hover:bg-slate-100 font-black text-base rounded-2xl shadow-xl transition-all flex items-center justify-center gap-2 active:scale-98"
        >
          <PhoneCall className="w-6 h-6 text-rose-600 animate-pulse" />
          <span>ACTIVATE ONE-TOUCH EMERGENCY SOS</span>
        </button>
      </div>

      {/* Hotline Directory */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-4">
        <h3 className="font-bold text-slate-900 text-base border-b border-slate-100 pb-3">
          Direct Medical Hotlines
        </h3>

        <div className="space-y-3">
          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 flex items-center justify-between">
            <div>
              <h4 className="font-extrabold text-slate-900 text-sm">Hospital Rapid Response Ambulance (108)</h4>
              <p className="text-xs text-slate-500">24/7 Command Desk for ICU Transport</p>
            </div>
            <button
              onClick={() => alert('Dialing 108 Emergency Ambulance...')}
              className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold rounded-xl shadow-xs"
            >
              Dial 108
            </button>
          </div>

          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 flex items-center justify-between">
            <div>
              <h4 className="font-extrabold text-slate-900 text-sm">Primary Caregiver ({currentPatient.emergencyContact.name})</h4>
              <p className="text-xs text-slate-500">{currentPatient.emergencyContact.phone}</p>
            </div>
            <button
              onClick={() => alert(`Calling ${currentPatient.emergencyContact.phone}...`)}
              className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold rounded-xl shadow-xs"
            >
              Call Caregiver
            </button>
          </div>

          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 flex items-center justify-between">
            <div>
              <h4 className="font-extrabold text-slate-900 text-sm">Attending Surgeon Desk ({currentPatient.doctorName})</h4>
              <p className="text-xs text-slate-500">Apollo Orthopedic Post-Op Line</p>
            </div>
            <button
              onClick={() => alert('Connecting to Doctor Duty Desk...')}
              className="px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white text-xs font-bold rounded-xl shadow-xs"
            >
              Call Doctor Desk
            </button>
          </div>
        </div>
      </div>

    </div>
  );
};
