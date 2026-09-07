/**
 * TypeScript SDK client for Phase 5.51 Enterprise AI Unified Intelligence Platform.
 */

export interface UnifiedSignalInput {
  domain: string;
  entity_reference: string;
  signal_type: string;
  severity?: string;
  confidence_score?: number;
  risk_score?: number;
  evidence_references?: string[];
  metadata?: Record<string, any>;
  idempotency_key?: string;
}

export class UnifiedIntelligenceClient {
  private baseUrl: string;
  private apiKey?: string;

  constructor(baseUrl: string = "http://localhost:8000", apiKey?: string) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.apiKey = apiKey;
  }

  private getHeaders(tenantId: string = "default_tenant"): Record<string, string> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "x-tenant-id": tenantId
    };
    if (this.apiKey) {
      headers["Authorization"] = `Bearer ${this.apiKey}`;
    }
    return headers;
  }

  async ingestSignal(input: UnifiedSignalInput, tenantId: string = "default_tenant"): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/intelligence/signals`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify(input)
    });
    return res.json();
  }

  async evaluateSituations(tenantId: string = "default_tenant"): Promise<any[]> {
    const res = await fetch(`${this.baseUrl}/v1/intelligence/situations/evaluate`, {
      method: "POST",
      headers: this.getHeaders(tenantId)
    });
    return res.json();
  }

  async evaluateRisk(tenantId: string = "default_tenant"): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/intelligence/risk`, {
      method: "GET",
      headers: this.getHeaders(tenantId)
    });
    return res.json();
  }

  async evaluateAssurance(tenantId: string = "default_tenant"): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/intelligence/assurance`, {
      method: "GET",
      headers: this.getHeaders(tenantId)
    });
    return res.json();
  }

  async evaluateTrust(entityRef: string, tenantId: string = "default_tenant"): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/intelligence/trust/${encodeURIComponent(entityRef)}`, {
      method: "GET",
      headers: this.getHeaders(tenantId)
    });
    return res.json();
  }

  async generateRecommendations(situationId: string, tenantId: string = "default_tenant"): Promise<any[]> {
    const res = await fetch(`${this.baseUrl}/v1/intelligence/recommendations/${situationId}`, {
      method: "POST",
      headers: this.getHeaders(tenantId)
    });
    return res.json();
  }

  async getAnalytics(tenantId: string = "default_tenant"): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/intelligence/analytics`, {
      method: "GET",
      headers: this.getHeaders(tenantId)
    });
    return res.json();
  }

  async getBilling(tenantId: string = "default_tenant"): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/intelligence/billing`, {
      method: "GET",
      headers: this.getHeaders(tenantId)
    });
    return res.json();
  }
}
