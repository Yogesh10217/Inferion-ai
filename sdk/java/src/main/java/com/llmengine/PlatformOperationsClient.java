package com.llmengine;

public class PlatformOperationsClient {
    private final String baseUrl;
    private final String apiKey;

    public PlatformOperationsClient(String baseUrl, String apiKey) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }

    public String listServices(String tenantId) {
        return "ListServices for tenant " + tenantId + " at " + baseUrl;
    }

    public String executeRemediation(String planId, String tenantId) {
        return "ExecuteRemediation plan " + planId + " for tenant " + tenantId;
    }
}
