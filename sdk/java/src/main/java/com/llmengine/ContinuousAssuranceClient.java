package com.llmengine;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class ContinuousAssuranceClient {
    private final String baseUrl;
    private final String apiKey;
    private final HttpClient httpClient;

    public ContinuousAssuranceClient(String baseUrl, String apiKey) {
        this.baseUrl = baseUrl.replaceAll("/$", "");
        this.apiKey = apiKey;
        this.httpClient = HttpClient.newHttpClient();
    }

    public String recordObservation(String tenantId, String jsonPayload) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/v1/continuous-assurance/observations"))
                .header("Content-Type", "application/json")
                .header("X-Tenant-ID", tenantId)
                .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }
}
