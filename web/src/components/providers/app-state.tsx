"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { Artifact, ViewId } from "@/lib/types";

type AppState = {
  view: ViewId;
  setView: (v: ViewId) => void;
  navCollapsed: boolean;
  setNavCollapsed: (v: boolean) => void;
  artifactsOpen: boolean;
  setArtifactsOpen: (v: boolean) => void;
  artifacts: Artifact[];
  activeArtifactId: string | null;
  setActiveArtifactId: (id: string | null) => void;
  pushArtifact: (a: Omit<Artifact, "id" | "createdAt"> & { id?: string }) => void;
  clearArtifacts: () => void;
};

const Ctx = createContext<AppState | null>(null);

export function AppStateProvider({ children }: { children: ReactNode }) {
  const [view, setView] = useState<ViewId>("dashboard");
  const [navCollapsed, setNavCollapsed] = useState(false);
  const [artifactsOpen, setArtifactsOpen] = useState(false);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [activeArtifactId, setActiveArtifactId] = useState<string | null>(null);

  const pushArtifact = useCallback(
    (a: Omit<Artifact, "id" | "createdAt"> & { id?: string }) => {
      const id = a.id ?? `art_${Math.random().toString(36).slice(2, 10)}`;
      const next: Artifact = {
        ...a,
        id,
        createdAt: new Date().toISOString(),
      };
      setArtifacts((prev) => {
        const without = prev.filter((x) => x.id !== id);
        return [next, ...without].slice(0, 24);
      });
      setActiveArtifactId(id);
      setArtifactsOpen(true);
    },
    [],
  );

  const clearArtifacts = useCallback(() => {
    setArtifacts([]);
    setActiveArtifactId(null);
  }, []);

  const value = useMemo(
    () => ({
      view,
      setView,
      navCollapsed,
      setNavCollapsed,
      artifactsOpen,
      setArtifactsOpen,
      artifacts,
      activeArtifactId,
      setActiveArtifactId,
      pushArtifact,
      clearArtifacts,
    }),
    [
      view,
      navCollapsed,
      artifactsOpen,
      artifacts,
      activeArtifactId,
      pushArtifact,
      clearArtifacts,
    ],
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useAppState() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useAppState must be used within AppStateProvider");
  return ctx;
}
