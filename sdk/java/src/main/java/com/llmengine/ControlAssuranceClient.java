package com.llmengine;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

/**
 * Java SDK Client for Control Assurance Subsystem (Phase 5.38).
 */
public class ControlAssuranceClient {
    private final String baseUrl;
    private final String apiKey;
    private final HttpClient httpClient;

    public ControlAssuranceClient(String baseUrl, String apiKey) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
        this.httpClient = HttpClient.newHttpClient();
    }

    public String listControls(String tenantId) throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/v1/control-assurance/controls"))
                .header("X-Tenant-ID", tenantId)
                .header("Authorization", "Bearer " + apiKey)
                .GET()
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

    public String getAnalytics(String tenantId) throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/v1/control-assurance/analytics"))
                .header("X-Tenant-ID", tenantId)
                .header("Authorization", "Bearer " + apiKey)
                .GET()
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }
}
