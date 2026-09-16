/**
 * TypeScript SDK for Model Intelligence Platform (Phase 5.44).
 */

export class ModelIntelligenceClient {
  private baseUrl: string;
  private apiKey: string;

  constructor(baseUrl: string, apiKey: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  async listModels(): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/models`, {
      headers: { Authorization: `Bearer ${this.apiKey}` },
    });
    return res.json();
  }

  async evaluateModel(modelId: string, versionTag: string = "1.0.0"): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/models/evaluate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify({ model_id: modelId, version_tag: versionTag }),
    });
    return res.json();
  }

  async getTrust(modelId: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/models/${modelId}/trust`, {
      headers: { Authorization: `Bearer ${this.apiKey}` },
    });
    return res.json();
  }

  async getAssurance(modelId: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/models/${modelId}/assurance`, {
      headers: { Authorization: `Bearer ${this.apiKey}` },
    });
    return res.json();
  }

  async getAnalytics(): Promise<any> {
    const res = await fetch(`${this.baseUrl}/v1/models/analytics/summary`, {
      headers: { Authorization: `Bearer ${this.apiKey}` },
    });
    return res.json();
  }
}

export interface ChatMessage {
  role: string;
  content: string;
}

export interface ChatCompletionRequest {
  model: string;
  messages: ChatMessage[];
  temperature?: number;
  max_tokens?: number;
  stream?: boolean;
  metadata?: Record<string, any>;
}

export interface ChatCompletionChoice {
  index: number;
  message: ChatMessage;
  finish_reason: string;
}

export interface UsageInfo {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

export interface ChatCompletionResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: ChatCompletionChoice[];
  usage?: UsageInfo;
}

