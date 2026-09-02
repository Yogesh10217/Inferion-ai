/**
 * TypeScript SDK Client for Enterprise AI Access Intelligence (Phase 5.39).
 */

export interface AccessIdentity {
  identity_id: str;
  tenant_id: str;
  name: str;
  identity_type: str;
  status: str;
  risk_level: str;
}

export interface AuthorizationDecision {
  decision_id: str;
  request_id: str;
  tenant_id: str;
  outcome: string;
  reason: string;
  risk_score: number;
}

export class AccessIntelligenceClient {
  private baseUrl: string;
  private apiKey: string;
  private tenantId: string;

  constructor(baseUrl: string, apiKey: string, tenantId: string = "default") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.apiKey = apiKey;
    this.tenantId = tenantId;
  }

  private getHeaders(): Record<string, string> {
    return {
      "Authorization": `Bearer ${this.apiKey}`,
      "X-Tenant-ID": this.tenantId,
      "Content-Type": "application/json",
    };
  }

  async listIdentities(): Promise<AccessIdentity[]> {
    const res = await fetch(`${this.baseUrl}/v1/access/identities`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error(`Failed to list identities: ${res.statusText}`);
    return res.json() as Promise<AccessIdentity[]>;
  }

  async evaluateAuthorization(
    subjectIdentityId: string,
    action: string,
    resourceId: string,
    resourceType: string
  ): Promise<AuthorizationDecision> {
    const params = new URLSearchParams({
      subject_identity_id: subjectIdentityId,
      action,
      resource_id: resourceId,
      resource_type: resourceType,
    });
    const res = await fetch(`${this.baseUrl}/v1/access/authorization/evaluate?${params.toString()}`, {
      method: "POST",
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error(`Failed to evaluate authorization: ${res.statusText}`);
    return res.json() as Promise<AuthorizationDecision>;
  }

  async runFullLifecycle(): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/v1/access/lifecycle/run`, {
      method: "POST",
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error(`Failed to run lifecycle: ${res.statusText}`);
    return res.json() as Promise<Record<string, any>>;
  }
}
