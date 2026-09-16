/**
 * TypeScript SDK client for Phase 5.46 Knowledge Assurance platform.
 */

export interface KnowledgeReference {
  reference_id: string;
  tenant_id: string;
  external_key: string;
  resource_type: string;
  status: string;
  classification: string;
  sha256_checksum: string;
  is_immutable: boolean;
  created_at: string;
}

export interface KnowledgeTrustAssessment {
  assessment_id: string;
  tenant_id: string;
  target_resource_id: string;
  overall_score: number;
  trust_band: string;
  confidence_level: string;
  created_at: string;
}

export class KnowledgeAssuranceClient {
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
      throw new Error(`Knowledge Assurance API error: ${res.statusText}`);
    }
    return res.json();
  }

  async getStatus(tenantId = "default_tenant"): Promise<any> {
    return this.request("/v1/knowledge/status", { method: "GET" }, tenantId);
  }

  async createReference(
    externalKey: string,
    resourceType = "DOCUMENT",
    classification = "INTERNAL",
    tenantId = "default_tenant"
  ): Promise<KnowledgeReference> {
    return this.request(
      "/v1/knowledge/references",
      {
        method: "POST",
        body: JSON.stringify({ external_key: externalKey, resource_type: resourceType, classification }),
      },
      tenantId
    );
  }

  async listReferences(tenantId = "default_tenant"): Promise<KnowledgeReference[]> {
    return this.request("/v1/knowledge/references", { method: "GET" }, tenantId);
  }

  async registerSource(
    name: string,
    sourceType = "DOCUMENT_REPOSITORY",
    authority = "AUTHORITATIVE",
    tenantId = "default_tenant"
  ): Promise<any> {
    return this.request(
      "/v1/knowledge/sources",
      {
        method: "POST",
        body: JSON.stringify({ name, source_type: sourceType, authority }),
      },
      tenantId
    );
  }

  async evaluateTrust(targetResourceId: string, tenantId = "default_tenant"): Promise<KnowledgeTrustAssessment> {
    return this.request(`/v1/knowledge/trust/${targetResourceId}`, { method: "GET" }, tenantId);
  }

  async assessAssurance(targetResourceId: string, tenantId = "default_tenant"): Promise<any> {
    return this.request(`/v1/knowledge/assurance/${targetResourceId}`, { method: "GET" }, tenantId);
  }

  async getAnalyticsReport(tenantId = "default_tenant"): Promise<any> {
    return this.request("/v1/knowledge/analytics/report", { method: "GET" }, tenantId);
  }
}

export class KnowledgeClient {
  constructor(
    private fetchFn: typeof fetch,
    private baseUrl: string,
    private headers: Record<string, string>
  ) {}

  async search(query: string): Promise<any> {
    const res = await this.fetchFn(`${this.baseUrl}/v1/knowledge/search`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({ query }),
    });
    return res.json();
  }
}

