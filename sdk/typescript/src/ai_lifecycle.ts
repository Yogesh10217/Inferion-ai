/**
 * TypeScript SDK Client for Enterprise AI Lifecycle Platform (Phase 5.33).
 */

export class AILifecycleClient {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async registerAsset(tenantId: string, name: string, assetType: string = "MODEL", description: string = ""): Promise<any> {
    return this.client.post(`/v1/ai-lifecycle/assets?tenant_id=${tenantId}`, { name, asset_type: assetType, description });
  }

  async registerDataset(tenantId: string, name: string, classification: string = "INTERNAL"): Promise<any> {
    return this.client.post(`/v1/ai-lifecycle/datasets?tenant_id=${tenantId}`, { name, classification });
  }

  async registerModel(tenantId: string, name: string, modelType: string = "LLM", framework: string = "TRANSFORMERS"): Promise<any> {
    return this.client.post(`/v1/ai-lifecycle/models?tenant_id=${tenantId}`, { name, model_type: modelType, framework });
  }

  async registerAgent(tenantId: string, name: string, agentType: string = "TASK_AGENT", autonomyLevel: string = "HUMAN_APPROVED"): Promise<any> {
    return this.client.post(`/v1/ai-lifecycle/agents?tenant_id=${tenantId}`, { name, agent_type: agentType, autonomy_level: autonomyLevel });
  }

  async runEvaluation(tenantId: string, targetAssetId: string, suiteId: string, overallPassed: boolean = true): Promise<any> {
    return this.client.post(`/v1/ai-lifecycle/evaluations?tenant_id=${tenantId}`, { target_asset_id: targetAssetId, suite_id: suiteId, overall_passed: overallPassed });
  }

  async createGate(tenantId: string, name: string, gateType: string = "SECURITY", isHardGate: boolean = true): Promise<any> {
    return this.client.post(`/v1/ai-lifecycle/gates?tenant_id=${tenantId}`, { name, gate_type: gateType, is_hard_gate: isHardGate });
  }

  async requestPromotion(tenantId: string, assetId: string, target: string = "STAGING", isHighRisk: boolean = false): Promise<any> {
    return this.client.post(`/v1/ai-lifecycle/promotions?tenant_id=${tenantId}`, { asset_id: assetId, target, is_high_risk: isHighRisk });
  }

  async createRelease(tenantId: string, title: string, assetId: string, version: string = "1.0.0", riskLevel: string = "MEDIUM"): Promise<any> {
    return this.client.post(`/v1/ai-lifecycle/releases?tenant_id=${tenantId}`, { title, asset_id: assetId, version, risk_level: riskLevel });
  }

  async detectDrift(tenantId: string, assetId: string, driftType: string = "PERFORMANCE_DRIFT", severity: string = "HIGH"): Promise<any> {
    return this.client.post(`/v1/ai-lifecycle/drift?tenant_id=${tenantId}`, { asset_id: assetId, drift_type: driftType, severity });
  }

  async requestRollback(tenantId: string, assetId: string, targetVersion: string = "1.0.0", reason: string = "Performance degradation"): Promise<any> {
    return this.client.post(`/v1/ai-lifecycle/rollbacks?tenant_id=${tenantId}`, { asset_id: assetId, target_version: targetVersion, reason });
  }

  async requestRetirement(tenantId: string, assetId: string, reason: string = "DEPRECATED"): Promise<any> {
    return this.client.post(`/v1/ai-lifecycle/retirement?tenant_id=${tenantId}`, { asset_id: assetId, reason });
  }

  async getAnalyticsReport(tenantId: string): Promise<any> {
    return this.client.get(`/v1/ai-lifecycle/analytics?tenant_id=${tenantId}`);
  }
}
