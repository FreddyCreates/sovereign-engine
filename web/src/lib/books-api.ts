/**
 * Client for the Sovereign Books API (sovereign_dashboard_server.py, port 8090).
 * Set NEXT_PUBLIC_BOOKS_API to point at another host.
 */

export const BOOKS_API_BASE =
  process.env.NEXT_PUBLIC_BOOKS_API?.replace(/\/$/, "") ?? "http://localhost:8090";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BOOKS_API_BASE}${path}`, {
    ...init,
    headers: { Accept: "application/json", ...(init?.headers ?? {}) },
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} for ${path}`);
  return (await res.json()) as T;
}

export function apiGet<T>(path: string): Promise<T> {
  return request<T>(path);
}

export function apiPost<T>(path: string, body: unknown = {}): Promise<T> {
  return request<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

// --- types ------------------------------------------------------------------

export type CashPoint = { month: string; cash: number };

export type BankAccount = {
  id: string;
  name: string;
  mask: string | null;
  type: string | null;
  subtype: string | null;
  current_balance: number;
  available_balance?: number | null;
  currency?: string;
  institution_name?: string;
};

export type BooksHome = {
  business_id: string;
  business_name: string;
  mode: "live" | "mock" | string;
  bank_connected: boolean;
  cash_balance: number;
  inbox_count: number;
  accounts: BankAccount[];
  connections: Record<string, unknown>[];
  ledger_accounts: Record<string, unknown>[];
  trial_balance_ok: boolean;
  cash_series: CashPoint[];
  categories: string[];
  status: string;
};

export type InboxTxn = {
  id: string;
  date: string;
  name: string;
  merchant_name: string | null;
  /** Plaid convention: positive is money out, negative is money in. */
  amount: number;
  pending: number | boolean;
  category_suggested: string | null;
  status: string;
  account_name: string;
  mask: string;
};

export type Category = { name: string; account_code: string };

export type Entitlements = {
  app_user_id: string;
  pro_active: boolean;
  entitlements: string[];
  features: string[];
  source: string;
  mode: string;
  status: string;
  hint?: string;
  warning?: string;
};

export type Grant = {
  id: string;
  title: string;
  amount: string;
  type: string;
  deadline: string;
  fit: string;
  summary: string;
  eligibility?: string[];
  source?: string;
};

export type LinkToken = {
  link_token: string;
  mode: "live" | "mock" | string;
  user_id?: string;
  business_id?: string;
  expiration?: string;
};

export type ConnectResult = {
  status: string;
  error?: string;
  pro_required?: boolean;
  institution_name?: string;
  account_count?: number;
  business_id?: string;
  plaid_item_id?: string;
  sync?: SyncResult;
};

export type SyncResult = {
  status: string;
  error?: string;
  imported?: number;
  skipped_duplicates?: number;
  inbox_count?: number;
};

export type ConfirmResult = {
  status: string;
  error?: string;
  txn_id?: string;
  category?: string;
  gl_entry_id?: string;
  inbox_count?: number;
  categories?: Category[];
};

export type ChatArtifact = {
  kind: string;
  title: string;
  subtitle?: string;
  payload?: Record<string, unknown>;
};

export type ChatResponse = {
  reply: string;
  engine?: string;
  artifacts?: ChatArtifact[];
  tools_used?: string[];
};

// --- books ------------------------------------------------------------------

export const fetchBooksHome = () => apiGet<BooksHome>("/api/v1/books/home");

export const fetchInbox = (limit = 50) =>
  apiGet<{ business_id: string; count: number; transactions: InboxTxn[] }>(
    `/api/v1/books/inbox?limit=${limit}`,
  );

export const fetchCategories = () =>
  apiGet<{ categories: Category[]; status: string }>("/api/v1/books/categories");

export const fetchCashSeries = () =>
  apiGet<{ business_id?: string; points: CashPoint[] }>("/api/v1/books/cash_series");

export const createLinkToken = (userId?: string) =>
  apiPost<LinkToken>("/api/v1/books/link_token", userId ? { user_id: userId } : {});

export const connectBank = (publicToken: string, institutionName?: string, businessId?: string) =>
  apiPost<ConnectResult>("/api/v1/books/connect", {
    public_token: publicToken,
    institution_name: institutionName,
    business_id: businessId,
    post_to_ledger: true,
  });

export const syncBank = (postToLedger = false) =>
  apiPost<SyncResult>("/api/v1/books/sync", { post_to_ledger: postToLedger });

export const confirmTransaction = (txnId: string, category?: string) =>
  apiPost<ConfirmResult>("/api/v1/books/transactions/confirm", {
    txn_id: txnId,
    category,
  });

// --- entitlements -----------------------------------------------------------

export const fetchEntitlements = (appUserId?: string) =>
  apiGet<Entitlements>(
    `/api/v1/books/entitlements${appUserId ? `?app_user_id=${encodeURIComponent(appUserId)}` : ""}`,
  );

export const activateProLocal = (productId = "sovereign_pro_monthly", appUserId?: string) =>
  apiPost<Entitlements & Record<string, unknown>>("/api/v1/books/pro/activate", {
    product_id: productId,
    app_user_id: appUserId,
  });

// --- grants and chat --------------------------------------------------------

export const fetchGrants = (fit?: string, q?: string) => {
  const params = new URLSearchParams();
  if (fit) params.set("fit", fit);
  if (q) params.set("q", q);
  const qs = params.toString();
  return apiGet<{ grants: Grant[]; count?: number; status: string }>(
    `/api/v1/books/grants${qs ? `?${qs}` : ""}`,
  );
};

export const sendChat = (message: string, businessId?: string) =>
  apiPost<ChatResponse>("/api/v1/books/chat", { message, business_id: businessId });

// --- tax credits (agentic QuickBooks engine) --------------------------------

export type TaxCredits = {
  jurisdiction: string;
  cloud_compute_qre: number;
  rd_payroll_qre: number;
  total_qualified_research_expenses: number;
  federal_section_41_credit: number;
  state_tax_credit: number;
  total_estimated_tax_credits: number;
  sec_174_annual_amortization_deduction: number;
  statutory_references?: Array<string | Record<string, unknown>>;
  compliance_status?: string;
};

export const fetchTaxCredits = (state = "CA") =>
  apiGet<TaxCredits>(`/api/v1/agentic_qb/tax_credits?state=${encodeURIComponent(state)}`);

export type ApprovalRow = {
  id: string;
  card_id: string;
  kind: string;
  decision: string;
  subject: string | null;
  amount: number | null;
  source: string;
  created_at: string;
};

export const fetchApprovals = (limit = 50) =>
  apiGet<{ approvals: ApprovalRow[]; count: number; status: string }>(`/api/v1/books/approvals?limit=${limit}`);

export const recordApproval = (body: {
  kind: "categorize" | "tax_credit" | "invoice_chase" | "other";
  decision: "approved" | "skipped" | "sent";
  card_id: string;
  subject?: string;
  amount?: number;
  payload?: Record<string, unknown>;
}) => apiPost<{ id: string; status: string; error?: string }>("/api/v1/books/approvals", { ...body, source: "web" });

// --- tax classification and opportunities ----------------------------------

export type TaxAnswer = { id: string; label: string; tax_class?: string; deductible_pct: number };

export type TaxQuestion = {
  transaction_id: string;
  question: string;
  answers: TaxAnswer[];
  merchant: string;
  date: string;
  amount: number;
  current_class: string;
  current_deductible_pct: number;
};

export type TaxClassTotal = {
  tax_class: string;
  label: string;
  deductible_pct: number;
  count: number;
  spent: number;
  deductible: number;
  nondeductible: number;
  irc_reference: string;
  form_line: string;
};

export type TaxSummary = {
  tax_year: number;
  total_spent: number;
  total_deductible: number;
  total_nondeductible: number;
  open_questions: number;
  qre_candidate_spend: number;
  by_class: TaxClassTotal[];
  status: string;
};

export type TaxOpportunity = {
  id: string;
  title: string;
  action: string;
  reference: string;
  status: "close" | "qualified" | "not_yet" | string;
  estimated_value: number;
  value_note: string;
  gap: string;
  deadline: string | null;
  detail?: Record<string, unknown> | null;
};

export type TaxOpportunities = {
  tax_year: number;
  state: string;
  marginal_rate: number;
  days_left_in_year: number;
  summary: { total_spent: number; total_deductible: number; total_nondeductible: number; open_questions: number };
  next_action: TaxOpportunity | null;
  opportunities: TaxOpportunity[];
  disclaimer: string;
  status: string;
};

export const fetchTaxQuestions = (limit = 10) =>
  apiGet<{ questions: TaxQuestion[]; count: number }>(`/api/v1/books/tax/questions?limit=${limit}`);

export const fetchTaxSummary = (year?: number) =>
  apiGet<TaxSummary>(`/api/v1/books/tax/summary${year ? `?year=${year}` : ""}`);

export const fetchTaxOpportunities = (state = "CA", marginalRate = 0.24) =>
  apiGet<TaxOpportunities>(`/api/v1/books/tax/opportunities?state=${encodeURIComponent(state)}&marginal_rate=${marginalRate}`);

export const answerTaxQuestion = (txnId: string, attendees: string) =>
  apiPost<{ status: string; tax_class?: string; deductible_pct?: number; deductible_amount?: number; error?: string }>(
    "/api/v1/books/tax/classify",
    { txn_id: txnId, attendees },
  );
