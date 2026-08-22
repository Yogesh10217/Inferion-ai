/**
 * TypeScript SDK Client for Extension Framework.
 */

export class ExtensionsClient {
  private baseUrl: string;

  constructor(baseUrl: string = "http://localhost:8000") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async listExtensions(): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/v1/extensions`);
    if (!res.ok) throw new Error(`Fetch failed: ${res.statusText}`);
    return res.json();
  }
}
