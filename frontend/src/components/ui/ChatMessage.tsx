import type { ReactNode } from 'react';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  metadata?: {
    timestamp?: Date;
    powered_by?: 'gemini' | 'rule-based';
    query?: string;
  };
  actions?: Array<{
    label: string;
    onClick: () => void;
  }>;
  children?: ReactNode;
}

export const ChatMessage = ({
  role,
  content,
  metadata,
  actions,
  children,
}: ChatMessageProps) => {
  const isUser = role === 'user';

  return (
    <div
      className={`flex gap-3 mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#06B6D4] to-[#0891B2] flex items-center justify-center flex-shrink-0">
          <span className="text-xs font-bold text-white">AI</span>
        </div>
      )}

      <div className={`max-w-[70%] ${isUser ? 'flex flex-col items-end' : ''}`}>
        <div
          className={`rounded-lg px-4 py-3 ${
            isUser
              ? 'bg-[#06B6D4] text-[#0A0A0A] font-medium'
              : 'bg-[#111111] border border-[#1E293B] text-[#CBD5E1]'
          }`}
        >
          <p className="text-sm leading-relaxed whitespace-pre-wrap">
            {content}
          </p>
        </div>

        {children && (
          <div className={`mt-3 ${isUser ? 'flex flex-col items-end' : ''}`}>
            {children}
          </div>
        )}

        {actions && actions.length > 0 && (
          <div className={`mt-3 flex gap-2 flex-wrap ${isUser ? 'justify-end' : 'justify-start'}`}>
            {actions.map((action, idx) => (
              <button
                key={idx}
                onClick={action.onClick}
                className="px-3 py-1.5 text-xs font-medium rounded bg-[#06B6D4]/20 text-[#06B6D4] border border-[#06B6D4]/50 hover:bg-[#06B6D4]/30 transition-colors"
              >
                {action.label}
              </button>
            ))}
          </div>
        )}

        {metadata && (
          <div className="text-xs text-[#475569] mt-2 space-y-1">
            {metadata.powered_by && (
              <div>Powered by: {metadata.powered_by}</div>
            )}
            {metadata.timestamp && (
              <div>
                {metadata.timestamp.toLocaleTimeString()}
              </div>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-full bg-[#1E293B] flex items-center justify-center flex-shrink-0">
          <span className="text-xs font-bold text-[#64748B]">👤</span>
        </div>
      )}
    </div>
  );
};
