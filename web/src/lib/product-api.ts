/** CRM and app-management endpoints served by sovereign_books/http_api.py. */

import { apiGet, apiPost } from "@/lib/books-api";
import type { AppsTab, CrmTab } from "@/lib/types";

type Row = Record<string, unknown>;

export type CrmListResponse = { records: Row[]; count?: number; status?: string };

export const fetchCrmList = (tab: CrmTab) => apiGet<CrmListResponse>(`/api/v1/crm/${tab}`);

export const createCrmRecord = (tab: CrmTab, body: Row) => apiPost<Row>(`/api/v1/crm/${tab}`, body);

export const fetchAppsProjects = () =>
  apiGet<{ projects: Row[]; count?: number; status?: string }>("/api/v1/apps/projects");

export const fetchAppsBuilds = (projectId?: string) =>
  apiGet<{ builds: Row[]; count?: number; status?: string }>(
    `/api/v1/apps/builds${projectId ? `?project_id=${encodeURIComponent(projectId)}` : ""}`,
  );

export const fetchAppsReleases = () =>
  apiGet<{ releases: Row[]; count?: number; status?: string }>("/api/v1/apps/releases");

export const fetchAppsStores = () =>
  apiGet<{ submissions: Row[]; count?: number; status?: string }>("/api/v1/apps/stores");

export const fetchAppsWeb = () =>
  apiGet<{ deploys: Row[]; count?: number; status?: string }>("/api/v1/apps/web");

export const fetchAppsPipelines = () =>
  apiGet<{ pipelines: Row[]; count?: number; status?: string }>("/api/v1/apps/pipelines");

export const triggerAppBuild = (projectId: string, platform = "android", profile = "preview") =>
  apiPost<Row>("/api/v1/apps/builds", { project_id: projectId, platform, profile });

export const appsTabEndpoint: Record<AppsTab, string> = {
  projects: "/api/v1/apps/projects",
  builds: "/api/v1/apps/builds",
  releases: "/api/v1/apps/releases",
  stores: "/api/v1/apps/stores",
  web: "/api/v1/apps/web",
  pipelines: "/api/v1/apps/pipelines",
};
