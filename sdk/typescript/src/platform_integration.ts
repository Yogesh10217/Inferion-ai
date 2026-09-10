/**
 * TypeScript SDK Client for Platform Integration Fabric (Phase 5.58).
 */

export class PlatformIntegrationClient {
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

  async buildContext(tenantId: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/platform-integration/context`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({}),
    });
    return res.json();
  }

  async correlate(tenantId: string, contextId: string, threshold: number = 0.5): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/platform-integration/correlate?context_id=${contextId}`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({ threshold }),
    });
    return res.json();
  }

  async getAssurance(tenantId: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/platform-integration/assurance`, {
      method: "GET",
      headers: this.getHeaders(tenantId),
    });
    return res.json();
  }

  async investigate(tenantId: string, rootPlatform: string, incidentDescription: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/platform-integration/investigations`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({ root_platform: rootPlatform, incident_description: incidentDescription }),
    });
    return res.json();
  }

  async getRecommendations(tenantId: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/platform-integration/recommendations`, {
      method: "GET",
      headers: this.getHeaders(tenantId),
    });
    return res.json();
  }

  async delegate(tenantId: string, recommendationId: string, approvalId?: string, approvalToken?: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/platform-integration/delegations`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({ recommendation_id: recommendationId, approval_id: approvalId, approval_token: approvalToken }),
    });
    return res.json();
  }

  async verify(tenantId: string, delegationId: string, preScore: number, postScore: number, requiredDelta: number = 0.05): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/platform-integration/verification`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({ delegation_id: delegationId, pre_score: preScore, post_score: postScore, required_delta: requiredDelta }),
    });
    return res.json();
  }

  async captureSnapshot(tenantId: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/platform-integration/snapshots`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({}),
    });
    return res.json();
  }
}
