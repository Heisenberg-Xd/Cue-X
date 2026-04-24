interface SegmentBadgeProps {
  name: string;
  count?: number;
  percentage?: number;
  size?: 'sm' | 'md' | 'lg';
}

const segmentColors: Record<string, { bg: string; text: string; border: string }> = {
  Champions: {
    bg: 'bg-amber-500/20',
    text: 'text-amber-400',
    border: 'border-amber-500/50',
  },
  'Loyal Customers': {
    bg: 'bg-green-500/20',
    text: 'text-green-400',
    border: 'border-green-500/50',
  },
  'Potential Loyalists': {
    bg: 'bg-blue-500/20',
    text: 'text-blue-400',
    border: 'border-blue-500/50',
  },
  'At Risk': {
    bg: 'bg-red-500/20',
    text: 'text-red-400',
    border: 'border-red-500/50',
  },
  'At Risk / Lost': {
    bg: 'bg-red-500/20',
    text: 'text-red-400',
    border: 'border-red-500/50',
  },
  Lost: {
    bg: 'bg-red-600/20',
    text: 'text-red-300',
    border: 'border-red-600/50',
  },
  Hibernating: {
    bg: 'bg-slate-500/20',
    text: 'text-slate-400',
    border: 'border-slate-500/50',
  },
};

const getSegmentColors = (name: string) => {
  return (
    segmentColors[name] || {
      bg: 'bg-cyan-500/20',
      text: 'text-cyan-400',
      border: 'border-cyan-500/50',
    }
  );
};

const sizeStyles = {
  sm: 'px-2.5 py-1 text-xs',
  md: 'px-3 py-1.5 text-sm',
  lg: 'px-4 py-2 text-base',
};

export const SegmentBadge = ({
  name,
  count,
  percentage,
  size = 'md',
}: SegmentBadgeProps) => {
  const colors = getSegmentColors(name);

  return (
    <div
      className={`${colors.bg} border ${colors.border} rounded-full font-medium ${colors.text} ${sizeStyles[size]} flex items-center gap-2 w-fit`}
    >
      <span>{name}</span>
      {(count !== undefined || percentage !== undefined) && (
        <span className="opacity-75">
          {count !== undefined && `${count}`}
          {count !== undefined && percentage !== undefined && ' • '}
          {percentage !== undefined && `${percentage}%`}
        </span>
      )}
    </div>
  );
};
