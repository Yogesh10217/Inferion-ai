/**
 * TypeScript SDK Client for Operations Intelligence Platform (Phase 5.41).
 */

export class OperationsClient {
  private baseUrl: string;

  constructor(baseUrl: string = "http://localhost:8000") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async listServices(tenantId: string = "global"): Promise<any[]> {
    const res = await fetch(`${this.baseUrl}/v1/operations/services?tenant_id=${tenantId}`);
    if (!res.ok) throw new Error(`Fetch failed: ${res.statusText}`);
    return res.json();
  }

  async createService(tenantId: string, name: string, ownerTeam: string): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/v1/operations/services`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tenant_id: tenantId, name, owner_team: ownerTeam }),
    });
    if (!res.ok) throw new Error(`Fetch failed: ${res.statusText}`);
    return res.json();
  }

  async listIncidents(tenantId: string = "global"): Promise<any[]> {
    const res = await fetch(`${this.baseUrl}/v1/operations/incidents?tenant_id=${tenantId}`);
    if (!res.ok) throw new Error(`Fetch failed: ${res.statusText}`);
    return res.json();
  }
}

export const OperationsIntelligenceClient = OperationsClient;
