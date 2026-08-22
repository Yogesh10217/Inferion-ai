/**
 * TypeScript SDK Client for Enterprise AI Observability, Monitoring & AIOps Platform
 */

export interface TraceSpan {
  span_id: string;
  trace_id: string;
  name: string;
  parent_span_id?: string;
  start_time: number;
  end_time?: number;
  duration_ms: number;
  status: string;
  component: string;
  tokens: { input: number; output: number; total: number };
  cost: number;
  attributes: Record<string, any>;
  events: any[];
}

export interface ExecutionTimeline {
  trace_id: string;
  execution_id?: string;
  total_duration_ms: number;
  total_cost: number;
  total_tokens: number;
  items: any[];
}

export class ObservabilityClient {
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

  async getTrace(traceId: string): Promise<{ trace_id: string; spans: TraceSpan[] }> {
    const res = await fetch(`${this.baseUrl}/v1/observability/traces/${traceId}`, {
      headers: this.getHeaders(),
    });
    return res.json();
  }

  async getExecution(executionId: string): Promise<{ execution_id: string; spans: TraceSpan[] }> {
    const res = await fetch(`${this.baseUrl}/v1/observability/executions/${executionId}`, {
      headers: this.getHeaders(),
    });
    return res.json();
  }

  async getTimeline(executionId: string): Promise<ExecutionTimeline> {
    const res = await fetch(`${this.baseUrl}/v1/observability/executions/${executionId}/timeline`, {
      headers: this.getHeaders(),
    });
    return res.json();
  }

  async replay(executionId: str, forceExternalEffects: boolean = false): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/observability/executions/${executionId}/replay`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ force_external_effects: forceExternalEffects }),
    });
    return res.json();
  }

  async getCosts(executionId?: string): Promise<any> {
    const url = executionId
      ? `${this.baseUrl}/v1/observability/costs?execution_id=${executionId}`
      : `${this.baseUrl}/v1/observability/costs`;
    const res = await fetch(url, { headers: this.getHeaders() });
    return res.json();
  }

  async getCostBreakdown(): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/observability/costs/breakdown`, {
      headers: this.getHeaders(),
    });
    return res.json();
  }

  async getPerformance(component?: string): Promise<any> {
    const url = component
      ? `${this.baseUrl}/v1/observability/performance?component=${component}`
      : `${this.baseUrl}/v1/observability/performance`;
    const res = await fetch(url, { headers: this.getHeaders() });
    return res.json();
  }

  async getFailures(executionId: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/observability/failures?execution_id=${executionId}`, {
      headers: this.getHeaders(),
    });
    return res.json();
  }

  async getAnomalies(limit: number = 50): Promise<any[]> {
    const res = await fetch(`${this.baseUrl}/v1/observability/anomalies?limit=${limit}`, {
      headers: this.getHeaders(),
    });
    return res.json();
  }

  async getAlerts(status?: string, level?: string): Promise<any[]> {
    let url = `${this.baseUrl}/v1/observability/alerts`;
    const params = new URLSearchParams();
    if (status) params.append("status", status);
    if (level) params.append("level", level);
    if (params.toString()) url += `?${params.toString()}`;
    const res = await fetch(url, { headers: this.getHeaders() });
    return res.json();
  }

  async acknowledgeAlert(alertId: string, userId: string = "system"): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/observability/alerts/${alertId}/acknowledge`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ user_id: userId }),
    });
    return res.json();
  }

  async getSLOs(): Promise<any[]> {
    const res = await fetch(`${this.baseUrl}/v1/observability/slos`, {
      headers: this.getHeaders(),
    });
    return res.json();
  }

  async getEvaluations(): Promise<any[]> {
    const res = await fetch(`${this.baseUrl}/v1/observability/evaluations`, {
      headers: this.getHeaders(),
    });
    return res.json();
  }

  async getStatus(): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/operations/status`, {
      headers: this.getHeaders(),
    });
    return res.json();
  }

  async getDashboard(): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/operations/dashboard`, {
      headers: this.getHeaders(),
    });
    return res.json();
  }
}
