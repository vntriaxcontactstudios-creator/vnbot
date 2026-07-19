/**
 * VNBOT Web — Error Boundary.
 *
 * Catches render errors in child components and shows a fallback.
 * Used to wrap MascotStateView (which uses Canvas + Atropos + browser APIs
 * that may not be available in all environments).
 */

import { Component, type ReactNode, type ErrorInfo } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('[ErrorBoundary]', error, errorInfo);
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div
            role="alert"
            className="inline-block p-4 border border-vnbot-red/40 bg-vnbot-red/5 text-vnbot-red font-mono text-xs"
          >
            ⚠ {this.state.error?.message ?? 'Render error'}
          </div>
        )
      );
    }
    return this.props.children;
  }
}
