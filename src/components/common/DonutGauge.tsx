import React from 'react';

interface DonutGaugeProps {
  value: number; // 0 to 100
  size?: number;
  strokeWidth?: number;
  label?: string;
  sublabel?: string;
  colorClass?: string;
}

export const DonutGauge: React.FC<DonutGaugeProps> = ({
  value,
  size = 128,
  strokeWidth = 12,
  label,
  sublabel,
  colorClass = 'text-blue-600',
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const clampedValue = Math.min(100, Math.max(0, value));
  const strokeDashoffset = circumference - (clampedValue / 100) * circumference;

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg className="transform -rotate-90" width={size} height={size}>
        {/* Background track */}
        <circle
          className="text-slate-200 dark:text-slate-800"
          stroke="currentColor"
          fill="transparent"
          strokeWidth={strokeWidth}
          r={radius}
          cx={size / 2}
          cy={size / 2}
        />
        {/* Filled progress */}
        <circle
          className={`${colorClass} transition-all duration-1000 ease-out`}
          stroke="currentColor"
          fill="transparent"
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          r={radius}
          cx={size / 2}
          cy={size / 2}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center select-none">
        <span className="text-2xl font-bold font-sans text-slate-900 dark:text-white leading-none">
          {label ?? `${Math.round(clampedValue)}%`}
        </span>
        {sublabel && (
          <span className="text-[10px] uppercase font-semibold text-slate-400 mt-1">
            {sublabel}
          </span>
        )}
      </div>
    </div>
  );
};
