/**
 * TypeScript SDK Client for Data Fabric API.
 */

export class DataFabricClient {
  private baseUrl: string;

  constructor(baseUrl: string = "http://localhost:8000") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async listDataSources(): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/v1/data-sources`);
    if (!res.ok) throw new Error(`Fetch failed: ${res.statusText}`);
    return res.json();
  }

  async listCatalog(): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/v1/data-catalog`);
    if (!res.ok) throw new Error(`Fetch failed: ${res.statusText}`);
    return res.json();
  }
}
