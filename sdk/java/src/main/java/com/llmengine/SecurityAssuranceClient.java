package com.llmengine;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class SecurityAssuranceClient {
    private final String baseUrl;
    private final String apiKey;
    private final HttpClient httpClient;

    public SecurityAssuranceClient(String baseUrl, String apiKey) {
        this.baseUrl = baseUrl.replaceAll("/$", "");
        this.apiKey = apiKey;
        this.httpClient = HttpClient.newHttpClient();
    }

    public String registerAsset(String tenantId, String name, String assetType) throws IOException, InterruptedException {
        String jsonPayload = String.format(
            "{\"name\":\"%s\",\"asset_type\":\"%s\"}",
            name, assetType
        );

        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "/v1/security/assets"))
            .header("Content-Type", "application/json")
            .header("x-tenant-id", tenantId)
            .header("Authorization", "Bearer " + apiKey)
            .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
            .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

    public String evaluatePosture(String tenantId) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "/v1/security/posture"))
            .header("x-tenant-id", tenantId)
            .header("Authorization", "Bearer " + apiKey)
            .GET()
            .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }
}
