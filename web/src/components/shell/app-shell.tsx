"use client";

import { LeftNav } from "@/components/shell/left-nav";
import { ArtifactsPanel } from "@/components/shell/artifacts-panel";
import { useAppState } from "@/components/providers/app-state";
import { DashboardView } from "@/components/views/dashboard-view";
import { BooksView } from "@/components/views/books-view";
import { ChatView } from "@/components/views/chat-view";
import { GrantsView } from "@/components/views/grants-view";
import { CrmView } from "@/components/views/crm-view";
import { AppsView } from "@/components/views/apps-view";
import { SettingsView } from "@/components/views/settings-view";

export function AppShell() {
  const { view } = useAppState();
  const isCrm = view.startsWith("crm_");
  const isApps = view.startsWith("apps_");

  return (
    <div className="flex h-dvh w-full overflow-hidden bg-background text-foreground">
      <LeftNav />
      <main className="min-w-0 flex-1 overflow-hidden">
        {view === "dashboard" && <DashboardView />}
        {view === "books" && <BooksView />}
        {view === "chat" && <ChatView />}
        {view === "grants" && <GrantsView />}
        {isCrm && <CrmView />}
        {isApps && <AppsView />}
        {view === "settings" && <SettingsView />}
      </main>
      <ArtifactsPanel />
    </div>
  );
}
