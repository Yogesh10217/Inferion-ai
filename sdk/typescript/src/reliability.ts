/**
 * TypeScript SDK Client for Reliability Intelligence (Phase 5.55).
 */

export class ReliabilityIntelligenceClient {
  private baseUrl: string;
  private apiKey: string;

  constructor(baseUrl: string, apiKey: string = "") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.apiKey = apiKey;
  }

  private getHeaders(tenantId: string): Record<string, string> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "X-Tenant-ID": tenantId,
    };
    if (this.apiKey) {
      headers["Authorization"] = `Bearer ${this.apiKey}`;
    }
    return headers;
  }

  async evaluateServiceHealth(
    tenantId: string,
    serviceId: string,
    rawMetrics: Record<string, any> = {}
  ): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/reliability/health`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({ service_id: serviceId, metrics: rawMetrics }),
    });
    return res.json();
  }

  async predictFailure(
    tenantId: string,
    serviceId: string,
    horizonMinutes: number = 60
  ): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/reliability/predictions`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({ service_id: serviceId, horizon_minutes: horizonMinutes }),
    });
    return res.json();
  }

  async planRecovery(
    tenantId: string,
    serviceId: string,
    strategy: string = "FAILOVER"
  ): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/reliability/recovery/plan`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({ service_id: serviceId, strategy }),
    });
    return res.json();
  }

  async proposeChaosExperiment(
    tenantId: string,
    experimentName: string,
    targetService: string,
    hypothesis: string
  ): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/reliability/chaos/propose`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({
        experiment_name: experimentName,
        target_service: targetService,
        hypothesis,
      }),
    });
    return res.json();
  }
}
