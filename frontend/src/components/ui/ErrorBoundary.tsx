import React from 'react';
import type { ReactNode } from 'react';
import { Button } from './Button';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught error:', error, errorInfo);
  }

  resetError = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="flex flex-col items-center justify-center min-h-screen bg-[#0A0A0A] text-[#FFFFFF]">
            <div className="text-center space-y-4 max-w-md">
              <div className="text-6xl mb-4">⚠️</div>

              <h2 className="text-2xl font-bold">Something went wrong</h2>

              <p className="text-[#64748B]">
                We encountered an error while rendering this page. Please try again.
              </p>

              {this.state.error && (
                <details className="text-left bg-[#111111] rounded-lg p-4 border border-red-900/50 text-xs text-red-200">
                  <summary className="cursor-pointer font-mono">Error details</summary>
                  <pre className="mt-2 whitespace-pre-wrap overflow-x-auto">
                    {this.state.error.message}
                  </pre>
                </details>
              )}

              <Button
                onClick={this.resetError}
                variant="primary"
                size="md"
                className="w-full"
              >
                Try Again
              </Button>
            </div>
          </div>
        )
      );
    }

    return this.props.children;
  }
}
