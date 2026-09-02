package com.llmengine;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class FinOpsIntelligenceClient {
    private final String baseUrl;
    private final HttpClient client;

    public FinOpsIntelligenceClient(String baseUrl) {
        this.baseUrl = baseUrl.replaceAll("/$", "");
        this.client = HttpClient.newHttpClient();
    }

    public String listCosts(String tenantId) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/v1/finops/costs?tenant_id=" + tenantId))
                .GET()
                .build();
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

    public String listBudgets(String tenantId) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/v1/finops/budgets?tenant_id=" + tenantId))
                .GET()
                .build();
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }
}
