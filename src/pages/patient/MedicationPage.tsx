import React from 'react';
import { useApp } from '../../context/AppContext';
import { mockAdherenceWeeklyData } from '../../data/mockData';
import { Pill, CheckCircle2, XCircle, BellRing, Clock, Award } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export const MedicationPage: React.FC = () => {
  const { medications, toggleMedicationStatus } = useApp();

  const takenCount = medications.filter((m) => m.status === 'taken').length;
  const totalCount = medications.length;
  const adherencePercent = Math.round((takenCount / totalCount) * 100);

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Header */}
      <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-emerald-50 text-emerald-600 rounded-2xl border border-emerald-100">
            <Pill className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-900">Medication Schedule & Adherence</h1>
            <p className="text-xs text-slate-500">Track doses, log intakes and view weekly compliance analytics</p>
          </div>
        </div>

        <div className="flex items-center gap-3 bg-slate-50 p-3 rounded-2xl border border-slate-200">
          <Award className="w-6 h-6 text-teal-600" />
          <div>
            <span className="text-[10px] uppercase font-bold text-slate-400 block">Today's Adherence Rate</span>
            <span className="text-xl font-black text-slate-900">{adherencePercent}% Compliance</span>
          </div>
        </div>
      </div>

      {/* TODAY'S SCHEDULE CARDS */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Clock className="w-5 h-5 text-teal-600" />
            <span>Today's Prescribed Dose Timeline</span>
          </h2>
          <span className="text-xs text-slate-500 font-semibold">{takenCount} of {totalCount} Doses Completed</span>
        </div>

        <div className="space-y-4">
          {medications.map((med) => (
            <div
              key={med.id}
              className={`p-5 rounded-2xl border transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
                med.status === 'taken'
                  ? 'bg-emerald-50/60 border-emerald-200'
                  : med.status === 'missed'
                  ? 'bg-rose-50/60 border-rose-200'
                  : 'bg-white border-slate-200 hover:border-slate-300 shadow-2xs'
              }`}
            >
              <div className="flex items-start gap-4">
                <div className="p-3 bg-slate-100 rounded-2xl text-slate-700 font-black text-xs shrink-0 text-center">
                  <div className="text-slate-900 text-sm font-extrabold">{med.scheduledTime.split(' ')[0]}</div>
                  <div className="text-[10px] text-slate-500 font-semibold uppercase">{med.scheduledTime.split(' ')[1]}</div>
                </div>

                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-extrabold text-slate-900 text-base">{med.name}</h3>
                    <span className="px-2 py-0.5 rounded-md bg-teal-100 text-teal-800 text-xs font-bold">
                      {med.dosage}
                    </span>
                    <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 text-[11px] font-semibold">
                      {med.timing}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">{med.instructions}</p>
                </div>
              </div>

              {/* Action Buttons: TAKEN / MISSED / REMIND ME LATER */}
              <div className="flex items-center gap-2 shrink-0 pt-3 sm:pt-0 border-t sm:border-t-0 border-slate-100">
                <button
                  onClick={() => toggleMedicationStatus(med.id, 'taken')}
                  className={`px-3 py-2 rounded-xl text-xs font-extrabold flex items-center gap-1.5 transition-all ${
                    med.status === 'taken'
                      ? 'bg-emerald-600 text-white shadow-xs'
                      : 'bg-emerald-50 text-emerald-800 hover:bg-emerald-100 border border-emerald-200'
                  }`}
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>TAKEN</span>
                </button>

                <button
                  onClick={() => toggleMedicationStatus(med.id, 'missed')}
                  className={`px-3 py-2 rounded-xl text-xs font-extrabold flex items-center gap-1.5 transition-all ${
                    med.status === 'missed'
                      ? 'bg-rose-600 text-white shadow-xs'
                      : 'bg-rose-50 text-rose-800 hover:bg-rose-100 border border-rose-200'
                  }`}
                >
                  <XCircle className="w-4 h-4" />
                  <span>MISSED</span>
                </button>

                <button
                  onClick={() => alert(`Reminder set for 30 minutes later for ${med.name}.`)}
                  className="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl flex items-center gap-1.5 transition-colors"
                >
                  <BellRing className="w-3.5 h-3.5 text-slate-500" />
                  <span className="hidden sm:inline">REMIND ME LATER</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* WEEKLY MEDICATION ADHERENCE CHART */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="font-bold text-slate-900 text-lg">Weekly Medication Adherence Trend</h3>
            <p className="text-xs text-slate-500">Historical 7-day adherence vs target safety threshold (90%)</p>
          </div>
          <span className="px-3 py-1 bg-emerald-100 text-emerald-800 text-xs font-extrabold rounded-full">
            Average: 91.2% Compliance
          </span>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={mockAdherenceWeeklyData} margin={{ top: 10, right: 10, bottom: 0, left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="day" stroke="#64748b" fontSize={12} tickLine={false} />
              <YAxis domain={[0, 100]} stroke="#64748b" fontSize={12} tickLine={false} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderRadius: '12px', color: '#fff' }}
                formatter={(val) => [`${val}%`, 'Adherence']}
              />
              <Bar dataKey="percentage" fill="#0d9488" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
};
