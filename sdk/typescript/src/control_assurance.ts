/**
 * TypeScript SDK Client for Enterprise AI Control Assurance (Phase 5.38).
 */

export interface AssuranceReport {
    report_id: string;
    tenant_id: string;
    total_controls: number;
    assurance_score_avg: float;
    insights: any[];
}

export class ControlAssuranceClient {
    private baseUrl: string;
    private apiKey: string;

    constructor(baseUrl: string, apiKey: string) {
        this.baseUrl = baseUrl.replace(/\/$/, "");
        this.apiKey = apiKey;
    }

    private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
        const url = `${this.baseUrl}${path}`;
        const headers = {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${this.apiKey}`,
            "X-Tenant-ID": "default",
            ...options.headers,
        };

        const response = await fetch(url, { ...options, headers });
        if (!response.ok) {
            throw new Error(`Control Assurance API Error: ${response.statusText}`);
        }
        return response.json() as Promise<T>;
    }

    async listControls(category?: string): Promise<Record<string, any>[]> {
        const query = category ? `?category=${encodeURIComponent(category)}` : "";
        return this.request<Record<string, any>[]>(`/v1/control-assurance/controls${query}`, { method: "GET" });
    }

    async registerControl(code: string, name: string, description: string, category: string = "SECURITY"): Promise<Record<string, any>> {
        return this.request<Record<string, any>>(
            `/v1/control-assurance/controls?code=${encodeURIComponent(code)}&name=${encodeURIComponent(name)}&description=${encodeURIComponent(description)}&category=${category}`,
            { method: "POST" }
        );
    }

    async evaluateControl(controlId: string, scopeTargetId: string = "InferenceEngine_Core"): Promise<Record<string, any>> {
        return this.request<Record<string, any>>(
            `/v1/control-assurance/controls/${encodeURIComponent(controlId)}/evaluate?scope_target_id=${encodeURIComponent(scopeTargetId)}`,
            { method: "POST" }
        );
    }

    async getAssurance(targetId: string = "InferenceEngine_Core"): Promise<Record<string, any>> {
        return this.request<Record<string, any>>(
            `/v1/control-assurance/assurance?target_id=${encodeURIComponent(targetId)}`,
            { method: "GET" }
        );
    }

    async getAnalytics(): Promise<AssuranceReport> {
        return this.request<AssuranceReport>("/v1/control-assurance/analytics", { method: "GET" });
    }

    async runFullLifecycle(): Promise<Record<string, any>> {
        return this.request<Record<string, any>>("/v1/control-assurance/lifecycle/run", { method: "POST" });
    }
}
