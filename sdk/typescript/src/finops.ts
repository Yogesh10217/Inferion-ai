/**
 * TypeScript SDK Client for FinOps API.
 */

export class FinOpsClient {
  private baseUrl: string;

  constructor(baseUrl: string = "http://localhost:8000") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async listCosts(): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/v1/finops/costs`);
    if (!res.ok) throw new Error(`Fetch failed: ${res.statusText}`);
    return res.json();
  }

  async listBudgets(): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/v1/finops/budgets`);
    if (!res.ok) throw new Error(`Fetch failed: ${res.statusText}`);
    return res.json();
  }
}
