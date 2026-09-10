package com.llmengine.sdk;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

/**
 * Java SDK Client for Platform Integration Fabric (Phase 5.58).
 */
public class PlatformIntegrationClient {
    private final String baseUrl;
    private final String apiKey;
    private final HttpClient client;

    public PlatformIntegrationClient(String baseUrl, String apiKey) {
        this.baseUrl = baseUrl.replaceAll("/$", "");
        this.apiKey = apiKey;
        this.client = HttpClient.newHttpClient();
    }

    public String buildContext(String tenantId) throws Exception {
        HttpRequest.Builder builder = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/v1/platform-integration/context"))
                .header("Content-Type", "application/json")
                .header("X-Tenant-ID", tenantId)
                .POST(HttpRequest.BodyPublishers.ofString("{}"));

        if (apiKey != null && !apiKey.isEmpty()) {
            builder.header("Authorization", "Bearer " + apiKey);
        }

        HttpResponse<String> response = client.send(builder.build(), HttpResponse.BodyHandlers.ofString());
        return response.body();
    }
}
