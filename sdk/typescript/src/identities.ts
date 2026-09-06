/**
 * TypeScript SDK client for Phase 5.48 Identity Assurance platform.
 */

export interface IdentityReference {
  identity_id: string;
  tenant_id: string;
  name: string;
  identity_type: string;
  category: string;
  status: string;
  external_id?: string;
  created_at: string;
}

export interface IdentityTrustAssessment {
  assessment_id: string;
  identity_id: string;
  tenant_id: string;
  is_trusted: boolean;
  risk_level: string;
  evaluated_at: string;
}

export class IdentityAssuranceClient {
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
      throw new Error(`Identity Assurance API error: ${res.statusText}`);
    }
    return res.json();
  }

  async registerIdentity(
    name: string,
    identityType = "HUMAN",
    category = "EMPLOYEE",
    externalId?: string,
    tenantId = "default_tenant"
  ): Promise<IdentityReference> {
    return this.request(
      "/v1/identities",
      {
        method: "POST",
        body: JSON.stringify({ name, identity_type: identityType, category, external_id: externalId }),
      },
      tenantId
    );
  }

  async getIdentity(identityId: string, tenantId = "default_tenant"): Promise<IdentityReference> {
    return this.request(`/v1/identities/${identityId}`, { method: "GET" }, tenantId);
  }

  async assessTrust(identityId: string, tenantId = "default_tenant"): Promise<IdentityTrustAssessment> {
    return this.request(`/v1/identities/${identityId}/trust`, { method: "POST" }, tenantId);
  }

  async evaluateAssurance(identityId: string, tenantId = "default_tenant"): Promise<any> {
    return this.request(`/v1/identities/${identityId}/assurance`, { method: "GET" }, tenantId);
  }
}
