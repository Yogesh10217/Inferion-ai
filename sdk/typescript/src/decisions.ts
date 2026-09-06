/**
 * TypeScript SDK client for Decision Governance platform.
 */

export interface Decision {
  decision_id: str;
  tenant_id: str;
  title: str;
  description?: str;
  decision_type: string;
  status: string;
  priority: string;
  outcome?: string;
  confidence: number;
  risk_score: number;
  fingerprint?: string;
  is_immutable: boolean;
  created_at: string;
}

export class DecisionsClient {
  constructor(private baseUrl: string, private apiKey?: string) {}

  private async request(path: string, options: RequestInit = {}, tenantId = "default_tenant"): Promise<any> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "x-tenant-id": tenantId,
      ...(this.apiKey ? { Authorization: `Bearer ${this.apiKey}` } : {}),
      ...(options.headers as Record<string, string>),
    };

    const res = await fetch(`${this.baseUrl}${path}`, { ...options, headers });
    if (!res.ok) {
      throw new Error(`Decisions API error: ${res.statusText}`);
    }
    return res.json();
  }

  async createDecision(title: string, decisionType = "OPERATIONAL", description = "", tenantId = "default_tenant"): Promise<Decision> {
    return this.request("/v1/decisions", {
      method: "POST",
      body: JSON.stringify({ title, decision_type: decisionType, description }),
    }, tenantId);
  }

  async listDecisions(tenantId = "default_tenant"): Promise<Decision[]> {
    return this.request("/v1/decisions", { method: "GET" }, tenantId);
  }

  async getDecision(decisionId: string, tenantId = "default_tenant"): Promise<Decision> {
    return this.request(`/v1/decisions/${decisionId}`, { method: "GET" }, tenantId);
  }

  async analyzeDecision(decisionId: string, tenantId = "default_tenant"): Promise<any> {
    return this.request(`/v1/decisions/${decisionId}/analyze`, { method: "POST" }, tenantId);
  }

  async approveDecision(decisionId: string, tenantId = "default_tenant"): Promise<Decision> {
    return this.request(`/v1/decisions/${decisionId}/approve`, { method: "POST" }, tenantId);
  }
}
