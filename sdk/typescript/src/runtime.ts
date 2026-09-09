/**
 * TypeScript SDK Client for Runtime Intelligence (Phase 5.54).
 */

export class RuntimeIntelligenceClient {
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

  async ingestObservation(
    tenantId: string,
    subsystem: string,
    metricName: string,
    value: number,
    dimensions: Record<string, string> = {}
  ): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/runtime/observations`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({ subsystem, metric_name: metricName, value, dimensions }),
    });
    return res.json();
  }

  async evaluateHealth(
    tenantId: string,
    subsystem: string,
    rawTelemetry: Record<string, any> = {}
  ): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/runtime/health`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({ subsystem, raw_telemetry: rawTelemetry }),
    });
    return res.json();
  }

  async detectAnomalies(
    tenantId: string,
    subsystem: string,
    timeSeriesData: Array<Record<string, any>> = []
  ): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/runtime/anomalies`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({ subsystem, time_series_data: timeSeriesData }),
    });
    return res.json();
  }

  async detectDrift(
    tenantId: string,
    subsystem: string,
    currentData: Record<string, any> = {},
    baselineData: Record<string, any> = {}
  ): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/runtime/drift`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({ subsystem, current_data: currentData, baseline_data: baselineData }),
    });
    return res.json();
  }

  async requestDelegation(
    tenantId: string,
    targetDomain: string,
    actionType: string,
    payload: Record<string, any> = {},
    riskLevel: string = "MEDIUM"
  ): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/runtime/delegation`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({ target_domain: targetDomain, action_type: actionType, payload, risk_level: riskLevel }),
    });
    return res.json();
  }
}
