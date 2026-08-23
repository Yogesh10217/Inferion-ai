/**
 * TypeScript SDK Client for Platform Operations
 */

export class PlatformOperationsClient {
  private baseUrl: string;
  private apiKey: string;

  constructor(baseUrl: string, apiKey: string = "") {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  async listServices(tenantId: string = "global"): Promise<any[]> {
    const res = await fetch(`${this.baseUrl}/v1/platform-operations/services?tenant_id=${tenantId}`);
    return res.json();
  }

  async createService(name: string, tenantId: string = "global", serviceTier: string = "TIER_1_HIGH"): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/platform-operations/services`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, tenant_id: tenantId, service_tier: serviceTier }),
    });
    return res.json();
  }

  async getIncidentContext(incidentId: string, tenantId: string = "global"): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/platform-operations/incidents/${incidentId}/context?tenant_id=${tenantId}`);
    return res.json();
  }

  async executeRemediationPlan(planId: string, tenantId: string = "global"): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/platform-operations/remediations/${planId}/execute?tenant_id=${tenantId}`, {
      method: "POST",
    });
    return res.json();
  }
}
