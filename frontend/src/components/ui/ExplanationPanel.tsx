import { ChevronDown } from 'lucide-react';
import { useState } from 'react';

interface ExplanationPanelProps {
  what: string;
  why: string;
  action: string;
  defaultOpen?: boolean;
}

export const ExplanationPanel = ({
  what,
  why,
  action,
  defaultOpen = false,
}: ExplanationPanelProps) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="rounded-lg border border-[#1E293B] bg-[#111111] overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-[#0F0F0F] transition-colors"
      >
        <span className="font-semibold text-[#FFFFFF]">
          {isOpen ? 'Hide Details' : 'Show Details'}
        </span>
        <ChevronDown
          className={`w-5 h-5 text-[#06B6D4] transition-transform duration-300 ${
            isOpen ? 'rotate-180' : ''
          }`}
        />
      </button>

      {isOpen && (
        <div className="px-6 pb-6 pt-4 space-y-4 border-t border-[#1E293B] bg-[#0F0F0F]">
          <div>
            <h4 className="text-xs font-semibold text-[#06B6D4] uppercase tracking-wide mb-2 flex items-center gap-2">
              <span>ℹ️</span> What This Shows
            </h4>
            <p className="text-sm text-[#CBD5E1] leading-relaxed">{what}</p>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-[#06B6D4] uppercase tracking-wide mb-2 flex items-center gap-2">
              <span>💡</span> Why It Matters
            </h4>
            <p className="text-sm text-[#CBD5E1] leading-relaxed">{why}</p>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-[#06B6D4] uppercase tracking-wide mb-2 flex items-center gap-2">
              <span>🎯</span> Action
            </h4>
            <p className="text-sm text-[#CBD5E1] leading-relaxed">{action}</p>
          </div>
        </div>
      )}
    </div>
  );
};
