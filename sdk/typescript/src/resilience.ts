/**
 * TypeScript SDK Client for Enterprise AI Platform Resilience (Phase 5.37).
 */

export interface ResilienceServiceRegistration {
    status: string;
    service: Record<string, any>;
}

export interface ResilienceReport {
    report_id: string;
    tenant_id: string;
    availability_pct: number;
    metrics: any[];
    insights: any[];
}

export class ResilienceClient {
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
            throw new Error(`Platform Resilience API Error: ${response.statusText}`);
        }
        return response.json() as Promise<T>;
    }

    async registerService(serviceName: string, tier: string = "TIER_2_STANDARD", region: string = "us-east-1"): Promise<ResilienceServiceRegistration> {
        return this.request<ResilienceServiceRegistration>(
            `/v1/resilience/services/register?service_name=${encodeURIComponent(serviceName)}&tier=${tier}&region=${region}`,
            { method: "POST" }
        );
    }

    async evaluateCapacity(resourceId: string): Promise<Record<string, any>> {
        return this.request<Record<string, any>>(
            `/v1/resilience/capacity/evaluate?resource_id=${encodeURIComponent(resourceId)}`,
            { method: "GET" }
        );
    }

    async requestFailover(serviceId: string, sourceRegion: string = "us-east-1", targetRegion: string = "us-west-2"): Promise<Record<string, any>> {
        return this.request<Record<string, any>>(
            `/v1/resilience/failover/request?service_id=${encodeURIComponent(serviceId)}&source_region=${sourceRegion}&target_region=${targetRegion}`,
            { method: "POST" }
        );
    }

    async activateDR(drPlanId: string): Promise<Record<string, any>> {
        return this.request<Record<string, any>>(
            `/v1/resilience/dr/activate?dr_plan_id=${encodeURIComponent(drPlanId)}`,
            { method: "POST" }
        );
    }

    async assessReadiness(serviceId: string): Promise<Record<string, any>> {
        return this.request<Record<string, any>>(
            `/v1/resilience/readiness/assess?service_id=${encodeURIComponent(serviceId)}`,
            { method: "GET" }
        );
    }

    async getAnalytics(): Promise<ResilienceReport> {
        return this.request<ResilienceReport>("/v1/resilience/analytics/report", { method: "GET" });
    }

    async runFullLifecycle(): Promise<Record<string, any>> {
        return this.request<Record<string, any>>("/v1/resilience/lifecycle/run", { method: "POST" });
    }
}
