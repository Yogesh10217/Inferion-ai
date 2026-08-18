/**
 * TypeScript SDK Client for Enterprise Multi-Agent Collaboration Platform
 */

export interface TeamMember {
  member_id: string;
  is_active: boolean;
  assigned_tasks_count: number;
}

export interface TeamDetails {
  team_id: string;
  name: string;
  type: string;
  status: string;
  members: TeamMember[];
}

export class TeamsClient {
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

  async create(name: string, teamType: string = "custom", description: string = "", budgetDollars: number = 10.0): Promise<{ status: string; team_id: string }> {
    const res = await fetch(`${this.baseUrl}/v1/teams`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ name, team_type: teamType, description, budget_dollars: budgetDollars }),
    });
    return res.json();
  }

  async list(tenantId: string = "global"): Promise<any[]> {
    const res = await fetch(`${this.baseUrl}/v1/teams?tenant_id=${tenantId}`, {
      headers: this.getHeaders(),
    });
    const data = await res.json();
    return data.teams || [];
  }

  async get(teamId: string): Promise<TeamDetails> {
    const res = await fetch(`${this.baseUrl}/v1/teams/${teamId}`, {
      headers: this.getHeaders(),
    });
    return res.json();
  }

  async update(teamId: string, description?: string, budgetDollars?: number): Promise<{ status: string; team_id: string }> {
    const params = new URLSearchParams();
    if (description) params.append("description", description);
    if (budgetDollars !== undefined) params.append("budget_dollars", budgetDollars.toString());

    const res = await fetch(`${this.baseUrl}/v1/teams/${teamId}?${params.toString()}`, {
      method: "PATCH",
      headers: this.getHeaders(),
    });
    return res.json();
  }

  async delete(teamId: string): Promise<{ status: string; team_id: string }> {
    const res = await fetch(`${this.baseUrl}/v1/teams/${teamId}`, {
      method: "DELETE",
      headers: this.getHeaders(),
    });
    return res.json();
  }

  async run(teamId: string, goal: string, inputs?: Record<string, any>): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/teams/${teamId}/run`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ goal, inputs: inputs || {} }),
    });
    const data = await res.json();
    return data.result;
  }

  async pause(teamId: string): Promise<{ status: string }> {
    const res = await fetch(`${this.baseUrl}/v1/teams/${teamId}/pause`, {
      method: "POST",
      headers: this.getHeaders(),
    });
    return res.json();
  }

  async resume(teamId: string): Promise<{ status: string }> {
    const res = await fetch(`${this.baseUrl}/v1/teams/${teamId}/resume`, {
      method: "POST",
      headers: this.getHeaders(),
    });
    return res.json();
  }

  async cancel(teamId: string): Promise<{ status: string }> {
    const res = await fetch(`${this.baseUrl}/v1/teams/${teamId}/cancel`, {
      method: "POST",
      headers: this.getHeaders(),
    });
    return res.json();
  }

  async members(teamId: string): Promise<TeamMember[]> {
    const res = await fetch(`${this.baseUrl}/v1/teams/${teamId}/members`, {
      headers: this.getHeaders(),
    });
    const data = await res.json();
    return data.members || [];
  }

  async addMember(teamId: string, name: string, role: string = "executor", systemPrompt: string = ""): Promise<TeamMember> {
    const res = await fetch(`${this.baseUrl}/v1/teams/${teamId}/members`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ name, role, system_prompt: systemPrompt }),
    });
    const data = await res.json();
    return data.member;
  }

  async messages(teamId: string): Promise<any[]> {
    const res = await fetch(`${this.baseUrl}/v1/teams/${teamId}/messages`, {
      headers: this.getHeaders(),
    });
    const data = await res.json();
    return data.messages || [];
  }

  async history(teamId: string): Promise<any[]> {
    const res = await fetch(`${this.baseUrl}/v1/teams/${teamId}/history`, {
      headers: this.getHeaders(),
    });
    const data = await res.json();
    return data.history || [];
  }

  async metrics(teamId: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/teams/${teamId}/metrics`, {
      headers: this.getHeaders(),
    });
    const data = await res.json();
    return data.metrics;
  }

  async billing(teamId: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/teams/${teamId}/billing`, {
      headers: this.getHeaders(),
    });
    const data = await res.json();
    return data.billing;
  }
}
