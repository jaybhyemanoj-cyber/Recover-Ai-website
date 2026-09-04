import React, { useState, useRef, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import {
  Bot,
  Send,
  Sparkles,
  AlertTriangle,
  X,
  Loader2,
  ShieldCheck,
  PhoneCall,
  Calendar,
  Clock,
  MapPin,
  CheckCircle2,
  CalendarCheck,
  CalendarX,
  ChevronRight
} from 'lucide-react';

import type { AssistantMessage } from '../../types';

interface RecoveryAssistantModalProps {
  isOpen: boolean;
  onClose: () => void;
}

let assistantMsgSeq = 1;
const createMsgId = (type: string) => `${type}-${assistantMsgSeq++}`;

export const RecoveryAssistantModal: React.FC<RecoveryAssistantModalProps> = ({ isOpen, onClose }) => {
  const { currentPatient, setEmergencyModalOpen } = useApp();
  const [language, setLanguage] = useState<'en' | 'hi'>('en');
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [messages, setMessages] = useState<AssistantMessage[]>([
    {
      id: 'init-1',
      sender: 'assistant',
      text: `Hello ${currentPatient.name}! I am your AI Clinical & Appointment Assistant. I can help you schedule doctor appointments, find available specialist slots, check upcoming visits, or answer post-op recovery questions. How can I assist you today?`,
      language: 'en',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      quickReplies: [
        '📅 Book Doctor Appointment',
        '📋 When is my next appointment?',
        '💊 What medicines am I taking?',
        'How do I reduce knee swelling?'
      ]
    }
  ]);

  const quickPromptsEn = [
    "📅 Book doctor appointment tomorrow evening",
    "📋 When is my next appointment?",
    "🔄 Reschedule my appointment",
    "I have fever and cough. Suggest doctor",
    "💊 Show my prescribed medicines",
    "Is mild knee pain normal today?"
  ];

  const quickPromptsHi = [
    "📅 मुझे कल शाम डॉक्टर से अपॉइंटमेंट चाहिए",
    "📋 मेरी अगली अपॉइंटमेंट कब है?",
    "🔄 अपॉइंटमेंट री-शेड्यूल करें",
    "मुझे बुखार और खांसी है, डॉक्टर बताएं",
    "💊 मेरी सुझाई गई दवाएं दिखाओ",
    "क्या सर्जरी के बाद दर्द सामान्य है?"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (textToSend?: string) => {
    const query = (textToSend || inputValue).trim();
    if (!query || isLoading) return;

    const userMsg: AssistantMessage = {
      id: createMsgId('usr'),
      sender: 'user',
      text: query,
      language,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputValue('');
    setIsLoading(true);

    try {
      const res = await fetch('http://localhost:5000/api/assistant/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: query,
          language,
          patient_id: currentPatient.id,
          patient_data: {
            name: currentPatient.name,
            surgery: currentPatient.surgeryType,
            recovery_day: currentPatient.recoveryDay,
            target_recovery_days: currentPatient.targetRecoveryDays,
            doctor: currentPatient.doctorName,
            caregiver: currentPatient.caregiverName,
            caregiver_phone: currentPatient.emergencyContact?.phone || '+91 74989 64628'
          }
        })
      });

      if (!res.ok) {
        throw new Error('Assistant API response error');
      }

      const data = await res.json();
      const botMsg: AssistantMessage = {
        id: createMsgId('bot'),
        sender: 'assistant',
        text: data.response || (language === 'hi' ? 'कृपया अपने डॉक्टर से सलाह लें।' : 'Please consult your physician.'),
        language: data.language || language,
        isEmergency: data.is_emergency || false,
        actionType: data.action_type,
        actionData: data.action_data,
        quickReplies: data.quick_replies,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch {
      // Graceful fallback if backend is offline
      const fallbackText = language === 'hi'
        ? `नमस्ते ${currentPatient.name} जी! रिकवरी डे ${currentPatient.recoveryDay} पर आराम, बर्फ की सिकाई और डॉक्टर ${currentPatient.doctorName} द्वारा सुझाई गई दवाएं समय पर लें। अपॉइंटमेंट के लिए कृपया क्लिनिक से संपर्क करें।`
        : `Hello ${currentPatient.name}! On Recovery Day ${currentPatient.recoveryDay}, please follow Dr. ${currentPatient.doctorName}'s care guidelines. For urgent symptoms, please use the SOS Emergency option.`;

      const botMsg: AssistantMessage = {
        id: createMsgId('bot'),
        sender: 'assistant',
        text: fallbackText,
        language,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, botMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-3xl w-full max-w-2xl h-[88vh] max-h-[750px] flex flex-col shadow-2xl overflow-hidden relative animate-fadeIn">
        
        {/* Header */}
        <div className="bg-gradient-to-r from-teal-900 via-slate-900 to-indigo-950 p-4 sm:p-5 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-teal-500/20 text-teal-300 border border-teal-400/30 rounded-2xl shadow-md shadow-teal-500/10">
              <Bot className="w-6 h-6 text-teal-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-extrabold text-white text-base">RecoverAI Appointment & Clinical Assistant</h3>
                <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[10px] font-bold rounded-full">
                  Live Scheduling 🟢
                </span>
              </div>
              <p className="text-xs text-slate-300">
                Patient: {currentPatient.name} • Dr. {currentPatient.doctorName}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Language Toggle */}
            <div className="flex bg-slate-800/80 border border-slate-700 rounded-xl p-0.5 text-xs font-bold">
              <button
                onClick={() => setLanguage('en')}
                className={`px-2.5 py-1 rounded-lg transition-all ${
                  language === 'en' ? 'bg-teal-600 text-white shadow-xs' : 'text-slate-400 hover:text-white'
                }`}
              >
                English
              </button>
              <button
                onClick={() => setLanguage('hi')}
                className={`px-2.5 py-1 rounded-lg transition-all ${
                  language === 'hi' ? 'bg-teal-600 text-white shadow-xs' : 'text-slate-400 hover:text-white'
                }`}
              >
                हिंदी
              </button>
            </div>

            <button
              onClick={onClose}
              className="p-1.5 rounded-xl bg-slate-800/80 text-slate-400 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Safety & Navigation Banner */}
        <div className="bg-slate-950 px-4 py-2 border-b border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400">
          <div className="flex items-center gap-1.5 text-teal-400">
            <ShieldCheck className="w-3.5 h-3.5 shrink-0" />
            <span>Triage & appointment scheduling. Never diagnoses diseases.</span>
          </div>
          <button
            onClick={() => {
              onClose();
              setEmergencyModalOpen(true);
            }}
            className="text-rose-400 hover:text-rose-300 font-bold flex items-center gap-1 cursor-pointer"
          >
            <PhoneCall className="w-3 h-3" />
            <span>Emergency SOS</span>
          </button>
        </div>

        {/* Messages Body */}
        <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-slate-900/60">
          {messages.map((m) => {
            const isUser = m.sender === 'user';
            const isEmergency = m.isEmergency;

            return (
              <div
                key={m.id}
                className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
              >
                {!isUser && (
                  <div className="w-8 h-8 rounded-full bg-teal-600/30 border border-teal-500/40 text-teal-300 flex items-center justify-center shrink-0 mt-0.5">
                    <Sparkles className="w-4 h-4" />
                  </div>
                )}

                <div
                  className={`max-w-[85%] rounded-2xl p-4 text-xs sm:text-sm leading-relaxed ${
                    isUser
                      ? 'bg-teal-600 text-white rounded-tr-xs shadow-md font-medium'
                      : isEmergency
                      ? 'bg-rose-950/80 border-2 border-rose-500 text-rose-100 rounded-tl-xs shadow-xl'
                      : 'bg-slate-800/90 border border-slate-700 text-slate-100 rounded-tl-xs shadow-xs'
                  }`}
                >
                  {isEmergency && (
                    <div className="flex items-center gap-1.5 text-rose-400 font-bold text-xs uppercase mb-2">
                      <AlertTriangle className="w-4 h-4" />
                      <span>Immediate Medical Attention Required</span>
                    </div>
                  )}

                  <p className="whitespace-pre-line">{m.text}</p>

                  {/* 1. Interactive Slot Selection Cards */}
                  {m.actionType === 'slots_list' && Array.isArray(m.actionData) && m.actionData.length > 0 && (
                    <div className="mt-3 space-y-2 border-t border-slate-700/60 pt-3">
                      <div className="text-[11px] font-extrabold text-teal-300 uppercase tracking-wider flex items-center gap-1.5">
                        <CalendarCheck className="w-3.5 h-3.5" />
                        <span>Select Available Appointment Slot</span>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {m.actionData.map((slot: any, idx: number) => (
                          <div
                            key={idx}
                            className={`p-2.5 rounded-xl border transition-all ${
                              slot.recommended
                                ? 'bg-teal-950/60 border-teal-500/60 shadow-sm'
                                : 'bg-slate-900/80 border-slate-700/80 hover:border-slate-600'
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <span className="font-bold text-slate-100 text-xs truncate">{slot.doctor_name}</span>
                              {slot.recommended && (
                                <span className="px-1.5 py-0.2 bg-teal-500 text-slate-950 text-[9px] font-black rounded-sm">
                                  BEST MATCH
                                </span>
                              )}
                            </div>
                            <div className="text-[11px] text-teal-400 font-semibold mt-0.5">{slot.specialty}</div>
                            <div className="flex items-center gap-2 text-[10px] text-slate-400 mt-1">
                              <Clock className="w-3 h-3 text-slate-400" />
                              <span className="font-bold text-slate-200">{slot.time}</span>
                              <span>•</span>
                              <span>{slot.distance_km} km away</span>
                            </div>
                            <button
                              onClick={() => handleSend(`Confirm booking with ${slot.doctor_name} on ${slot.date} at ${slot.time}`)}
                              className="w-full mt-2 py-1.5 bg-teal-600 hover:bg-teal-500 text-white font-bold rounded-lg text-[11px] transition-colors flex items-center justify-center gap-1 cursor-pointer"
                            >
                              <span>Book {slot.time}</span>
                              <ChevronRight className="w-3 h-3" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 2. Confirmed Appointment Card */}
                  {m.actionType === 'appointment_card' && m.actionData && (
                    <div className="mt-3 p-3 bg-teal-950/70 border border-teal-500/60 rounded-xl space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5 text-teal-300 font-extrabold text-xs">
                          <CheckCircle2 className="w-4 h-4 text-teal-400" />
                          <span>Appointment {m.actionData.status === 'cancelled' ? 'Cancelled' : 'Confirmed'}</span>
                        </div>
                        <span className="text-[10px] bg-teal-500/20 text-teal-200 px-2 py-0.5 rounded-full font-bold">
                          ID: {m.actionData.id}
                        </span>
                      </div>
                      <div className="text-xs space-y-1 text-slate-200">
                        <div className="font-bold text-white">{m.actionData.doctorName} ({m.actionData.specialty})</div>
                        <div className="flex items-center gap-1 text-[11px] text-teal-200">
                          <Calendar className="w-3.5 h-3.5" />
                          <span>{m.actionData.date} at {m.actionData.time}</span>
                        </div>
                        <div className="flex items-center gap-1 text-[11px] text-slate-400">
                          <MapPin className="w-3.5 h-3.5" />
                          <span>{m.actionData.hospital}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* 3. Upcoming Appointments Card */}
                  {m.actionType === 'upcoming_list' && Array.isArray(m.actionData) && m.actionData.length > 0 && (
                    <div className="mt-3 space-y-2 border-t border-slate-700/60 pt-3">
                      {m.actionData.map((apt: any, i: number) => (
                        <div key={i} className="p-3 bg-slate-900/90 border border-slate-700 rounded-xl space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-white text-xs">{apt.doctorName}</span>
                            <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 text-[10px] font-extrabold rounded-md">
                              {apt.status.toUpperCase()}
                            </span>
                          </div>
                          <div className="text-[11px] text-slate-300 flex items-center gap-2">
                            <Clock className="w-3.5 h-3.5 text-teal-400" />
                            <span>{apt.date} at {apt.time}</span>
                            <span>•</span>
                            <span>{apt.hospital}</span>
                          </div>
                          <div className="flex gap-2 pt-1">
                            <button
                              onClick={() => handleSend(`Reschedule appointment ${apt.id}`)}
                              className="flex-1 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold rounded-lg text-[10px] border border-slate-700 transition-colors flex items-center justify-center gap-1 cursor-pointer"
                            >
                              <CalendarCheck className="w-3 h-3 text-teal-400" />
                              <span>Reschedule</span>
                            </button>
                            <button
                              onClick={() => handleSend(`Cancel appointment ${apt.id}`)}
                              className="flex-1 py-1.5 bg-rose-950/60 hover:bg-rose-900/80 text-rose-300 font-bold rounded-lg text-[10px] border border-rose-800/60 transition-colors flex items-center justify-center gap-1 cursor-pointer"
                            >
                              <CalendarX className="w-3 h-3 text-rose-400" />
                              <span>Cancel</span>
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* 4. Cancellation Confirmation Action Prompt */}
                  {m.actionType === 'confirm_cancel' && m.actionData && (
                    <div className="mt-3 p-3 bg-rose-950/60 border border-rose-500/50 rounded-xl space-y-2">
                      <div className="text-xs font-bold text-rose-200">
                        Cancel booking with {m.actionData.doctorName} on {m.actionData.date}?
                      </div>
                      <div className="flex gap-2 pt-1">
                        <button
                          onClick={() => handleSend(`Yes, confirm cancellation of ${m.actionData.id}`)}
                          className="flex-1 py-1.5 bg-rose-600 hover:bg-rose-700 text-white font-extrabold rounded-lg text-[11px] transition-colors cursor-pointer"
                        >
                          Confirm Cancel
                        </button>
                        <button
                          onClick={() => handleSend('Keep my appointment, do not cancel')}
                          className="flex-1 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold rounded-lg text-[11px] transition-colors cursor-pointer"
                        >
                          Keep Appointment
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Dynamic Quick Replies */}
                  {m.quickReplies && m.quickReplies.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-1.5 pt-2 border-t border-slate-700/40">
                      {m.quickReplies.map((reply, ridx) => (
                        <button
                          key={ridx}
                          onClick={() => handleSend(reply)}
                          className="px-2.5 py-1 bg-teal-950/80 hover:bg-teal-900 border border-teal-700/60 text-teal-200 text-[11px] font-semibold rounded-lg transition-colors cursor-pointer"
                        >
                          {reply}
                        </button>
                      ))}
                    </div>
                  )}

                  <span className={`text-[10px] mt-2 block ${isUser ? 'text-teal-200' : 'text-slate-400'}`}>
                    {m.timestamp}
                  </span>
                </div>
              </div>
            );
          })}

          {isLoading && (
            <div className="flex gap-3 items-center text-teal-400 text-xs">
              <div className="w-8 h-8 rounded-full bg-teal-600/30 flex items-center justify-center shrink-0">
                <Loader2 className="w-4 h-4 animate-spin" />
              </div>
              <span>Searching real doctor availability & scheduling records...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Suggestion Chips */}
        <div className="px-4 py-2 bg-slate-950/70 border-t border-slate-800 overflow-x-auto flex gap-2 no-scrollbar">
          {(language === 'hi' ? quickPromptsHi : quickPromptsEn).map((prompt, i) => (
            <button
              key={i}
              onClick={() => handleSend(prompt)}
              className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-xs rounded-full whitespace-nowrap transition-colors cursor-pointer"
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div className="p-3 sm:p-4 bg-slate-950 border-t border-slate-800 flex items-center gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder={
              language === 'hi'
                ? "अपॉइंटमेंट बुक करें या रिकवरी संबंधी प्रश्न पूछें..."
                : "Ask to book a doctor, check slots, or recovery advice..."
            }
            className="flex-1 bg-slate-900 border border-slate-700 rounded-2xl px-4 py-3 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-teal-500 transition-colors"
          />

          <button
            onClick={() => handleSend()}
            disabled={!inputValue.trim() || isLoading}
            className="p-3 bg-teal-600 hover:bg-teal-500 disabled:opacity-40 text-white rounded-2xl transition-all shadow-md shrink-0 cursor-pointer"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>

      </div>
    </div>
  );
};
