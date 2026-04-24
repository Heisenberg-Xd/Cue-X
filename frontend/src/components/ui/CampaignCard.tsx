import { Button } from './Button';

interface CampaignCardProps {
  priority: number;
  emoji: string;
  title: string;
  detail: string;
  expectedImpact?: string;
  primaryAction?: {
    label: string;
    onClick: () => void;
  };
  secondaryAction?: {
    label: string;
    onClick: () => void;
  };
}

export const CampaignCard = ({
  priority,
  emoji,
  title,
  detail,
  expectedImpact,
  primaryAction,
  secondaryAction,
}: CampaignCardProps) => {
  return (
    <div className="bg-[#111111] border border-[#1E293B] rounded-lg p-6 hover:border-[#06B6D4]/30 transition-all duration-300">
      {/* Header */}
      <div className="flex items-start gap-4 mb-4">
        <div className="flex items-center gap-3 flex-1">
          <div className="w-10 h-10 rounded-full bg-[#06B6D4]/20 border border-[#06B6D4]/50 flex items-center justify-center flex-shrink-0">
            <span className="text-lg">{emoji}</span>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="inline-block px-2 py-0.5 bg-[#06B6D4]/20 text-[#06B6D4] text-xs font-semibold rounded">
                Priority {priority}
              </span>
            </div>
            <h3 className="font-semibold text-[#FFFFFF]">{title}</h3>
          </div>
        </div>
      </div>

      {/* Detail */}
      <p className="text-sm text-[#CBD5E1] mb-4 leading-relaxed">{detail}</p>

      {/* Impact */}
      {expectedImpact && (
        <div className="mb-4 p-3 bg-green-500/10 border border-green-500/30 rounded text-sm text-green-300">
          <span className="font-semibold">Expected Impact: </span>
          {expectedImpact}
        </div>
      )}

      {/* Actions */}
      {(primaryAction || secondaryAction) && (
        <div className="flex gap-2">
          {primaryAction && (
            <Button
              onClick={primaryAction.onClick}
              variant="primary"
              size="sm"
              className="flex-1"
            >
              {primaryAction.label}
            </Button>
          )}

          {secondaryAction && (
            <Button
              onClick={secondaryAction.onClick}
              variant="secondary"
              size="sm"
              className="flex-1"
            >
              {secondaryAction.label}
            </Button>
          )}
        </div>
      )}
    </div>
  );
};
