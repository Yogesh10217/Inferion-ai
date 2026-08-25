/**
 * TypeScript SDK Client for Enterprise AI Security Intelligence Platform (Phase 5.32).
 */

export class SecurityClient {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async registerAsset(tenantId: string, name: string, assetType: string = "MODEL_GATEWAY", criticality: string = "HIGH"): Promise<any> {
    return this.client.post(`/v1/security/assets?tenant_id=${tenantId}`, { name, asset_type: assetType, criticality });
  }

  async ingestSignal(tenantId: string, assetId: string, signalType: string, severity: string = "HIGH", payload: any = {}): Promise<any> {
    return this.client.post(`/v1/security/signals?tenant_id=${tenantId}`, { asset_id: assetId, signal_type: signalType, severity, payload });
  }

  async createThreat(tenantId: string, assetId: string, threatType: string, severity: string = "HIGH"): Promise<any> {
    return this.client.post(`/v1/security/threats?tenant_id=${tenantId}`, { asset_id: assetId, threat_type: threatType, severity });
  }

  async analyzeAIThreat(tenantId: string, modelOrAgentId: string, threatType: string = "PROMPT_INJECTION", severity: string = "HIGH"): Promise<any> {
    return this.client.post(`/v1/security/ai-threats?tenant_id=${tenantId}`, { model_or_agent_id: modelOrAgentId, threat_type: threatType, severity });
  }

  async createVulnerability(tenantId: string, assetId: string, title: string, severity: string = "HIGH", cveId?: string): Promise<any> {
    return this.client.post(`/v1/security/vulnerabilities?tenant_id=${tenantId}`, { asset_id: assetId, title, severity, cve_id: cveId });
  }

  async createIncident(tenantId: string, assetId: string, title: string, severity: string = "SEV_1_HIGH"): Promise<any> {
    return this.client.post(`/v1/security/incidents?tenant_id=${tenantId}`, { asset_id: assetId, title, severity });
  }

  async planRemediation(tenantId: string, incidentId: string, idempotencyKey: string, actionName: string = "REVOKE_KEY", priority: string = "HIGH"): Promise<any> {
    return this.client.post(`/v1/security/remediation/plan?tenant_id=${tenantId}`, { incident_id: incidentId, idempotency_key: idempotencyKey, action_name: actionName, priority });
  }

  async getPosture(tenantId: string): Promise<any> {
    return this.client.get(`/v1/security/posture?tenant_id=${tenantId}`);
  }

  async getAnalyticsReport(tenantId: string): Promise<any> {
    return this.client.get(`/v1/security/analytics/report?tenant_id=${tenantId}`);
  }
}
