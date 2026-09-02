import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { StatusBadge } from '../../components/ui/StatusBadge';
import type { TriageStatus } from '../../types';
import { Stethoscope, Search, ShieldAlert, ArrowRight } from 'lucide-react';

export const DoctorDashboard: React.FC = () => {
  const { patientsList, setSelectedPatientId, setActiveTab } = useApp();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState<string>('all');

  const filteredPatients = patientsList.filter((p) => {
    const matchesSearch =
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.surgeryType.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = selectedFilter === 'all' || p.status === selectedFilter;
    return matchesSearch && matchesFilter;
  });

  const countByStatus = (status: TriageStatus) => patientsList.filter((p) => p.status === status).length;

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 p-6 sm:p-8 rounded-3xl text-white shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-blue-300 text-xs font-bold uppercase tracking-wider mb-1">
            <Stethoscope className="w-4 h-4" />
            <span>Chief Surgeon Command Desk</span>
          </div>
          <h1 className="text-3xl font-black">Post-Op Clinical Dashboard</h1>
          <p className="text-xs text-slate-300 mt-1">Real-time triage telemetry across active discharged patients</p>
        </div>

        <button
          onClick={() => {
            const criticalP = patientsList.find((p) => p.status === 'critical') || patientsList[0];
            setSelectedPatientId(criticalP.id);
            setActiveTab('patient_detail');
          }}
          className="px-4 py-2.5 bg-rose-600 hover:bg-rose-500 text-white font-extrabold rounded-xl text-xs transition-all shadow-md flex items-center gap-2 shrink-0"
        >
          <ShieldAlert className="w-4 h-4 animate-bounce" />
          <span>Inspect Critical Cases ({countByStatus('critical')})</span>
        </button>
      </div>

      {/* KPI METRIC CARDS */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        <button
          onClick={() => setSelectedFilter('all')}
          className={`p-4 rounded-2xl border text-left transition-all ${
            selectedFilter === 'all' ? 'bg-slate-900 text-white border-slate-800 shadow-md' : 'bg-white border-slate-200 hover:border-slate-300'
          }`}
        >
          <span className="text-[10px] uppercase font-bold text-slate-400 block">Total Active</span>
          <div className="text-2xl font-black mt-0.5">{patientsList.length}</div>
        </button>

        <button
          onClick={() => setSelectedFilter('critical')}
          className={`p-4 rounded-2xl border text-left transition-all ${
            selectedFilter === 'critical' ? 'bg-rose-600 text-white border-rose-500 shadow-md' : 'bg-rose-50 border-rose-200 hover:border-rose-300'
          }`}
        >
          <span className="text-[10px] uppercase font-bold text-rose-600 block">Critical 🔴</span>
          <div className="text-2xl font-black text-rose-900 mt-0.5">{countByStatus('critical')}</div>
        </button>

        <button
          onClick={() => setSelectedFilter('doctor_review')}
          className={`p-4 rounded-2xl border text-left transition-all ${
            selectedFilter === 'doctor_review' ? 'bg-orange-600 text-white border-orange-500 shadow-md' : 'bg-orange-50 border-orange-200 hover:border-orange-300'
          }`}
        >
          <span className="text-[10px] uppercase font-bold text-orange-600 block">Doctor Review 🟠</span>
          <div className="text-2xl font-black text-orange-900 mt-0.5">{countByStatus('doctor_review')}</div>
        </button>

        <button
          onClick={() => setSelectedFilter('attention')}
          className={`p-4 rounded-2xl border text-left transition-all ${
            selectedFilter === 'attention' ? 'bg-amber-500 text-white border-amber-400 shadow-md' : 'bg-amber-50 border-amber-200 hover:border-amber-300'
          }`}
        >
          <span className="text-[10px] uppercase font-bold text-amber-600 block">Attention 🟡</span>
          <div className="text-2xl font-black text-amber-900 mt-0.5">{countByStatus('attention')}</div>
        </button>

        <button
          onClick={() => setSelectedFilter('stable')}
          className={`p-4 rounded-2xl border text-left transition-all ${
            selectedFilter === 'stable' ? 'bg-emerald-600 text-white border-emerald-500 shadow-md' : 'bg-emerald-50 border-emerald-200 hover:border-emerald-300'
          }`}
        >
          <span className="text-[10px] uppercase font-bold text-emerald-600 block">Stable 🟢</span>
          <div className="text-2xl font-black text-emerald-900 mt-0.5">{countByStatus('stable')}</div>
        </button>
      </div>

      {/* PATIENT TABLE & SEARCH */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-xs overflow-hidden space-y-4 p-6">
        
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search by patient name or surgery..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold"
            />
          </div>

          <div className="text-xs font-semibold text-slate-500">
            Showing {filteredPatients.length} of {patientsList.length} Discharged Patients
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-100 border-b border-slate-200 text-slate-700 font-bold uppercase tracking-wider">
                <th className="p-3.5">Patient Details</th>
                <th className="p-3.5">Triage Risk</th>
                <th className="p-3.5">Temp (°F)</th>
                <th className="p-3.5">Pain Level</th>
                <th className="p-3.5">Mobility</th>
                <th className="p-3.5">Adherence</th>
                <th className="p-3.5">Last Activity</th>
                <th className="p-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 font-medium">
              {filteredPatients.map((patient) => (
                <tr key={patient.id} className="hover:bg-slate-50 transition-colors">
                  <td className="p-3.5">
                    <div className="font-extrabold text-slate-900 text-sm">{patient.name}</div>
                    <div className="text-[11px] text-slate-500">{patient.surgeryType} • Day {patient.recoveryDay}</div>
                  </td>
                  <td className="p-3.5">
                    <StatusBadge status={patient.status} size="sm" />
                  </td>
                  <td className={`p-3.5 font-bold ${patient.vitals.temperature > 100 ? 'text-rose-600' : 'text-slate-800'}`}>
                    {patient.vitals.temperature} °F
                  </td>
                  <td className="p-3.5 font-bold text-slate-800">{patient.vitals.painLevel}/10</td>
                  <td className="p-3.5 text-slate-700">{patient.vitals.mobility}</td>
                  <td className="p-3.5 font-extrabold text-teal-700">{patient.medicationAdherence}%</td>
                  <td className="p-3.5 text-slate-500 text-[11px]">{patient.lastActivity}</td>
                  <td className="p-3.5 text-right">
                    <button
                      onClick={() => {
                        setSelectedPatientId(patient.id);
                        setActiveTab('patient_detail');
                      }}
                      className="px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl text-xs transition-colors flex items-center gap-1 ml-auto"
                    >
                      <span>Open Chart</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      </div>

    </div>
  );
};
