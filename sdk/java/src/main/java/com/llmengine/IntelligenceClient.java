package com.llmengine;

public class IntelligenceClient {
    private final String baseUrl;
    private final String apiKey;

    public IntelligenceClient(String baseUrl, String apiKey) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }

    public String ingestSignal(String source, String signalType, String message, String tenantId) {
        return "IngestSignal " + source + "/" + signalType + " for tenant " + tenantId + " at " + baseUrl;
    }

    public String listRecommendations(String tenantId) {
        return "ListRecommendations for tenant " + tenantId + " at " + baseUrl;
    }
}
