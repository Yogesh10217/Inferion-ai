/**
 * TypeScript SDK Client for Enterprise AI Decision Intelligence Platform (Phase 5.29).
 */

export class DecisionsClient {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async createContext(title: string, description: string): Promise<any> {
    return this.client.request('POST', '/v1/decisions/context', { title, description });
  }

  async createScenario(contextId: string, title: string, scenarioType: string = 'BASELINE'): Promise<any> {
    return this.client.request('POST', '/v1/decisions/scenarios', { context_id: contextId, title, scenario_type: scenarioType });
  }

  async analyze(title: string): Promise<any> {
    return this.client.request('POST', '/v1/decisions/analyze', { title });
  }

  async getDecision(decisionId: string): Promise<any> {
    return this.client.request('GET', `/v1/decisions/${decisionId}`);
  }

  async finalizeDecision(decisionId: string): Promise<any> {
    return this.client.request('POST', `/v1/decisions/${decisionId}/finalize`);
  }

  async getAnalytics(): Promise<any> {
    return this.client.request('GET', '/v1/decisions/analytics');
  }
}
