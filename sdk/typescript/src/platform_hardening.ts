/**
 * TypeScript SDK Client for Enterprise AI Platform Hardening & Certification.
 */

export interface PlatformAuditResponse {
  audit_id: string;
  tenant_id: string;
  status: string;
  findings_count: number;
  critical_findings_count: number;
  readiness_score: number;
  release_decision: string;
  certification_status: string;
}

export class PlatformHardeningClient {
  private baseUrl: string;
  private apiKey?: string;

  constructor(baseUrl: string = "http://localhost:8000", apiKey?: string) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.apiKey = apiKey;
  }

  private getHeaders(tenantId: string = "system"): Record<string, string> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "X-Tenant-ID": tenantId,
    };
    if (this.apiKey) {
      headers["Authorization"] = `Bearer ${this.apiKey}`;
    }
    return headers;
  }

  async runAudit(tenantId: string = "system"): Promise<PlatformAuditResponse> {
    const response = await fetch(`${this.baseUrl}/v1/platform-hardening/audit`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({ tenant_id: tenantId, include_ast_scan: true }),
    });
    if (!response.ok) {
      throw new Error(`Platform Audit failed: ${response.statusText}`);
    }
    return (await response.json()) as PlatformAuditResponse;
  }

  async getHealth(tenantId: string = "system"): Promise<any> {
    const response = await fetch(`${this.baseUrl}/v1/platform-hardening/health`, {
      method: "GET",
      headers: this.getHeaders(tenantId),
    });
    return await response.json();
  }

  async certifyPlatform(tenantId: string = "system"): Promise<any> {
    const response = await fetch(`${this.baseUrl}/v1/platform-hardening/certify`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({ tenant_id: tenantId, force_audit: false }),
    });
    return await response.json();
  }

  async getReadiness(tenantId: string = "system"): Promise<any> {
    const response = await fetch(`${this.baseUrl}/v1/platform-hardening/readiness`, {
      method: "GET",
      headers: this.getHeaders(tenantId),
    });
    return await response.json();
  }

  async scanStubs(tenantId: string = "system"): Promise<any> {
    const response = await fetch(`${this.baseUrl}/v1/platform-hardening/scan/stubs`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({ tenant_id: tenantId }),
    });
    return await response.json();
  }
}
