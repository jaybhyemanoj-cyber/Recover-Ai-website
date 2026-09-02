import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { StatusBadge } from '../../components/ui/StatusBadge';
import type { CheckupSubmission, TriageStatus } from '../../types';
import {
  ClipboardCheck,
  Thermometer,
  Activity,
  Smile,
  Gauge,
  AlertCircle,
  CheckCircle2,
  ArrowRight,
  ArrowLeft,
  RotateCcw,
  Sparkles,
} from 'lucide-react';

export const DailyHealthCheckPage: React.FC = () => {
  const { addCheckupSubmission } = useApp();
  const [step, setStep] = useState<number>(1);
  const [submitted, setSubmitted] = useState<CheckupSubmission | null>(null);

  // Form State
  const [temp, setTemp] = useState<number>(98.6);
  const [systolic, setSystolic] = useState<number>(120);
  const [diastolic, setDiastolic] = useState<number>(80);
  const [heartRate, setHeartRate] = useState<number>(72);
  const [spO2, setSpO2] = useState<number>(98);
  const [painLevel, setPainLevel] = useState<number>(2);
  const [mobility, setMobility] = useState<string>('Independent Walking with Cane');
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([]);
  const [notes, setNotes] = useState<string>('');

  const symptomList = [
    'Fever',
    'Dizziness',
    'Nausea',
    'Vomiting',
    'Weakness',
    'Breathing difficulty',
    'Swelling',
    'Redness',
    'Wound discharge',
  ];

  const toggleSymptom = (sym: string) => {
    if (selectedSymptoms.includes(sym)) {
      setSelectedSymptoms((prev) => prev.filter((s) => s !== sym));
    } else {
      setSelectedSymptoms((prev) => [...prev, sym]);
    }
  };

  // Mock Triage Scoring Algorithm
  const calculateTriage = (): { status: TriageStatus; reasoning: string } => {
    const isHighTemp = temp > 101.0;
    const isHighPain = painLevel >= 8;
    const isCriticalSymptoms = selectedSymptoms.includes('Breathing difficulty') || selectedSymptoms.includes('Wound discharge');

    if (isHighTemp || isHighPain || isCriticalSymptoms || spO2 < 93) {
      return {
        status: 'critical',
        reasoning:
          'Critical triage triggered due to elevated temperature, high pain score, low oxygen saturation, or urgent clinical symptoms. Caregiver dispatch notified.',
      };
    }

    if (temp > 99.5 || painLevel >= 5 || selectedSymptoms.length >= 2 || spO2 < 96) {
      return {
        status: 'doctor_review',
        reasoning:
          'Doctor review recommended. Moderate symptoms or elevated pain score logged during morning health assessment.',
      };
    }

    if (temp > 99.0 || painLevel >= 4 || selectedSymptoms.length === 1) {
      return {
        status: 'attention',
        reasoning:
          'Attention needed. Mild symptoms detected. Continue taking prescribed medications and rest.',
      };
    }

    return {
      status: 'stable',
      reasoning:
        'All vital telemetry parameters, pain levels, and mobility scores are within optimal target recovery ranges.',
    };
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const triage = calculateTriage();

    const newSub: CheckupSubmission = {
      id: `CHK-${Date.now().toString().slice(-4)}`,
      date: new Date().toLocaleString([], { dateStyle: 'short', timeStyle: 'short' }),
      temperature: temp,
      systolicBp: systolic,
      diastolicBp: diastolic,
      heartRate,
      spO2,
      painLevel,
      mobility,
      symptoms: selectedSymptoms,
      notes,
      resultStatus: triage.status,
      triageReasoning: triage.reasoning,
    };

    addCheckupSubmission(newSub);
    setSubmitted(newSub);
  };

  const resetForm = () => {
    setSubmitted(null);
    setStep(1);
    setTemp(98.6);
    setSystolic(120);
    setDiastolic(80);
    setHeartRate(72);
    setSpO2(98);
    setPainLevel(2);
    setSelectedSymptoms([]);
    setNotes('');
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fadeIn">
      
      {/* Header */}
      <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-xs flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-teal-50 text-teal-600 rounded-2xl border border-teal-100">
            <ClipboardCheck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-900">Daily Health Checkup</h1>
            <p className="text-xs text-slate-500">Multi-step post-operative symptom triage assessment</p>
          </div>
        </div>

        {!submitted && (
          <div className="hidden sm:flex items-center gap-1.5 text-xs font-bold text-slate-500 bg-slate-50 px-3 py-1.5 rounded-xl border border-slate-200">
            <span>Step {step} of 6</span>
          </div>
        )}
      </div>

      {/* SUBMITTED RESULT VIEW */}
      {submitted ? (
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-xl space-y-6 animate-fadeIn">
          
          <div className="text-center space-y-3">
            <div className="w-16 h-16 bg-teal-50 text-teal-600 rounded-full mx-auto flex items-center justify-center border-4 border-teal-100">
              <CheckCircle2 className="w-10 h-10" />
            </div>
            <h2 className="text-2xl font-black text-slate-900">Daily Checkup Submitted!</h2>
            <p className="text-xs text-slate-500">Timestamp: {submitted.date}</p>
          </div>

          {/* Triage Output Card */}
          <div className="bg-slate-50 border border-slate-200 rounded-3xl p-6 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Calculated Recovery Triage</span>
              <StatusBadge status={submitted.resultStatus} size="lg" />
            </div>

            <p className="text-sm font-medium text-slate-700 leading-relaxed bg-white p-4 rounded-2xl border border-slate-200">
              "{submitted.triageReasoning}"
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
              <div className="p-3 bg-white rounded-2xl border border-slate-100">
                <span className="text-[10px] text-slate-400 font-bold block">Temperature</span>
                <strong className="text-base text-slate-900">{submitted.temperature} °F</strong>
              </div>
              <div className="p-3 bg-white rounded-2xl border border-slate-100">
                <span className="text-[10px] text-slate-400 font-bold block">BP / HR</span>
                <strong className="text-base text-slate-900">{submitted.systolicBp}/{submitted.diastolicBp} • {submitted.heartRate}</strong>
              </div>
              <div className="p-3 bg-white rounded-2xl border border-slate-100">
                <span className="text-[10px] text-slate-400 font-bold block">Pain Score</span>
                <strong className="text-base text-slate-900">{submitted.painLevel}/10</strong>
              </div>
              <div className="p-3 bg-white rounded-2xl border border-slate-100">
                <span className="text-[10px] text-slate-400 font-bold block">SpO2 Oxygen</span>
                <strong className="text-base text-slate-900">{submitted.spO2} %</strong>
              </div>
            </div>
          </div>

          <button
            onClick={resetForm}
            className="w-full py-3 bg-slate-900 hover:bg-slate-800 text-white font-extrabold rounded-2xl text-xs transition-colors flex items-center justify-center gap-2"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Submit Another Daily Log</span>
          </button>
        </div>
      ) : (
        /* MULTI-STEP FORM */
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
          
          {/* Progress Bar */}
          <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
            <div
              className="bg-gradient-to-r from-teal-500 to-emerald-500 h-full transition-all duration-300"
              style={{ width: `${(step / 6) * 100}%` }}
            />
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            
            {/* STEP 1: TEMPERATURE */}
            {step === 1 && (
              <div className="space-y-4 animate-fadeIn">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-amber-50 text-amber-600 rounded-2xl">
                    <Thermometer className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-xs uppercase font-bold text-teal-600">Step 1 of 6</span>
                    <h3 className="text-xl font-bold text-slate-900">Body Temperature (°F)</h3>
                  </div>
                </div>

                <div className="p-6 bg-slate-50 rounded-3xl border border-slate-200 space-y-4">
                  <div className="flex items-center justify-center gap-2 text-4xl font-black text-slate-900">
                    <span>{temp}</span>
                    <span className="text-xl text-slate-400">°F</span>
                  </div>

                  <input
                    type="range"
                    min="95.0"
                    max="104.0"
                    step="0.1"
                    value={temp}
                    onChange={(e) => setTemp(parseFloat(e.target.value))}
                    className="w-full h-3 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-teal-600"
                  />

                  <div className="flex justify-between text-xs font-semibold text-slate-500">
                    <span>95.0 °F (Hypothermia)</span>
                    <span className="text-emerald-600 font-bold">98.6 °F (Normal)</span>
                    <span>104.0 °F (High Fever)</span>
                  </div>
                </div>
              </div>
            )}

            {/* STEP 2: BP, HR, SPO2 */}
            {step === 2 && (
              <div className="space-y-4 animate-fadeIn">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-blue-50 text-blue-600 rounded-2xl">
                    <Activity className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-xs uppercase font-bold text-teal-600">Step 2 of 6</span>
                    <h3 className="text-xl font-bold text-slate-900">Blood Pressure, Heart Rate & SpO2</h3>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2">
                    <label className="text-xs font-bold text-slate-700 block">Systolic BP (mmHg)</label>
                    <input
                      type="number"
                      value={systolic}
                      onChange={(e) => setSystolic(parseInt(e.target.value))}
                      className="w-full p-2.5 bg-white border border-slate-200 rounded-xl text-base font-extrabold"
                    />
                  </div>

                  <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2">
                    <label className="text-xs font-bold text-slate-700 block">Diastolic BP (mmHg)</label>
                    <input
                      type="number"
                      value={diastolic}
                      onChange={(e) => setDiastolic(parseInt(e.target.value))}
                      className="w-full p-2.5 bg-white border border-slate-200 rounded-xl text-base font-extrabold"
                    />
                  </div>

                  <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2">
                    <label className="text-xs font-bold text-slate-700 block">Heart Rate (bpm)</label>
                    <input
                      type="number"
                      value={heartRate}
                      onChange={(e) => setHeartRate(parseInt(e.target.value))}
                      className="w-full p-2.5 bg-white border border-slate-200 rounded-xl text-base font-extrabold"
                    />
                  </div>

                  <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2">
                    <label className="text-xs font-bold text-slate-700 block">Oxygen Saturation SpO2 (%)</label>
                    <input
                      type="number"
                      value={spO2}
                      onChange={(e) => setSpO2(parseInt(e.target.value))}
                      className="w-full p-2.5 bg-white border border-slate-200 rounded-xl text-base font-extrabold"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* STEP 3: PAIN LEVEL 0-10 */}
            {step === 3 && (
              <div className="space-y-4 animate-fadeIn">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-purple-50 text-purple-600 rounded-2xl">
                    <Smile className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-xs uppercase font-bold text-teal-600">Step 3 of 6</span>
                    <h3 className="text-xl font-bold text-slate-900">Current Pain Level (0 – 10 Visual Scale)</h3>
                  </div>
                </div>

                <div className="p-6 bg-slate-50 rounded-3xl border border-slate-200 space-y-5 text-center">
                  <div className="text-4xl font-black text-slate-900">
                    {painLevel} <span className="text-lg text-slate-400 font-medium">/ 10</span>
                  </div>

                  <div className="flex justify-center gap-2">
                    {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
                      <button
                        type="button"
                        key={num}
                        onClick={() => setPainLevel(num)}
                        className={`w-9 h-11 rounded-xl text-xs font-black transition-all ${
                          painLevel === num
                            ? 'bg-purple-600 text-white shadow-md scale-110'
                            : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-100'
                        }`}
                      >
                        {num}
                      </button>
                    ))}
                  </div>

                  <p className="text-xs font-semibold text-purple-700 bg-purple-50 p-3 rounded-2xl border border-purple-200">
                    {painLevel === 0
                      ? '🟢 No Pain'
                      : painLevel <= 3
                      ? '🟢 Mild Discomfort (Manageable)'
                      : painLevel <= 6
                      ? '🟡 Moderate Pain (Requires Medication)'
                      : '🔴 Severe Intolerable Pain (Requires Immediate Doctor Review)'}
                  </p>
                </div>
              </div>
            )}

            {/* STEP 4: MOBILITY */}
            {step === 4 && (
              <div className="space-y-4 animate-fadeIn">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-indigo-50 text-indigo-600 rounded-2xl">
                    <Gauge className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-xs uppercase font-bold text-teal-600">Step 4 of 6</span>
                    <h3 className="text-xl font-bold text-slate-900">Mobility Assessment</h3>
                  </div>
                </div>

                <div className="space-y-2.5">
                  {[
                    'Bed Rest Required (Inability to stand)',
                    'Assisted Bed Exit & Standing',
                    'Assisted Walking with Support/Crutches',
                    'Independent Walking with Cane',
                    'Normal Unassisted Walking',
                  ].map((mob) => (
                    <button
                      type="button"
                      key={mob}
                      onClick={() => setMobility(mob)}
                      className={`w-full p-4 rounded-2xl text-left border text-xs font-bold transition-all flex items-center justify-between ${
                        mobility === mob
                          ? 'bg-teal-50 border-teal-500 text-teal-900 shadow-2xs'
                          : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                      }`}
                    >
                      <span>{mob}</span>
                      {mobility === mob && <CheckCircle2 className="w-4 h-4 text-teal-600" />}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* STEP 5: SYMPTOMS CHECKLIST */}
            {step === 5 && (
              <div className="space-y-4 animate-fadeIn">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-rose-50 text-rose-600 rounded-2xl">
                    <AlertCircle className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-xs uppercase font-bold text-teal-600">Step 5 of 6</span>
                    <h3 className="text-xl font-bold text-slate-900">Symptom Checklist</h3>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {symptomList.map((sym) => {
                    const isChecked = selectedSymptoms.includes(sym);
                    return (
                      <button
                        type="button"
                        key={sym}
                        onClick={() => toggleSymptom(sym)}
                        className={`p-3.5 rounded-2xl text-left border text-xs font-bold transition-all flex items-center justify-between ${
                          isChecked
                            ? 'bg-rose-50 border-rose-400 text-rose-900 shadow-2xs'
                            : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                        }`}
                      >
                        <span>{sym}</span>
                        <input type="checkbox" checked={isChecked} readOnly className="rounded-md text-rose-600" />
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {/* STEP 6: ADDITIONAL NOTES & SUBMIT */}
            {step === 6 && (
              <div className="space-y-4 animate-fadeIn">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-emerald-50 text-emerald-600 rounded-2xl">
                    <Sparkles className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-xs uppercase font-bold text-teal-600">Step 6 of 6</span>
                    <h3 className="text-xl font-bold text-slate-900">Additional Observations & Submit</h3>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                    Patient Recovery Notes / Concerns
                  </label>
                  <textarea
                    rows={4}
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Describe wound appearance, appetite, sleep quality or any unusual discomfort..."
                    className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-medium text-slate-900 focus:outline-hidden focus:ring-2 focus:ring-teal-500"
                  />
                </div>
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-100">
              {step > 1 ? (
                <button
                  type="button"
                  onClick={() => setStep((s) => s - 1)}
                  className="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl text-xs flex items-center gap-1.5 transition-colors"
                >
                  <ArrowLeft className="w-4 h-4" />
                  <span>Previous</span>
                </button>
              ) : (
                <div />
              )}

              {step < 6 ? (
                <button
                  type="button"
                  onClick={() => setStep((s) => s + 1)}
                  className="px-6 py-2.5 bg-teal-600 hover:bg-teal-700 text-white font-extrabold rounded-xl text-xs flex items-center gap-1.5 transition-all shadow-md"
                >
                  <span>Next Step</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              ) : (
                <button
                  type="submit"
                  className="px-8 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-black rounded-2xl text-xs transition-all shadow-lg flex items-center gap-2"
                >
                  <span>Submit Daily Health Checkup</span>
                  <CheckCircle2 className="w-5 h-5" />
                </button>
              )}
            </div>

          </form>
        </div>
      )}

    </div>
  );
};
