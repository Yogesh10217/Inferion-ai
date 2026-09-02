/**
 * TypeScript SDK Client for FinOps Intelligence Platform (Phase 5.42).
 */

export class FinOpsClient {
  private baseUrl: string;

  constructor(baseUrl: string = "http://localhost:8000") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async listCosts(tenantId: string = "global"): Promise<any[]> {
    const res = await fetch(`${this.baseUrl}/v1/finops/costs?tenant_id=${tenantId}`);
    if (!res.ok) throw new Error(`Fetch failed: ${res.statusText}`);
    return res.json();
  }

  async recordCost(tenantId: string, category: string, amountUsd: number): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/v1/finops/costs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tenant_id: tenantId, category, amount_usd: amountUsd }),
    });
    if (!res.ok) throw new Error(`Fetch failed: ${res.statusText}`);
    return res.json();
  }

  async listBudgets(tenantId: string = "global"): Promise<any[]> {
    const res = await fetch(`${this.baseUrl}/v1/finops/budgets?tenant_id=${tenantId}`);
    if (!res.ok) throw new Error(`Fetch failed: ${res.statusText}`);
    return res.json();
  }

  async createBudget(tenantId: string, name: string, amountUsd: number): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/v1/finops/budgets`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tenant_id: tenantId, name, amount_usd: amountUsd }),
    });
    if (!res.ok) throw new Error(`Fetch failed: ${res.statusText}`);
    return res.json();
  }
}

export const FinOpsIntelligenceClient = FinOpsClient;
