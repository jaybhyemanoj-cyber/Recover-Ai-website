import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { VitalCard } from '../../components/ui/VitalCard';
import { mockRecoveryGraphData } from '../../data/mockData';
import { Activity, FileText, Plus, MessageSquare } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export const PatientDetailPage: React.FC = () => {
  const { currentPatient, medications, clinicalNotes, addClinicalNote } = useApp();
  const [newNoteText, setNewNoteText] = useState('');
  const [noteCategory, setNoteCategory] = useState<'Observation' | 'Prescription Change' | 'Discharge Plan' | 'General'>('Observation');
  const [showNoteModal, setShowNoteModal] = useState(false);

  const handleAddNote = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNoteText.trim()) return;

    addClinicalNote({
      id: `CN-${Date.now().toString().slice(-4)}`,
      patientId: currentPatient.id,
      doctorName: 'Dr. Vikramaditya Rao',
      date: new Date().toISOString().split('T')[0],
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      note: newNoteText,
      category: noteCategory,
    });

    setNewNoteText('');
    setShowNoteModal(false);
  };

  const patientNotes = clinicalNotes.filter((n) => n.patientId === currentPatient.id);

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* HEADER PROFILE */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="flex items-start gap-4">
          <div className="w-16 h-16 rounded-2xl bg-teal-600 text-white font-black text-xl flex items-center justify-center shadow-md">
            {currentPatient.name.split(' ').map((n) => n[0]).join('')}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-black text-slate-900">{currentPatient.name}</h1>
              <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700">
                MRN: {currentPatient.id}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              {currentPatient.surgeryType} • Discharged {currentPatient.dischargeDate} (Day {currentPatient.recoveryDay})
            </p>
            <div className="flex items-center gap-4 text-xs font-semibold text-slate-700 mt-2">
              <span>Caregiver: <strong>{currentPatient.caregiverName}</strong></span>
              <span>Room: <strong>{currentPatient.roomNumber}</strong></span>
            </div>
          </div>
        </div>

        <div className="flex flex-col items-start md:items-end gap-2 shrink-0">
          <span className="text-[10px] text-slate-400 font-bold uppercase">Clinical Triage Rating</span>
          <StatusBadge status={currentPatient.status} size="lg" />
        </div>
      </div>

      {/* VITALS GRID */}
      <div>
        <h2 className="text-base font-bold text-slate-900 mb-3 flex items-center gap-2">
          <Activity className="w-5 h-5 text-teal-600" />
          <span>Patient Telemetry Summary</span>
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <VitalCard title="Temperature" value={currentPatient.vitals.temperature} unit="°F" idealRange="98.6 °F" type="temp" />
          <VitalCard title="Blood Pressure" value={`${currentPatient.vitals.bpSystolic}/${currentPatient.vitals.bpDiastolic}`} unit="mmHg" idealRange="120/80" type="bp" />
          <VitalCard title="Heart Rate" value={currentPatient.vitals.heartRate} unit="bpm" idealRange="70-80" type="hr" />
          <VitalCard title="Oxygen SpO2" value={currentPatient.vitals.spO2} unit="%" idealRange="98%" type="spo2" />
          <VitalCard title="Pain Score" value={`${currentPatient.vitals.painLevel}/10`} unit="Score" idealRange="< 3" type="pain" />
          <VitalCard title="Mobility" value={currentPatient.vitals.mobility.split(' ')[0]} unit="" idealRange="Active" type="mobility" />
        </div>
      </div>

      {/* RECOVERY TREND CHART */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs">
        <h3 className="font-bold text-slate-900 text-lg mb-4">Post-Op Recovery Trajectory</h3>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={mockRecoveryGraphData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="day" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderRadius: '12px', color: '#fff' }} />
              <Line type="monotone" dataKey="pain" name="Pain Level" stroke="#f43f5e" strokeWidth={3} />
              <Line type="monotone" dataKey="mobility" name="Mobility Score %" stroke="#14b8a6" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* CLINICAL NOTES & PRESCRIPTIONS ROW */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Doctor Clinical Notes */}
        <div className="lg:col-span-7 bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-teal-600" />
              <h3 className="font-bold text-slate-900 text-base">Doctor Clinical Notes</h3>
            </div>
            <button
              onClick={() => setShowNoteModal(true)}
              className="px-3 py-1.5 bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs rounded-xl shadow-2xs flex items-center gap-1"
            >
              <Plus className="w-4 h-4" />
              <span>Add Note</span>
            </button>
          </div>

          <div className="space-y-3">
            {patientNotes.length === 0 ? (
              <p className="text-xs text-slate-400 py-6 text-center">No clinical notes recorded yet.</p>
            ) : (
              patientNotes.map((note) => (
                <div key={note.id} className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-extrabold text-slate-900">{note.doctorName}</span>
                    <span className="text-[11px] text-slate-400">{note.date} • {note.time}</span>
                  </div>
                  <span className="px-2 py-0.5 rounded-md bg-teal-100 text-teal-800 text-[10px] font-bold inline-block">
                    {note.category}
                  </span>
                  <p className="text-xs text-slate-700 leading-relaxed pt-1">{note.note}</p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Prescriptions Overview */}
        <div className="lg:col-span-5 bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-teal-600" />
              <h3 className="font-bold text-slate-900 text-base">Active Orders</h3>
            </div>
            <span className="text-xs text-slate-500 font-bold">{medications.length} Prescribed</span>
          </div>

          <div className="space-y-2.5">
            {medications.map((med) => (
              <div key={med.id} className="p-3.5 bg-slate-50 rounded-2xl border border-slate-200 text-xs space-y-1">
                <div className="flex items-center justify-between">
                  <strong className="text-slate-900 font-extrabold">{med.name} ({med.dosage})</strong>
                  <span className="text-teal-700 font-bold">{med.scheduledTime}</span>
                </div>
                <div className="text-slate-500">{med.timing} • {med.durationDays} Days</div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* ADD NOTE MODAL */}
      {showNoteModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white w-full max-w-md rounded-3xl p-6 shadow-2xl border border-slate-200 space-y-4">
            <h3 className="font-extrabold text-slate-900 text-lg">Add Doctor Clinical Note</h3>

            <form onSubmit={handleAddNote} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Category</label>
                <select
                  value={noteCategory}
                  onChange={(e) => setNoteCategory(e.target.value as any)}
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold"
                >
                  <option value="Observation">Observation</option>
                  <option value="Prescription Change">Prescription Change</option>
                  <option value="Discharge Plan">Discharge Plan</option>
                  <option value="General">General</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Clinical Observation</label>
                <textarea
                  rows={4}
                  value={newNoteText}
                  onChange={(e) => setNewNoteText(e.target.value)}
                  placeholder="Enter medical evaluation..."
                  className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium"
                  required
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowNoteModal(false)}
                  className="px-4 py-2 bg-slate-100 text-slate-700 rounded-xl text-xs font-bold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-teal-600 text-white rounded-xl text-xs font-extrabold"
                >
                  Save Note
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};
