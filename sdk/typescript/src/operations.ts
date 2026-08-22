/**
 * TypeScript SDK Client for Operations API.
 */

export class OperationsClient {
  private baseUrl: string;

  constructor(baseUrl: string = "http://localhost:8000") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async getHealth(): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/v1/operations/health`);
    if (!res.ok) throw new Error(`Fetch failed: ${res.statusText}`);
    return res.json();
  }

  async listIncidents(): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/v1/operations/incidents`);
    if (!res.ok) throw new Error(`Fetch failed: ${res.statusText}`);
    return res.json();
  }
}
