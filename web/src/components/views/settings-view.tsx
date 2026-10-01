"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { DitherButton } from "@/components/dither-kit/button";
import {
  activateProLocal,
  fetchEntitlements,
  type Entitlements,
} from "@/lib/books-api";

export function SettingsView() {
  const [ent, setEnt] = useState<Entitlements | null>(null);
  const [status, setStatus] = useState("");

  useEffect(() => {
    fetchEntitlements()
      .then(setEnt)
      .catch(() => setStatus("Books API offline"));
  }, []);

  async function onActivate() {
    try {
      const res = await activateProLocal();
      setEnt(res as unknown as Entitlements);
      setStatus("Local Pro activated (scripts/activate_pro.py equivalent)");
      const fresh = await fetchEntitlements();
      setEnt(fresh);
    } catch (e) {
      setStatus(e instanceof Error ? e.message : "Activate failed");
    }
  }

  return (
    <div className="flex h-full flex-col">
      <header className="border-b border-border px-6 py-4">
        <p className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground">System</p>
        <h1 className="text-xl font-medium tracking-tight">Settings</h1>
      </header>
      <div className="space-y-4 p-6">
        <section className="rounded-lg border border-border p-4">
          <h2 className="text-sm font-medium">Connections</h2>
          <ul className="mt-3 space-y-2 text-sm">
            <li className="flex items-center justify-between border-b border-border/60 py-2">
              <span>Plaid (books API)</span>
              <Badge variant="outline" className="rounded-sm font-mono text-[10px]">
                :8090
              </Badge>
            </li>
            <li className="flex items-center justify-between border-b border-border/60 py-2">
              <span>RevenueCat</span>
              <Badge variant="outline" className="rounded-sm font-mono text-[10px]">
                {ent ? `${ent.mode}${ent.pro_active ? " · pro" : ""}` : "—"}
              </Badge>
            </li>
            <li className="flex items-center justify-between py-2">
              <span>Theme</span>
              <Badge variant="outline" className="rounded-sm text-[10px]">
                dark · mono
              </Badge>
            </li>
          </ul>
        </section>

        <section className="rounded-lg border border-border p-4">
          <h2 className="text-sm font-medium">Sovereign Pro</h2>
          <p className="mt-1 text-xs text-muted-foreground">
            Entitlement <code className="font-mono">pro_access</code>. Live mode uses{" "}
            <code className="font-mono">REVENUECAT_SECRET_API_KEY</code>; offline uses local SQLite
            via Settings or <code className="font-mono">scripts/activate_pro.py</code>.
          </p>
          <ul className="mt-3 space-y-1 font-mono text-[11px] text-muted-foreground">
            <li>user · {ent?.app_user_id ?? "—"}</li>
            <li>active · {String(ent?.pro_active ?? false)}</li>
            <li>source · {ent?.source ?? "—"}</li>
            <li>
              features · {(ent?.features || []).join(", ") || "none"}
            </li>
          </ul>
          <div className="mt-3">
            <DitherButton color="grey" variant="hatched" onClick={() => void onActivate()}>
              Activate Pro (local)
            </DitherButton>
          </div>
          {status && <p className="mt-2 text-xs text-muted-foreground">{status}</p>}
        </section>

        <p className="text-xs text-muted-foreground">
          Set <code className="font-mono">NEXT_PUBLIC_BOOKS_API</code> to point at the Python books
          server (default http://localhost:8090).
        </p>
      </div>
    </div>
  );
}
