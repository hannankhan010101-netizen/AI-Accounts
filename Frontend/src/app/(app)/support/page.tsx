/** Support hub — catalog §2.2 / §2.3. */
"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { PageHeader } from "@/components/ui/page-header";
import { Input } from "@/components/ui/input";
import { SUPPORT_ARTICLES, SUPPORT_CATEGORIES } from "@/config/support-catalog";
import { matchText } from "@/lib/list/document-list-filters";

export default function SupportPage() {
  const [category, setCategory] = useState<string>("All");
  const [search, setSearch] = useState("");

  const articles = useMemo(() => {
    const q = search.trim().toLowerCase();
    return SUPPORT_ARTICLES.filter((a) => {
      if (category !== "All" && a.category !== category) return false;
      if (q && !matchText([a.title, a.summary, a.category], q)) return false;
      return true;
    });
  }, [category, search]);

  return (
    <>
      <PageHeader
        title="Support"
        breadcrumb="Help / Support"
        description="In-app guides and links to official FastAccounts help articles."
      />

      <div className="mb-4 flex flex-wrap items-center gap-3">
        <div className="max-w-md flex-1">
          <Input
            type="search"
            placeholder="Search help…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search support articles"
          />
        </div>
        <div className="flex flex-wrap gap-2">
          {SUPPORT_CATEGORIES.map((c) => (
            <button
              key={c}
              type="button"
              onClick={() => setCategory(c)}
              className={`rounded-md border px-3 py-1.5 text-sm ${
                category === c
                  ? "border-brand bg-brand/10 text-brand"
                  : "border-border bg-surface text-fg hover:bg-canvas"
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      <ul className="grid gap-3 sm:grid-cols-2">
        {articles.map((article) => (
          <li key={article.id} className="rounded-lg border border-border bg-surface p-4">
            <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-fg-muted">
              {article.category}
            </div>
            <h2 className="text-sm font-semibold text-fg">{article.title}</h2>
            <p className="mt-1 text-sm text-fg-muted">{article.summary}</p>
            {article.external ? (
              <a
                href={article.href}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-3 inline-block text-sm font-medium text-brand hover:underline"
              >
                Open external site →
              </a>
            ) : (
              <Link
                href={article.href}
                className="mt-3 inline-block text-sm font-medium text-brand hover:underline"
              >
                Open →
              </Link>
            )}
          </li>
        ))}
      </ul>
      {articles.length === 0 && (
        <p className="text-sm text-fg-muted">No articles match your filters.</p>
      )}
    </>
  );
}
