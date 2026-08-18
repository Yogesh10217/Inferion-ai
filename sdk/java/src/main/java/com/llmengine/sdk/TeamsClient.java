package com.llmengine.sdk;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class TeamsClient {
    private final String baseUrl;
    private final String apiKey;
    private final HttpClient httpClient;

    public TeamsClient(String baseUrl, String apiKey) {
        this.baseUrl = baseUrl.replaceAll("/$", "");
        this.apiKey = apiKey;
        this.httpClient = HttpClient.newHttpClient();
    }

    public String createTeam(String name, String teamType) throws Exception {
        String url = this.baseUrl + "/v1/teams";
        String body = "{\"name\":\"" + name + "\",\"team_type\":\"" + teamType + "\"}";
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

    public String runTeam(String teamId, String goal) throws Exception {
        String url = this.baseUrl + "/v1/teams/" + teamId + "/run";
        String body = "{\"goal\":\"" + goal + "\"}";
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }
}
