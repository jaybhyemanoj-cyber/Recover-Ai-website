import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { ShieldAlert, PhoneCall, AlertTriangle, MapPin, CheckCircle2, X } from 'lucide-react';

export const EmergencyModal: React.FC = () => {
  const { emergencyModalOpen, setEmergencyModalOpen, currentPatient } = useApp();
  const [callActive, setCallActive] = useState<string | null>(null);
  const [dispatched, setDispatched] = useState(false);

  if (!emergencyModalOpen) return null;

  const handleSimulateCall = (contact: string) => {
    setCallActive(contact);
    setTimeout(() => {
      setCallActive(null);
    }, 4000);
  };

  const handleDispatchAmbulance = () => {
    setDispatched(true);
    setTimeout(() => {
      setDispatched(false);
      setEmergencyModalOpen(false);
    }, 3000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-fadeIn">
      <div className="bg-white w-full max-w-lg rounded-3xl shadow-2xl border border-rose-100 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-rose-600 via-red-600 to-rose-700 p-6 text-white relative">
          <button
            onClick={() => setEmergencyModalOpen(false)}
            className="absolute top-4 right-4 text-white/80 hover:text-white bg-white/10 p-1.5 rounded-full hover:bg-white/20 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-3">
            <div className="p-3 bg-white/15 rounded-2xl backdrop-blur-xs border border-white/20 shadow-inner">
              <ShieldAlert className="w-8 h-8 text-white animate-bounce" />
            </div>
            <div>
              <span className="text-xs uppercase tracking-widest font-bold text-rose-200">Emergency Protocol Active</span>
              <h2 className="text-2xl font-black text-white">EMERGENCY ASSISTANCE</h2>
            </div>
          </div>
        </div>

        {/* Body */}
        <div className="p-6 space-y-5">
          {dispatched ? (
            <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-6 text-center space-y-3">
              <CheckCircle2 className="w-12 h-12 text-emerald-600 mx-auto animate-bounce" />
              <h3 className="text-xl font-bold text-emerald-900">Emergency Response Dispatched!</h3>
              <p className="text-sm text-emerald-700">
                Hospital Rapid Response Team and Caregiver <strong>{currentPatient.caregiverName}</strong> have been notified with GPS location coordinates.
              </p>
            </div>
          ) : callActive ? (
            <div className="bg-rose-50 border border-rose-200 rounded-2xl p-6 text-center space-y-3">
              <PhoneCall className="w-12 h-12 text-rose-600 mx-auto animate-pulse" />
              <h3 className="text-xl font-bold text-rose-900">Connecting Call to {callActive}...</h3>
              <p className="text-sm text-rose-700">
                Simulating encrypted audio connection with emergency hotline center.
              </p>
            </div>
          ) : (
            <>
              {/* Patient Info Card */}
              <div className="bg-slate-50 rounded-2xl p-4 border border-slate-200 flex items-start justify-between">
                <div>
                  <h4 className="font-bold text-slate-900 text-base">{currentPatient.name}</h4>
                  <p className="text-xs text-slate-500 mt-0.5">{currentPatient.surgeryType} (Day {currentPatient.recoveryDay})</p>
                  <div className="flex items-center gap-1.5 mt-2 text-xs font-medium text-slate-700">
                    <MapPin className="w-4 h-4 text-rose-500 shrink-0" />
                    <span>{currentPatient.roomNumber}</span>
                  </div>
                </div>
                <span className="px-2.5 py-1 text-xs font-bold bg-rose-100 text-rose-700 rounded-full border border-rose-200">
                  HIGH PRIORITY
                </span>
              </div>

              {/* Action Hotlines */}
              <div className="space-y-2.5">
                <button
                  onClick={() => handleSimulateCall('Hospital ICU Emergency (108 / +91 1800-425-999)')}
                  className="w-full flex items-center justify-between p-4 bg-rose-600 hover:bg-rose-700 text-white rounded-2xl font-bold transition-all shadow-lg hover:shadow-rose-600/30 active:scale-[0.99]"
                >
                  <div className="flex items-center gap-3">
                    <PhoneCall className="w-5 h-5 animate-pulse" />
                    <div className="text-left">
                      <div className="text-sm font-extrabold">Call Hospital Ambulance (108)</div>
                      <div className="text-xs text-rose-100 font-normal">Direct line to Hospital Command Desk</div>
                    </div>
                  </div>
                  <span className="text-xs bg-white/20 px-2.5 py-1 rounded-lg">DIAL NOW</span>
                </button>

                <button
                  onClick={() => handleSimulateCall(`Caregiver ${currentPatient.emergencyContact.name}`)}
                  className="w-full flex items-center justify-between p-4 bg-slate-900 hover:bg-slate-800 text-white rounded-2xl font-bold transition-all shadow-md active:scale-[0.99]"
                >
                  <div className="flex items-center gap-3">
                    <PhoneCall className="w-5 h-5 text-emerald-400" />
                    <div className="text-left">
                      <div className="text-sm font-bold">Call Caregiver ({currentPatient.emergencyContact.name})</div>
                      <div className="text-xs text-slate-400 font-normal">{currentPatient.emergencyContact.phone}</div>
                    </div>
                  </div>
                  <span className="text-xs bg-slate-800 px-2.5 py-1 rounded-lg">CALL</span>
                </button>

                <button
                  onClick={handleDispatchAmbulance}
                  className="w-full flex items-center justify-center gap-2 p-3.5 bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold rounded-2xl transition-all shadow-md"
                >
                  <AlertTriangle className="w-5 h-5" />
                  <span>Broadcast Rapid Response SOS Dispatch</span>
                </button>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-50 border-t border-slate-100 flex justify-between items-center text-xs text-slate-500">
          <span>GPS Sensor Lock: Active</span>
          <button
            onClick={() => setEmergencyModalOpen(false)}
            className="text-slate-600 hover:text-slate-900 font-semibold underline"
          >
            Cancel / Close
          </button>
        </div>
      </div>
    </div>
  );
};
