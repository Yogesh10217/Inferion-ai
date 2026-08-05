import { KnowledgeClient } from './knowledge.js';
import { ChatCompletionRequest, ChatCompletionResponse } from './models.js';
import { APIKeyAuth } from './auth.js';
import { AuthenticationError, RateLimitError, SDKError } from './errors.js';

export interface ClientConfig {
  baseUrl?: string;
  apiKey?: string;
  organizationId?: string;
  timeoutMs?: number;
}

export class LLMEngineClient {
  public knowledge: KnowledgeClient;
  private baseUrl: string;
  private headers: Record<string, string>;

  constructor(config: ClientConfig) {
    this.baseUrl = (config.baseUrl || 'http://localhost:8000').replace(/\/+$/, '');
    this.headers = { 'Content-Type': 'application/json' };

    if (config.organizationId) {
      this.headers['X-Organization-ID'] = config.organizationId;
    }
    this.knowledge = new KnowledgeClient(fetch, this.baseUrl, this.headers);
    if (config.apiKey) {
      Object.assign(this.headers, new APIKeyAuth(config.apiKey).getHeaders());
    }
  }

  async health(): Promise<Record<string, any>> {
    const res = await fetch(`${this.baseUrl}/health`, { headers: this.headers });
    return res.json();
  }

  async createChatCompletion(request: ChatCompletionRequest): Promise<ChatCompletionResponse> {
    const res = await fetch(`${this.baseUrl}/v1/chat/completions`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(request),
    });

    if (res.status === 401) throw new AuthenticationError();
    if (res.status === 429) throw new RateLimitError();
    if (!res.ok) throw new SDKError(`API Error ${res.status}`);

    return res.json() as Promise<ChatCompletionResponse>;
  }
}
