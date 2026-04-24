import type { ReactNode } from 'react';
import { X } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  children: ReactNode;
}

const sizeStyles = {
  sm: 'w-full max-w-sm',
  md: 'w-full max-w-md',
  lg: 'w-full max-w-lg',
  xl: 'w-full max-w-xl',
};

export const Modal = ({
  isOpen,
  onClose,
  title,
  size = 'lg',
  children,
}: ModalProps) => {
  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-[#000000]/80 backdrop-blur-sm z-40 transition-opacity duration-300"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div
          className={`${sizeStyles[size]} bg-[#0A0A0A] border border-[#1E293B] rounded-lg shadow-2xl max-h-[90vh] overflow-hidden flex flex-col animate-in fade-in duration-300`}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-[#1E293B]">
            <h2 className="text-xl font-bold text-[#FFFFFF]">{title}</h2>
            <button
              onClick={onClose}
              className="p-1 hover:bg-[#1E293B] rounded-lg transition-colors text-[#64748B] hover:text-[#FFFFFF]"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6">
            {children}
          </div>
        </div>
      </div>
    </>
  );
};
