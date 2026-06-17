"use client";

import { Component, type ErrorInfo, type ReactNode } from "react";
import { AlertTriangle } from "lucide-react";

import { Button } from "@/components/ui/button";

type Props = { children: ReactNode; fallbackLabel?: string };
type State = { error: Error | null };

export class OnboardingErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    if (process.env.NODE_ENV === "development") {
      console.error("[onboarding]", error, info.componentStack);
    }
  }

  render() {
    if (this.state.error) {
      return (
        <div
          role="alert"
          className="fixed bottom-24 right-4 z-tour max-w-sm rounded-lg border border-status-danger/30 bg-surface p-4 shadow-lg"
        >
          <div className="flex items-start gap-2">
            <AlertTriangle className="h-5 w-5 shrink-0 text-status-danger" aria-hidden />
            <div>
              <p className="text-sm font-semibold text-fg">
                {this.props.fallbackLabel ?? "Learning hub paused"}
              </p>
              <p className="mt-1 text-xs text-fg-muted">
                Something went wrong loading guided tours. You can keep using the app.
              </p>
              <Button
                type="button"
                size="sm"
                variant="outline"
                className="mt-3"
                onClick={() => this.setState({ error: null })}
              >
                Try again
              </Button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
