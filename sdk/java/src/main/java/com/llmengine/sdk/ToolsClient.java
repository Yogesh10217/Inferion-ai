package com.llmengine.sdk;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class ToolsClient {
    private final String baseUrl;
    private final String apiKey;
    private final HttpClient httpClient;

    public ToolsClient(String baseUrl, String apiKey) {
        this.baseUrl = baseUrl.replaceAll("/$", "");
        this.apiKey = apiKey;
        this.httpClient = HttpClient.newHttpClient();
    }

    public String listTools(String tenantId) throws Exception {
        String url = this.baseUrl + "/v1/tools?tenant_id=" + tenantId;
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Accept", "application/json")
                .GET()
                .build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

    public String executeTool(String toolId, String jsonParams) throws Exception {
        String url = this.baseUrl + "/v1/tools/" + toolId + "/execute";
        String body = "{\"parameters\":" + jsonParams + "}";
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }
}
