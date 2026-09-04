import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import {
  Calendar,
  Clock,
  MapPin,
  Bot,
  Plus,
  Stethoscope,
  CalendarCheck,
  CalendarX,
  Phone,
  CheckCircle2,
  RefreshCw,
  Sparkles
} from 'lucide-react';
import type { Appointment } from '../../types';

export const AppointmentsPage: React.FC = () => {
  const { currentPatient, setAssistantModalOpen } = useApp();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [doctors, setDoctors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [toastMsg, setToastMsg] = useState<string | null>(null);

  const fetchAppointmentsAndDoctors = async () => {
    setLoading(true);
    try {
      const [aptRes, docRes] = await Promise.all([
        fetch(`http://localhost:5000/api/appointments?patient_id=${currentPatient.id}`),
        fetch('http://localhost:5000/api/doctors')
      ]);

      if (aptRes.ok) {
        const data = await aptRes.json();
        setAppointments(data.appointments || []);
      }
      if (docRes.ok) {
        const docData = await docRes.json();
        setDoctors(docData.doctors || []);
      }
    } catch {
      // Local fallback
      setAppointments([
        {
          id: 'APT-1001',
          patientId: currentPatient.id,
          patientName: currentPatient.name,
          doctorId: 'DOC-01',
          doctorName: currentPatient.doctorName,
          specialty: 'Orthopedic Surgeon',
          hospital: 'Apollo Joint Replacement Institute',
          distanceKm: 2.4,
          date: new Date(Date.now() + 86400000 * 2).toISOString().split('T')[0],
          time: '05:30 PM',
          status: 'confirmed',
          type: 'in_person',
          reason: 'Post-Op Knee Replacement Day 10 Suture Inspection & X-Ray Review'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAppointmentsAndDoctors();
  }, [currentPatient.id]);

  const handleCancel = async (aptId: string) => {
    try {
      const res = await fetch(`http://localhost:5000/api/appointments/${aptId}/cancel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason: 'Patient requested cancellation' })
      });
      if (res.ok) {
        setToastMsg(`Appointment ${aptId} cancelled successfully.`);
        fetchAppointmentsAndDoctors();
      }
    } catch {
      setToastMsg('Failed to cancel appointment.');
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fadeIn">
      {/* Toast Alert */}
      {toastMsg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-2xl flex items-center justify-between text-xs font-bold animate-fadeIn">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>{toastMsg}</span>
          </div>
          <button onClick={() => setToastMsg(null)} className="text-emerald-600 hover:text-emerald-950">✕</button>
        </div>
      )}

      {/* Header Card */}
      <div className="bg-gradient-to-r from-slate-900 via-teal-950 to-slate-900 p-6 sm:p-8 rounded-3xl text-white shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-6 border border-slate-800">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 bg-teal-500/20 text-teal-300 border border-teal-500/30 rounded-full text-xs font-extrabold uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5" />
              <span>AI Connected Scheduling</span>
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">Doctor Appointments & Schedule</h1>
          <p className="text-xs sm:text-sm text-slate-300 max-w-xl leading-relaxed">
            Manage your post-operative follow-up consultations, review upcoming doctor visits, or use the conversational AI Assistant for natural language scheduling.
          </p>
        </div>

        <button
          onClick={() => setAssistantModalOpen(true)}
          className="px-5 py-3.5 bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-slate-950 font-black text-xs uppercase tracking-wider rounded-2xl transition-all shadow-lg shadow-teal-500/20 flex items-center gap-2.5 shrink-0 cursor-pointer active:scale-95"
        >
          <Bot className="w-5 h-5" />
          <span>Book via AI Assistant</span>
        </button>
      </div>

      {/* Main Grid: Scheduled Appointments & Available Doctors */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left 2 Cols: Active Scheduled Consultations */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-black text-slate-900 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-teal-600" />
              <span>Your Scheduled Consultations</span>
            </h2>
            <button
              onClick={fetchAppointmentsAndDoctors}
              className="p-1.5 hover:bg-slate-100 rounded-lg text-slate-500 text-xs font-semibold flex items-center gap-1 cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Refresh</span>
            </button>
          </div>

          {loading ? (
            <div className="p-8 bg-white rounded-3xl border border-slate-200 text-center text-xs text-slate-500">
              Loading scheduled appointments...
            </div>
          ) : appointments.length === 0 ? (
            <div className="p-8 bg-white rounded-3xl border border-slate-200 text-center space-y-3">
              <CalendarX className="w-10 h-10 text-slate-300 mx-auto" />
              <div className="font-bold text-slate-700 text-sm">No Upcoming Appointments</div>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                You currently have no scheduled appointments. Use our AI Assistant to book with your surgeon or physician.
              </p>
              <button
                onClick={() => setAssistantModalOpen(true)}
                className="px-4 py-2 bg-teal-600 text-white text-xs font-bold rounded-xl shadow-xs inline-flex items-center gap-1.5 cursor-pointer"
              >
                <Plus className="w-4 h-4" />
                <span>Schedule New Appointment</span>
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {appointments.map((apt) => (
                <div
                  key={apt.id}
                  className="bg-white rounded-3xl p-5 sm:p-6 border border-slate-200 shadow-xs space-y-4 hover:border-teal-300 transition-all"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-11 h-11 bg-teal-50 text-teal-700 border border-teal-200 rounded-2xl flex items-center justify-center font-bold">
                        <Stethoscope className="w-6 h-6 text-teal-600" />
                      </div>
                      <div>
                        <h3 className="font-extrabold text-slate-900 text-sm">{apt.doctorName}</h3>
                        <p className="text-xs text-teal-700 font-semibold">{apt.specialty}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[11px] font-extrabold">
                        {apt.status.toUpperCase()}
                      </span>
                      <span className="text-[10px] text-slate-400 font-mono">ID: {apt.id}</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                    <div className="flex items-center gap-2 text-slate-700">
                      <Clock className="w-4 h-4 text-slate-400" />
                      <span className="font-bold">{apt.date}</span>
                      <span>at</span>
                      <span className="font-extrabold text-teal-700">{apt.time}</span>
                    </div>

                    <div className="flex items-center gap-2 text-slate-600">
                      <MapPin className="w-4 h-4 text-slate-400" />
                      <span className="truncate">{apt.hospital} ({apt.distanceKm || 2.4} km)</span>
                    </div>
                  </div>

                  <div className="p-3 bg-slate-50 rounded-2xl text-xs text-slate-600">
                    <strong className="text-slate-800 font-semibold block text-[11px] uppercase tracking-wider mb-0.5">
                      Consultation Purpose
                    </strong>
                    <span>{apt.reason}</span>
                  </div>

                  <div className="flex items-center justify-end gap-2 pt-1 border-t border-slate-100">
                    <button
                      onClick={() => setAssistantModalOpen(true)}
                      className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl text-xs flex items-center gap-1 transition-colors cursor-pointer"
                    >
                      <CalendarCheck className="w-3.5 h-3.5 text-teal-600" />
                      <span>Reschedule via AI</span>
                    </button>
                    <button
                      onClick={() => handleCancel(apt.id)}
                      className="px-3 py-1.5 bg-rose-50 hover:bg-rose-100 text-rose-700 font-bold rounded-xl text-xs flex items-center gap-1 transition-colors cursor-pointer"
                    >
                      <CalendarX className="w-3.5 h-3.5 text-rose-600" />
                      <span>Cancel</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right 1 Col: Specialist Directory & Quick Book */}
        <div className="space-y-4">
          <h2 className="text-base font-black text-slate-900 flex items-center gap-2">
            <Stethoscope className="w-5 h-5 text-teal-600" />
            <span>Recommended Specialists</span>
          </h2>

          <div className="space-y-3">
            {doctors.map((doc) => (
              <div
                key={doc.id}
                className="bg-white rounded-3xl p-4 border border-slate-200 shadow-xs space-y-2 hover:border-slate-300 transition-all"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h4 className="font-bold text-slate-900 text-xs">{doc.name}</h4>
                    <p className="text-[11px] text-teal-700 font-semibold">{doc.specialty}</p>
                    <p className="text-[10px] text-slate-400">{doc.hospital}</p>
                  </div>
                  <span className="px-2 py-0.5 bg-amber-50 text-amber-800 text-[10px] font-extrabold rounded-md shrink-0">
                    ⭐ {doc.rating}
                  </span>
                </div>

                <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1 border-t border-slate-100">
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3 h-3 text-slate-400" />
                    <span>{doc.distance_km} km</span>
                  </span>
                  <span className="font-bold text-slate-700">₹{doc.consultation_fee}</span>
                </div>

                <button
                  onClick={() => setAssistantModalOpen(true)}
                  className="w-full py-2 bg-teal-50 hover:bg-teal-600 text-teal-800 hover:text-white font-extrabold rounded-xl text-xs transition-all flex items-center justify-center gap-1 cursor-pointer"
                >
                  <Bot className="w-3.5 h-3.5" />
                  <span>Book Slot with AI</span>
                </button>
              </div>
            ))}
          </div>

          {/* Emergency Assistance Notice */}
          <div className="p-4 bg-rose-50 border border-rose-200 rounded-3xl space-y-1.5">
            <div className="flex items-center gap-1.5 text-rose-800 font-bold text-xs">
              <Phone className="w-4 h-4 text-rose-600" />
              <span>Acute Symptoms?</span>
            </div>
            <p className="text-[11px] text-rose-700 leading-relaxed">
              Do not wait for regular appointment slots if you experience chest pain, severe shortness of breath, or bleeding. Tap SOS Emergency immediately.
            </p>
          </div>
        </div>

      </div>
    </div>
  );
};
