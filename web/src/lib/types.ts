export type ViewId =
  | "dashboard"
  | "books"
  | "chat"
  | "grants"
  | "credits"
  | "crm_companies"
  | "crm_people"
  | "crm_opportunities"
  | "crm_tasks"
  | "crm_notes"
  | "crm_workflows"
  | "apps_projects"
  | "apps_builds"
  | "apps_releases"
  | "apps_stores"
  | "apps_web"
  | "apps_pipelines"
  | "settings";

export type CrmTab = "companies" | "people" | "opportunities" | "tasks" | "notes" | "workflows";

export type AppsTab = "projects" | "builds" | "releases" | "stores" | "web" | "pipelines";

export type NavItem = { id: ViewId; label: string; hint?: string };

export type NavSection = { id: string; label: string; items: NavItem[] };

export type ArtifactKind = "chart" | "grant" | "transactions" | "ledger" | "document" | "crm" | "apps";

export type Artifact = {
  id: string;
  kind: ArtifactKind;
  title: string;
  subtitle?: string;
  payload?: Record<string, unknown>;
  createdAt: string;
};
