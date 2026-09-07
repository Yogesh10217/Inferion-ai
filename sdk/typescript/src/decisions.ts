/**
 * TypeScript SDK for Phase 5.52 Enterprise AI Decision Intelligence Platform.
 */

export interface Decision {
  id: string;
  tenant_id: string;
  title: string;
  description?: string;
  state: string;
  decision_type: string;
  scope: string;
  risk_level: string;
  confidence_score: number;
  uncertainty_score: number;
  created_at: string;
  updated_at: string;
  fingerprint?: string;
}

export interface DecisionSimulationResult {
  simulation_id: string;
  decision_id: string;
  tenant_id: string;
  compared_options: any[];
  best_option_id?: string;
  tradeoffs: any[];
  simulated_impact: Record<string, any>;
  simulated_risk: Record<string, any>;
}

export class DecisionIntelligenceClient {
  private baseUrl: string;
  private apiKey?: string;
  private tenantId: string;

  constructor(baseUrl: string = "http://localhost:8000", apiKey?: string, tenantId: string = "default") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.apiKey = apiKey;
    this.tenantId = tenantId;
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      "X-Tenant-ID": this.tenantId,
      "Content-Type": "application/json",
    };
    if (this.apiKey) {
      headers["Authorization"] = `Bearer ${this.apiKey}`;
    }
    return headers;
  }

  async createDecision(title: string, options?: { description?: string; decision_type?: string; risk_level?: string }): Promise<Decision> {
    const res = await fetch(`${this.baseUrl}/v1/decisions`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({
        title,
        description: options?.description,
        decision_type: options?.decision_type || "OPERATIONAL",
        risk_level: options?.risk_level || "MEDIUM",
      }),
    });
    if (!res.ok) throw new Error(`Create decision failed: ${res.statusText}`);
    return res.json();
  }

  async getDecision(decisionId: string): Promise<Decision> {
    const res = await fetch(`${this.baseUrl}/v1/decisions/${decisionId}`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error(`Get decision failed: ${res.statusText}`);
    return res.json();
  }

  async transitionState(decisionId: string, targetState: string, reason?: string): Promise<Decision> {
    const res = await fetch(`${this.baseUrl}/v1/decisions/${decisionId}/transition`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ target_state: targetState, reason }),
    });
    if (!res.ok) throw new Error(`State transition failed: ${res.statusText}`);
    return res.json();
  }

  async simulate(decisionId: string, scenarios?: string[]): Promise<DecisionSimulationResult> {
    const res = await fetch(`${this.baseUrl}/v1/decisions/${decisionId}/simulate`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ scenarios: scenarios || ["BASELINE", "HIGH_LOAD"] }),
    });
    if (!res.ok) throw new Error(`Decision simulation failed: ${res.statusText}`);
    return res.json();
  }
}
