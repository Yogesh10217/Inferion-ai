/**
 * TypeScript SDK Client for Enterprise AI Knowledge Intelligence Platform (Phase 5.35).
 */

export class KnowledgeIntelligenceClient {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async createItem(tenantId: string, title: str, knowledgeType: string = "DOCUMENT", classification: string = "INTERNAL"): Promise<any> {
    return this.client.post(`/v1/knowledge/items?tenant_id=${tenantId}`, { title, knowledge_type: knowledgeType, classification });
  }

  async listItems(tenantId: string): Promise<any> {
    return this.client.get(`/v1/knowledge/items?tenant_id=${tenantId}`);
  }

  async getItem(itemId: string, tenantId: string): Promise<any> {
    return this.client.get(`/v1/knowledge/items/${itemId}?tenant_id=${tenantId}`);
  }

  async getProvenance(targetId: string, tenantId: string): Promise<any> {
    return this.client.get(`/v1/knowledge/provenance?target_id=${targetId}&tenant_id=${tenantId}`);
  }

  async getGraph(startNodeId: string, tenantId: string, depth: number = 2): Promise<any> {
    return this.client.get(`/v1/knowledge/graph?start_node_id=${startNodeId}&tenant_id=${tenantId}&depth=${depth}`);
  }

  async retrieve(tenantId: string, query: string): Promise<any> {
    return this.client.post(`/v1/knowledge/retrieval?tenant_id=${tenantId}`, { query });
  }

  async assembleContext(tenantId: string, itemIds: string[]): Promise<any> {
    return this.client.post(`/v1/knowledge/context?tenant_id=${tenantId}`, { item_ids: itemIds });
  }

  async getAnalytics(tenantId: string): Promise<any> {
    return this.client.get(`/v1/knowledge/analytics?tenant_id=${tenantId}`);
  }
}
