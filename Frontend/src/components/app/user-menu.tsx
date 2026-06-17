"use client";
import { useTenantReferenceQuery } from "@/lib/api/tenant-query";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { ChevronDown, LogOut, Settings, User } from "lucide-react";
import { useEffect, useRef, useState } from "react";


import { Button } from "@/components/ui/button";
import { authApi } from "@/lib/api/auth";
import { clearTokens } from "@/lib/auth/storage";


interface UserMenuProps {
  onOpenSettings: () => void;
}

export function UserMenu({ onOpenSettings }: UserMenuProps) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  const { data: profile } = useTenantReferenceQuery(["auth-me"], () => authApi.me());

  useEffect(() => {
    if (!open) return;
    function onDoc(e: MouseEvent) {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", onDoc);
    window.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDoc);
      window.removeEventListener("keydown", onKey);
    };
  }, [open]);

  function signOut() {
    clearTokens();
    router.push("/login");
  }

  const label = profile
    ? `${profile.firstName} ${profile.lastName}`.trim() || profile.email
    : "Profile";

  return (
    <div ref={rootRef} className="relative">
      <Button
        variant="ghost"
        size="sm"
        data-tour="user-profile"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="menu"
        aria-expanded={open}
      >
        <User className="mr-1.5 h-4 w-4" />
        <span className="hidden max-w-[120px] truncate sm:inline">{label}</span>
        <ChevronDown className="ml-1 h-3.5 w-3.5 text-fg-muted" />
      </Button>
      {open && (
        <div
          role="menu"
          className="absolute right-0 z-30 mt-1 w-52 rounded-md border border-border bg-surface py-1 shadow-lg"
        >
          {profile && (
            <div className="border-b border-border px-3 py-2 text-xs text-fg-muted">
              <div className="truncate font-medium text-fg">{label}</div>
              <div className="truncate">{profile.email}</div>
            </div>
          )}
          <Link
            href="/profile"
            role="menuitem"
            className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-canvas"
            onClick={() => setOpen(false)}
          >
            <User className="h-4 w-4" />
            Profile
          </Link>
          <Link
            href="/profile/change-password"
            role="menuitem"
            className="block px-3 py-2 text-sm hover:bg-canvas"
            onClick={() => setOpen(false)}
          >
            Change password
          </Link>
          <button
            type="button"
            role="menuitem"
            className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm hover:bg-canvas"
            onClick={() => {
              setOpen(false);
              onOpenSettings();
            }}
          >
            <Settings className="h-4 w-4" />
            Settings catalog
          </button>
          <button
            type="button"
            role="menuitem"
            className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-status-danger hover:bg-status-danger/10"
            onClick={() => {
              setOpen(false);
              signOut();
            }}
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>
      )}
    </div>
  );
}
