import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import {
  LayoutDashboard,
  ClipboardCheck,
  Pill,
  Camera,
  BellRing,
  Menu,
  X,
  HeartPulse,
  FileText,
  Clock,
  User,
  PhoneCall,
} from 'lucide-react';

export const MobileNav: React.FC = () => {
  const { role, activeTab, setActiveTab, unreadAlertCount } = useApp();
  const [drawerOpen, setDrawerOpen] = useState(false);

  if (role === 'landing') return null;

  const quickNav = [
    { id: 'dashboard', label: 'Home', icon: LayoutDashboard },
    { id: 'checkup', label: 'Checkup', icon: ClipboardCheck },
    { id: 'medications', label: 'Medicines', icon: Pill },
    { id: 'camera', label: 'Camera', icon: Camera },
    { id: 'alerts', label: 'Alerts', icon: BellRing, badge: unreadAlertCount },
  ];

  const fullNav = [
    { id: 'dashboard', label: 'Patient Dashboard', icon: LayoutDashboard },
    { id: 'recovery', label: 'My Recovery Plan', icon: HeartPulse },
    { id: 'checkup', label: 'Daily Health Checkup', icon: ClipboardCheck },
    { id: 'prescription', label: 'Prescription Viewer', icon: FileText },
    { id: 'medications', label: 'Medication Schedule', icon: Pill },
    { id: 'timeline', label: 'Recovery Timeline', icon: Clock },
    { id: 'camera', label: 'Camera Monitoring UI', icon: Camera },
    { id: 'alerts', label: 'Incident Alert Center', icon: BellRing, badge: unreadAlertCount },
    { id: 'profile', label: 'My Profile Settings', icon: User },
    { id: 'emergency', label: 'Emergency Hotline SOS', icon: PhoneCall, danger: true },
  ];

  return (
    <>
      {/* Mobile Drawer Overlay */}
      {drawerOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs lg:hidden animate-fadeIn">
          <div className="fixed inset-y-0 left-0 max-w-xs w-full bg-white shadow-2xl p-5 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-100">
                <span className="font-extrabold text-lg text-slate-900">
                  Recover<span className="text-teal-600">AI</span> Menu
                </span>
                <button
                  onClick={() => setDrawerOpen(false)}
                  className="p-1 text-slate-400 hover:text-slate-600 rounded-lg"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="space-y-1.5 overflow-y-auto max-h-[70vh]">
                {fullNav.map((item) => {
                  const Icon = item.icon;
                  const isActive = activeTab === item.id;

                  return (
                    <button
                      key={item.id}
                      onClick={() => {
                        setActiveTab(item.id);
                        setDrawerOpen(false);
                      }}
                      className={`w-full flex items-center justify-between p-3 rounded-xl text-xs font-semibold ${
                        isActive
                          ? 'bg-teal-600 text-white font-bold'
                          : item.danger
                          ? 'text-rose-600 bg-rose-50'
                          : 'text-slate-700 hover:bg-slate-100'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <Icon className="w-4 h-4" />
                        <span>{item.label}</span>
                      </div>
                      {item.badge !== undefined && item.badge > 0 && (
                        <span className="px-2 py-0.5 text-[10px] bg-rose-500 text-white rounded-full font-bold">
                          {item.badge}
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="pt-4 border-t border-slate-100 text-xs text-slate-400 text-center">
              RecoverAI Mobile Companion
            </div>
          </div>
        </div>
      )}

      {/* Sticky Bottom Navigation Bar */}
      <nav className="fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-slate-200 lg:hidden shadow-lg">
        <div className="flex items-center justify-around h-16 px-2">
          {quickNav.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;

            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`relative flex flex-col items-center justify-center w-full h-full text-[10px] font-semibold transition-colors ${
                  isActive ? 'text-teal-600 font-extrabold' : 'text-slate-500 hover:text-slate-900'
                }`}
              >
                <Icon className={`w-5 h-5 mb-0.5 ${isActive ? 'text-teal-600 scale-110' : ''}`} />
                <span>{item.label}</span>

                {item.badge !== undefined && item.badge > 0 && (
                  <span className="absolute top-2 right-4 w-4 h-4 bg-rose-500 text-white text-[9px] font-bold rounded-full flex items-center justify-center">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}

          {/* Drawer Menu Button */}
          <button
            onClick={() => setDrawerOpen(true)}
            className="flex flex-col items-center justify-center w-full h-full text-[10px] font-semibold text-slate-500 hover:text-slate-900"
          >
            <Menu className="w-5 h-5 mb-0.5" />
            <span>More</span>
          </button>
        </div>
      </nav>
    </>
  );
};
