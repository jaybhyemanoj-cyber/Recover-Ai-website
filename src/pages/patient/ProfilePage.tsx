import React from 'react';
import { useApp } from '../../context/AppContext';
import { Phone, MapPin, Building } from 'lucide-react';

export const ProfilePage: React.FC = () => {
  const { currentPatient } = useApp();

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn">
      
      {/* Header Profile Card */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-xs flex flex-col sm:flex-row items-start sm:items-center gap-6">
        <div className="w-20 h-20 rounded-full bg-gradient-to-tr from-teal-600 to-emerald-400 text-white font-black text-2xl flex items-center justify-center shadow-lg shadow-teal-500/20 shrink-0">
          {currentPatient.name.split(' ').map((n) => n[0]).join('')}
        </div>

        <div className="space-y-1 flex-1">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-slate-900">{currentPatient.name}</h1>
            <span className="px-2.5 py-0.5 rounded-full bg-teal-100 text-teal-800 text-xs font-bold">
              MRN: {currentPatient.id}
            </span>
          </div>
          <p className="text-xs text-slate-500 font-medium">
            {currentPatient.gender}, {currentPatient.age} Years Old • Discharged on {currentPatient.dischargeDate}
          </p>
          <div className="flex items-center gap-2 text-xs font-bold text-teal-700 pt-1">
            <MapPin className="w-4 h-4 text-teal-600" />
            <span>{currentPatient.roomNumber}</span>
          </div>
        </div>
      </div>

      {/* Details Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Surgical Information */}
        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <Building className="w-5 h-5 text-teal-600" />
            <h2 className="font-bold text-slate-900 text-base">Surgery & Hospital Plan</h2>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <span className="text-slate-400 font-bold block text-[10px] uppercase">Procedure Name</span>
              <strong className="text-slate-900 text-sm">{currentPatient.surgeryType}</strong>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <span className="text-slate-400 font-bold block text-[10px] uppercase">Surgery Date</span>
                <strong className="text-slate-900">{currentPatient.surgeryDate}</strong>
              </div>
              <div>
                <span className="text-slate-400 font-bold block text-[10px] uppercase">Discharge Date</span>
                <strong className="text-slate-900">{currentPatient.dischargeDate}</strong>
              </div>
            </div>

            <div>
              <span className="text-slate-400 font-bold block text-[10px] uppercase">Known Allergies</span>
              <div className="flex flex-wrap gap-1.5 mt-1">
                {currentPatient.allergies.length > 0 ? (
                  currentPatient.allergies.map((alg, i) => (
                    <span key={i} className="px-2 py-0.5 bg-rose-100 text-rose-800 text-[11px] font-bold rounded-md">
                      {alg}
                    </span>
                  ))
                ) : (
                  <span className="text-slate-500">No known drug allergies reported.</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Primary Contacts */}
        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <Phone className="w-5 h-5 text-teal-600" />
            <h2 className="font-bold text-slate-900 text-base">Healthcare Contacts</h2>
          </div>

          <div className="space-y-3 text-xs">
            <div className="p-3 bg-slate-50 rounded-2xl border border-slate-200">
              <span className="text-slate-400 font-bold block text-[10px] uppercase">Attending Surgeon</span>
              <strong className="text-slate-900 font-extrabold text-sm block">{currentPatient.doctorName}</strong>
              <span className="text-teal-600 font-semibold text-[11px]">Apollo Joint Replacement Institute</span>
            </div>

            <div className="p-3 bg-slate-50 rounded-2xl border border-slate-200">
              <span className="text-slate-400 font-bold block text-[10px] uppercase">Primary Caregiver</span>
              <strong className="text-slate-900 font-extrabold text-sm block">{currentPatient.caregiverName}</strong>
              <span className="text-slate-600 font-medium">{currentPatient.emergencyContact.phone}</span>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};
