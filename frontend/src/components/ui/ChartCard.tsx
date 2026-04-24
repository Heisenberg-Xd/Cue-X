import { useState } from 'react';
import type { ReactNode } from 'react';
import { ChevronDown, Download } from 'lucide-react';

interface ChartCardProps {
  title: string;
  icon?: string;
  children: ReactNode;
  explanation?: {
    what: string;
    why: string;
    action: string;
  };
  onExportChart?: () => void;
}

export const ChartCard = ({
  title,
  icon = '📊',
  children,
  explanation,
  onExportChart,
}: ChartCardProps) => {
  const [showExplanation, setShowExplanation] = useState(false);

  return (
    <div className="bg-[#111111] border border-[#1E293B] rounded-lg overflow-hidden hover:border-[#06B6D4]/30 transition-all duration-300">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-[#1E293B]">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{icon}</span>
          <h3 className="text-lg font-semibold text-[#FFFFFF]">{title}</h3>
        </div>
        {onExportChart && (
          <button
            onClick={onExportChart}
            className="p-2 hover:bg-[#06B6D4]/10 rounded-lg transition-colors text-[#06B6D4]"
            title="Export as PNG"
          >
            <Download className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Chart Container */}
      <div className="p-6 min-h-[300px] flex items-center justify-center bg-[#0A0A0A]">
        {children}
      </div>

      {/* Explanation Panel */}
      {explanation && (
        <div className="border-t border-[#1E293B]">
          <button
            onClick={() => setShowExplanation(!showExplanation)}
            className="w-full px-6 py-4 flex items-center justify-between hover:bg-[#0F0F0F] transition-colors text-sm text-[#64748B]"
          >
            <span className="font-medium">
              {showExplanation ? 'Hide Explanation' : 'Show Explanation'}
            </span>
            <ChevronDown
              className={`w-4 h-4 transition-transform duration-300 ${
                showExplanation ? 'rotate-180' : ''
              }`}
            />
          </button>

          {showExplanation && (
            <div className="px-6 pb-6 space-y-4 bg-[#0F0F0F]">
              <div>
                <h4 className="text-xs font-semibold text-[#06B6D4] uppercase tracking-wide mb-2 flex items-center gap-2">
                  <span>ℹ️</span> What this shows
                </h4>
                <p className="text-sm text-[#CBD5E1] leading-relaxed">
                  {explanation.what}
                </p>
              </div>

              <div>
                <h4 className="text-xs font-semibold text-[#06B6D4] uppercase tracking-wide mb-2 flex items-center gap-2">
                  <span>💡</span> Why it matters
                </h4>
                <p className="text-sm text-[#CBD5E1] leading-relaxed">
                  {explanation.why}
                </p>
              </div>

              <div>
                <h4 className="text-xs font-semibold text-[#06B6D4] uppercase tracking-wide mb-2 flex items-center gap-2">
                  <span>🎯</span> Action
                </h4>
                <p className="text-sm text-[#CBD5E1] leading-relaxed">
                  {explanation.action}
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
