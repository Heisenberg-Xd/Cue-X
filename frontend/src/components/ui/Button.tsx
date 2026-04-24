import type { ReactNode } from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  icon?: ReactNode;
  iconPosition?: 'left' | 'right';
  loading?: boolean;
  children: ReactNode;
}

const variantStyles = {
  primary:
    'bg-[#06B6D4] text-[#0A0A0A] font-semibold hover:bg-[#0891B2] active:bg-[#0E7490] shadow-[0_0_20px_rgba(6,182,212,0.3)]',
  secondary:
    'bg-[#1E293B] text-[#FFFFFF] font-medium hover:bg-[#334155] active:bg-[#475569] border border-[#334155]',
  ghost:
    'text-[#64748B] hover:text-[#FFFFFF] hover:bg-[#1E293B]/50 font-medium',
  danger:
    'bg-red-600 text-[#FFFFFF] font-semibold hover:bg-red-700 active:bg-red-800',
};

const sizeStyles = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2.5 text-base',
  lg: 'px-6 py-3 text-lg',
};

export const Button = ({
  variant = 'primary',
  size = 'md',
  icon,
  iconPosition = 'left',
  loading = false,
  children,
  disabled,
  className = '',
  ...props
}: ButtonProps) => {
  return (
    <button
      className={`
        inline-flex items-center justify-center gap-2
        rounded-lg transition-all duration-200
        disabled:opacity-50 disabled:cursor-not-allowed
        focus:outline-none focus:ring-2 focus:ring-[#06B6D4]/50 focus:ring-offset-2 focus:ring-offset-[#0A0A0A]
        ${variantStyles[variant]}
        ${sizeStyles[size]}
        ${className}
      `}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      )}

      {!loading && icon && iconPosition === 'left' && icon}

      <span>{children}</span>

      {!loading && icon && iconPosition === 'right' && icon}
    </button>
  );
};
