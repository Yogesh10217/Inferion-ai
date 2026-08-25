/**
 * TypeScript SDK Client for Enterprise AI Reliability Platform (Phase 5.31).
 */

export class ReliabilityClient {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async registerService(tenantId: string, name: string, tier: string = "TIER_1_HIGH"): Promise<any> {
    return this.client.post(`/v1/reliability/services?tenant_id=${tenantId}`, { name, tier });
  }

  async createSLO(tenantId: string, serviceId: string, name: string, targetPercentage: number = 99.9): Promise<any> {
    return this.client.post(`/v1/reliability/slos?tenant_id=${tenantId}`, {
      service_id: serviceId,
      name,
      target_percentage: targetPercentage,
    });
  }

  async createIncident(tenantId: string, serviceId: string, title: str, severity: string = "SEV_1_HIGH"): Promise<any> {
    return this.client.post(`/v1/reliability/incidents?tenant_id=${tenantId}`, {
      service_id: serviceId,
      title,
      severity,
    });
  }

  async planRemediation(tenantId: string, incidentId: string, idempotencyKey: string, actionName: string = "RESTART_POD", isHighRisk: boolean = false): Promise<any> {
    return this.client.post(`/v1/reliability/remediations/plan?tenant_id=${tenantId}`, {
      incident_id: incidentId,
      idempotency_key: idempotencyKey,
      action_name: actionName,
      is_high_risk: isHighRisk,
    });
  }

  async createPostmortem(tenantId: string, incidentId: string, summary: string, rootCause: string): Promise<any> {
    return this.client.post(`/v1/reliability/postmortems?tenant_id=${tenantId}`, {
      incident_id: incidentId,
      summary,
      root_cause: rootCause,
    });
  }

  async getAnalyticsReport(tenantId: string): Promise<any> {
    return this.client.get(`/v1/reliability/analytics/report?tenant_id=${tenantId}`);
  }
}
