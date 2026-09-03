"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { DitherButton } from "@/components/dither-kit/button";
import { useAppState } from "@/components/providers/app-state";
import {
  fetchAppsBuilds,
  fetchAppsPipelines,
  fetchAppsProjects,
  fetchAppsReleases,
  fetchAppsStores,
  fetchAppsWeb,
  triggerAppBuild,
} from "@/lib/product-api";
import type { AppsTab, ViewId } from "@/lib/types";

const VIEW_TO_TAB: Partial<Record<ViewId, AppsTab>> = {
  apps_projects: "projects",
  apps_builds: "builds",
  apps_releases: "releases",
  apps_stores: "stores",
  apps_web: "web",
  apps_pipelines: "pipelines",
};

const LABELS: Record<AppsTab, string> = {
  projects: "Projects",
  builds: "Builds",
  releases: "Releases",
  stores: "Stores",
  web: "Web deploy",
  pipelines: "Pipelines",
};

export function AppsView() {
  const { view, pushArtifact } = useAppState();
  const tab = VIEW_TO_TAB[view] ?? "projects";
  const [cols, setCols] = useState<string[]>([]);
  const [rows, setRows] = useState<string[][]>([]);
  const [projectId, setProjectId] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);

  async function refresh() {
    setBusy(true);
    try {
      if (tab === "projects") {
        const data = await fetchAppsProjects();
        const projects = data.projects || [];
        if (projects[0]?.id) setProjectId(String(projects[0].id));
        setCols(["name", "platforms", "repo", "channel", "id"]);
        setRows(
          projects.map((p) => {
            let platforms = "";
            try {
              const raw = p.platforms_json ?? p.platforms;
              platforms = Array.isArray(raw)
                ? (raw as string[]).join(" · ")
                : Array.isArray(JSON.parse(String(raw || "[]")))
                  ? (JSON.parse(String(raw)) as string[]).join(" · ")
                  : String(raw ?? "");
            } catch {
              platforms = String(p.platforms_json ?? "");
            }
            return [
              String(p.name ?? ""),
              platforms,
              String(p.git_url ?? "—"),
              "production",
              String(p.id ?? ""),
            ];
          }),
        );
      } else if (tab === "builds") {
        const data = await fetchAppsBuilds(projectId ?? undefined);
        const builds = data.builds || [];
        setCols(["id", "platform", "profile", "fingerprint", "status"]);
        setRows(
          builds.map((b) => [
            String(b.id ?? "").slice(0, 12),
            String(b.platform ?? ""),
            String(b.profile ?? ""),
            String(b.fingerprint ?? "—").slice(0, 10),
            String(b.status ?? ""),
          ]),
        );
      } else if (tab === "releases") {
        const data = await fetchAppsReleases();
        const releases = data.releases || [];
        setCols(["id", "version", "channel", "rollout", "notes"]);
        setRows(
          releases.map((r) => [
            String(r.id ?? "").slice(0, 12),
            String(r.version ?? ""),
            String(r.channel ?? ""),
            String(r.rollout_pct ?? ""),
            String(r.notes ?? "—").slice(0, 32),
          ]),
        );
      } else if (tab === "stores") {
        const data = await fetchAppsStores();
        const subs = data.submissions || [];
        setCols(["store", "track", "version", "status", "id"]);
        setRows(
          subs.map((s) => [
            String(s.store ?? ""),
            String(s.track ?? ""),
            String(s.version ?? "—"),
            String(s.status ?? ""),
            String(s.id ?? "").slice(0, 12),
          ]),
        );
      } else if (tab === "web") {
        const data = await fetchAppsWeb();
        const deploys = data.deploys || [];
        setCols(["env", "url", "framework", "status", "id"]);
        setRows(
          deploys.map((d) => [
            String(d.env ?? ""),
            String(d.url ?? "—"),
            String(d.framework ?? "—"),
            String(d.status ?? ""),
            String(d.id ?? "").slice(0, 12),
          ]),
        );
      } else {
        const data = await fetchAppsPipelines();
        const pipes = data.pipelines || [];
        setCols(["name", "project_id", "created_at", "id"]);
        setRows(
          pipes.map((p) => [
            String(p.name ?? ""),
            String(p.project_id ?? "").slice(0, 12),
            String(p.created_at ?? ""),
            String(p.id ?? "").slice(0, 12),
          ]),
        );
      }
      setErr(null);
    } catch {
      setErr("Apps API offline — start sovereign_dashboard_server.py on :8090");
      setRows([]);
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    void refresh();
  }, [tab]);

  async function onBuild() {
    if (!projectId) {
      setStatus("No project — open Projects or run scripts/seed_apps.py");
      return;
    }
    setBusy(true);
    try {
      const res = (await triggerAppBuild(projectId)) as { status?: string; id?: string };
      setStatus(`Build ${res.id ?? ""} · ${res.status ?? "queued"}`);
      await refresh();
    } catch (e) {
      setStatus(e instanceof Error ? e.message : "Build failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex h-full flex-col">
      <header className="border-b border-border px-6 py-4">
        <p className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground">
          App management
        </p>
        <div className="mt-1 flex flex-wrap items-end justify-between gap-3">
          <h1 className="text-xl font-medium tracking-tight">{LABELS[tab]}</h1>
          <div className="flex flex-wrap gap-2">
            <Badge variant="outline" className="rounded-sm font-mono text-[10px]">
              {rows.length}
            </Badge>
            {tab === "builds" && (
              <DitherButton
                color="grey"
                variant="gradient"
                className="h-7 text-[10px]"
                disabled={busy}
                onClick={() => void onBuild()}
              >
                Trigger build
              </DitherButton>
            )}
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
                  kind: "apps",
                  title: LABELS[tab],
                  subtitle: `${rows.length} rows`,
                  payload: { tab, rows },
                })
              }
            >
              Pin
            </DitherButton>
          </div>
        </div>
        {status && <p className="mt-2 text-xs text-muted-foreground">{status}</p>}
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
                    {c}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {!rows.length && (
                <tr>
                  <td colSpan={Math.max(cols.length, 1)} className="px-3 py-6 text-sm text-muted-foreground">
                    No rows — run scripts/seed_apps.py
                  </td>
                </tr>
              )}
              {rows.map((row, i) => (
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
