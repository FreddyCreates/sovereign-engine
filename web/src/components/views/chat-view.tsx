"use client";

import { useState } from "react";
import { DitherButton } from "@/components/dither-kit/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useAppState } from "@/components/providers/app-state";
import { sendChat } from "@/lib/books-api";

type Msg = { role: "user" | "assistant"; text: string };

export function ChatView() {
  const { pushArtifact } = useAppState();
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [msgs, setMsgs] = useState<Msg[]>([
    {
      role: "assistant",
      text: "Ask about cash, inbox, grants, or Pro. Answers come from your books data (script engine; optional LLM polish if keys are set).",
    },
  ]);

  async function send() {
    const text = input.trim();
    if (!text || busy) return;
    setInput("");
    setMsgs((m) => [...m, { role: "user", text }]);
    setBusy(true);
    try {
      const res = await sendChat(text);
      for (const a of res.artifacts || []) {
        pushArtifact({
          kind: a.kind as "chart" | "grant" | "transactions" | "ledger" | "document",
          title: a.title,
          subtitle: a.subtitle,
          payload: a.payload,
        });
      }
      setMsgs((m) => [
        ...m,
        {
          role: "assistant",
          text: res.reply + (res.engine ? ` · ${res.engine}` : ""),
        },
      ]);
    } catch {
      setMsgs((m) => [
        ...m,
        {
          role: "assistant",
          text: "Books API offline on :8090 — start sovereign_dashboard_server.py, or run scripts/chat_books.py locally.",
        },
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex h-full flex-col">
      <header className="border-b border-border px-6 py-4">
        <p className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground">Assistant</p>
        <h1 className="text-xl font-medium tracking-tight">Chat</h1>
      </header>
      <ScrollArea className="flex-1 px-6 py-4">
        <div className="mx-auto flex max-w-2xl flex-col gap-3">
          {msgs.map((m, i) => (
            <div
              key={i}
              className={
                m.role === "user"
                  ? "ml-8 rounded-lg border border-border bg-secondary px-3 py-2 text-sm"
                  : "mr-8 rounded-lg border border-border bg-card px-3 py-2 text-sm text-muted-foreground"
              }
            >
              {m.text}
            </div>
          ))}
        </div>
      </ScrollArea>
      <div className="border-t border-border p-4">
        <div className="mx-auto flex max-w-2xl gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about cash, grants, books…"
            className="min-h-[44px] resize-none bg-background"
            disabled={busy}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                void send();
              }
            }}
          />
          <DitherButton
            color="grey"
            variant="gradient"
            className="shrink-0 self-end"
            disabled={busy}
            onClick={() => void send()}
          >
            Send
          </DitherButton>
        </div>
      </div>
    </div>
  );
}
