"use client";

import { useEffect, useState } from "react";
import { DitherButton } from "@/components/dither-kit/button";
import { Badge } from "@/components/ui/badge";
import { useAppState } from "@/components/providers/app-state";
import { fetchGrants, type Grant } from "@/lib/books-api";

export function GrantsView() {
  const { pushArtifact } = useAppState();
  const [grants, setGrants] = useState<Grant[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    fetchGrants()
      .then((r) => setGrants(r.grants))
      .catch(() => setErr("Grants API offline — start books server on :8090"));
  }, []);

  return (
    <div className="flex h-full flex-col">
      <header className="border-b border-border px-6 py-4">
        <p className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground">Capital</p>
        <h1 className="text-xl font-medium tracking-tight">Grants & non-dilutive capital</h1>
      </header>
      <div className="flex-1 space-y-3 overflow-auto p-6">
        {err && (
          <p className="rounded-md border border-border bg-muted/40 px-3 py-2 text-xs text-muted-foreground">
            {err}
          </p>
        )}
        {!err && !grants.length && (
          <p className="text-sm text-muted-foreground">Loading catalog…</p>
        )}
        {grants.map((g) => (
          <article
            key={g.id}
            className="flex flex-col gap-3 rounded-lg border border-border bg-card/40 p-4 sm:flex-row sm:items-start sm:justify-between"
          >
            <div className="min-w-0 space-y-1">
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="text-base font-medium">{g.title}</h2>
                <Badge variant="outline" className="rounded-sm font-mono text-[10px]">
                  {g.type}
                </Badge>
                <Badge variant="secondary" className="rounded-sm text-[10px]">
                  Fit {g.fit}
                </Badge>
              </div>
              <p className="font-mono text-sm tabular-nums">{g.amount}</p>
              <p className="text-xs text-muted-foreground">Deadline · {g.deadline}</p>
              <p className="max-w-prose text-sm text-muted-foreground">{g.summary}</p>
            </div>
            <DitherButton
              color="grey"
              variant="hatched"
              className="shrink-0 self-start text-[11px]"
              onClick={() =>
                pushArtifact({
                  id: `grant_${g.id}`,
                  kind: "grant",
                  title: g.title,
                  subtitle: g.amount,
                  payload: g,
                })
              }
            >
              Preview
            </DitherButton>
          </article>
        ))}
      </div>
    </div>
  );
}
