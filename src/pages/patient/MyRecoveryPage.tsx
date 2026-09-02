import React from 'react';
import { useApp } from '../../context/AppContext';
import { HeartPulse, CheckCircle2, ShieldCheck, Award, Stethoscope } from 'lucide-react';

export const MyRecoveryPage: React.FC = () => {
  const { currentPatient, setActiveTab } = useApp();

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Header */}
      <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-teal-50 text-teal-600 rounded-2xl border border-teal-100">
            <HeartPulse className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-900">My Recovery Plan</h1>
            <p className="text-xs text-slate-500">Post-operative rehabilitation goals & discharge directives</p>
          </div>
        </div>

        <button
          onClick={() => setActiveTab('checkup')}
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs transition-colors flex items-center gap-1.5 shadow-xs"
        >
          <CheckCircle2 className="w-4 h-4" />
          <span>Log Daily Vitals</span>
        </button>
      </div>

      {/* RECOVERY OVERVIEW CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-teal-700 to-teal-900 text-white p-6 rounded-3xl space-y-3 shadow-lg">
          <div className="flex items-center justify-between text-teal-200 text-xs font-bold uppercase">
            <span>Discharge Progress</span>
            <Award className="w-5 h-5 text-teal-300" />
          </div>
          <div className="text-3xl font-black">Day {currentPatient.recoveryDay} <span className="text-sm font-medium text-teal-200">of {currentPatient.targetRecoveryDays} Days</span></div>
          <p className="text-xs text-teal-100 leading-relaxed">
            Target discharge clearance scheduled for <strong>September 20, 2026</strong>.
          </p>
        </div>

        <div className="bg-white p-6 rounded-3xl border border-slate-200 space-y-3 shadow-xs">
          <div className="flex items-center justify-between text-slate-400 text-xs font-bold uppercase">
            <span>Surgical Site Health</span>
            <ShieldCheck className="w-5 h-5 text-emerald-600" />
          </div>
          <div className="text-xl font-extrabold text-slate-900">Clean & Intact</div>
          <p className="text-xs text-slate-600 leading-relaxed">
            No erythema or wound discharge reported during morning checkup.
          </p>
        </div>

        <div className="bg-white p-6 rounded-3xl border border-slate-200 space-y-3 shadow-xs">
          <div className="flex items-center justify-between text-slate-400 text-xs font-bold uppercase">
            <span>Primary Surgeon</span>
            <Stethoscope className="w-5 h-5 text-blue-600" />
          </div>
          <div className="text-xl font-extrabold text-slate-900">{currentPatient.doctorName}</div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Apollo Joint Replacement Institute • Tele-consult active.
          </p>
        </div>
      </div>

      {/* REHABILITATION GOALS */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-4">
        <h3 className="font-bold text-slate-900 text-lg border-b border-slate-100 pb-3">
          Post-Op Rehabilitation Milestones
        </h3>

        <div className="space-y-3">
          {[
            { goal: 'Ankle Pumps & Quad Sets', status: 'Completed', details: '10 repetitions, 3 times daily' },
            { goal: 'Active Knee Flexion to 90°', status: 'In Progress', details: 'Achieved 85° in morning rehab session' },
            { goal: 'Independent Stair Climbing', status: 'Upcoming', details: 'Scheduled for Day 14 post-op phase' },
          ].map((item, idx) => (
            <div key={idx} className="p-4 bg-slate-50 rounded-2xl border border-slate-200 flex items-center justify-between text-xs">
              <div>
                <h4 className="font-bold text-slate-900 text-sm">{item.goal}</h4>
                <p className="text-slate-500 mt-0.5">{item.details}</p>
              </div>
              <span
                className={`px-3 py-1 rounded-full font-extrabold ${
                  item.status === 'Completed'
                    ? 'bg-emerald-100 text-emerald-800'
                    : item.status === 'In Progress'
                    ? 'bg-teal-100 text-teal-800'
                    : 'bg-slate-200 text-slate-700'
                }`}
              >
                {item.status}
              </span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
