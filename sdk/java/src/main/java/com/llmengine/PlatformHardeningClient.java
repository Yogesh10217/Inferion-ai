package com.llmengine;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class PlatformHardeningClient {
    private final String baseUrl;
    private final HttpClient httpClient;

    public PlatformHardeningClient(String baseUrl) {
        this.baseUrl = baseUrl.replaceAll("/$", "");
        this.httpClient = HttpClient.newHttpClient();
    }

    public String runAudit(String tenantId) throws IOException, InterruptedException {
        String url = this.baseUrl + "/v1/platform-hardening/audit";
        String jsonPayload = String.format("{\"tenant_id\":\"%s\",\"include_ast_scan\":true}", tenantId);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Content-Type", "application/json")
                .header("X-Tenant-ID", tenantId)
                .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }
}
