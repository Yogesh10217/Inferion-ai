/**
 * TypeScript SDK Client for Autonomous Execution & Digital Workforce Platform
 */

export class AutonomyClient {
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

  async submitGoal(goal: string, tenantId: string = "global"): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/autonomy/goals`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ goal, tenant_id: tenantId }),
    });
    const data = await res.json();
    return data.execution;
  }

  async pause(executionId: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/autonomy/pause?execution_id=${executionId}`, {
      method: "POST",
      headers: this.getHeaders(),
    });
    return res.json();
  }

  async resume(executionId: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/autonomy/resume?execution_id=${executionId}`, {
      method: "POST",
      headers: this.getHeaders(),
    });
    return res.json();
  }

  async stop(executionId: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/autonomy/stop?execution_id=${executionId}`, {
      method: "POST",
      headers: this.getHeaders(),
    });
    return res.json();
  }

  async listExecutions(): Promise<any[]> {
    const res = await fetch(`${this.baseUrl}/v1/autonomy/executions`, {
      headers: this.getHeaders(),
    });
    const data = await res.json();
    return data.executions || [];
  }
}

export class WorkersClient {
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

  async create(name: string, templateType: string = "custom", tenantId: string = "global"): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/workers`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ name, template_type: templateType, tenant_id: tenantId }),
    });
    const data = await res.json();
    return data.worker;
  }

  async list(tenantId: string = "global"): Promise<any[]> {
    const res = await fetch(`${this.baseUrl}/v1/workers?tenant_id=${tenantId}`, {
      headers: this.getHeaders(),
    });
    const data = await res.json();
    return data.workers || [];
  }

  async get(workerId: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/workers/${workerId}`, {
      headers: this.getHeaders(),
    });
    const data = await res.json();
    return data.worker;
  }

  async terminate(workerId: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/workers/${workerId}`, {
      method: "DELETE",
      headers: this.getHeaders(),
    });
    return res.json();
  }

  async assignGoal(workerId: string, goal: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/workers/${workerId}/goal`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ goal }),
    });
    const data = await res.json();
    return data.result;
  }
}
