"use client";

import { cn } from "@/lib/utils";

export type WizardStep = {
  id: string;
  label: string;
};

type WizardShellProps = {
  steps: WizardStep[];
  currentStepId: string;
  title: string;
  description?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
};

/** Multi-step settings / migration wizard chrome. */
export function WizardShell({
  steps,
  currentStepId,
  title,
  description,
  children,
  footer,
}: WizardShellProps) {
  const currentIndex = steps.findIndex((s) => s.id === currentStepId);

  return (
    <div className="space-y-6">
      <nav aria-label="Progress">
        <ol className="flex flex-wrap gap-2">
          {steps.map((step, index) => {
            const active = step.id === currentStepId;
            const done = index < currentIndex;
            return (
              <li
                key={step.id}
                className={cn(
                  "rounded-full px-3 py-1 text-xs font-medium motion-safe-transition",
                  active && "bg-brand-600 text-on-brand",
                  done && !active && "bg-brand-50 text-brand-700 dark:bg-brand-100/15 dark:text-brand-300",
                  !active && !done && "bg-canvas text-fg-muted",
                )}
              >
                {index + 1}. {step.label}
              </li>
            );
          })}
        </ol>
      </nav>
      <div>
        <h2 className="text-section font-semibold text-fg">{title}</h2>
        {description ? <p className="mt-1 text-sm text-fg-muted">{description}</p> : null}
      </div>
      <div className="surface-elevated rounded-xl bg-surface p-4 dark:border-0">{children}</div>
      {footer ? <div className="flex flex-wrap justify-end gap-2">{footer}</div> : null}
    </div>
  );
}
