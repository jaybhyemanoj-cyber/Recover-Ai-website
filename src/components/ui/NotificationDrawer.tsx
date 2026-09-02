import React from 'react';
import { useApp } from '../../context/AppContext';
import { Bell, Check, X } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

interface NotificationDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const NotificationDrawer: React.FC<NotificationDrawerProps> = ({ isOpen, onClose }) => {
  const { alerts, acknowledgeAlert, setActiveTab, setRole, role } = useApp();

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/30 backdrop-blur-2xs animate-fadeIn">
      <div className="absolute inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-white shadow-2xl border-l border-slate-200 flex flex-col">
          {/* Drawer Header */}
          <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/80">
            <div className="flex items-center gap-2.5">
              <div className="p-2 bg-teal-50 text-teal-600 rounded-xl border border-teal-100">
                <Bell className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-lg">Alert Center</h3>
                <p className="text-xs text-slate-500">Real-time incident & health updates</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-200/60 rounded-full transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Drawer Content */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {alerts.length === 0 ? (
              <div className="text-center py-12 text-slate-400">
                <Bell className="w-12 h-12 mx-auto mb-2 opacity-30" />
                <p>No notifications available.</p>
              </div>
            ) : (
              alerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`p-4 rounded-2xl border transition-all ${
                    alert.acknowledged
                      ? 'bg-slate-50 border-slate-200 opacity-75'
                      : alert.severity === 'critical'
                      ? 'bg-rose-50/60 border-rose-200 shadow-xs'
                      : 'bg-white border-slate-200 shadow-2xs hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <StatusBadge status={alert.severity} size="sm" />
                    <span className="text-[11px] text-slate-400 font-medium">{alert.time}</span>
                  </div>

                  <h4 className="font-bold text-slate-900 text-sm mb-1">{alert.title}</h4>
                  <p className="text-xs text-slate-600 mb-3 leading-relaxed">{alert.message}</p>

                  <div className="flex items-center justify-between pt-2 border-t border-slate-100/80 text-xs">
                    <span className="text-slate-500 font-medium">Patient: <strong className="text-slate-700">{alert.patientName}</strong></span>
                    {alert.acknowledged ? (
                      <span className="flex items-center gap-1 text-emerald-600 font-medium text-[11px]">
                        <Check className="w-3.5 h-3.5" /> Ack by {alert.acknowledgedBy || 'User'}
                      </span>
                    ) : (
                      <button
                        onClick={() => acknowledgeAlert(alert.id)}
                        className="px-3 py-1 bg-slate-900 hover:bg-slate-800 text-white rounded-lg font-semibold text-xs transition-colors shadow-2xs"
                      >
                        Acknowledge
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Drawer Footer */}
          <div className="p-4 border-t border-slate-100 bg-slate-50/80 flex items-center justify-between">
            <button
              onClick={() => {
                onClose();
                if (role !== 'patient') setRole('patient');
                setActiveTab('alerts');
              }}
              className="text-xs font-bold text-teal-600 hover:text-teal-700 underline"
            >
              View Full Incident Center
            </button>
            <span className="text-[11px] text-slate-400">RecoverAI Gateway v2.4</span>
          </div>
        </div>
      </div>
    </div>
  );
};
