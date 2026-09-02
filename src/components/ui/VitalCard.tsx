import React from 'react';
import { Thermometer, Heart, Activity, Wind, Smile, Gauge } from 'lucide-react';

interface VitalCardProps {
  title: string;
  value: string | number;
  unit: string;
  idealRange: string;
  status?: 'normal' | 'warning' | 'critical';
  type: 'temp' | 'bp' | 'hr' | 'spo2' | 'pain' | 'mobility';
  lastUpdated?: string;
  onClick?: () => void;
}

export const VitalCard: React.FC<VitalCardProps> = ({
  title,
  value,
  unit,
  idealRange,
  status = 'normal',
  type,
  lastUpdated,
  onClick,
}) => {
  const getIcon = () => {
    switch (type) {
      case 'temp':
        return <Thermometer className="w-5 h-5 text-amber-500" />;
      case 'bp':
        return <Activity className="w-5 h-5 text-blue-500" />;
      case 'hr':
        return <Heart className="w-5 h-5 text-rose-500" />;
      case 'spo2':
        return <Wind className="w-5 h-5 text-teal-500" />;
      case 'pain':
        return <Smile className="w-5 h-5 text-purple-500" />;
      case 'mobility':
        return <Gauge className="w-5 h-5 text-indigo-500" />;
      default:
        return <Activity className="w-5 h-5 text-teal-500" />;
    }
  };

  const statusStyles = {
    normal: {
      border: 'border-slate-200 hover:border-emerald-300 hover:shadow-emerald-50/50',
      badge: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      text: 'Normal',
    },
    warning: {
      border: 'border-amber-200 bg-amber-50/30 hover:border-amber-400',
      badge: 'bg-amber-100 text-amber-800 border-amber-300',
      text: 'Attention',
    },
    critical: {
      border: 'border-rose-300 bg-rose-50/40 hover:border-rose-500 animate-pulse',
      badge: 'bg-rose-100 text-rose-800 border-rose-300',
      text: 'High',
    },
  };

  const style = statusStyles[status];

  return (
    <div
      onClick={onClick}
      className={`bg-white rounded-2xl p-4 sm:p-5 border transition-all duration-200 shadow-xs hover:shadow-md cursor-pointer ${style.border}`}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2.5">
          <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100 shadow-2xs">
            {getIcon()}
          </div>
          <div>
            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</h4>
            <span className={`text-[10px] px-1.5 py-0.5 rounded-full border ${style.badge}`}>
              {style.text}
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-baseline gap-1.5 my-1">
        <span className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">{value}</span>
        <span className="text-xs font-semibold text-slate-500">{unit}</span>
      </div>

      <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <span>Target: <strong className="text-slate-700 font-medium">{idealRange}</strong></span>
        {lastUpdated && <span className="text-[11px] text-slate-400">{lastUpdated}</span>}
      </div>
    </div>
  );
};
