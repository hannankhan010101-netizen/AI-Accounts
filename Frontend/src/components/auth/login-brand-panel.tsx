"use client";

import { BarChart3, ShieldCheck, Sparkles, Zap } from "lucide-react";

import { BrandLogo } from "@/components/brand/brand-logo";
import { useHydrated } from "@/lib/hooks/use-hydrated";
import { cn } from "@/lib/utils";

const FEATURES = [
  {
    icon: Sparkles,
    title: "AI-assisted workflows",
    description: "Smart categorization and guided actions across your ledger.",
  },
  {
    icon: BarChart3,
    title: "Real-time insights",
    description: "Live dashboards that surface what matters before month-end.",
  },
  {
    icon: ShieldCheck,
    title: "Enterprise security",
    description: "Role-based access, audit trails, and encrypted sessions.",
  },
  {
    icon: Zap,
    title: "Automated close",
    description: "Reconciliation and reporting that keeps pace with your team.",
  },
] as const;

const STATS = [
  { value: "99.9%", label: "Uptime SLA" },
  { value: "<2s", label: "Avg. load time" },
  { value: "256-bit", label: "Encryption" },
] as const;

export function LoginBrandPanel({ className }: { className?: string }) {
  const hydrated = useHydrated();

  return (
    <aside
      className={cn(
        "auth-panel-gradient relative hidden overflow-hidden lg:flex lg:flex-col lg:justify-between",
        hydrated && "auth-enter auth-enter-delayed",
        className,
      )}
      aria-hidden
    >
      <div className="auth-panel-orb auth-panel-orb--one" />
      <div className="auth-panel-orb auth-panel-orb--two" />
      <div className="auth-panel-grid" />

      <div className="relative z-10 flex flex-col gap-10 p-10 xl:p-14">
        <div className="[&_.text-brand-600]:text-brand-300 [&_.text-fg]:text-white [&_.text-fg-muted]:text-white/70">
          <BrandLogo variant="auth" href="/login" priority />
        </div>

        <div className="space-y-4">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-white/55">
            Intelligent accounting
          </p>
          <h2 className="max-w-md text-[clamp(1.75rem,1.5rem+1vw,2.5rem)] font-semibold leading-tight tracking-tight text-white">
            Clarity for finance teams that move fast.
          </h2>
          <p className="max-w-sm text-sm leading-relaxed text-white/70">
            One workspace for books, reporting, and AI guidance — built for operators who
            need accuracy without the overhead.
          </p>
        </div>

        <ul className="grid max-w-lg gap-3">
          {FEATURES.map(({ icon: Icon, title, description }) => (
            <li
              key={title}
              className="auth-feature-card flex gap-3 rounded-xl p-3.5"
            >
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white/10 text-white">
                <Icon className="h-4 w-4" strokeWidth={1.75} />
              </span>
              <span className="min-w-0">
                <span className="block text-sm font-medium text-white">{title}</span>
                <span className="mt-0.5 block text-xs leading-relaxed text-white/65">
                  {description}
                </span>
              </span>
            </li>
          ))}
        </ul>
      </div>

      <div className="relative z-10 border-t border-white/10 px-10 py-6 xl:px-14">
        <dl className="grid grid-cols-3 gap-4">
          {STATS.map(({ value, label }) => (
            <div key={label}>
              <dt className="text-[10px] font-medium uppercase tracking-wider text-white/50">
                {label}
              </dt>
              <dd className="mt-1 text-lg font-semibold tabular-nums text-white">{value}</dd>
            </div>
          ))}
        </dl>
      </div>
    </aside>
  );
}
