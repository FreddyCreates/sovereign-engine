"use client";

import { useEffect, useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { DitherButton } from "@/components/dither-kit/button";
import { useAppState } from "@/components/providers/app-state";
import { fetchCrmList } from "@/lib/product-api";
import type { CrmTab, ViewId } from "@/lib/types";

const VIEW_TO_TAB: Partial<Record<ViewId, CrmTab>> = {
  crm_companies: "companies",
  crm_people: "people",
  crm_opportunities: "opportunities",
  crm_tasks: "tasks",
  crm_notes: "notes",
  crm_workflows: "workflows",
};

const COLUMNS: Record<CrmTab, string[]> = {
  companies: ["name", "domain", "icp", "arr", "industry"],
  people: ["first_name", "last_name", "email", "role", "company_id"],
  opportunities: ["name", "company_id", "stage", "amount", "close_date"],
  tasks: ["title", "status", "due_date", "company_id"],
  notes: ["body", "company_id", "person_id"],
  workflows: ["name", "status", "trigger_json"],
};

const LABELS: Record<CrmTab, string> = {
  companies: "Companies",
  people: "People",
  opportunities: "Opportunities",
  tasks: "Tasks",
  notes: "Notes",
  workflows: "Workflows",
};

export function CrmView() {
  const { view, pushArtifact } = useAppState();
  const tab = VIEW_TO_TAB[view] ?? "companies";
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const cols = COLUMNS[tab];

  async function refresh() {
    setBusy(true);
    try {
      const data = await fetchCrmList(tab);
      setRows(data.records || []);
      setErr(null);
    } catch {
      setErr("CRM API offline — start sovereign_dashboard_server.py on :8090");
      setRows([]);
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    void refresh();
  }, [tab]);

  const display = useMemo(
    () =>
      rows.map((r) =>
        cols.map((c) => {
          const v = r[c];
          if (v == null) return "—";
          if (typeof v === "object") return JSON.stringify(v).slice(0, 48);
          return String(v);
        }),
      ),
    [rows, cols],
  );

  return (
    <div className="flex h-full flex-col">
      <header className="border-b border-border px-6 py-4">
        <p className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground">CRM</p>
        <div className="mt-1 flex flex-wrap items-end justify-between gap-3">
          <h1 className="text-xl font-medium tracking-tight">{LABELS[tab]}</h1>
          <div className="flex gap-2">
            <Badge variant="outline" className="rounded-sm font-mono text-[10px]">
              {rows.length} records
            </Badge>
            <DitherButton
              color="grey"
              variant="hatched"
              className="h-7 text-[10px]"
              disabled={busy}
              onClick={() => void refresh()}
            >
              Refresh
            </DitherButton>
            <DitherButton
              color="grey"
              variant="dotted"
              className="h-7 text-[10px]"
              onClick={() =>
                pushArtifact({
                  kind: "crm",
                  title: LABELS[tab],
                  subtitle: `${rows.length} records`,
                  payload: { tab, rows },
                })
              }
            >
              Pin
            </DitherButton>
          </div>
        </div>
      </header>
      <div className="flex-1 overflow-auto p-6">
        {err && (
          <p className="mb-3 rounded-md border border-border bg-muted/40 px-3 py-2 text-xs text-muted-foreground">
            {err}
          </p>
        )}
        <div className="overflow-hidden rounded-lg border border-border">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead className="border-b border-border bg-muted/30 text-[10px] uppercase tracking-wider text-muted-foreground">
              <tr>
                {cols.map((c) => (
                  <th key={c} className="px-3 py-2 font-medium">
                    {c.replace(/_/g, " ")}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {!display.length && (
                <tr>
                  <td colSpan={cols.length} className="px-3 py-6 text-sm text-muted-foreground">
                    No records yet — seed via scripts/seed_crm.py
                  </td>
                </tr>
              )}
              {display.map((row, i) => (
                <tr key={i} className="border-b border-border/60 last:border-0">
                  {row.map((cell, j) => (
                    <td
                      key={j}
                      className={
                        j === 0
                          ? "px-3 py-2.5 font-medium"
                          : "px-3 py-2.5 font-mono text-xs text-muted-foreground"
                      }
                    >
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
