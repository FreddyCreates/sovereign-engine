# Build Log — External Connector Work (ItsNotAILABS)

Facts below are pulled directly from GitHub (public repo pages, PR, and raw file contents), not from chat transcripts. Anything not yet visible on GitHub is marked "not yet pushed" rather than assumed.

Last verified: 2026-07-08, 22:49 UTC

---

## 1. `ItsNotAILABS/x-mcp-skills` — active

**Status:** Draft PR open, real commits, real files.

- **PR:** [#1 — Add external AI connector skills for Caffeine and Grok Build](https://github.com/ItsNotAILABS/x-mcp-skills/pull/1)
- **Author:** FreddyCreates
- **Branch:** `codex/external-ai-connectors` → `main`
- **Commits (5):**
  1. Add Caffeine MTP bridge skill
  2. Add Grok Build bridge skill
  3. Add external connector registry
  4. Document external AI connector skills
  5. Add MDFUC surface record

**Files added (confirmed by direct read):**

| File | What it actually contains |
|---|---|
| `README.md` | Defines x-mcp-skills' role in the "Medina Development Federation Unified Catalog" (MDFUC): owns MCP/external-AI connector skills, reports to `nexus` (registry), `nova-intelligence` (runtime contracts), `PhantomSDK` (SDK packaging). Lists both connectors and first-use steps for each. |
| `connector-registry.json` | Machine-readable registry, schema `nova.external_connector_registry.v1`. Two connectors registered: `caffeine-mtp-bridge`, `grok-build-bridge`, each with an explicit `proof_gates` list. |
| `skills/caffeine-mtp-bridge/SKILL.md` | Bridge spec for Caffeine CLI and Caffeine MTP/MCP servers. Documents CLI workflow, MTP/MCP server workflow (register URL → discover tools → submit build → import artifact with hash into NOVA), required operator inputs, and proof gates — including an explicit **"no fake deploy claim"** rule. |
| `skills/grok-build-bridge/SKILL.md` | (Referenced in registry/README; same proof-gate pattern — plan captured, approval boundary recorded, diff captured, tests captured.) |
| `mdfuc.surface.json` | Repo-family role and proof-gate record (added in commit 5). |

**Read on this:** this is real, working scaffolding for connecting NOVA to two external AI tools (Caffeine, Grok Build) with self-imposed guardrails against overclaiming ("no fake deploy claim," "origin and credential boundary recorded"). Still a draft PR — not merged to `main` yet.

**Open before this can move to "live":**
- Real Caffeine MTP/MCP server URL and tool schema (flagged in the PR description as a known gap)
- No tests yet — PR description calls this "a connector skill/documentation seed"

---

## 2. `ItsNotAILABS/x-organism-bots-mcp` — just started

**Status:** Repository initialized only. Direction was given ~10 minutes before this log entry — logging current state as a baseline, not a finished result.

- **Contents on `main`:** `README.md`, `LICENSE` (Apache-2.0)
- **Commits:** 1 (initial)
- **No connector skills, registry, or SKILL.md files present yet**

This is the honest starting point. Will re-check after the work you mentioned lands.

---

## 3. `ItsNotAILABS/nexus` — active (checked 2026-07-09)

**Status:** 14 real commits. Registry/coordination role for the whole repo family (MDFUC — Medina Development Federation Unified Catalog).

- Files: `mdfuc.catalog.json`, `registry/repo-family.json`, `registry/artifacts-v0.3.8.json`, `docs/MDFUC.md`, `docs/PRODUCTION_READINESS.md`, `tools/validate_mdfuc_catalog.py`
- **Notable:** the README has an explicit "Release Truth Line" section: *"The v0.3.8 zip artifacts are registered with checksums, but binary upload is still pending in PhantomSDK... Do not claim the binaries are committed until their upload status changes."* That's a real, self-imposed honesty gate, not something I'm adding — it's already in the repo.
- Lists 5 active repos in the family and 5 "activation candidates" not yet started.

## 4. `ItsNotAILABS/PhantomSDK` — active (checked 2026-07-09)

**Status:** 14 real commits. SDK packaging surface, explicitly labeled "contract-first" (manifests and validators exist before publication claims).

- Files: `phantom-sdk.manifest.json`, `docs/PACKAGE_SURFACES.md`, `docs/RELEASE_VERIFICATION.md`, TypeScript + Python starter exports, `releases/v0.3.8/RELEASE_MANIFEST.json`
- Same truth-line discipline: binary upload for v0.3.8 explicitly marked pending, not claimed as done.

## 5. `ItsNotAILABS/nova-intelligence` — active (checked 2026-07-09)

**Status:** 21 commits, 1 open PR. Research/contract layer — "does not claim every paper is deployed by merge alone."

- 10-paper research packet (`research/RESEARCH_INDEX.md`, `research/RESEARCH_CERTIFICATION_MATRIX.md`) with an explicit proof-status/promotion-gate matrix.
- Truth line: *"Research becomes trunk doctrine only after executable claims are verified against code, tests, release artifacts, or tracked implementation tickets."*

---

## Not yet checked this pass

- `ItsNotAILABS/demo-repository` (private — will need repo access to verify)
- `ItsNotAILABS/organism-bots-mcp-server` (referenced by nexus's registry as active — check next pass)

---

## Update — 2026-07-10

Last verified: 2026-07-10 (UTC time not captured by fetch tool)

### 1. `ItsNotAILABS/x-mcp-skills` — grown since last check

**Status:** `main` branch now shows **21 commits** (up from the PR-only state logged 2026-07-08). New top-level folders on `main`: `assets`, `docs`, `examples`, `platform`, `research`, `schemas`, `skills`, `tools` — none of these existed in the last log entry, which only had `README.md`, `connector-registry.json`, `mdfuc.surface.json`, and the two skill files.

- README now titled "NOVA External AI Connector Control Plane." Adds references to `docs/CONNECTOR_CONTROL_PLANE_WORKING_PAPER.md`, `docs/PRODUCTION_READINESS.md`, `tools/validate_connector_registry.py` — none previously logged.
- **Readiness section (verbatim):** "Caffeine and Grok connector contracts are registered and documented. Registry validation is available. Live callable adapters require operator-provided credentials, endpoints, and exact tool contracts." Next build listed: `connectorctl`, CI validation, live MCP discovery capture, dashboard.
- **PR #1 unchanged:** still Draft, still 5 commits (`codex/external-ai-connectors` → `main`), same "Remaining gaps" language (no real Caffeine MTP/MCP server URL yet; no tests, called "a connector skill/documentation seed"). Not merged.

### 2. `ItsNotAILABS/x-organism-bots-mcp` — no change

Still 1 commit, still just `README.md` + `LICENSE` (Apache-2.0), no description. Matches 2026-07-08 baseline exactly.

### 3. `ItsNotAILABS/organism-bots-mcp-server` — now confirmed real and active (previously unverified)

This closes the "not yet checked" item from the last log pass. **This is the real/active repo** — nexus's registry entry for `organism-bots-mcp-server` checks out; `x-organism-bots-mcp` (above) remains a disconnected stub.

- **16 commits** on `main`. Files: `.github/workflows`, `assets`, `docs`, `examples`, `mcp`, `research`, `server`, `skills/organism-bot-orchestrator`, `tools`, `LICENSE`, `README.md`, `organism-bots.registry.json`.
- Title: "NOVA Organism Bots MCP" — "registry-governed platform for launching role-specific AI workflow organisms." README states explicitly: "This is not a chatbot wrapper."
- **Initial Bot Family (5 bots currently live on `main`):** ORIGO Builder Bot, TRANSITUS Connector Bot, SACE Proof Bot, MERCATUS Launch Bot, MEMORIA Consequence Bot.
- **Launch Levels table (L0–L4) with explicit self-assessment:** "Current state: L2 is present for the platform substrate. L3 is partially present through deterministic receipts. The next hardening step is persistent receipt storage plus CI validation." Carrying this caveat forward as-is.
- **Operating Law (verbatim):** "No organism bot can claim completion without an artifact or proof record."
- **Pull requests: 1 open, 2 closed.** Open PR [#3 — "Expand organism bot family and runnable MCP surface"](https://github.com/ItsNotAILABS/organism-bots-mcp-server/pull/3) is a **Draft**, 6 commits, wants to merge `codex/organism-bots-production-hardening` → `main`. PR description says it's a "Follow-up to the merged hardening PR" (accounting for the 2 closed PRs) and proposes expanding the registry from 5 to 12 bots (adding AEDIFICIUM, SPECULUM, CUSTOS, VIGIL, INDEXUS, PRETIUM, CIVITAS), plus new `/bots/{bot_id}`, `POST /route`, `POST /readiness` endpoints and a `docs/BOT_CATALOG.md`. **Not merged yet** — the 12-bot registry and new endpoints are not live on `main`. PR's own verification note: "Local clone validation could not run from the container because GitHub clone traffic returned `CONNECT tunnel failed, response 403`" — self-reported, unresolved.

### 4. `ItsNotAILABS/nexus` — no material change

Still 14 commits. Same Release Truth Line verbatim ("binary upload is still pending in PhantomSDK... Do not claim the binaries are committed until their upload status changes"). Active Repository Family table now explicitly lists `organism-bots-mcp-server` as active (5 repos total, matching item 3 above) and the same 5 Activation Candidates as last pass: `nova-connector-control-plane`, `mercatus-launch-studio`, `specforge-launch-studio`, `MatDaemon`, `containers-nova-APPS`.

### 5. `ItsNotAILABS/PhantomSDK` — no material change

Still 14 commits, same contract-first framing, same Release Truth Line on the v0.3.8 binaries being unpublished.

### 6. `ItsNotAILABS/nova-intelligence` — no material change

Still 21 commits, still 1 open PR, same Truth Line verbatim.

### Not verifiable this pass

- The org repositories tab (`github.com/ItsNotAILABS?tab=repositories`) returned no usable content via the fetch tool (JS-rendered listing) — could not confirm or rule out new repos this way.
- The five "activation candidates" (`nova-connector-control-plane`, `mercatus-launch-studio`, `specforge-launch-studio`, `MatDaemon`, `containers-nova-APPS`) appear only as plain repo names in nexus's README, not as clickable links, so their URLs were never fetched and the web-fetch tool's provenance restriction blocked direct guesses at `github.com/ItsNotAILABS/<name>`. Still unverified — not claiming these do or don't exist yet.
- `ItsNotAILABS/demo-repository` — still private, still unverified.

---

*Methodology: every claim above was fetched live from github.com at the timestamp noted, not taken from the pasted conversation. Nothing here is inferred from documentation elsewhere in the project.*
