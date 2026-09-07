package com.llmengine;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class DecisionIntelligenceClient {
    private final String baseUrl;
    private final String apiKey;
    private final String tenantId;
    private final HttpClient httpClient;

    public DecisionIntelligenceClient(String baseUrl, String apiKey, String tenantId) {
        this.baseUrl = baseUrl != null ? baseUrl.replaceAll("/$", "") : "http://localhost:8000";
        this.apiKey = apiKey;
        this.tenantId = tenantId != null ? tenantId : "default";
        this.httpClient = HttpClient.newHttpClient();
    }

    public String createDecision(String title, String description, String decisionType) throws Exception {
        String jsonPayload = String.format(
            "{\"title\":\"%s\",\"description\":\"%s\",\"decision_type\":\"%s\"}",
            title, description != null ? description : "", decisionType != null ? decisionType : "OPERATIONAL"
        );

        HttpRequest.Builder builder = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "/v1/decisions"))
            .header("Content-Type", "application/json")
            .header("X-Tenant-ID", tenantId)
            .POST(HttpRequest.BodyPublishers.ofString(jsonPayload));

        if (apiKey != null) {
            builder.header("Authorization", "Bearer " + apiKey);
        }

        HttpResponse<String> response = httpClient.send(builder.build(), HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() >= 400) {
            throw new RuntimeException("Create decision failed: " + response.body());
        }
        return response.body();
    }
}
