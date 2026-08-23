/**
 * TypeScript SDK Client for Enterprise AI Architecture Platform (Phase 5.26).
 */

export class ArchitectureClient {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async createNode(name: string, nodeType: string, environment: string = 'production', attributes: Record<string, any> = {}): Promise<any> {
    return this.client.request('POST', '/v1/architecture/nodes', {
      name,
      node_type: nodeType,
      environment,
      attributes,
    });
  }

  async listNodes(environment?: string): Promise<any[]> {
    return this.client.request('GET', '/v1/architecture/nodes', undefined, { environment });
  }

  async addDependency(sourceNodeId: string, targetNodeId: string, dependencyType: string = 'DEPENDS_ON'): Promise<any> {
    return this.client.request('POST', '/v1/architecture/dependencies', {
      source_node_id: sourceNodeId,
      target_node_id: targetNodeId,
      dependency_type: dependencyType,
    });
  }

  async getTopology(environment: string = 'production'): Promise<any> {
    return this.client.request('GET', '/v1/architecture/topology', undefined, { environment });
  }

  async createSnapshot(environment: string = 'production', description: string = 'Snapshot'): Promise<any> {
    return this.client.request('POST', '/v1/architecture/snapshots', { environment, description });
  }

  async proposeChange(idempotencyKey: string, actionType: string, targetNodeIds: string[]): Promise<any> {
    return this.client.request('POST', '/v1/architecture/changes', {
      idempotency_key: idempotencyKey,
      action_type: actionType,
      target_node_ids: targetNodeIds,
    });
  }

  async getDrift(): Promise<any[]> {
    return this.client.request('GET', '/v1/architecture/drift');
  }

  async getTrust(): Promise<any> {
    return this.client.request('GET', '/v1/architecture/trust');
  }

  async getAnalytics(): Promise<any> {
    return this.client.request('GET', '/v1/architecture/analytics');
  }
}
