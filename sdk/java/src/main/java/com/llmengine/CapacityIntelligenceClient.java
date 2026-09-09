package com.llmengine;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

/**
 * Java SDK Client for Enterprise AI Capacity Intelligence Platform (Phase 5.56).
 */
public class CapacityIntelligenceClient {
    private final String baseUrl;
    private final String apiKey;
    private final HttpClient httpClient;

    public CapacityIntelligenceClient(String baseUrl, String apiKey) {
        this.baseUrl = baseUrl.replaceAll("/$", "");
        this.apiKey = apiKey;
        this.httpClient = HttpClient.newHttpClient();
    }

    public String registerResource(String tenantId, String jsonPayload) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/v1/capacity/resources"))
                .header("Content-Type", "application/json")
                .header("X-Tenant-ID", tenantId)
                .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

    public String assessCapacity(String tenantId, String jsonPayload) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/v1/capacity/assessments"))
                .header("Content-Type", "application/json")
                .header("X-Tenant-ID", tenantId)
                .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

    public String forecastCapacity(String tenantId, String jsonPayload) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/v1/capacity/forecasts"))
                .header("Content-Type", "application/json")
                .header("X-Tenant-ID", tenantId)
                .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }
}
