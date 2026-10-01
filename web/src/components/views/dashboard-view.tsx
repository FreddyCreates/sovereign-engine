"use client";

import { useEffect, useMemo, useState } from "react";
import { AreaChart } from "@/components/dither-kit/area-chart";
import { Area } from "@/components/dither-kit/area";
import { XAxis } from "@/components/dither-kit/x-axis";
import { YAxis } from "@/components/dither-kit/y-axis";
import { Tooltip } from "@/components/dither-kit/tooltip";
import { DitherButton } from "@/components/dither-kit/button";
import { DitherGradient } from "@/components/dither-kit/gradient";
import {
  fetchBooksHome,
  fetchCashSeries,
  fetchEntitlements,
  type BooksHome,
  type CashPoint,
  type Entitlements,
} from "@/lib/books-api";
import { useAppState } from "@/components/providers/app-state";

export function DashboardView() {
  const { pushArtifact, setView } = useAppState();
  const [home, setHome] = useState<BooksHome | null>(null);
  const [series, setSeries] = useState<CashPoint[]>([]);
  const [ent, setEnt] = useState<Entitlements | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([fetchBooksHome(), fetchCashSeries(), fetchEntitlements()])
      .then(([h, c, e]) => {
        setHome(h);
        setSeries(
          (c.points?.length ? c.points : h.cash_series) || [
            { month: "now", cash: h.cash_balance },
          ],
        );
        setEnt(e);
      })
      .catch(() => setErr("Books API offline — start sovereign_dashboard_server.py"));
  }, []);

  const chartData = useMemo(
    () =>
      series.map((p) => ({
        month: p.month.length > 7 ? p.month.slice(5) : p.month,
        cash: Number((p.cash / 1000).toFixed(2)),
      })),
    [series],
  );

  return (
    <div className="relative flex h-full flex-col">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-28 overflow-hidden opacity-40">
        <div className="relative h-full w-full">
          <DitherGradient from="grey" direction="down" />
        </div>
      </div>
      <header className="relative z-10 border-b border-border px-6 py-4">
        <p className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground">Overview</p>
        <h1 className="text-xl font-medium tracking-tight">Dashboard</h1>
      </header>
      <div className="relative z-10 flex-1 space-y-6 overflow-auto p-6">
        {err && (
          <p className="rounded-md border border-border bg-muted/40 px-3 py-2 text-xs text-muted-foreground">
            {err}
          </p>
        )}
        <div className="grid gap-3 sm:grid-cols-4">
          <Stat
            label="Cash on hand"
            value={home ? money(home.cash_balance) : "—"}
            hint={home?.bank_connected ? "From linked depository" : "Connect a bank"}
          />
          <Stat
            label="Needs review"
            value={home ? String(home.inbox_count) : "—"}
            hint="Inbox transactions"
          />
          <Stat
            label="Plaid mode"
            value={home?.mode ?? "—"}
            hint={home?.trial_balance_ok ? "Ledger balanced" : "Ledger pending"}
          />
          <Stat
            label="Pro"
            value={ent ? (ent.pro_active ? "active" : "free") : "—"}
            hint={ent ? `${ent.source} · ${ent.mode}` : "RevenueCat / local"}
          />
        </div>

        <section className="rounded-lg border border-border bg-card/40 p-4">
          <div className="mb-3 flex items-center justify-between gap-2">
            <h2 className="text-sm font-medium">Cash trajectory</h2>
            <DitherButton
              color="grey"
              variant="hatched"
              className="h-7 text-[10px]"
              onClick={() =>
                pushArtifact({
                  kind: "chart",
                  title: "Cash trajectory",
                  subtitle: "From linked transactions",
                  payload: { data: chartData },
                })
              }
            >
              Open artifact
            </DitherButton>
          </div>
          <div className="h-56 w-full">
            {chartData.length > 0 ? (
              <AreaChart
                data={chartData}
                config={{ cash: { label: "Cash ($k)", color: "grey" } }}
                bloom="low"
                className="h-full w-full"
              >
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip labelKey="month" />
                <Area dataKey="cash" variant="gradient" />
              </AreaChart>
            ) : (
              <p className="text-sm text-muted-foreground">No cash series yet.</p>
            )}
          </div>
        </section>

        <div className="flex flex-wrap gap-2">
          <DitherButton color="grey" variant="gradient" onClick={() => setView("books")}>
            Go to Books
          </DitherButton>
          <DitherButton color="grey" variant="dotted" onClick={() => setView("grants")}>
            Browse grants
          </DitherButton>
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value, hint }: { label: string; value: string; hint: string }) {
  return (
    <div className="rounded-lg border border-border bg-card/50 px-4 py-3">
      <div className="text-[10px] uppercase tracking-wider text-muted-foreground">{label}</div>
      <div className="mt-1 font-mono text-2xl tabular-nums tracking-tight">{value}</div>
      <div className="mt-1 text-[11px] text-muted-foreground">{hint}</div>
    </div>
  );
}

function money(n: number) {
  return n.toLocaleString("en-US", { style: "currency", currency: "USD" });
}
