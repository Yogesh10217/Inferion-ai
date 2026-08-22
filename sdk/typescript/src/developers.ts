/**
 * TypeScript SDK Client for Developers & Webhooks API.
 */

export class DevelopersClient {
  private baseUrl: string;

  constructor(baseUrl: string = "http://localhost:8000") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async listProjects(): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/v1/developers/projects`);
    if (!res.ok) throw new Error(`Fetch failed: ${res.statusText}`);
    return res.json();
  }
}
