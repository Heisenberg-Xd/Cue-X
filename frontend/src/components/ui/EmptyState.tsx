import type { ReactNode } from 'react';
import { Button } from './Button';

interface EmptyStateProps {
  icon?: string;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  children?: ReactNode;
}

export const EmptyState = ({
  icon = '📭',
  title,
  description,
  action,
  children,
}: EmptyStateProps) => {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div className="text-6xl mb-4">{icon}</div>

      <h3 className="text-xl font-semibold text-[#FFFFFF] mb-2">{title}</h3>

      <p className="text-[#64748B] max-w-md mb-6">{description}</p>

      {action && (
        <Button onClick={action.onClick} variant="primary" size="md">
          {action.label}
        </Button>
      )}

      {children}
    </div>
  );
};
