interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}

const sizeStyles = {
  sm: 'w-6 h-6',
  md: 'w-10 h-10',
  lg: 'w-16 h-16',
};

export const LoadingSpinner = ({ size = 'md', text }: LoadingSpinnerProps) => {
  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <div className={`${sizeStyles[size]} relative`}>
        {/* Outer rotating ring */}
        <svg
          className={`${sizeStyles[size]} animate-spin`}
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="#1E293B"
            strokeWidth="4"
          />
          <path
            className="opacity-75 text-[#06B6D4]"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>

        {/* Inner pulsing dot */}
        <div
          className="absolute inset-0 flex items-center justify-center"
          style={{
            animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
          }}
        >
          <div className="w-1 h-1 rounded-full bg-[#06B6D4]" />
        </div>
      </div>

      {text && (
        <div className="text-sm font-medium text-[#64748B] text-center">{text}</div>
      )}

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
};
