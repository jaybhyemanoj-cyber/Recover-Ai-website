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
  PhoneCall
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
      text: `Hello ${currentPatient.name}! I am your Post-Op Recovery Companion. You are on Day ${currentPatient.recoveryDay} of recovery from your ${currentPatient.surgeryType}. How can I assist you with your recovery plan today?`,
      language: 'en',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);

  const quickPromptsEn = [
    "Is mild knee pain normal today?",
    "How do I reduce surgical swelling?",
    "Can I take a regular shower?",
    "When should I walk with my cane?"
  ];

  const quickPromptsHi = [
    "क्या सर्जरी के बाद हल्का दर्द सामान्य है?",
    "घुटने की सूजन कैसे कम करें?",
    "क्या मैं नहा सकता हूँ?",
    "छड़ी के साथ कितनी देर चलना चाहिए?"
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
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch {
      // Local graceful fallback if backend is unreachable
      const fallbackText = language === 'hi'
        ? `नमस्ते ${currentPatient.name} जी! रिकवरी डे ${currentPatient.recoveryDay} पर आराम, बर्फ की सिकाई और डॉक्टर ${currentPatient.doctorName} द्वारा सुझाई गई दवाएं समय पर लें। किसी भी तेज दर्द या आपातकाल में तुरंत SOS दबाएं।`
        : `Hello ${currentPatient.name}! On Recovery Day ${currentPatient.recoveryDay}, please focus on scheduled rest, cold compression, and following Dr. ${currentPatient.doctorName}'s guidelines. Press SOS for acute symptoms.`;

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
      <div className="bg-slate-900 border border-slate-700 rounded-3xl w-full max-w-2xl h-[85vh] max-h-[700px] flex flex-col shadow-2xl overflow-hidden relative animate-fadeIn">
        
        {/* Header */}
        <div className="bg-gradient-to-r from-teal-900 via-slate-900 to-indigo-950 p-4 sm:p-5 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-teal-500/20 text-teal-300 border border-teal-400/30 rounded-2xl">
              <Bot className="w-6 h-6 text-teal-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-extrabold text-white text-base">RecoverAI Recovery Assistant</h3>
                <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[10px] font-bold rounded-full">
                  AI Guardrails Active 🟢
                </span>
              </div>
              <p className="text-xs text-slate-300">
                Tailored for {currentPatient.name} • {currentPatient.surgeryType}
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

        {/* Safety Disclaimer Banner */}
        <div className="bg-slate-950 px-4 py-2 border-b border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400">
          <div className="flex items-center gap-1.5 text-teal-400">
            <ShieldCheck className="w-3.5 h-3.5 shrink-0" />
            <span>Non-prescriptive recovery guidance. For emergencies, tap SOS.</span>
          </div>
          <button
            onClick={() => {
              onClose();
              setEmergencyModalOpen(true);
            }}
            className="text-rose-400 hover:text-rose-300 font-bold flex items-center gap-1"
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
                  className={`max-w-[82%] rounded-2xl p-4 text-xs sm:text-sm leading-relaxed ${
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
              <span>Processing clinical guidelines...</span>
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
              className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-xs rounded-full whitespace-nowrap transition-colors"
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
                ? "रिकवरी संबंधी कोई भी प्रश्न पूछें..."
                : "Ask any recovery question..."
            }
            className="flex-1 bg-slate-900 border border-slate-700 rounded-2xl px-4 py-3 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-teal-500 transition-colors"
          />

          <button
            onClick={() => handleSend()}
            disabled={!inputValue.trim() || isLoading}
            className="p-3 bg-teal-600 hover:bg-teal-500 disabled:opacity-40 text-white rounded-2xl transition-all shadow-md shrink-0"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>

      </div>
    </div>
  );
};
