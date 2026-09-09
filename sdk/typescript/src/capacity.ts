/**
 * TypeScript SDK Client for Capacity Intelligence (Phase 5.56).
 */

export class CapacityIntelligenceClient {
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

  async registerResource(
    tenantId: string,
    resourceId: string,
    name: string,
    resourceType: string,
    totalCapacity: number,
    capacityUnit: string = "units"
  ): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/capacity/resources`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({ resource_id: resourceId, name, resource_type: resourceType, total_capacity: totalCapacity, capacity_unit: capacityUnit }),
    });
    return res.json();
  }

  async assessCapacity(
    tenantId: string,
    resourceId: string,
    scope: string = "RESOURCE"
  ): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/capacity/assessments`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({ resource_id: resourceId, scope }),
    });
    return res.json();
  }

  async forecastCapacity(
    tenantId: string,
    resourceId: string,
    horizonDays: number = 30
  ): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/capacity/forecasts`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({ resource_id: resourceId, horizon_days: horizonDays }),
    });
    return res.json();
  }

  async optimizeCapacity(
    tenantId: string,
    resourceId: string,
    objective: string = "COST_PERFORMANCE"
  ): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/capacity/optimizations`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({ resource_id: resourceId, objective }),
    });
    return res.json();
  }
}
