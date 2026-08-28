/**
 * TypeScript SDK Client for Enterprise AI Agent Orchestration Platform (Phase 5.36).
 */

export class AgentsClient {
  private baseUrl: string;
  private apiKey?: string;

  constructor(baseUrl: string, apiKey?: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }
    return headers;
  }

  async register(tenantId: string, payload: { name: string; agent_type?: string; role?: string; capabilities?: string[]; description?: string }): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/agents/register?tenant_id=${tenantId}`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`Agent register failed: ${res.statusText}`);
    return res.json();
  }

  async list(tenantId: string = 'default'): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/agents?tenant_id=${tenantId}`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error(`Agent list failed: ${res.statusText}`);
    return res.json();
  }

  async get(agentId: string, tenantId: string = 'default'): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/agents/${agentId}?tenant_id=${tenantId}`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error(`Agent get failed: ${res.statusText}`);
    return res.json();
  }

  async executeTask(tenantId: string, payload: { goal: string; prompt: string; agent_id?: string; is_destructive?: boolean }): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/agents/execute?tenant_id=${tenantId}`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`Task execute failed: ${res.statusText}`);
    return res.json();
  }

  async getTrace(traceId: string, tenantId: string = 'default'): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/agents/traces/${traceId}?tenant_id=${tenantId}`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error(`Trace get failed: ${res.statusText}`);
    return res.json();
  }

  async getAnalytics(tenantId: string = 'default'): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/agents/analytics?tenant_id=${tenantId}`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error(`Analytics get failed: ${res.statusText}`);
    return res.json();
  }
}
