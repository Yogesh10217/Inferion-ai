/**
 * TypeScript SDK client for Security Assurance platform.
 */

export interface SecurityAssetPayload {
  name: string;
  asset_type?: string;
  criticality?: string;
  location?: string;
  owner?: string;
  metadata?: Record<string, any>;
}

export class SecurityAssuranceClient {
  private baseUrl: string;
  private apiKey: string;

  constructor(baseUrl: string, apiKey: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  async registerAsset(payload: SecurityAssetPayload, tenantId: string = 'default_tenant'): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/security/assets`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`,
        'x-tenant-id': tenantId,
      },
      body: JSON.stringify(payload),
    });
    return res.json();
  }

  async evaluatePosture(tenantId: string = 'default_tenant'): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/security/posture`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'x-tenant-id': tenantId,
      },
    });
    return res.json();
  }

  async evaluateAssurance(tenantId: string = 'default_tenant'): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/security/assurance`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'x-tenant-id': tenantId,
      },
    });
    return res.json();
  }
}
