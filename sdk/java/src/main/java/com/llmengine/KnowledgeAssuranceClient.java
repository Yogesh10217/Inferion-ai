package com.llmengine;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class KnowledgeAssuranceClient {
    private final String baseUrl;
    private final String apiKey;
    private final HttpClient httpClient;

    public KnowledgeAssuranceClient(String baseUrl, String apiKey) {
        this.baseUrl = baseUrl.replaceAll("/$", "");
        this.apiKey = apiKey;
        this.httpClient = HttpClient.newHttpClient();
    }

    public String getStatus(String tenantId) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "/v1/knowledge/status"))
            .header("x-tenant-id", tenantId)
            .header("Authorization", "Bearer " + apiKey)
            .GET()
            .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

    public String createReference(String tenantId, String externalKey, String resourceType, String classification) throws IOException, InterruptedException {
        String jsonPayload = String.format(
            "{\"external_key\":\"%s\",\"resource_type\":\"%s\",\"classification\":\"%s\"}",
            externalKey, resourceType, classification
        );

        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "/v1/knowledge/references"))
            .header("Content-Type", "application/json")
            .header("x-tenant-id", tenantId)
            .header("Authorization", "Bearer " + apiKey)
            .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
            .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

    public String evaluateTrust(String tenantId, String targetResourceId) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "/v1/knowledge/trust/" + targetResourceId))
            .header("x-tenant-id", tenantId)
            .header("Authorization", "Bearer " + apiKey)
            .GET()
            .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

    public String assessAssurance(String tenantId, String targetResourceId) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "/v1/knowledge/assurance/" + targetResourceId))
            .header("x-tenant-id", tenantId)
            .header("Authorization", "Bearer " + apiKey)
            .GET()
            .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }
}
