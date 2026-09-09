/**
 * TypeScript SDK Client for Continuous Assurance (Phase 5.54).
 */

export class ContinuousAssuranceClient {
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

  async recordObservation(
    tenantId: string,
    sourceDomain: string,
    observationType: string,
    payload: Record<string, any>,
    severity: string = "INFO"
  ): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/continuous-assurance/observations`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({
        source_domain: sourceDomain,
        observation_type: observationType,
        payload,
        severity,
      }),
    });
    return res.json();
  }

  async evaluateAssurance(tenantId: string, scope: string = "global"): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/continuous-assurance/assessments`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({ scope }),
    });
    return res.json();
  }

  async getCurrentAssurance(tenantId: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/continuous-assurance/assessments/current`, {
      method: "GET",
      headers: this.getHeaders(tenantId),
    });
    return res.json();
  }

  async analyzeDrift(
    tenantId: string,
    driftType: string,
    expectedState: Record<string, any>,
    observedState: Record<string, any>
  ): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/continuous-assurance/drift/analyze`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({
        drift_type: driftType,
        expected_state: expectedState,
        observed_state: observedState,
      }),
    });
    return res.json();
  }

  async verify(
    tenantId: string,
    targetResourceId: string,
    expectedHash: string,
    actualHash: string
  ): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/continuous-assurance/verify`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({
        target_resource_id: targetResourceId,
        expected_hash: expectedHash,
        actual_hash: actualHash,
      }),
    });
    return res.json();
  }
}
