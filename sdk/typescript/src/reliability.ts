/**
 * TypeScript SDK Client for Reliability, Security, Governance, and Jobs.
 */

export class ReliabilityClient {
  private baseUrl: string;

  constructor(baseUrl: string = "http://localhost:8002") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async getHealth(): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/v1/reliability/health`);
    if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
    return res.json();
  }

  async getCircuitBreakers(): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/v1/reliability/circuit-breakers`);
    if (!res.ok) throw new Error(`Circuit breakers fetch failed: ${res.statusText}`);
    return res.json();
  }
}
