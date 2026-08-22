/**
 * TypeScript SDK Client for Marketplace Platform.
 */

export class MarketplaceClient {
  private baseUrl: string;

  constructor(baseUrl: string = "http://localhost:8000") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async listItems(): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/v1/marketplace/items`);
    if (!res.ok) throw new Error(`Fetch failed: ${res.statusText}`);
    return res.json();
  }
}
