/**
 * SOVEREIGN ENGINE CORE SDK (TYPESCRIPT / JAVASCRIPT)
 * Provides clean client interfaces for QuickBooks & Stripe Replacement powered by RevenueCat.
 */

export interface SovereignOverview {
  mrr: number;
  arr: number;
  ltv_cac_ratio: number;
  net_profit_margin_pct: number;
  forma_burned: number;
  active_subscribers: number;
  cores_entangled: number;
}

export interface InvoiceResult {
  invoice_id: string;
  client: string;
  amount_usd: number;
  aura_credit_score: number;
  status: string;
}

export class SovereignClient {
  private baseUrl: string;

  constructor(baseUrl: string = "http://localhost:8090") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async getOverview(): Promise<SovereignOverview> {
    const res = await fetch(`${this.baseUrl}/api/v1/overview`);
    return await res.json();
  }

  async getLedger(): Promise<any> {
    const res = await fetch(`${this.baseUrl}/api/v1/ledger`);
    return await res.json();
  }

  async createInvoice(client: string, amount: number): Promise<InvoiceResult> {
    const res = await fetch(`${this.baseUrl}/api/v1/invoices/create`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ client, amount })
    });
    return await res.json();
  }

  async mutatePaywall(variantId: string, theme: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/api/v1/paywall/mutate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ variant_id: variantId, theme })
    });
    return await res.json();
  }

  async interceptCancellation(subscriberId: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/api/v1/customer_center/intercept`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ subscriber_id: subscriberId })
    });
    return await res.json();
  }
}
