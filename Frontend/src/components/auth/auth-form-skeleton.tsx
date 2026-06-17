export function AuthFormSkeleton() {
  return (
    <div className="space-y-6 animate-pulse motion-reduce:animate-none" aria-busy="true" aria-label="Loading form">
      <div className="space-y-2">
        <div className="h-6 w-2/3 rounded-md bg-surface-muted" />
        <div className="h-4 w-full rounded-md bg-surface-muted" />
      </div>
      <div className="space-y-4">
        <div className="h-10 rounded-md bg-surface-muted" />
        <div className="h-10 rounded-md bg-surface-muted" />
        <div className="h-10 rounded-md bg-surface-muted" />
        <div className="h-10 rounded-md bg-brand-600/20" />
      </div>
    </div>
  );
}
