interface KPICardProps {
  label: string;
  value: string | number;
  unit?: string;
  trend?: {
    value: number;
    direction: 'up' | 'down';
  };
  icon?: string;
  highlight?: boolean;
}

export const KPICard = ({
  label,
  value,
  unit,
  trend,
  icon = '📊',
  highlight = false,
}: KPICardProps) => {
  return (
    <div
      className={`rounded-lg p-6 border transition-all duration-300 ${
        highlight
          ? 'bg-gradient-to-br from-[#06B6D4]/20 to-[#0891B2]/20 border-[#06B6D4]/50 shadow-[0_0_20px_rgba(6,182,212,0.1)]'
          : 'bg-[#111111] border-[#1E293B] hover:border-[#06B6D4]/30'
      }`}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex flex-col gap-1 flex-1">
          <p className="text-sm font-medium text-[#64748B]">{label}</p>
        </div>
        <span className="text-2xl">{icon}</span>
      </div>

      <div className="flex items-baseline gap-2 mb-3">
        <span className={`text-3xl font-bold ${highlight ? 'text-[#06B6D4]' : 'text-[#FFFFFF]'}`}>
          {typeof value === 'number' ? value.toLocaleString() : value}
        </span>
        {unit && <span className="text-sm text-[#64748B]">{unit}</span>}
      </div>

      {trend && (
        <div
          className={`flex items-center gap-1 text-sm ${
            trend.direction === 'up' ? 'text-green-500' : 'text-red-500'
          }`}
        >
          <span>{trend.direction === 'up' ? '↑' : '↓'}</span>
          <span>{trend.value}%</span>
        </div>
      )}
    </div>
  );
};
