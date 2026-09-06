package com.llmengine;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class DecisionGovernanceClient {
    private final String baseUrl;
    private final String apiKey;
    private final HttpClient httpClient;

    public DecisionGovernanceClient(String baseUrl, String apiKey) {
        this.baseUrl = baseUrl.replaceAll("/$", "");
        this.apiKey = apiKey;
        this.httpClient = HttpClient.newHttpClient();
    }

    public String createDecision(String tenantId, String title, String decisionType, String description) throws IOException, InterruptedException {
        String jsonPayload = String.format(
            "{\"title\":\"%s\",\"decision_type\":\"%s\",\"description\":\"%s\"}",
            title, decisionType, description
        );

        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "/v1/decisions"))
            .header("Content-Type", "application/json")
            .header("x-tenant-id", tenantId)
            .header("Authorization", "Bearer " + apiKey)
            .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
            .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

    public String listDecisions(String tenantId) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "/v1/decisions"))
            .header("x-tenant-id", tenantId)
            .header("Authorization", "Bearer " + apiKey)
            .GET()
            .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

    public String getDecision(String tenantId, String decisionId) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "/v1/decisions/" + decisionId))
            .header("x-tenant-id", tenantId)
            .header("Authorization", "Bearer " + apiKey)
            .GET()
            .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }
}
