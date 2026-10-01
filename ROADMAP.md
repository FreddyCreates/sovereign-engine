# Sovereign Books + CRM + App Management — What Companies Use It For

**Product:** Books tied to the bank, a CRM for relationships, and an **App Deployment Manager** so shipping mobile/web apps is as easy as the best publish stacks (Expo EAS, Fastlane, Bitrise, Codemagic, Vercel, Railway).

**Who buys it:** SMBs and operators who fight QuickBooks *and* a bolted-on CRM *and* painful store/web releases — and want money, customers, and shipping in one place.

**Status (verified):** All roadmap IDs **1–250** are registered and pass `scripts/verify_roadmap.py` against SQLite (external services simulated when credentials are absent). CRM / App Management / Books-extended APIs are on `:8090`; web UI loads live lists.

```bash
.venv/bin/python scripts/verify_roadmap.py   # passed=250 failed=0
.venv/bin/python scripts/seed_crm.py
.venv/bin/python scripts/seed_apps.py
```

---

## Company types that want this

| Company | Why they open the app |
|---------|------------------------|
| Solo / micro SMB (1–5 people) | Know cash and payables without a bookkeeper every week |
| Service business (agency, shop, contractor) | Match bank activity to clients; pipeline → invoice → paid |
| Subscription / app company | MRR deposits + customers + **ship to stores** without DevOps hire |
| Indie / small product studio | Build → TestFlight/Play → OTA hotfix → web preview in one console |
| Sales-led SMB | Companies, people, opportunities without Salesforce tax |
| Multi-entity owner (2–5 companies) | One login, several businesses, banks that don’t kick each other off |
| Bookkeeping firm | Clean client workspaces + accountant-ready export |
| Non-dilutive / grant-seeking startup | Books + capital catalog when fundraising without equity |

---

## Feature list — Books (jobs companies hire us for)

Each item is a **use**, not an engineering milestone. Status reflects the product today.

### Core money ops

1. **Connect the business bank (and keep it connected)** — *live (Plaid sandbox + mock).*
2. **Review a transaction inbox, not a raw bank dump** — *live.*
3. **Post confirmed spend/income into a real ledger** — *live (SQLite GL).*
4. **See cash on hand and a simple cash trajectory** — *live.*
5. **Reconcile bank balance to books** — *planned.*
6. **Produce P&L and balance sheet for the owner or CPA** — *partial; export planned.*

### Getting paid and paying others

7. **Create and track invoices** — *planned.*
8. **Enter bills and see what’s due** — *planned.*
9. **Capture receipts into expenses** — *planned.*
10. **Pull sales from Stripe / Square / Shopify into books** — *planned.*

### Cash clarity and control

11. **Safe-to-spend / runway style alerts** — *Pro entitlement wired; rules planned.*
12. **Rules: “if merchant contains X → always category Y”** — *planned.*
13. **Ask the books in plain language** — *live (script engine).*
14. **Flag weird activity** — *planned (Pro).*
15. **Tax bucket / quarterly estimate view** — *planned.*

### Multi-business and accountants

16. **Switch between multiple companies under one login** — *planned.*
17. **Link more than one bank (Pro: unlimited)** — *gate live.*
18. **Accountant / bookkeeper read-only access** — *planned.*
19. **Migrate off QuickBooks / Xero once** — *planned.*

### Growth and monetization

20. **Browse non-dilutive capital / grants** — *live.*
21. **Unlock Pro (RevenueCat `pro_access`)** — *bridge live; store products needed.*
22. **Agency: bill clients and keep books in one stack** — *planned.*
23. **“Close the month” / “prep Q1 for the CPA” guided run** — *vision.*
24. **Connect payroll or storefront when ready** — *vision.*

---

## Feature list — CRM (Twenty parity)

Sourced from Twenty’s product + docs ([what is Twenty](https://docs.twenty.com/user-guide/getting-started/capabilities/what-is-twenty), key features, views, workflows, AI, apps, permissions). **Status: UI shell in nav (Companies / People / Opportunities / Tasks / Notes / Workflows); data is sample until persistence ships.**

### Standard objects & records

25. **Companies (accounts)** — company records with domain, ICP, ARR, owner, industry, address, LinkedIn, employees, main contact.
26. **People (contacts)** — people linked to companies; roles and emails.
27. **Opportunities (deals)** — pipeline deals with stage, amount, close date, company relation.
28. **Tasks** — tasks linked to companies / people / opportunities; due dates and status.
29. **Notes** — notes linked to records for collaboration.
30. **Favorites** — pin frequently used records / views in the workspace.
31. **Record detail pages** — per-record page with tabs, widgets, and related lists.
32. **Activity timeline** — chronological activity on a record (emails, notes, field changes, app events).
33. **File attachments** — attach files to records.

### Views & pipelines

34. **Table views** — spreadsheet-like lists of any object.
35. **Kanban board views** — stage boards for opportunities / projects.
36. **Calendar views** — records with dates on a calendar (e.g. tasks due).
37. **Filters & sorting** — find exact subsets of records.
38. **Fields & columns** — choose visible fields and column order.
39. **View settings** — name, icon, visibility, organization of saved views.
40. **Grouping in table views** — collapsible groups by field value.
41. **Sales pipeline setup** — configure opportunity stages.
42. **Expected amount in pipeline** — weighted deal values from stage probability.
43. **Time-in-stage tracking** — how long opportunities sit in each stage.
44. **Restrict access to a view** — who can see a custom view.

### Custom data model

45. **Custom objects** — unlimited objects beyond standard CRM entities.
46. **Custom fields** — text, number, select, dates, etc. on any object.
47. **Relations** — MANY_TO_ONE / ONE_TO_MANY between objects.
48. **Unique constraints** — enforce uniqueness on fields (e.g. domain, email).
49. **Customize data model in settings** — no-code object/field builder.
50. **Extend standard objects with extra fields** — People, Companies, etc.
51. **Page layouts** — tabs and widgets on record pages.
52. **Formula fields** (workflow-assisted until native) — computed values on records.

### Calendar & email

53. **Mailbox sync** — connect email; see threads on CRM records.
54. **Calendar sync** — meetings visible against people / companies.
55. **Multiple mailboxes per user**.
56. **Limit which emails are imported**.
57. **Email activity on objects** — track email activity across record types.
58. **Send emails from workflows** (and clarify in-product send / book-meeting capabilities as Twenty documents them).

### Workflows & automation

59. **Visual workflow builder**.
60. **Workflow triggers** — record events, schedules, webhooks, etc.
61. **Workflow actions** — create/update records, notify, HTTP, AI, email, etc.
62. **Workflow branches** — conditional / parallel paths.
63. **Workflow iterator** — loop over arrays of records.
64. **Workflow runs** — monitor executions.
65. **Workflow versions / drafts**.
66. **Workflow credits** — metered automation usage.
67. **Closed-won automations** — post-win tasks, invoices, handoffs.
68. **Detect stale opportunities** — alert when deals go quiet.
69. **Task-due email alerts**.
70. **Notify teammates of a note to review**.
71. **Count / display emails received per contact**.
72. **Display related record data on opportunities** (e.g. company fields).
73. **Auto-reply / AI triage for inbound emails**.
74. **Webhook trigger from external tools**.
75. **Bring Typeform (or form) submissions into CRM**.
76. **Bring product / warehouse data into CRM on a schedule**.
77. **Generate quote or invoice from a closed deal** (into books or external tool).
78. **Generate PDF (quote) and attach to a record**.
79. **Code actions** in workflows (arrays / custom logic).

### AI

80. **AI chatbot over CRM data** — natural-language read/write assistance.
81. **AI agents in workflows** — agentic steps inside automations.
82. **AI skills** — reusable agent capabilities for apps / workflows.
83. **Permissions & access control for AI agents**.
84. **Smart suggestions / data enrichment** (as Twenty ships them).

### Dashboards & reporting (CRM)

85. **CRM dashboards** with tabs.
86. **Dashboard widgets** (charts, metrics).
87. **Chart settings** — configure visualizations on CRM data.
88. **Sales / GTM performance views** — pipeline health next to books cash (product goal: one command center).

### Permissions, members & workspace

89. **Role-based permissions** — object / field / settings access.
90. **SSO configuration** (organization tier parity).
91. **Row-level permissions** (organization tier parity).
92. **Member management** — invite teammates, roles.
93. **Workspace settings** — name, branding.
94. **Profile & security settings**.
95. **Experience settings** — theme, locale/region.
96. **Domain settings** — workspace domain, approved access domains, custom app domains.
97. **Early access / community feature flags**.

### Data import & export

98. **CSV import — companies**.
99. **CSV import — people / contacts**.
100. **CSV import — relations between objects**.
101. **CSV field mapping**.
102. **Import uniqueness constraints**.
103. **Import error handling & validation UI**.
104. **Update existing records via import**.
105. **Bulk import via API** (large migrations).
106. **Export data (CSV / API)**.
107. **Migrate from Salesforce / HubSpot** (CSV or API path).

### API, webhooks & developer platform

108. **REST API** for all objects.
109. **GraphQL API**.
110. **Webhooks** for real-time events.
111. **API keys** for programmatic access.
112. **Native MCP server** — Claude / ChatGPT / Cursor can read-write CRM via OAuth.
113. **Apps framework** — TypeScript packages (`create-twenty-app` style) for custom objects, logic, UI.
114. **Logic functions** — HTTP, cron, database event triggers.
115. **Background jobs** for long / rate-limited work.
116. **App key-value store**.
117. **OAuth connections** — app acts on user’s behalf in third-party services.
118. **Front components** — sandboxed React UI inside the CRM.
119. **Navigation menu items from apps**.
120. **Saved views shipped with apps**.
121. **Timeline activity types** defined by apps.
122. **Install / upgrade / uninstall hooks** for apps.
123. **Public assets** for apps.
124. **App marketplace metadata / publishing**.
125. **Self-hosting path** — run CRM on own infra (open-source option).
126. **Zapier / no-code connectors** (or equivalent webhook + workflow path).

### Command palette & UX speed

127. **Command palette (⌘K)** — navigate, create, bulk actions.
128. **Keyboard shortcuts** (e.g. go to People / Opportunities / Settings).
129. **Bulk record actions** — export selection, delete, send email.
130. **Live collaborative-feeling UI** — modern Notion-like CRM experience.

### Billing for CRM seats (product)

131. **Per-seat CRM plans** (map to RevenueCat / Stripe: Free / Pro / Org with SSO).
132. **Credits balance** for workflows + AI chat + agents (Twenty-style metering).

---

## Feature list — App management (publish-stack parity)

**Research note (2026):** Easiest paths — **Expo EAS** for React Native (cloud build + submit + OTA + workflows), **Vercel** for Next.js web, **Railway** for full-stack API/DB, **Fastlane** for store metadata/screenshots/signing scripts, **Codemagic** for Flutter/fast Mac builds, **Bitrise** for visual mobile pipelines + 300+ steps. Sovereign App Management targets the union of these capabilities.  
**Status:** UI shell in nav (Projects / Builds / Releases / Stores / Web deploy / Pipelines); sample data until wired to real CI/store APIs.

### Projects & workspace

133. **Link app projects** — connect Git repos / Expo projects / Android-app modules to a workspace.
134. **Multi-platform project cards** — Android, iOS, Web (and Wear later) on one project.
135. **Environments** — development / preview / production with separate secrets.
136. **eas.json / app config profiles** — named build & submit profiles (dev, preview, production).
137. **Team access to projects** — who can trigger builds vs approve store submits.
138. **Project dashboard** — latest build, latest OTA, store status, web URL at a glance.
139. **Expo Orbit–style install** — install internal builds on devices from a desktop/helper flow.
140. **QR / deep link to install** preview and internal builds on device.

### Cloud builds (EAS Build · Codemagic · Bitrise)

141. **Cloud Android builds** — AAB/APK without local SDK hell.
142. **Cloud iOS builds** — no local Mac required for release binaries.
143. **Apple Silicon / fast Mac runners** — prioritize build speed (Codemagic/Bitrise-class).
144. **Automatic credential provisioning** — generate/manage signing certs & keystores.
145. **Bring-your-own credentials** — upload existing certs / play service accounts.
146. **Fastlane match–style cert sync** — shared encrypted signing repo for the team.
147. **Build profiles** — debug, development client, preview, production.
148. **Custom native code builds** — Expo/RN with native modules; Flutter; bare native.
149. **Docker / custom build images** — reproducible native toolchains.
150. **Build caching** — dependency & derived-data caches to cut time.
151. **Build logs & artifacts** — download IPA/AAB, dSYMs, mapping files.
152. **SSH into failing builds** (Codemagic-style) — debug stuck CI interactively.
153. **Fingerprint native tree** — hash native characteristics to decide rebuild vs OTA.
154. **Get existing build by fingerprint** — reuse binary when native unchanged.
155. **Repack / JS-only rebuild** — ship JS onto existing native binary in ~minutes (EAS repack).
156. **Skip redundant native builds** — fingerprint-based pipeline short-circuit.
157. **Concurrent builds** — queue / concurrency limits for the team.
158. **Build from GitHub App / PR / tag / branch**.
159. **Manual “Run build” from UI / CLI**.
160. **Internal distribution** — ad hoc / enterprise / Play internal links for QA.

### OTA updates & channels (EAS Update)

161. **Over-the-air JS/asset updates** — fix bugs without store review when native allows.
162. **Release channels** — preview vs production (and custom channels).
163. **Runtime version policy** — only compatible updates install on a binary.
164. **Publish update from CI or CLI**.
165. **Roll back to previous update**.
166. **Update rollout / percentage** (when platform supports staged OTA).
167. **Update insights** — who got which bundle (EAS Insights–class).
168. **Channel ↔ build profile mapping**.

### Store submission & listing (EAS Submit · Fastlane deliver/supply · Play / ASC)

169. **Submit to Google Play** from a successful build.
170. **Submit to Apple App Store / App Store Connect** from a successful build.
171. **Auto-submit after successful production build**.
172. **TestFlight upload** with changelog and group targeting.
173. **TestFlight beta review control**.
174. **Play tracks** — internal, closed, open testing, production.
175. **Promote between Play tracks**.
176. **App Store phased release / hold for review** controls (where APIs allow).
177. **EAS Metadata / Fastlane deliver** — upload listing copy, keywords, categories, URLs.
178. **Screenshot automation** (Fastlane snapshot) across device sizes.
179. **Frame / localize screenshots** for store listings.
180. **Upload store screenshots & preview videos**.
181. **Privacy nutrition labels / data safety forms** assist (checklist + export).
182. **Age rating / content questionnaire** assist.
183. **App Store Connect API + Play Developer API** connected accounts.
184. **Service account / API key vault** for store credentials (never in git).
185. **Release notes / “What’s New” per locale**.
186. **Version / build number bump automation**.
187. **Reject / cancel pending submission** from the console.
188. **Store status timeline** — Waiting for Review → In Review → Ready for Sale / Live.

### Web deploy (Vercel · Netlify · Railway · Render · Fly · EAS Hosting)

189. **Git-linked web deploys** — push to deploy.
190. **Framework auto-detect** (Next.js, static, Expo web / Router).
191. **Preview deployments per PR** with unique URL.
192. **Production promote** from a preview.
193. **Custom domains + automatic HTTPS / TLS**.
194. **Environment variables & secrets** per env (preview/prod).
195. **Edge / CDN for static + SSR**.
196. **Serverless / edge functions** for API routes.
197. **Always-on web services** (Railway/Render-style) for long-lived Node/Python APIs.
198. **Background workers / cron jobs**.
199. **Managed Postgres provisioning** with auto-injected connection strings.
200. **Managed Redis / queues**.
201. **Private networking between services**.
202. **Docker deploy** for arbitrary backends.
203. **Multi-region / edge placement** (Fly-class) for latency-sensitive APIs.
204. **Instant rollbacks** to prior web deployment.
205. **Deploy hooks / webhook notify** on succeed/fail.
206. **Bandwidth / usage metering view** (avoid bill shock).
207. **EAS Hosting** for Expo Router / RN web + API routes.
208. **Split testing / branch A-B** (Netlify-class) for marketing sites.
209. **Forms / identity add-ons** optional for JAMstack marketing (Netlify-class).

### Pipelines & CI/CD (EAS Workflows · GitHub Actions · Bitrise · Codemagic)

210. **YAML-defined release pipelines**.
211. **Visual workflow editor** (Bitrise-style) for non-DevOps teammates.
212. **Pre-packaged jobs** — build, submit, update, deploy, test, notify.
213. **Custom shell jobs** — run any script (Fastlane lanes, curl, Node).
214. **Triggers** — push, PR, label, tag, cron, manual, store events, REST API.
215. **Job dependencies / DAG** — build → test → submit → notify.
216. **Require-approval gate** before production submit.
217. **Slack notifications** with build links / QR.
218. **GitHub PR comments** with preview links / install QR.
219. **Maestro / E2E tests** on emulators & simulators.
220. **Unit / lint / typecheck** on every PR.
221. **Matrix builds** — multi-OS / multi-flavor.
222. **Bitrise Steps marketplace–class integrations** — Firebase, Crashlytics, Sonar, Jira, etc.
223. **Firebase App Distribution** for QA builds.
224. **Codemagic.yaml / bitrise.yml / eas workflow import** — bring existing pipelines.
225. **Pipeline run history** — logs, artifacts, duration, flaky detection.
226. **Concurrency & credit metering** for CI minutes.
227. **Self-hosted runners** option for regulated teams.
228. **Monorepo filters** — only build changed apps (web vs android-app).

### Quality, observability & insights

229. **Crash / ANR feed** (Play Vitals / Crashlytics link-in).
230. **EAS Insights–class analytics** — installs, updates, reach.
231. **EAS Observe–class performance monitoring**.
232. **Sourcemap / dSYM upload** for readable crash stacks.
233. **Release health** — crash-free sessions after a ship.
234. **Store review rating pulse** next to release.

### Distribution beyond stores

235. **Enterprise / MDM distribution** hooks.
236. **Public download page** for sideload / APK (where allowed).
237. **Invite-only beta cohorts** (email lists → TestFlight / Play closed).
238. **Wear OS / Galaxy Store submit path** (Shipaton-aligned later).

### RevenueCat & monetization wiring (app ship ↔ money)

239. **Attach RevenueCat project** to an app (public SDK key + products).
240. **Verify first purchase event** after store release (Shipaton / Pro loop).
241. **Promo codes / offering checklist** before submit.
242. **Paywall screenshot regression** in E2E before production.

### CLI, API & developer experience

243. **`sovereign apps` CLI** (EAS CLI–class) — build, submit, update, deploy.
244. **REST API for builds / submits / deploys**.
245. **Webhooks for build finished / submit accepted / deploy live**.
246. **Status badges** for README (build passing / production version).
247. **Audit log** — who shipped what, when.

### Billing for App Management

248. **Build minute / credit packs** (EAS/Bitrise-style metering).
249. **Seats for who can approve production**.
250. **Pro unlock** — unlimited projects / OTA / preview deploys (map to `pro_access`).

---

## Books ↔ CRM ↔ Apps bridge

| Job | Books | CRM | App management |
|-----|-------|-----|----------------|
| Ship a paid app | Pro + RevenueCat revenue in ledger | Customers / opportunities | Build → submit → live |
| Hotfix after launch | — | Support notes/tasks | OTA update channel |
| Won enterprise deal | Invoice | Closed-won | Promote store + custom domain |
| Can we afford eng? | Runway | Pipeline | CI credit burn |

---

## Priority order

| Priority | Company job | Features |
|----------|-------------|----------|
| **Now** | Bank + cash + Pro | Books 1–4, 13, 17, 21 |
| **Next** | CRM core objects | CRM 25–33 |
| **Next** | Ship Android/web for Shipaton | Apps 133–140, 141–160, 169–176, 189–194 |
| **Then** | Close books + OTA | Books 5–6 · Apps 161–168 |
| **Then** | Pipeline + AR/AP + store metadata | Books 7–10 · CRM 41–43 · Apps 177–188 |
| **Then** | Workflows / AI / full CI | CRM 53–84 · Apps 210–228 |
| **Later** | Custom CRM model + multi-region PaaS | CRM 45–52, 108–126 · Apps 197–203 |

---

## What we are *not* selling as the hero (yet)

- Full payroll / HRIS as the primary story  
- Inventory / warehouse WMS  
- Fake MRR / tokenomics / IoT demos as buyer features  
- Claiming Twenty-complete CRM or EAS-complete CI before persistence / real API keys ship  

---

## How this maps to tiers

| Free | Pro (`pro_access`) |
|------|---------------------|
| One bank, inbox, ledger, cash, chat, grants, CRM sample, App Management sample | Unlimited banks, AI categorization, runway alerts, accountant export; extra CRM seats / build credits / OTA as metering lands |

Offline Pro: `scripts/activate_pro.py` or Settings → Activate Pro (local).

---

*Last updated: September 2026 — Books + Twenty CRM + App Management (EAS / Fastlane / Bitrise / Codemagic / Vercel / Railway / Netlify / Render parity).*
