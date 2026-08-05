export class KnowledgeClient {
  private _fetch: (url: string, options: any) => Promise<Response>;
  private _baseUrl: string;
  private _headers: Record<string, string>;

  constructor(fetchImpl: (url: string, options: any) => Promise<Response>, baseUrl: string, headers: Record<string, string>) {
    this._fetch = fetchImpl;
    this._baseUrl = baseUrl;
    this._headers = headers;
  }

  private async request(method: string, path: string, body?: any, isStream = false) {
    const res = await this._fetch(`${this._baseUrl}${path}`, {
      method,
      headers: this._headers,
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) throw new Error(`API Error ${res.status}`);
    return isStream ? res : res.json();
  }

  async create(name: string, description: string = '') {
    return this.request('POST', '/v1/knowledge/create', { name, description });
  }

  async list() {
    return this.request('GET', '/v1/knowledge/list');
  }

  async search(indexId: string, query: string, k: number = 5) {
    return this.request('POST', '/v1/knowledge/search', { index_id: indexId, query, k });
  }

  async retrieve(documentId: string) {
    return this.request('GET', `/v1/knowledge/retrieve/${documentId}`);
  }

  async delete(resourceType: 'index'|'document', id: string) {
    return this.request('DELETE', `/v1/knowledge/delete/${resourceType}/${id}`);
  }

  async reindex(indexId: string) {
    return this.request('POST', '/v1/knowledge/reindex', { index_id: indexId }, true);
  }

  async citations(query: string, indexId: string) {
    return this.request('POST', '/v1/knowledge/citations', { query, index_id: indexId });
  }

  async jobs() {
    return this.request('GET', '/v1/knowledge/jobs');
  }

  async status(jobId: string) {
    return this.request('GET', `/v1/knowledge/status/${jobId}`);
  }
}
