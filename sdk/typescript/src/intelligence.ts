/**
 * TypeScript SDK Client for Intelligence Platform
 */

export class IntelligenceClient {
  private baseUrl: string;
  private apiKey: string;

  constructor(baseUrl: string, apiKey: string = "") {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  async ingestSignal(source: string, signalType: string, message: str, tenantId: string = "global"): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/intelligence/signals`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source, signal_type: signalType, message, tenant_id: tenantId }),
    });
    return res.json();
  }

  async runAnalysis(tenantId: string = "global", resourceId: string = "res_1"): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/intelligence/analyze?tenant_id=${tenantId}&resource_id=${resourceId}`, {
      method: "POST",
    });
    return res.json();
  }

  async listInsights(tenantId: string = "global"): Promise<any[]> {
    const res = await fetch(`${this.baseUrl}/v1/intelligence/insights?tenant_id=${tenantId}`);
    return res.json();
  }

  async listRecommendations(tenantId: string = "global"): Promise<any[]> {
    const res = await fetch(`${this.baseUrl}/v1/intelligence/recommendations?tenant_id=${tenantId}`);
    return res.json();
  }
}
