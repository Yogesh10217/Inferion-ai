/**
 * TypeScript SDK client for Phase 5.53 Enterprise AI Autonomous Assurance Orchestration Platform.
 */

export interface CreateWorkflowInput {
  name: string;
  description?: string;
  workflow_type?: string;
  priority?: string;
  max_duration_seconds?: number;
}

export class AutonomousAssuranceClient {
  private baseUrl: string;
  private apiKey?: string;

  constructor(baseUrl: string = "http://localhost:8000", apiKey?: string) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.apiKey = apiKey;
  }

  private getHeaders(tenantId: string = "default"): Record<string, string> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "X-Tenant-ID": tenantId
    };
    if (this.apiKey) {
      headers["Authorization"] = `Bearer ${this.apiKey}`;
    }
    return headers;
  }

  async createWorkflow(input: CreateWorkflowInput, tenantId: string = "default"): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/autonomous/workflows`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify(input)
    });
    return res.json();
  }

  async getWorkflow(workflowId: string, tenantId: string = "default"): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/autonomous/workflows/${workflowId}`, {
      method: "GET",
      headers: this.getHeaders(tenantId)
    });
    return res.json();
  }

  async planWorkflow(workflowId: string, tenantId: string = "default"): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/autonomous/workflows/${workflowId}/plan`, {
      method: "POST",
      headers: this.getHeaders(tenantId)
    });
    return res.json();
  }

  async submitApproval(workflowId: string, approver: string, approved: boolean, comments?: string, tenantId: string = "default"): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/autonomous/workflows/${workflowId}/approve`, {
      method: "POST",
      headers: this.getHeaders(tenantId),
      body: JSON.stringify({ approver, approved, comments })
    });
    return res.json();
  }

  async runFlow(name: string = "Enterprise Autonomous Assurance Flow", tenantId: string = "default"): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/autonomous/flow?name=${encodeURIComponent(name)}`, {
      method: "POST",
      headers: this.getHeaders(tenantId)
    });
    return res.json();
  }
}
