import React from 'react';
import { useApp } from '../../context/AppContext';
import { FileText, Download, Lock, Building } from 'lucide-react';

export const PrescriptionPage: React.FC = () => {
  const { currentPatient, medications } = useApp();

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn">
      
      {/* Header */}
      <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-blue-50 text-blue-600 rounded-2xl border border-blue-100">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-900">Doctor's E-Prescription</h1>
            <p className="text-xs text-slate-500">Official post-operative medication orders</p>
          </div>
        </div>

        <button
          onClick={() => alert('Downloading official signed PDF prescription document...')}
          className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl text-xs transition-colors flex items-center gap-2 shadow-xs"
        >
          <Download className="w-4 h-4" />
          <span>Download PDF Copy</span>
        </button>
      </div>

      {/* Safety Notice Banner */}
      <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 text-xs text-amber-900 flex items-start gap-3">
        <Lock className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <strong className="font-bold text-amber-950 block">Strict Medical Safety Directive:</strong>
          <span>
            Patients are strictly prohibited from modifying dosage, frequency, or duration without explicit written consent from the prescribing surgeon ({currentPatient.doctorName}).
          </span>
        </div>
      </div>

      {/* Official Prescription Paper Card */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-lg p-6 sm:p-10 space-y-8 relative overflow-hidden">
        
        {/* Hospital Header Header */}
        <div className="flex flex-col sm:flex-row justify-between border-b-2 border-slate-900 pb-6 gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Building className="w-6 h-6 text-teal-600" />
              <h2 className="text-xl font-black text-slate-900">APOLLO RECOVERY MEDICAL CENTER</h2>
            </div>
            <p className="text-xs text-slate-500">Department of Orthopedic & Trauma Surgery • Post-Op Home Care Unit</p>
            <p className="text-[11px] text-slate-400">Hospital Reg: #HOSP-2026-9901 • NABH Accredited</p>
          </div>

          <div className="text-left sm:text-right space-y-0.5 text-xs text-slate-600">
            <div className="font-bold text-slate-900">{currentPatient.doctorName}</div>
            <div>M.S. Orthopedics, M.Ch. Joint Replacement</div>
            <div>Reg No: <strong>KA-48921-MC</strong></div>
            <div className="text-teal-600 font-semibold mt-1">Tele-Health License Active 🟢</div>
          </div>
        </div>

        {/* Patient Info Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 bg-slate-50 rounded-2xl border border-slate-200 text-xs">
          <div>
            <span className="text-slate-400 font-bold block text-[10px] uppercase">Patient Name</span>
            <strong className="text-slate-900 font-extrabold">{currentPatient.name}</strong>
          </div>
          <div>
            <span className="text-slate-400 font-bold block text-[10px] uppercase">Age / Gender</span>
            <strong className="text-slate-900 font-extrabold">{currentPatient.age} Yrs / {currentPatient.gender}</strong>
          </div>
          <div>
            <span className="text-slate-400 font-bold block text-[10px] uppercase">Surgery Procedure</span>
            <strong className="text-slate-900 font-extrabold">{currentPatient.surgeryType}</strong>
          </div>
          <div>
            <span className="text-slate-400 font-bold block text-[10px] uppercase">Discharge Date</span>
            <strong className="text-slate-900 font-extrabold">{currentPatient.dischargeDate}</strong>
          </div>
        </div>

        {/* Rx Rx Section */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-slate-900 font-black text-2xl">
            <span className="italic text-teal-600">Rx</span>
            <span className="text-sm font-bold text-slate-500 uppercase tracking-wider">Prescribed Medication Table</span>
          </div>

          {/* Desktop Table / Mobile Cards */}
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-100 border-b border-slate-200 text-slate-700 font-bold uppercase tracking-wider">
                  <th className="p-3.5">Medicine Name</th>
                  <th className="p-3.5">Dosage</th>
                  <th className="p-3.5">Schedule Time</th>
                  <th className="p-3.5">Food Requirement</th>
                  <th className="p-3.5">Duration</th>
                  <th className="p-3.5">Instructions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 font-medium">
                {medications.map((med) => (
                  <tr key={med.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="p-3.5 font-extrabold text-slate-900">
                      {med.name}
                      <span className="block text-[10px] text-slate-400 font-normal">Rx ID: {med.id}</span>
                    </td>
                    <td className="p-3.5 text-teal-700 font-bold">{med.dosage}</td>
                    <td className="p-3.5 font-bold text-slate-800">{med.scheduledTime}</td>
                    <td className="p-3.5">
                      <span className="px-2 py-0.5 rounded-md bg-slate-100 font-semibold text-slate-700">
                        {med.timing}
                      </span>
                    </td>
                    <td className="p-3.5 font-bold text-slate-900">{med.durationDays} Days</td>
                    <td className="p-3.5 text-slate-600 max-w-xs leading-relaxed">{med.instructions}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Doctor Signature Seal */}
        <div className="pt-8 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="w-16 h-16 rounded-full border-2 border-dashed border-teal-600 flex items-center justify-center p-1 text-center">
              <span className="text-[9px] font-black text-teal-700 uppercase leading-tight">DOCTOR VERIFIED SEAL</span>
            </div>
            <div className="text-xs text-slate-500">
              <p className="font-bold text-slate-800">Digitally Signed & Timestamped</p>
              <p className="text-[11px]">Hash: 8f9a2b7c-2026-APOLLO</p>
            </div>
          </div>

          <div className="text-center sm:text-right">
            <div className="font-serif italic text-xl font-bold text-slate-900">Dr. Vikramaditya Rao</div>
            <div className="text-[11px] text-slate-400 uppercase font-bold tracking-wider">Chief Orthopedic Surgeon</div>
          </div>
        </div>

      </div>

    </div>
  );
};
