export interface DataAsset {
  tenant_id: string;
  asset_id: string;
  name: string;
  type: string;
  classification: string;
  domain: string;
  status: string;
}

export interface DataAccessRequest {
  tenant_id?: string;
  principal_id: string;
  asset_id: string;
  action?: string;
  purpose?: string;
}

export class DataGovernanceClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async listAssets(tenantId: string = "global"): Promise<{ assets: DataAsset[] }> {
    const res = await fetch(`${this.baseUrl}/v1/data-governance/assets?tenant_id=${tenantId}`);
    return res.json();
  }

  async evaluateAccess(req: DataAccessRequest): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/data-governance/access/evaluate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req),
    });
    return res.json();
  }

  async getTrustScore(assetId: string, tenantId: string = "global"): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/data-governance/trust/${assetId}?tenant_id=${tenantId}`);
    return res.json();
  }
}
