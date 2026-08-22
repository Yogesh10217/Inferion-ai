/**
 * TypeScript SDK Client for Autonomous Planning Platform
 */

export class PlanningClient {
  private baseUrl: string;
  private apiKey?: string;

  constructor(baseUrl: string = "http://localhost:8000", apiKey?: string) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.apiKey = apiKey;
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (this.apiKey) {
      headers["Authorization"] = `Bearer ${this.apiKey}`;
    }
    return headers;
  }

  async create(title: string, description: string = "", tenantId: string = "global"): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/plans`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ title, description, tenant_id: tenantId }),
    });
    const data = await res.json();
    return data.plan;
  }

  async list(tenantId: string = "global"): Promise<any[]> {
    const res = await fetch(`${this.baseUrl}/v1/plans?tenant_id=${tenantId}`, {
      headers: this.getHeaders(),
    });
    const data = await res.json();
    return data.plans || [];
  }

  async get(planId: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/plans/${planId}`, {
      headers: this.getHeaders(),
    });
    const data = await res.json();
    return data.plan;
  }

  async simulate(planId: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/plans/${planId}/simulate`, {
      method: "POST",
      headers: this.getHeaders(),
    });
    const data = await res.json();
    return data.simulation;
  }

  async execute(planId: string, budgetDollars: number = 50.0): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/plans/${planId}/execute`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ budget_dollars: budgetDollars }),
    });
    return res.json();
  }

  async reflect(planId: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/plans/${planId}/reflect`, {
      method: "POST",
      headers: this.getHeaders(),
    });
    const data = await res.json();
    return data.reflection;
  }

  async optimize(planId: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/plans/${planId}/optimize`, {
      method: "POST",
      headers: this.getHeaders(),
    });
    const data = await res.json();
    return data.plan;
  }

  async metrics(planId: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/plans/${planId}/metrics`, {
      headers: this.getHeaders(),
    });
    const data = await res.json();
    return data.metrics;
  }

  async billing(planId: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/plans/${planId}/billing`, {
      headers: this.getHeaders(),
    });
    const data = await res.json();
    return data.billing;
  }
}
