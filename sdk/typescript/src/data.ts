/**
 * TypeScript SDK Client for Enterprise AI Data Intelligence Platform (Phase 5.43).
 */

export class DataIntelligenceClient {
  private baseUrl: string;

  constructor(baseUrl: string = "http://localhost:8000") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async listDatasets(tenantId: string = "global"): Promise<any[]> {
    const res = await fetch(`${this.baseUrl}/v1/data/datasets?tenant_id=${tenantId}`);
    if (!res.ok) throw new Error(`Fetch failed: ${res.statusText}`);
    return res.json();
  }

  async registerDataset(name: string, tenantId: string = "global", datasetType: string = "TABLE"): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/v1/data/datasets`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, tenant_id: tenantId, dataset_type: datasetType }),
    });
    if (!res.ok) throw new Error(`Fetch failed: ${res.statusText}`);
    return res.json();
  }

  async getTrust(datasetId: string, tenantId: string = "global"): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/v1/data/trust?dataset_id=${datasetId}&tenant_id=${tenantId}`);
    if (!res.ok) throw new Error(`Fetch failed: ${res.statusText}`);
    return res.json();
  }

  async getAnalytics(tenantId: string = "global"): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/v1/data/analytics?tenant_id=${tenantId}`);
    if (!res.ok) throw new Error(`Fetch failed: ${res.statusText}`);
    return res.json();
  }
}

export const DataClient = DataIntelligenceClient;
