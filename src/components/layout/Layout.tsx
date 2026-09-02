import React from 'react';
import { useApp } from '../../context/AppContext';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';
import { MobileNav } from './MobileNav';
import { EmergencyModal } from '../ui/EmergencyModal';
import { RecoveryAssistantModal } from '../ui/RecoveryAssistantModal';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { role, assistantModalOpen, setAssistantModalOpen } = useApp();

  if (role === 'landing') {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900 font-sans flex flex-col antialiased">
        <Navbar />
        <main className="flex-1">{children}</main>
        <RecoveryAssistantModal
          isOpen={assistantModalOpen}
          onClose={() => setAssistantModalOpen(false)}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans flex flex-col antialiased selection:bg-teal-500 selection:text-white">
      <Navbar />

      <div className="flex-1 max-w-7xl w-full mx-auto flex">
        <Sidebar />
        <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto pb-24 lg:pb-8">
          {children}
        </main>
      </div>

      <MobileNav />
      <EmergencyModal />
      <RecoveryAssistantModal
        isOpen={assistantModalOpen}
        onClose={() => setAssistantModalOpen(false)}
      />
    </div>
  );
};

