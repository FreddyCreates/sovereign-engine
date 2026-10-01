"use client";

import { FileText, X } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { DitherButton } from "@/components/dither-kit/button";
import { AreaChart } from "@/components/dither-kit/area-chart";
import { Area } from "@/components/dither-kit/area";
import { XAxis } from "@/components/dither-kit/x-axis";
import { YAxis } from "@/components/dither-kit/y-axis";
import { Tooltip } from "@/components/dither-kit/tooltip";
import { useAppState } from "@/components/providers/app-state";
import { cn } from "@/lib/utils";

export function ArtifactsPanel() {
  const {
    artifactsOpen,
    setArtifactsOpen,
    artifacts,
    activeArtifactId,
    setActiveArtifactId,
    clearArtifacts,
  } = useAppState();

  if (!artifactsOpen) return null;

  const active = artifacts.find((a) => a.id === activeArtifactId) ?? artifacts[0];

  return (
    <aside className="flex h-full w-[340px] shrink-0 flex-col border-l border-border bg-card">
      <div className="flex items-center justify-between px-3 py-2.5">
        <div>
          <div className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
            Artifacts
          </div>
          <div className="text-sm font-medium">Preview</div>
        </div>
        <div className="flex items-center gap-1">
          {artifacts.length > 0 && (
            <DitherButton
              color="grey"
              variant="dotted"
              className="h-7 px-2 text-[10px]"
              onClick={clearArtifacts}
            >
              Clear
            </DitherButton>
          )}
          <button
            type="button"
            aria-label="Close artifacts"
            className="rounded-md p-1.5 text-muted-foreground hover:bg-accent hover:text-foreground"
            onClick={() => setArtifactsOpen(false)}
          >
            <X className="size-4" />
          </button>
        </div>
      </div>
      <Separator />
      <div className="grid grid-rows-[auto_1fr] min-h-0 flex-1">
        <ScrollArea className="max-h-28 border-b border-border">
          <ul className="flex flex-col gap-0.5 p-2">
            {artifacts.length === 0 && (
              <li className="px-2 py-3 text-xs text-muted-foreground">
                Artifacts from chat, grants, and books appear here.
              </li>
            )}
            {artifacts.map((a) => (
              <li key={a.id}>
                <button
                  type="button"
                  onClick={() => setActiveArtifactId(a.id)}
                  className={cn(
                    "flex w-full items-start gap-2 rounded-md px-2 py-1.5 text-left text-xs",
                    active?.id === a.id ? "bg-accent" : "hover:bg-accent/50",
                  )}
                >
                  <FileText className="mt-0.5 size-3.5 shrink-0 opacity-70" />
                  <span className="min-w-0">
                    <span className="block truncate font-medium">{a.title}</span>
                    <span className="block truncate text-[10px] text-muted-foreground">
                      {a.kind}
                      {a.subtitle ? ` · ${a.subtitle}` : ""}
                    </span>
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </ScrollArea>
        <ScrollArea className="min-h-0">
          <div className="p-3">
            {!active ? (
              <p className="text-sm text-muted-foreground">Nothing selected.</p>
            ) : (
              <ArtifactBody artifact={active} />
            )}
          </div>
        </ScrollArea>
      </div>
    </aside>
  );
}

function ArtifactBody({ artifact }: { artifact: NonNullable<ReturnType<typeof useAppState>["artifacts"][0]> }) {
  if (artifact.kind === "chart") {
    const data = (artifact.payload?.data as Array<Record<string, number | string>>) ?? [
      { month: "Jan", cash: 18 },
      { month: "Feb", cash: 21 },
      { month: "Mar", cash: 19 },
      { month: "Apr", cash: 24 },
    ];
    return (
      <div className="space-y-3">
        <Header artifact={artifact} />
        <div className="h-48 w-full">
          <AreaChart
            data={data}
            config={{ cash: { label: "Cash", color: "grey" } }}
            bloom="low"
            className="h-full w-full"
          >
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip labelKey="month" />
            <Area dataKey="cash" variant="hatched" />
          </AreaChart>
        </div>
      </div>
    );
  }

  if (artifact.kind === "grant") {
    const g = artifact.payload ?? {};
    return (
      <div className="space-y-3">
        <Header artifact={artifact} />
        <dl className="space-y-2 text-sm">
          <Row label="Amount" value={String(g.amount ?? "—")} />
          <Row label="Type" value={String(g.type ?? "Grant")} />
          <Row label="Deadline" value={String(g.deadline ?? "—")} />
          <Row label="Fit" value={String(g.fit ?? "—")} />
        </dl>
        <p className="text-xs leading-relaxed text-muted-foreground">
          {String(g.summary ?? "Non-dilutive capital opportunity for subscription apps.")}
        </p>
      </div>
    );
  }

  if (artifact.kind === "transactions") {
    const rows = (artifact.payload?.rows as Array<{ name: string; amount: number; date: string }>) ?? [];
    return (
      <div className="space-y-3">
        <Header artifact={artifact} />
        <ul className="space-y-2">
          {rows.map((r, i) => (
            <li key={i} className="flex justify-between gap-2 border-b border-border/60 pb-2 text-xs">
              <span>
                <span className="block font-medium">{r.name}</span>
                <span className="text-muted-foreground">{r.date}</span>
              </span>
              <span className="font-mono tabular-nums">
                {r.amount > 0 ? "−" : "+"}${Math.abs(r.amount).toFixed(2)}
              </span>
            </li>
          ))}
        </ul>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <Header artifact={artifact} />
      <pre className="overflow-auto rounded-md border border-border bg-background p-2 text-[11px] text-muted-foreground">
        {JSON.stringify(artifact.payload ?? {}, null, 2)}
      </pre>
    </div>
  );
}

function Header({ artifact }: { artifact: { title: string; subtitle?: string; kind: string } }) {
  return (
    <div className="space-y-1">
      <Badge variant="outline" className="rounded-sm font-mono text-[10px] uppercase">
        {artifact.kind}
      </Badge>
      <h3 className="text-base font-medium leading-tight">{artifact.title}</h3>
      {artifact.subtitle && (
        <p className="text-xs text-muted-foreground">{artifact.subtitle}</p>
      )}
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-3 border-b border-border/50 pb-1.5">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="font-mono text-right text-foreground">{value}</dd>
    </div>
  );
}
