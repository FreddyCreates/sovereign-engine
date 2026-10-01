"use client";

import { useCallback, useEffect, useState } from "react";
import { DitherButton } from "@/components/dither-kit/button";
import { Badge } from "@/components/ui/badge";
import {
  confirmTransaction,
  connectBank,
  createLinkToken,
  fetchBooksHome,
  fetchCategories,
  fetchInbox,
  syncBank,
  type BooksHome,
  type InboxTxn,
} from "@/lib/books-api";
import { useAppState } from "@/components/providers/app-state";

declare global {
  interface Window {
    Plaid?: {
      create: (opts: {
        token: string;
        onSuccess: (public_token: string, metadata: { institution?: { name?: string } }) => void;
        onExit?: (err: { display_message?: string; error_message?: string } | null) => void;
      }) => { open: () => void };
    };
  }
}

function loadPlaidScript(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (window.Plaid) {
      resolve();
      return;
    }
    const existing = document.querySelector('script[data-plaid]');
    if (existing) {
      existing.addEventListener("load", () => resolve());
      return;
    }
    const s = document.createElement("script");
    s.src = "https://cdn.plaid.com/link/v2/stable/link-initialize.js";
    s.async = true;
    s.dataset.plaid = "1";
    s.onload = () => resolve();
    s.onerror = () => reject(new Error("Plaid Link failed to load"));
    document.body.appendChild(s);
  });
}

export function BooksView() {
  const { pushArtifact } = useAppState();
  const [home, setHome] = useState<BooksHome | null>(null);
  const [inbox, setInbox] = useState<InboxTxn[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const [h, i, cats] = await Promise.all([
        fetchBooksHome(),
        fetchInbox(),
        fetchCategories(),
      ]);
      setHome(h);
      setInbox(i.transactions);
      setCategories(cats.categories.map((c) => c.name));
    } catch {
      setStatus("Books API offline on :8090");
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  async function openPlaid() {
    setBusy(true);
    setStatus("Creating link token…");
    try {
      await loadPlaidScript();
      const link = await createLinkToken();
      if (link.mode !== "live") {
        setStatus("API still mock — check .env PLAID_* and restart Python server");
        return;
      }
      if (!window.Plaid) throw new Error("Plaid unavailable");
      const handler = window.Plaid.create({
        token: link.link_token,
        onSuccess: async (public_token, metadata) => {
          setStatus("Exchanging & syncing…");
          const connected = await connectBank(
            public_token,
            metadata.institution?.name,
          );
          if (connected.status === "ERROR") {
            setStatus(connected.error || "Connect blocked");
            return;
          }
          setStatus(
            `Connected ${connected.institution_name ?? "bank"} · imported ${connected.sync?.imported ?? 0}`,
          );
          await refresh();
          pushArtifact({
            kind: "ledger",
            title: connected.institution_name ?? "Bank connected",
            subtitle: `${connected.account_count} accounts`,
            payload: connected as Record<string, unknown>,
          });
        },
        onExit: (err) => {
          if (err) setStatus(err.display_message || err.error_message || "Link closed");
        },
      });
      handler.open();
      setStatus("Plaid Link open — sandbox: user_good / pass_good");
    } catch (e) {
      setStatus(e instanceof Error ? e.message : "Connect failed");
    } finally {
      setBusy(false);
    }
  }

  async function onSync() {
    setBusy(true);
    try {
      const res = await syncBank();
      setStatus(`Synced · imported ${res.imported} · skipped ${res.skipped_duplicates}`);
      await refresh();
      if (inbox.length) {
        pushArtifact({
          kind: "transactions",
          title: "Review inbox",
          subtitle: `${res.inbox_count ?? inbox.length} items`,
          payload: {
            rows: inbox.slice(0, 12).map((t) => ({
              name: t.name,
              amount: t.amount,
              date: t.date,
            })),
          },
        });
      }
    } catch (e) {
      setStatus(e instanceof Error ? e.message : "Sync failed");
    } finally {
      setBusy(false);
    }
  }

  async function onConfirm(txn: InboxTxn, category?: string) {
    setBusy(true);
    try {
      const cat = category || txn.category_suggested || categories[0];
      const res = await confirmTransaction(txn.id, cat);
      if (res.status === "ERROR") {
        setStatus(res.error || "Confirm failed");
      } else {
        setStatus(`Confirmed · ${res.category} · inbox ${res.inbox_count}`);
        await refresh();
      }
    } catch (e) {
      setStatus(e instanceof Error ? e.message : "Confirm failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex h-full flex-col">
      <header className="border-b border-border px-6 py-4">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground">Ledger</p>
            <h1 className="text-xl font-medium tracking-tight">Books</h1>
          </div>
          <div className="flex flex-wrap gap-2">
            <DitherButton color="grey" variant="gradient" disabled={busy} onClick={openPlaid}>
              Connect with Plaid
            </DitherButton>
            <DitherButton color="grey" variant="hatched" disabled={busy} onClick={onSync}>
              Sync
            </DitherButton>
            <DitherButton color="grey" variant="dotted" disabled={busy} onClick={() => void refresh()}>
              Refresh
            </DitherButton>
          </div>
        </div>
        {status && <p className="mt-2 text-xs text-muted-foreground">{status}</p>}
        {home?.mode === "live" && (
          <p className="mt-1 font-mono text-[10px] text-muted-foreground">
            sandbox login · user_good / pass_good · mfa 1234
          </p>
        )}
      </header>

      <div className="grid flex-1 grid-cols-1 gap-0 overflow-hidden lg:grid-cols-2">
        <section className="overflow-auto border-b border-border p-6 lg:border-b-0 lg:border-r">
          <h2 className="mb-3 text-sm font-medium">Accounts</h2>
          {!home?.accounts?.length && (
            <p className="text-sm text-muted-foreground">No linked accounts yet.</p>
          )}
          <ul className="space-y-2">
            {home?.accounts?.map((a) => (
              <li
                key={a.id}
                className="flex items-center justify-between rounded-md border border-border px-3 py-2 text-sm"
              >
                <span>
                  <span className="font-medium">
                    {a.name}
                    {a.mask ? ` ····${a.mask}` : ""}
                  </span>
                  <span className="mt-0.5 block text-[10px] uppercase tracking-wide text-muted-foreground">
                    {a.type} / {a.subtype}
                  </span>
                </span>
                <span className="font-mono tabular-nums">
                  {a.current_balance.toLocaleString("en-US", {
                    style: "currency",
                    currency: "USD",
                  })}
                </span>
              </li>
            ))}
          </ul>
          <div className="mt-4 flex flex-wrap gap-2">
            <Badge variant="outline" className="rounded-sm font-mono text-[10px]">
              mode {home?.mode ?? "—"}
            </Badge>
            <Badge variant="outline" className="rounded-sm font-mono text-[10px]">
              {home?.bank_connected ? "connected" : "disconnected"}
            </Badge>
            <Badge variant="outline" className="rounded-sm font-mono text-[10px]">
              cash{" "}
              {home
                ? home.cash_balance.toLocaleString("en-US", {
                    style: "currency",
                    currency: "USD",
                  })
                : "—"}
            </Badge>
          </div>
        </section>

        <section className="overflow-auto p-6">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-sm font-medium">Review inbox</h2>
            <span className="font-mono text-xs text-muted-foreground">{inbox.length}</span>
          </div>
          {!inbox.length && (
            <p className="text-sm text-muted-foreground">Connect and sync to fill the inbox.</p>
          )}
          <ul className="space-y-3">
            {inbox.map((t) => (
              <li
                key={t.id}
                className="flex flex-col gap-2 border-b border-border/70 pb-3 text-sm sm:flex-row sm:items-center sm:justify-between"
              >
                <span className="min-w-0">
                  <span className="block truncate font-medium">{t.name}</span>
                  <span className="text-[11px] text-muted-foreground">
                    {t.date} · {t.category_suggested ?? "Uncategorized"}
                    {t.pending ? " · pending" : ""}
                  </span>
                </span>
                <div className="flex shrink-0 items-center gap-2">
                  <span className="font-mono tabular-nums">
                    {t.amount > 0 ? "−" : "+"}$
                    {Math.abs(t.amount).toFixed(2)}
                  </span>
                  <DitherButton
                    color="grey"
                    variant="hatched"
                    className="h-7 text-[10px]"
                    disabled={busy || Boolean(t.pending)}
                    onClick={() => void onConfirm(t)}
                  >
                    Confirm
                  </DitherButton>
                </div>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}
