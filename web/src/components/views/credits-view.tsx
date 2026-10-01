"use client";

import { useCallback, useEffect, useState } from "react";
import { DitherButton } from "@/components/dither-kit/button";
import { Badge } from "@/components/ui/badge";
import { useAppState } from "@/components/providers/app-state";
import {
  answerTaxQuestion,
  fetchApprovals,
  fetchTaxCredits,
  fetchTaxOpportunities,
  fetchTaxQuestions,
  fetchTaxSummary,
  type ApprovalRow,
  type TaxCredits,
  type TaxOpportunities,
  type TaxQuestion,
  type TaxSummary,
} from "@/lib/books-api";

const STATES = ["CA", "NY", "TX", "WA", "FL"] as const;

function money(n: number | undefined | null) {
  return (n ?? 0).toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
}

const STATUS_LABEL: Record<string, string> = { close: "Close", qualified: "Qualified", not_yet: "Not yet" };

export function CreditsView() {
  const { pushArtifact } = useAppState();
  const [state, setState] = useState<(typeof STATES)[number]>("CA");
  const [credits, setCredits] = useState<TaxCredits | null>(null);
  const [summary, setSummary] = useState<TaxSummary | null>(null);
  const [opps, setOpps] = useState<TaxOpportunities | null>(null);
  const [questions, setQuestions] = useState<TaxQuestion[]>([]);
  const [approvals, setApprovals] = useState<ApprovalRow[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  const load = useCallback(() => {
    setErr(null);
    fetchTaxCredits(state).then(setCredits).catch(() => setErr("Books API offline — start sovereign_dashboard_server.py on :8090"));
    fetchTaxSummary().then(setSummary).catch(() => setSummary(null));
    fetchTaxOpportunities(state).then(setOpps).catch(() => setOpps(null));
    fetchTaxQuestions(8).then((r) => setQuestions(r.questions)).catch(() => setQuestions([]));
    fetchApprovals(12).then((r) => setApprovals(r.approvals)).catch(() => setApprovals([]));
  }, [state]);

  useEffect(() => {
    load();
  }, [load]);

  async function answer(q: TaxQuestion, attendees: string) {
    setBusy(q.transaction_id);
    try {
      await answerTaxQuestion(q.transaction_id, attendees);
      setQuestions((qs) => qs.filter((x) => x.transaction_id !== q.transaction_id));
      fetchTaxSummary().then(setSummary).catch(() => undefined);
      fetchTaxOpportunities(state).then(setOpps).catch(() => undefined);
    } finally {
      setBusy(null);
    }
  }

  const refs = (credits?.statutory_references ?? []).map((r) =>
    typeof r === "string" ? r : String(r.citation ?? r.name ?? JSON.stringify(r)),
  );
  const next = opps?.next_action ?? null;

  return (
    <div className="flex h-full flex-col">
      <header className="border-b border-border px-6 py-4">
        <p className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground">Compliance</p>
        <div className="flex flex-wrap items-end justify-between gap-3">
          <h1 className="text-xl font-medium tracking-tight">Tax credits and deductions</h1>
          <div className="flex gap-1">
            {STATES.map((s) => (
              <DitherButton key={s} color="grey" variant={s === state ? "solid" : "hatched"} className="text-[11px]" onClick={() => setState(s)}>
                {s}
              </DitherButton>
            ))}
          </div>
        </div>
      </header>

      <div className="flex-1 space-y-4 overflow-auto p-6">
        {err && <p className="rounded-md border border-border bg-muted/40 px-3 py-2 text-xs text-muted-foreground">{err}</p>}

        {next && (
          <section className="rounded-lg border border-border bg-card/60 p-4">
            <p className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground">Go do this next</p>
            <div className="mt-1 flex flex-wrap items-start justify-between gap-3">
              <div className="min-w-0">
                <h2 className="text-base font-medium">{next.title}</h2>
                <p className="mt-1 max-w-prose text-sm text-muted-foreground">{next.action}</p>
                <p className="mt-1 text-xs text-muted-foreground">{next.gap} · {next.reference}</p>
              </div>
              <div className="text-right">
                <p className="font-mono text-2xl tabular-nums">{money(next.estimated_value)}</p>
                <p className="text-[10px] text-muted-foreground">{next.value_note || "estimated value"}</p>
                {opps && opps.days_left_in_year > 0 && next.deadline && (
                  <p className="text-[10px] text-muted-foreground">{opps.days_left_in_year} days left this year</p>
                )}
              </div>
            </div>
          </section>
        )}

        <div className="grid gap-3 sm:grid-cols-4">
          <Tile label="Deductible this year" value={money(summary?.total_deductible)} accent />
          <Tile label="Not deductible" value={money(summary?.total_nondeductible)} />
          <Tile label="Open questions" value={String(summary?.open_questions ?? 0)} />
          <Tile label="Est. research credits" value={money(credits?.total_estimated_tax_credits)} accent />
        </div>

        {questions.length > 0 && (
          <section className="rounded-lg border border-border bg-card/40 p-4">
            <h2 className="text-sm font-medium">Who was this meal with?</h2>
            <p className="text-xs text-muted-foreground">A whole-company event is 100% deductible; a client or employee meal is 50%; solo is 0%.</p>
            <ul className="mt-3 space-y-3">
              {questions.map((q) => (
                <li key={q.transaction_id} className="rounded-md border border-border p-3">
                  <div className="flex items-center justify-between gap-3 text-sm">
                    <span className="min-w-0 truncate font-medium">{q.merchant}</span>
                    <span className="shrink-0 font-mono tabular-nums">
                      {q.date} · {money(q.amount)}
                    </span>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-1">
                    {q.answers.map((a) => (
                      <DitherButton
                        key={a.id}
                        color="grey"
                        variant={a.deductible_pct === 1 ? "solid" : "hatched"}
                        className="text-[11px]"
                        disabled={busy === q.transaction_id}
                        onClick={() => answer(q, a.id)}
                      >
                        {a.label} · {Math.round(a.deductible_pct * 100)}%
                      </DitherButton>
                    ))}
                  </div>
                </li>
              ))}
            </ul>
          </section>
        )}

        <section className="rounded-lg border border-border bg-card/40 p-4">
          <h2 className="text-sm font-medium">Opportunities, nearest first</h2>
          <ul className="mt-2 divide-y divide-border">
            {(opps?.opportunities ?? []).map((o) => (
              <li key={o.id} className="flex flex-col gap-1 py-3 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-sm font-medium">{o.title}</span>
                    <Badge variant={o.status === "qualified" ? "secondary" : "outline"} className="rounded-sm text-[10px]">
                      {STATUS_LABEL[o.status] ?? o.status}
                    </Badge>
                    {o.deadline && <span className="text-[10px] text-muted-foreground">by {o.deadline}</span>}
                  </div>
                  <p className="mt-0.5 max-w-prose text-xs text-muted-foreground">{o.action}</p>
                  <p className="mt-0.5 text-[10px] text-muted-foreground">{o.gap} · {o.reference}</p>
                </div>
                <span className="shrink-0 font-mono text-sm tabular-nums">{money(o.estimated_value)}</span>
              </li>
            ))}
            {!opps && <li className="py-3 text-sm text-muted-foreground">Opportunities load from the books API.</li>}
          </ul>
        </section>

        {summary && summary.by_class.length > 0 && (
          <section className="rounded-lg border border-border bg-card/40 p-4">
            <h2 className="text-sm font-medium">Deductions by tax class ({summary.tax_year})</h2>
            <table className="mt-2 w-full text-xs">
              <thead className="text-left text-muted-foreground">
                <tr>
                  <th className="py-1 font-normal">Class</th>
                  <th className="py-1 text-right font-normal">%</th>
                  <th className="py-1 text-right font-normal">Spent</th>
                  <th className="py-1 text-right font-normal">Deductible</th>
                  <th className="hidden py-1 font-normal sm:table-cell">Reference</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {summary.by_class.map((c) => (
                  <tr key={c.tax_class}>
                    <td className="py-1 pr-2">{c.label}</td>
                    <td className="py-1 text-right font-mono tabular-nums">{Math.round(c.deductible_pct * 100)}</td>
                    <td className="py-1 text-right font-mono tabular-nums">{money(c.spent)}</td>
                    <td className="py-1 text-right font-mono tabular-nums">{money(c.deductible)}</td>
                    <td className="hidden py-1 pl-2 text-muted-foreground sm:table-cell">{c.irc_reference}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}

        <section className="rounded-lg border border-border bg-card/40 p-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-medium">Research credit estimate</h2>
            <Badge variant="outline" className="rounded-sm font-mono text-[10px]">{credits?.compliance_status ?? "—"}</Badge>
          </div>
          <dl className="mt-3 grid gap-2 text-sm sm:grid-cols-2">
            <Row k="Federal Section 41" v={money(credits?.federal_section_41_credit)} />
            <Row k={`${state} state credit`} v={money(credits?.state_tax_credit)} />
            <Row k="Engineering payroll QRE" v={money(credits?.rd_payroll_qre)} />
            <Row k="Cloud compute QRE" v={money(credits?.cloud_compute_qre)} />
            <Row k="Section 174 amortization deduction" v={money(credits?.sec_174_annual_amortization_deduction)} />
          </dl>
          {refs.length > 0 && (
            <ul className="mt-3 list-disc space-y-1 pl-5 text-xs text-muted-foreground">
              {refs.map((r, i) => <li key={i}>{r}</li>)}
            </ul>
          )}
          <div className="mt-4">
            <DitherButton
              color="grey"
              variant="hatched"
              className="text-[11px]"
              disabled={!credits}
              onClick={() =>
                credits &&
                pushArtifact({
                  id: `credits_${state}`,
                  kind: "document",
                  title: `${state} research credit claim file`,
                  subtitle: money(credits.total_estimated_tax_credits),
                  payload: credits as unknown as Record<string, unknown>,
                })
              }
            >
              Preview claim file
            </DitherButton>
          </div>
        </section>

        <section className="rounded-lg border border-border bg-card/40 p-4">
          <h2 className="text-sm font-medium">Recent decisions</h2>
          {!approvals.length && <p className="mt-2 text-sm text-muted-foreground">No approvals recorded yet. Decisions from the mobile app land here.</p>}
          <ul className="mt-2 divide-y divide-border text-sm">
            {approvals.map((a) => (
              <li key={a.id} className="flex items-center justify-between gap-3 py-2">
                <span className="min-w-0 truncate">
                  <span className="font-mono text-[10px] uppercase text-muted-foreground">{a.kind}</span> {a.subject ?? a.card_id}
                </span>
                <span className="flex shrink-0 items-center gap-2">
                  {a.amount != null && <span className="font-mono tabular-nums">{money(a.amount)}</span>}
                  <Badge variant="secondary" className="rounded-sm text-[10px]">{a.decision}</Badge>
                </span>
              </li>
            ))}
          </ul>
        </section>

        <p className="text-xs text-muted-foreground">
          {opps?.disclaimer ?? "Estimates only. Credits are claimed on the return by a tax professional; this view assembles the evidence."}
        </p>
      </div>
    </div>
  );
}

function Tile({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div className="rounded-lg border border-border bg-card/40 p-4">
      <p className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground">{label}</p>
      <p className={`mt-1 font-mono text-2xl tabular-nums ${accent ? "text-foreground" : "text-muted-foreground"}`}>{value}</p>
    </div>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <dt className="text-muted-foreground">{k}</dt>
      <dd className="font-mono tabular-nums">{v}</dd>
    </div>
  );
}
