/**
 * TypeScript SDK Client for Enterprise Control Plane & Platform Management.
 */

export class ControlPlaneClient {
  private baseUrl: string;

  constructor(baseUrl: string = "http://localhost:8002") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async getSummary(): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/v1/control-plane/summary`);
    if (!res.ok) throw new Error(`Summary fetch failed: ${res.statusText}`);
    return res.json();
  }

  async listTenants(): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/v1/control-plane/tenants`);
    if (!res.ok) throw new Error(`Tenants fetch failed: ${res.statusText}`);
    return res.json();
  }
}
