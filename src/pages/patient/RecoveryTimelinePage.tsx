import React from 'react';
import { useApp } from '../../context/AppContext';
import { Clock, CheckCircle2, Circle, Calendar, Award, Activity } from 'lucide-react';

export const RecoveryTimelinePage: React.FC = () => {
  const { currentPatient } = useApp();

  const timelineSteps = [
    {
      title: 'Hospital Admission & Pre-Op Prep',
      date: '2026-08-20',
      day: 'Pre-Op',
      completed: true,
      description: 'Patient admitted for routine pre-op diagnostic bloodwork & cardiology clearance.',
    },
    {
      title: 'Surgical Procedure Executed',
      date: currentPatient.surgeryDate,
      day: 'Day 0',
      completed: true,
      description: `${currentPatient.surgeryType} performed successfully by ${currentPatient.doctorName}. No intraoperative complications.`,
    },
    {
      title: 'Hospital Discharge & Home Transition',
      date: currentPatient.dischargeDate,
      day: 'Day 3',
      completed: true,
      description: 'Cleared for remote recovery. Privacy-first camera edge guard & telemetry monitoring initialized.',
    },
    {
      title: 'Active Mobility & Tele-Rehab Phase',
      date: '2026-08-29 (Today)',
      day: `Day ${currentPatient.recoveryDay}`,
      completed: false,
      active: true,
      description: 'Independent walking with cane achieved. Pain level 2/10. Daily checkup logs submitted.',
    },
    {
      title: 'Suture Inspection & Tele-Consult',
      date: '2026-09-04',
      day: 'Day 14',
      completed: false,
      description: 'Scheduled virtual wound inspection with surgeon and physical therapy assessment.',
    },
    {
      title: 'Full Recovery & Discharge Clearance',
      date: '2026-09-20',
      day: 'Day 30',
      completed: false,
      description: 'Target recovery completion date. Transition to routine maintenance.',
    },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn">
      
      {/* Header */}
      <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-xs flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-teal-50 text-teal-600 rounded-2xl border border-teal-100">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-900">Post-Operative Recovery Timeline</h1>
            <p className="text-xs text-slate-500">Visual milestone roadmap from surgery to full discharge</p>
          </div>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 bg-teal-100 text-teal-900 rounded-full text-xs font-bold">
          <Award className="w-4 h-4 text-teal-700" />
          <span>Day {currentPatient.recoveryDay} of {currentPatient.targetRecoveryDays} Goal</span>
        </div>
      </div>

      {/* Visual Timeline */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-8 relative">
        <div className="absolute left-8 sm:left-12 top-12 bottom-12 w-0.5 bg-slate-200" />

        <div className="space-y-8 relative z-10">
          {timelineSteps.map((step, idx) => (
            <div key={idx} className="flex items-start gap-4 sm:gap-6">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 border-2 transition-all ${
                  step.active
                    ? 'bg-teal-600 border-teal-300 text-white shadow-lg shadow-teal-500/30 scale-110 animate-pulse'
                    : step.completed
                    ? 'bg-emerald-500 border-emerald-400 text-white'
                    : 'bg-white border-slate-300 text-slate-400'
                }`}
              >
                {step.completed ? (
                  <CheckCircle2 className="w-5 h-5" />
                ) : step.active ? (
                  <Activity className="w-5 h-5" />
                ) : (
                  <Circle className="w-4 h-4" />
                )}
              </div>

              <div
                className={`flex-1 p-5 rounded-2xl border transition-all ${
                  step.active
                    ? 'bg-teal-50/70 border-teal-300 shadow-xs'
                    : step.completed
                    ? 'bg-slate-50 border-slate-200'
                    : 'bg-white border-slate-200 opacity-60'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-1">
                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-0.5 rounded-md bg-white border border-slate-200 text-slate-800 text-[11px] font-extrabold">
                      {step.day}
                    </span>
                    <h3 className="font-extrabold text-slate-900 text-base">{step.title}</h3>
                  </div>
                  <span className="text-xs font-semibold text-slate-500 flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5 text-slate-400" /> {step.date}
                  </span>
                </div>

                <p className="text-xs text-slate-600 leading-relaxed mt-1">{step.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
