/**
 * TypeScript SDK Client for Enterprise AI Event Intelligence Platform (Phase 5.34).
 */

export class EventsClient {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async create(tenantId: string, sourceName: string = "ExternalSystem", eventType: string = "CUSTOM_EVENT", category: string = "OPERATIONAL", severity: string = "MEDIUM", payload: any = {}, idempotencyReference?: string): Promise<any> {
    return this.client.post(`/v1/events?tenant_id=${tenantId}`, { source_name: sourceName, event_type: eventType, category, severity, payload, idempotency_reference: idempotencyReference });
  }

  async list(tenantId: string): Promise<any> {
    return this.client.get(`/v1/events?tenant_id=${tenantId}`);
  }

  async get(eventId: string, tenantId: string): Promise<any> {
    return this.client.get(`/v1/events/${eventId}?tenant_id=${tenantId}`);
  }

  async listCorrelations(tenantId: string): Promise<any> {
    return this.client.get(`/v1/events/correlations?tenant_id=${tenantId}`);
  }

  async getCorrelation(correlationId: string, tenantId: string): Promise<any> {
    return this.client.get(`/v1/events/correlations/${correlationId}?tenant_id=${tenantId}`);
  }

  async createRule(tenantId: string, name: string, actionName: string = "REQUEST_INVESTIGATION"): Promise<any> {
    return this.client.post(`/v1/events/automation/rules?tenant_id=${tenantId}`, { name, action_name: actionName });
  }

  async evaluateAutomation(tenantId: string, eventId: string, action: string = "REQUEST_INVESTIGATION", isHighRisk: boolean = false): Promise<any> {
    return this.client.post(`/v1/events/automation/evaluate?tenant_id=${tenantId}`, { event_id: eventId, action, is_high_risk: isHighRisk });
  }

  async investigate(eventId: string, tenantId: string): Promise<any> {
    return this.client.post(`/v1/events/${eventId}/investigate?tenant_id=${tenantId}`);
  }

  async respond(eventId: string, tenantId: string, target: string = "RELIABILITY_PLATFORM", actionType: string = "INVESTIGATE_INCIDENT"): Promise<any> {
    return this.client.post(`/v1/events/${eventId}/respond?tenant_id=${tenantId}`, { target, action_type: actionType });
  }

  async resolve(eventId: string, tenantId: string, targetStatus: string = "RESOLVED"): Promise<any> {
    return this.client.post(`/v1/events/${eventId}/resolve?tenant_id=${tenantId}`, { target_status: targetStatus });
  }

  async getAnalyticsReport(tenantId: string): Promise<any> {
    return this.client.get(`/v1/events/analytics?tenant_id=${tenantId}`);
  }

  async getPatterns(tenantId: string): Promise<any> {
    return this.client.get(`/v1/events/patterns?tenant_id=${tenantId}`);
  }
}
