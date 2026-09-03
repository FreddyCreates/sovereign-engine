"use client";

import {
  Banknote,
  Building2,
  CloudUpload,
  Contact,
  GitBranch,
  Globe,
  LayoutDashboard,
  ListTodo,
  MessageSquare,
  NotebookPen,
  Package,
  PanelLeftClose,
  PanelLeftOpen,
  PanelRightClose,
  PanelRightOpen,
  Rocket,
  Settings,
  Sparkles,
  SquareKanban,
  Store,
} from "lucide-react";
import { DitherAvatar } from "@/components/dither-kit/avatar";
import { DitherButton } from "@/components/dither-kit/button";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import type { NavSection, ViewId } from "@/lib/types";
import { useAppState } from "@/components/providers/app-state";

const SECTIONS: NavSection[] = [
  {
    id: "books",
    label: "Books",
    items: [
      { id: "dashboard", label: "Dashboard", hint: "Cash & runway" },
      { id: "books", label: "Books", hint: "Bank & inbox" },
      { id: "chat", label: "Chat", hint: "Ask the ledger" },
      { id: "grants", label: "Grants", hint: "Non-dilutive capital" },
    ],
  },
  {
    id: "crm",
    label: "CRM",
    items: [
      { id: "crm_companies", label: "Companies", hint: "Accounts" },
      { id: "crm_people", label: "People", hint: "Contacts" },
      { id: "crm_opportunities", label: "Opportunities", hint: "Pipeline" },
      { id: "crm_tasks", label: "Tasks", hint: "Follow-ups" },
      { id: "crm_notes", label: "Notes", hint: "Context" },
      { id: "crm_workflows", label: "Workflows", hint: "Automations" },
    ],
  },
  {
    id: "apps",
    label: "App management",
    items: [
      { id: "apps_projects", label: "Projects", hint: "Linked apps" },
      { id: "apps_builds", label: "Builds", hint: "Cloud compile" },
      { id: "apps_releases", label: "Releases", hint: "OTA & binary" },
      { id: "apps_stores", label: "Stores", hint: "Play · App Store" },
      { id: "apps_web", label: "Web deploy", hint: "Preview · prod" },
      { id: "apps_pipelines", label: "Pipelines", hint: "CI/CD" },
    ],
  },
  {
    id: "system",
    label: "System",
    items: [{ id: "settings", label: "Settings", hint: "Connections" }],
  },
];

const ICONS: Record<ViewId, typeof LayoutDashboard> = {
  dashboard: LayoutDashboard,
  books: Banknote,
  chat: MessageSquare,
  grants: Sparkles,
  crm_companies: Building2,
  crm_people: Contact,
  crm_opportunities: SquareKanban,
  crm_tasks: ListTodo,
  crm_notes: NotebookPen,
  crm_workflows: GitBranch,
  apps_projects: Package,
  apps_builds: CloudUpload,
  apps_releases: Rocket,
  apps_stores: Store,
  apps_web: Globe,
  apps_pipelines: GitBranch,
  settings: Settings,
};

export function LeftNav() {
  const { view, setView, navCollapsed, setNavCollapsed, artifactsOpen, setArtifactsOpen } =
    useAppState();

  return (
    <aside
      className={cn(
        "flex h-full shrink-0 flex-col border-r border-border bg-sidebar text-sidebar-foreground transition-[width] duration-200",
        navCollapsed ? "w-14" : "w-56",
      )}
    >
      <div className={cn("flex items-center gap-2 px-3 py-3", navCollapsed && "justify-center px-2")}>
        <DitherAvatar name="sovereign" size={28} />
        {!navCollapsed && (
          <div className="min-w-0">
            <div className="truncate text-sm font-medium tracking-tight">Sovereign</div>
            <div className="truncate text-[10px] uppercase tracking-wider text-muted-foreground">
              Books · CRM · Apps
            </div>
          </div>
        )}
      </div>
      <Separator />
      <ScrollArea className="flex-1 px-2 py-2">
        <nav className="flex flex-col gap-3">
          {SECTIONS.map((section) => (
            <div key={section.id}>
              {!navCollapsed && (
                <div className="mb-1 px-2 text-[10px] font-medium uppercase tracking-[0.18em] text-muted-foreground">
                  {section.label}
                </div>
              )}
              {navCollapsed && section.id !== "books" && (
                <Separator className="mb-1 opacity-40" />
              )}
              <div className="flex flex-col gap-0.5">
                {section.items.map((item) => {
                  const Icon = ICONS[item.id];
                  const active = view === item.id;
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => setView(item.id)}
                      title={item.label}
                      className={cn(
                        "flex w-full items-center gap-2 rounded-md px-2 py-2 text-left text-sm transition-colors",
                        active
                          ? "bg-sidebar-accent text-sidebar-accent-foreground"
                          : "text-muted-foreground hover:bg-sidebar-accent/60 hover:text-foreground",
                        navCollapsed && "justify-center px-0",
                      )}
                    >
                      <Icon className="size-4 shrink-0 opacity-80" />
                      {!navCollapsed && (
                        <span className="min-w-0">
                          <span className="block truncate font-medium">{item.label}</span>
                          <span className="block truncate text-[10px] text-muted-foreground">
                            {item.hint}
                          </span>
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>
      </ScrollArea>
      <Separator />
      <div className={cn("flex flex-col gap-1 p-2", navCollapsed && "items-center")}>
        <DitherButton
          color="grey"
          variant="hatched"
          className="h-8 w-full text-[11px]"
          onClick={() => setNavCollapsed(!navCollapsed)}
        >
          {navCollapsed ? (
            <PanelLeftOpen className="size-3.5" />
          ) : (
            <span className="inline-flex items-center gap-1.5">
              <PanelLeftClose className="size-3.5" /> Collapse
            </span>
          )}
        </DitherButton>
        <DitherButton
          color="grey"
          variant="dotted"
          className="h-8 w-full text-[11px]"
          onClick={() => setArtifactsOpen(!artifactsOpen)}
        >
          {artifactsOpen ? (
            navCollapsed ? (
              <PanelRightClose className="size-3.5" />
            ) : (
              <span className="inline-flex items-center gap-1.5">
                <PanelRightClose className="size-3.5" /> Hide pane
              </span>
            )
          ) : navCollapsed ? (
            <PanelRightOpen className="size-3.5" />
          ) : (
            <span className="inline-flex items-center gap-1.5">
              <PanelRightOpen className="size-3.5" /> Artifacts
            </span>
          )}
        </DitherButton>
      </div>
    </aside>
  );
}
