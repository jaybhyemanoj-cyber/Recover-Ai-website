import React from 'react';
import type { TriageStatus } from '../../types';
import { CheckCircle2, AlertCircle, AlertTriangle, ShieldAlert } from 'lucide-react';

interface StatusBadgeProps {
  status: TriageStatus;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  size = 'md',
  showIcon = true,
  className = '',
}) => {
  const config = {
    stable: {
      label: 'Stable Recovery',
      shortLabel: 'Stable',
      bg: 'bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100',
      dotBg: 'bg-emerald-500',
      icon: CheckCircle2,
    },
    attention: {
      label: 'Attention Needed',
      shortLabel: 'Attention',
      bg: 'bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100',
      dotBg: 'bg-amber-500',
      icon: AlertCircle,
    },
    doctor_review: {
      label: 'Doctor Review',
      shortLabel: 'Doctor Review',
      bg: 'bg-orange-50 text-orange-700 border-orange-200 hover:bg-orange-100',
      dotBg: 'bg-orange-500',
      icon: AlertTriangle,
    },
    critical: {
      label: 'Critical Incident',
      shortLabel: 'Critical',
      bg: 'bg-rose-50 text-rose-700 border-rose-200 hover:bg-rose-100 animate-pulse',
      dotBg: 'bg-rose-500',
      icon: ShieldAlert,
    },
  };

  const item = config[status] || config.stable;
  const Icon = item.icon;

  const sizeClasses = {
    sm: 'text-xs px-2.5 py-0.5 gap-1',
    md: 'text-sm px-3 py-1 gap-1.5 font-medium',
    lg: 'text-base px-4 py-1.5 gap-2 font-semibold',
  };

  return (
    <span
      className={`inline-flex items-center rounded-full border transition-colors shadow-2xs ${item.bg} ${sizeClasses[size]} ${className}`}
    >
      <span className={`h-2 w-2 rounded-full ${item.dotBg}`} />
      {showIcon && <Icon className={size === 'sm' ? 'w-3.5 h-3.5' : size === 'lg' ? 'w-5 h-5' : 'w-4 h-4'} />}
      <span>{size === 'sm' ? item.shortLabel : item.label}</span>
    </span>
  );
};
