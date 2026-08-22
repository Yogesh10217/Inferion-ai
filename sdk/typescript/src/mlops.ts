/**
 * TypeScript SDK Client for MLOps API.
 */

export class MLOpsClient {
  private baseUrl: string;

  constructor(baseUrl: string = "http://localhost:8000") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async listAssets(): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/v1/mlops/assets`);
    if (!res.ok) throw new Error(`Fetch failed: ${res.statusText}`);
    return res.json();
  }

  async listDeployments(): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/v1/mlops/deployments`);
    if (!res.ok) throw new Error(`Fetch failed: ${res.statusText}`);
    return res.json();
  }
}
