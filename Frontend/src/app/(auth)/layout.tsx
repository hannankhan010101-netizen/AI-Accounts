import { BrandLogo } from "@/components/brand/brand-logo";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="onboarding-mesh flex min-h-dvh flex-col items-center justify-center overflow-y-auto bg-canvas px-safe py-12 pb-[max(3rem,env(safe-area-inset-bottom))] max-sm:justify-start max-sm:py-8">
      <div className="mb-8 flex flex-col items-center text-center">
        <BrandLogo variant="auth" href="/login" priority />
      </div>
      <div className="gradient-border-brand w-full max-w-md rounded-lg bg-surface-elevated p-8 shadow-md">
        {children}
      </div>
    </div>
  );
}
