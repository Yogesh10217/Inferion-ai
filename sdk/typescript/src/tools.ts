/**
 * TypeScript SDK Client for Enterprise Tool Calling & MCP Platform
 */

export interface ToolMetadata {
  name: string;
  description: string;
  category: string;
  cost_estimate?: number;
  requires_approval?: boolean;
}

export interface ToolResult {
  execution_id: string;
  tool_name: string;
  status: string;
  output?: any;
  error?: string;
  execution_time_seconds: number;
  cost: number;
}

export class ToolsClient {
  private baseUrl: string;
  private apiKey?: string;

  constructor(baseUrl: string = "http://localhost:8000", apiKey?: string) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.apiKey = apiKey;
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (this.apiKey) {
      headers["Authorization"] = `Bearer ${this.apiKey}`;
    }
    return headers;
  }

  async create(tool: Partial<ToolMetadata>): Promise<{ status: string; tool: ToolMetadata }> {
    const res = await fetch(`${this.baseUrl}/v1/tools`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(tool),
    });
    return res.json();
  }

  async list(tenantId: string = "global"): Promise<ToolMetadata[]> {
    const res = await fetch(`${this.baseUrl}/v1/tools?tenant_id=${tenantId}`, {
      headers: this.getHeaders(),
    });
    const data = await res.json();
    return data.tools || [];
  }

  async get(toolId: string, tenantId: string = "global"): Promise<ToolMetadata> {
    const res = await fetch(`${this.baseUrl}/v1/tools/${toolId}?tenant_id=${tenantId}`, {
      headers: this.getHeaders(),
    });
    const data = await res.json();
    return data.tool;
  }

  async delete(toolId: string, tenantId: string = "global"): Promise<{ status: string; id: string }> {
    const res = await fetch(`${this.baseUrl}/v1/tools/${toolId}?tenant_id=${tenantId}`, {
      method: "DELETE",
      headers: this.getHeaders(),
    });
    return res.json();
  }

  async execute(toolId: string, parameters: Record<string, any>, context?: Record<string, any>): Promise<ToolResult> {
    const res = await fetch(`${this.baseUrl}/v1/tools/${toolId}/execute`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ parameters, context }),
    });
    const data = await res.json();
    return data.result;
  }

  async validate(toolId: string, parameters: Record<string, any>): Promise<{ valid: boolean; error?: string }> {
    const res = await fetch(`${this.baseUrl}/v1/tools/${toolId}/validate`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ parameters }),
    });
    return res.json();
  }

  async audit(toolId: string, tenantId: string = "global"): Promise<{ audit_logs: any[] }> {
    const res = await fetch(`${this.baseUrl}/v1/tools/${toolId}/audit?tenant_id=${tenantId}`, {
      headers: this.getHeaders(),
    });
    return res.json();
  }

  async metrics(toolId: string, tenantId: string = "global"): Promise<{ metrics: any }> {
    const res = await fetch(`${this.baseUrl}/v1/tools/${toolId}/metrics?tenant_id=${tenantId}`, {
      headers: this.getHeaders(),
    });
    return res.json();
  }
}
